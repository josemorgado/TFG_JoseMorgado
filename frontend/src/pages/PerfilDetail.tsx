// src/pages/PerfilDetail.tsx
import { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import type { Usuario } from "../types/perfil";
import { getUsuarioById } from "../api/perfil";
import "../styles/perfilDetail.css";
import type { Queja } from "../types/queja";
import { getQuejasByUser } from "../api/quejas";
import { useAuth } from "../context/AuthContext";
import editIcon from "../assets/icons/pencil-icon.png";
import { getTopCategorias } from "../api/stats";
import type { CategoriaStats } from "../api/stats";
import LogoutButton from "../components/LogoutButton";
export default function PerfilDetail() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [usuario, setUsuario] = useState<Usuario | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [quejas, setQuejas] = useState<Queja[]>([]);
  const { user: userActivo } = useAuth();
  const [topCategoria, setTopCategoria] = useState<CategoriaStats | null>(null);

  const estadoCompleto: Record<string, string> = {
    PEN: "Pendiente",
    ENP: "En Progreso",
    RES: "Resuelta",
    REC: "Rechazada",
  };

  useEffect(() => {
    if (!id) {
      setError("Falta la ID en la URL.");
      setLoading(false);
      return;
    }

    const userId = Number(id);
    if (Number.isNaN(userId)) {
      setError("La ID no es válida.");
      setLoading(false);
      return;
    }

    (async () => {
      try {
        setLoading(true);
        setError(null);

        // Cargamos todo en paralelo
        const [usuarioData, quejasResp, topCats] = await Promise.all([
          getUsuarioById(userId),
          getQuejasByUser(userId),
          getTopCategorias({
            user_id: userId,
            limit: 1,
            include_zero: false,
            ordering: "-total",
          }),
        ]);

        setUsuario(usuarioData);
        setQuejas(quejasResp);
        setTopCategoria(topCats?.[0] ?? null);
      } catch (e) {
        console.error(e);
        setError("No se pudo cargar el perfil.");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const iniciales = useMemo(() => {
    if (!usuario) return "";
    const nombre =
      `${usuario.first_name || ""} ${usuario.last_name || ""}`.trim();
    if (nombre.length > 0) {
      const partes = nombre.split(/\s+/).filter(Boolean);
      const letras = partes.slice(0, 2).map((p) => p[0]?.toUpperCase() || "");
      return (
        letras.join("") || (usuario.username?.slice(0, 2).toUpperCase() ?? "")
      );
    }
    return usuario.username?.slice(0, 2).toUpperCase() ?? "";
  }, [usuario]);

  if (loading) return <p>Cargando...</p>;
  if (error) return <p className="error">{error}</p>;
  if (!usuario) return <p>No hay datos de usuario</p>;

  const fotoPerfil = (usuario as any)?.perfil?.foto_perfil || null;
  const esMiPerfil = userActivo?.id === usuario.id;

  return (
    <div className="perfil-detail-page">
      <div className="perfil-detail">
        <div className="perfil-card">
          <div className="perfil-avatar-wrapper">
            <div className="perfil-avatar">
              {fotoPerfil ? (
                <img src={fotoPerfil} className="perfil-avatar__img" alt="foto" />
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

          </div>


          <div className="perfil-info">
            <div className="perfil-info-header">
              <h2 className="perfil-title">
                Perfil de: <strong>{usuario.username}</strong>
              </h2>
            </div>

            <div className="perfil-data">
              <p className="perfil-data-fields">
                <strong>Nombre completo:</strong> {usuario.first_name}{" "}
                {usuario.last_name}
              </p>

              {usuario.perfil.edad && (
                <p className="perfil-data-fields">
                  <strong>Edad:</strong> {usuario.perfil.edad} años
                </p>
              )}

              <p className="perfil-data-fields">
                <strong>Rol:</strong>{" "}
                {usuario.perfil.moderator ? "Moderador municipal" : "Ciudadano"}
              </p>

              <p className="perfil-data-fields">
                <strong>Biografía:</strong>{" "}
                {usuario.perfil.biografia || "Sin descripción."}
              </p>

              <p className="perfil-data-fields">
                <strong>Miembro desde:</strong>{" "}
                {new Date(usuario.date_joined).toLocaleDateString()}
              </p>

              <p className="perfil-data-fields">
                <strong>Quejas registradas:</strong> {quejas.length}
              </p>

              <p className="perfil-data-fields">
                {topCategoria ? (
                  <>
                    <strong>Categoría más usada:</strong> {topCategoria.nombre}{" "}

                    ({topCategoria.total})
                  </>
                ) : (
                  "Sin datos"
                )}
              </p>
            </div>
          </div>
        </div>

        {/* ---------- LISTA DE QUEJAS -------- */}
        <h3 className="quejas-title">Quejas del usuario</h3>

        {quejas.length > 0 ? (
          <div className="quejas-grid">
            {quejas.map((q) => (
              <div
                className="queja-card"
                key={q.id}
                onClick={() => navigate(`/quejas/${q.id}`)}
              >
                <h4 className="queja-title">{q.titulo}</h4>
                <p className="queja-meta">
                  Estado: {estadoCompleto[q.estado] || q.estado} · Fecha:{" "}
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
