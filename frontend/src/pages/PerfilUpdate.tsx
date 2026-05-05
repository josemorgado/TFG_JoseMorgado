import { useEffect, useLayoutEffect, useMemo, useRef, useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";

import { getUsuarioById, updateUsuario, deleteUsuario } from "../api/perfil";
import { useAuth } from "../context/AuthContext";

import type { Usuario } from "../types/perfil";

import deleteIcon from "../assets/icons/delete-icon.png";
import "../styles/form-layout.css";

import PageError from "../components/PageError";
import PageInfo from "../components/PageInfo";

export default function PerfilUpdate() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const { logout } = useAuth();
  if (!id) {
    return <PageError message="Falta la ID en la URL." />;
  }
  const idNumerico = Number(id);
  if (Number.isNaN(idNumerico)) {
    return <PageError message="La ID no es válida." />;
  }
  const formularioGuardado = location.state?.formData || null;

  const refBiografia = useRef<HTMLTextAreaElement | null>(null);
  const refInputArchivo = useRef<HTMLInputElement | null>(null);

  const [usuario, setUsuario] = useState<Usuario | null>(null);

  const [formulario, setFormulario] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    telefono: "",
    direccion: "",
    fecha_nacimiento: "",
    genero: "O",
    biografia: "",
    foto_url: null as string | null,
    foto_perfil: null as File | null,
    eliminar_foto: false,
  });

  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [errorFormulario, setErrorFormulario] = useState<string | null>(null);
  const [errorPagina, setErrorPagina] = useState<string | null>(null);
  useEffect(() => {
    if (formularioGuardado) {
      setFormulario(formularioGuardado);
      setCargando(false);
      return;
    }

    (async () => {
      try {
        const datosUsuario = await getUsuarioById(idNumerico);
        setUsuario(datosUsuario);
        setFormulario({
          username: datosUsuario.username,
          email: datosUsuario.email,
          first_name: datosUsuario.first_name,
          last_name: datosUsuario.last_name,
          telefono: datosUsuario.perfil.telefono,
          direccion: datosUsuario.perfil.direccion,
          fecha_nacimiento: datosUsuario.perfil.fecha_nacimiento,
          genero: datosUsuario.perfil.genero,
          biografia: datosUsuario.perfil.biografia,
          foto_url: datosUsuario.perfil.foto_perfil,
          foto_perfil: null,
          eliminar_foto: false,
        });
      } catch {
        setErrorPagina("No se pudieron cargar los datos.");
      } finally {
        setCargando(false);
      }
    })();
  }, [id, formularioGuardado]);

  const ajustarAlturaBiografia = (elemento: HTMLTextAreaElement | null) => {
    if (!elemento) return;
    elemento.style.height = "auto";
    elemento.style.height = `${elemento.scrollHeight}px`;
  };

  useLayoutEffect(() => {
    if (!cargando) ajustarAlturaBiografia(refBiografia.current);
  }, [cargando, formulario.biografia]);

  const handleCambioCampo = (e: any) => {
    setFormulario({ ...formulario, [e.target.name]: e.target.value });
    if (e.target.name === "biografia") {
      ajustarAlturaBiografia(refBiografia.current);
    }
  };

  const handleArchivo = (e: any) => {
    setFormulario({
      ...formulario,
      foto_perfil: e.target.files?.[0] || null,
    });
  };

  const handleEliminarFoto = () => {
    setFormulario((prev) => ({
      ...prev,
      foto_perfil: null,
      foto_url: null,
      eliminar_foto: true,
    }));
  };

  const handleEliminarCuenta = async () => {
    setErrorFormulario(null);

    const nombreUsuario = formulario.username || usuario?.username || "";
    if (!nombreUsuario) {
      window.alert("No se pudo determinar el nombre de usuario.");
      return;
    }

    const textoEsperado = `DELETE/${nombreUsuario}`;
    const entrada = window.prompt(
      `Esta accion eliminara definitivamente su cuenta.\n\n` +
      `Para continuar,escribe exactamente${textoEsperado}`,
    );

    if (entrada !== textoEsperado) {
      if (entrada !== null) {
        window.alert("El texto no coincide. Operacion cancelada.");
      }
      return;
    }

    const confirmacion = window.confirm(
      "¿Seguro que quieres eliminar tu cuenta? Esta accion es irreversible",
    );
    if (!confirmacion) return;

    try {
      setGuardando(true);
      logout();
      await deleteUsuario(idNumerico);
      navigate("/", { replace: true });
    } catch (e: any) {
      const detalle =
        e?.detail ||
        (typeof e === "string" ? e : null) ||
        "No se pudo eliminar la cuenta.";
      setErrorFormulario(detalle);
      window.alert(detalle);
    } finally {
      setGuardando(false);
    }
  };

  const iniciales = useMemo(() => {
    const nombre = `${usuario?.first_name ?? formulario.first_name} ${usuario?.last_name ?? formulario.last_name
      }`.trim();

    if (nombre) {
      return nombre
        .split(/\s+/)
        .slice(0, 2)
        .map((p) => p[0].toUpperCase())
        .join("");
    }

    const username = usuario?.username ?? formulario.username ?? "";
    return username.slice(0, 2).toUpperCase();
  }, [
    usuario,
    formulario.first_name,
    formulario.last_name,
    formulario.username,
  ]);

  const fotoPerfil =
    formulario.foto_perfil
      ? URL.createObjectURL(formulario.foto_perfil)
      : formulario.foto_url ?? null;

  const handleSubmit = async (e: any) => {
    e.preventDefault();

    if (!formulario.email.trim()) {
      setErrorFormulario("El email es obligatorio.");
      return;
    }

    if (!formulario.username.trim()) {
      setErrorFormulario("El nombre de usuario es obligatorio.");
      return;
    }

    if (!formulario.fecha_nacimiento.trim()) {
      setErrorFormulario("La fecha de nacimiento es obligatoria.");
      return;
    }

    if (!formulario.genero.trim()) {
      setErrorFormulario("El género es obligatorio.");
      return;
    }

    if (!formulario.telefono.trim()) {
      setErrorFormulario("El teléfono es obligatorio.");
      return;
    }
    setGuardando(true);
    setErrorFormulario(null);

    const payload = {
      username: formulario.username,
      email: formulario.email,
      first_name: formulario.first_name,
      last_name: formulario.last_name,
      perfil: {
        telefono: formulario.telefono,
        direccion: formulario.direccion,
        fecha_nacimiento: formulario.fecha_nacimiento,
        genero: formulario.genero,
        biografia: formulario.biografia,
        eliminar_foto: formulario.eliminar_foto,
      },
    };

    try {
      await updateUsuario(idNumerico, payload, formulario.foto_perfil);
      navigate(`/perfil/${id}`);
    } catch {
      setErrorFormulario("Error al guardar los cambios.");
    } finally {
      setGuardando(false);
    }
  };


  if (cargando) {
    return <PageInfo message="Cargando perfil..." />;
  }

  if (errorPagina) {
    return <PageError message={errorPagina} />;
  }


  return (
    <div className="form-page">
      <div className="form-card">
        <h1 className="form-title">Actualizar Perfil</h1>

        <form onSubmit={handleSubmit} className="form-container">
          <div
            className="profile-photo-wrapper"
            onClick={() => refInputArchivo.current?.click()}
          >
            {fotoPerfil ? (
              <img src={fotoPerfil} className="perfil-avatar__img" alt="foto" />
            ) : (
              <div className="perfil-avatar__fallback">{iniciales}</div>
            )}

            {fotoPerfil && (
              <button
                type="button"
                className="avatar-delete-btn avatar-delete-btn--icon"
                onClick={(e) => {
                  e.stopPropagation();
                  handleEliminarFoto();
                }}
                style={{ backgroundImage: `url(${deleteIcon})` }}
                aria-label="Eliminar perfil"
              />
            )}
          </div>

          <input
            type="file"
            accept="image/*"
            ref={refInputArchivo}
            className="file-hidden"
            onChange={handleArchivo}
          />

          <h3 className="form-section-title">Información del Usuario</h3>

          <label className="form-label">Nombre de usuario</label>
          <input
            className="form-input"
            name="username"
            value={formulario.username}
            onChange={handleCambioCampo}
          />

          <label className="form-label">Email</label>
          <input
            className="form-input"
            name="email"
            value={formulario.email}
            onChange={handleCambioCampo}
          />

          <label className="form-label">Nombre</label>
          <input
            className="form-input"
            name="first_name"
            value={formulario.first_name}
            onChange={handleCambioCampo}
          />

          <label className="form-label">Apellidos</label>
          <input
            className="form-input"
            name="last_name"
            value={formulario.last_name}
            onChange={handleCambioCampo}
          />

          <h3 className="form-section-title">Datos del Perfil</h3>

          <label className="form-label">Teléfono</label>
          <input
            className="form-input"
            name="telefono"
            value={formulario.telefono}
            onChange={handleCambioCampo}
          />

          <label className="form-label">Dirección</label>
          <input
            className="form-input"
            name="direccion"
            value={formulario.direccion}
            onChange={handleCambioCampo}
          />

          <label className="form-label">Fecha de nacimiento</label>
          <input
            type="date"
            className="form-input"
            name="fecha_nacimiento"
            value={formulario.fecha_nacimiento}
            onChange={handleCambioCampo}
          />

          <label className="form-label">Género</label>
          <select
            className="form-input"
            name="genero"
            value={formulario.genero}
            onChange={handleCambioCampo}
          >
            <option value="M">Masculino</option>
            <option value="F">Femenino</option>
            <option value="O">Otro</option>
          </select>

          <label className="form-label">Biografía</label>
          <textarea
            ref={refBiografia}
            className="form-input"
            name="biografia"
            value={formulario.biografia}
            onChange={handleCambioCampo}
          />

          <button
            type="button"
            className="btn btn-secondary form-button"
            onClick={() =>
              navigate(`/perfil/${id}/change-password`, {
                state: { formData: formulario },
              })
            }
          >
            Cambiar contraseña
          </button>

          <button
            type="button"
            className="btn btn-secondary form-button"
            onClick={() => navigate(`/perfil/${id}`)}
          >
            Descartar cambios
          </button>

          <button
            type="submit"
            className="btn btn-primary form-button"
            disabled={guardando}
          >
            {guardando ? "Guardando..." : "Guardar cambios"}
          </button>

          <button
            type="button"
            className="btn btn-danger form-button"
            onClick={handleEliminarCuenta}
            disabled={guardando}
          >
            Eliminar cuenta
          </button>

          {errorFormulario && (
            <p className="form-error">{errorFormulario}</p>
          )}
        </form>
      </div>
    </div>
  );
}