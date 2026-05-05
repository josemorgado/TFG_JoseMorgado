import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import type { Usuario } from "../types/perfil";
import type { Queja } from "../types/queja";
import type { CategoriaStats } from "../api/stats";

import { getUsuarioById } from "../api/perfil";
import { getQuejasByUser } from "../api/quejas";
import { getTopCategorias } from "../api/stats";

import { useAuth } from "../context/AuthContext";

import LogoutButton from "../components/LogoutButton";
import ModeradorButton from "../components/ModeradorButton";
import ModButton from "../components/ModButton";
import PageError from "../components/PageError";
import PageEmpty from "../components/PageEmpty";
import PageInfo from "../components/PageInfo";

import editIcon from "../assets/icons/pencil-icon.png";
import "../styles/PerfilDetail.css";

const MAPEO_ESTADOS: Record<string, string> = {
  PEN: "Pendiente",
  ENP: "En Progreso",
  RES: "Resuelta",
  REC: "Rechazada",
};

export default function PerfilDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user: usuarioActual } = useAuth();

  const idUsuario = Number(id);

  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [quejas, setQuejas] = useState<Queja[]>([]);
  const [categoriaDestacada, setCategoriaDestacada] =
    useState<CategoriaStats | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  if (!id) {
    return <PageError message="Falta la ID en la URL." />;
  }

  if (Number.isNaN(idUsuario)) {
    return <PageError message="La ID no es válida." />;
  }

  useEffect(() => {
    let cancelado = false;

    (async () => {
      try {
        setLoading(true);
        setError(null);

        const [datosUsuario, respuestaQuejas, categoriasTop] =
          await Promise.all([
            getUsuarioById(idUsuario),
            getQuejasByUser(idUsuario),
            getTopCategorias({
              user_id: idUsuario,
              limit: 1,
              include_zero: false,
              ordering: "-total",
            }),
          ]);

        if (!cancelado) {
          setUsuario(datosUsuario);
          setQuejas(respuestaQuejas);
          setCategoriaDestacada(categoriasTop?.[0] ?? null);
        }
      } catch (err: any) {
        if (!cancelado) {
          if (err?.response?.status === 404) {
            setError("Este usuario no existe.");
          } else {
            setError("No se pudo cargar el perfil.");
          }
        }
      } finally {
        if (!cancelado) setLoading(false);
      }
    })();

    return () => {
      cancelado = true;
    };
  }, [idUsuario]);

  const iniciales = useMemo(() => {
    if (!usuario) return "";

    const nombreCompleto = `${usuario.first_name || ""} ${
      usuario.last_name || ""
    }`.trim();

    if (nombreCompleto) {
      return nombreCompleto
        .split(/\s+/)
        .slice(0, 2)
        .map((p) => p[0].toUpperCase())
        .join("");
    }

    return usuario.username?.slice(0, 2).toUpperCase() ?? "";
  }, [usuario]);

  if (loading) {
    return <PageInfo message="Cargando perfil…" />;
  }

  if (error) {
    return <PageError message={error} />;
  }

  if (!usuario) {
    return <PageEmpty message="No hay datos para este usuario." />;
  }

  if (!usuarioActual) {
    return <PageInfo message="Debes iniciar sesión para ver este perfil." />;
  }

  const imagenPerfil = usuario.perfil?.foto_perfil ?? null;
  const esMiPerfil = usuarioActual.id === usuario.id;

  const puedeVerPanelModerador =
    esMiPerfil &&
    (usuario.perfil?.moderator ||
      usuarioActual.is_staff ||
      usuarioActual.is_superuser);

  return (
    <div className="perfil-detail-page">
      <div className="perfil-detail">
        <div className="perfil-card">
          <div className="perfil-avatar-wrapper">
            <div className="perfil-avatar">
              {imagenPerfil ? (
                <img
                  src={imagenPerfil}
                  className="perfil-avatar__img"
                  alt="Foto de perfil"
                />
              ) : (
                <div className="perfil-avatar__fallback">{iniciales}</div>
              )}

              {esMiPerfil && (
                <button
                  className="avatar-edit-btn avatar-edit-btn--icon"
                  onClick={() => navigate(`/perfil/${usuario.id}/update`)}
                  style={{ backgroundImage: `url(${editIcon})` }}
                  aria-label="Editar perfil"
                />
              )}
            </div>

            {esMiPerfil && (
              <div className="logout-wrapper">
                <LogoutButton />
              </div>
            )}

            {puedeVerPanelModerador && (
              <div className="logout-wrapper">
                <ModeradorButton />
              </div>
            )}

            {!esMiPerfil && usuarioActual.perfil?.moderator && (
              <div className="logout-wrapper">
                <ModButton
                  targetUserId={usuario.id}
                  targetIsModerator={usuario.perfil.moderator}
                  onUpdated={setUsuario}
                />
              </div>
            )}
          </div>

          <div className="perfil-info">
            <h2 className="perfil-title">
              Perfil de: <strong>{usuario.username}</strong>
            </h2>

            <div className="perfil-data">
              <p className="perfil-data-fields">
                <strong>Nombre completo:</strong>{" "}
                {usuario.first_name} {usuario.last_name}
              </p>

              {usuario.perfil.edad && (
                <p className="perfil-data-fields">
                  <strong>Edad:</strong> {usuario.perfil.edad} años
                </p>
              )}

              <p className="perfil-data-fields">
                <strong>Rol:</strong>{" "}
                {usuario.perfil.moderator
                  ? "Moderador municipal"
                  : "Ciudadano"}
              </p>

              <p className="perfil-data-fields">
                <strong>Biografía:</strong>{" "}
                {usuario.perfil.biografia || "Sin descripción."}
              </p>

              <p className="perfil-data-fields">
                <strong>Miembro desde:</strong> {usuario.date_joined}
              </p>

              <p className="perfil-data-fields">
                <strong>Quejas registradas:</strong> {quejas.length}
              </p>

              {categoriaDestacada && (
                <p className="perfil-data-fields">
                  <strong>Categoría más usada:</strong>{" "}
                  {categoriaDestacada.nombre} ({categoriaDestacada.total})
                </p>
              )}
            </div>
          </div>
        </div>

        <h3 className="quejas-title">Quejas del usuario</h3>

        {quejas.length > 0 ? (
          <div className="quejas-grid">
            {quejas.map((q) => (
              <div
                key={q.id}
                className="queja-card"
                onClick={() => navigate(`/quejas/${q.id}`)}
              >
                <h4 className="queja-title">{q.titulo}</h4>
                <p className="queja-meta">
                  Estado: {MAPEO_ESTADOS[q.estado] || q.estado} · Fecha:{" "}
                  {q.fecha_creacion}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty-state">
            Este usuario no tiene quejas registradas.
          </div>
        )}
      </div>
    </div>
  );
}