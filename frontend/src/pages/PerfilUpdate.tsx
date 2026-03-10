import { useEffect, useState, useMemo, useRef, useLayoutEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getUsuarioById, updateUsuario } from "../api/perfil";
import "../styles/form-layout.css";
import type { Usuario } from "../types/perfil";
import deleteIcon from "../assets/icons/delete-icon.png";

export default function PerfilUpdate() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [usuario, setUsuario] = useState<Usuario | null>(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const bioRef = useRef<HTMLTextAreaElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const [form, setForm] = useState({
    username: "",
    email: "",
    first_name: "",
    last_name: "",
    telefono: "",
    direccion: "",
    fecha_nacimiento: "",
    genero: "O",
    biografia: "",
    foto_url: "" as string | null,
    foto_perfil: null as File | null,
    eliminar_foto: false,
  });

  useEffect(() => {
    (async () => {
      try {
        const data = await getUsuarioById(Number(id));
        setForm({
          username: data.username,
          email: data.email,
          first_name: data.first_name,
          last_name: data.last_name,
          telefono: data.perfil.telefono,
          direccion: data.perfil.direccion,
          fecha_nacimiento: data.perfil.fecha_nacimiento,
          genero: data.perfil.genero,
          biografia: data.perfil.biografia,
          foto_url: data.perfil.foto_perfil,
          foto_perfil: null,
          eliminar_foto: false,
        });
      } catch {
        setError("No se pudieron cargar los datos.");
      } finally {
        setLoading(false);
      }
    })();
    (async () => {
      try {
        const data = await getUsuarioById(Number(id));
        setUsuario(data);
      } catch (e) {
        setError("No se pudo cargar el perfil.");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  const autoResize = (el: HTMLTextAreaElement | null) => {
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${el.scrollHeight}px`;
  };

  useLayoutEffect(() => {
    if (!loading) autoResize(bioRef.current);
  }, [loading, form.biografia]);

  const handleChange = (e: any) => {
    setForm({ ...form, [e.target.name]: e.target.value });
    if (e.target.name === "biografia") autoResize(bioRef.current);
  };
  const handleDeletePhoto = () => {
    setForm((prev) => ({
      ...prev,
      foto_perfil: null,
      foto_url: null,
      eliminar_foto: true,
    }));
  };
  const handleFile = (e: any) =>
    setForm({ ...form, foto_perfil: e.target.files?.[0] || null });

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

  const fotoPerfil = form.foto_perfil
    ? URL.createObjectURL(form.foto_perfil)
    : form.foto_url
      ? form.foto_url
      : null;

  const handleSubmit = async (e: any) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    const payload = {
      username: form.username,
      email: form.email,
      first_name: form.first_name,
      last_name: form.last_name,
      perfil: {
        telefono: form.telefono,
        direccion: form.direccion,
        fecha_nacimiento: form.fecha_nacimiento,
        genero: form.genero,
        biografia: form.biografia,
        eliminar_foto: form.eliminar_foto,
      },
    };

    try {
      await updateUsuario(Number(id), payload, form.foto_perfil);
      navigate(`/perfil/${id}`);
    } catch {
      setError("Error al guardar los cambios.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p>Cargando...</p>;
  if (error) return <p>{error}</p>;
  return (
    <div className="form-page">
      <div className="form-card">
        <h1 className="form-title">Actualizar Perfil</h1>

        <form onSubmit={handleSubmit} className="form-container">
          <div
            className="profile-photo-wrapper"
            onClick={() => fileInputRef.current?.click()}
          >
            {fotoPerfil ? (
              <img src={fotoPerfil} className="perfil-avatar__img" alt="foto" />
            ) : (
              <div className="perfil-avatar__fallback">{iniciales}</div>
            )}
            {fotoPerfil ? (
              <button
                type="button"
                className="avatar-delete-btn avatar-delete-btn--icon"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeletePhoto();
                }}
                style={{ backgroundImage: `url(${deleteIcon})` }}
                aria-label="Eliminar perfil"
              />
            ) : (
              <div />
            )}
          </div>

          <input
            type="file"
            accept="image/*"
            ref={fileInputRef}
            className="file-hidden"
            onChange={handleFile}
          />
          <h3 className="form-section-title">Información del Usuario</h3>

          <label className="form-label">Nombre de usuario</label>
          <input
            className="form-input"
            name="username"
            value={form.username}
            onChange={handleChange}
          />

          <label className="form-label">Email</label>
          <input
            className="form-input"
            name="email"
            value={form.email}
            onChange={handleChange}
          />

          <label className="form-label">Nombre</label>
          <input
            className="form-input"
            name="first_name"
            value={form.first_name}
            onChange={handleChange}
          />

          <label className="form-label">Apellidos</label>
          <input
            className="form-input"
            name="last_name"
            value={form.last_name}
            onChange={handleChange}
          />

          <h3 className="form-section-title">Datos del Perfil</h3>

          <label className="form-label">Teléfono</label>
          <input
            className="form-input"
            name="telefono"
            value={form.telefono}
            onChange={handleChange}
          />

          <label className="form-label">Dirección</label>
          <input
            className="form-input"
            name="direccion"
            value={form.direccion}
            onChange={handleChange}
          />

          <label className="form-label">Fecha de nacimiento</label>
          <input
            type="date"
            className="form-input"
            name="fecha_nacimiento"
            value={form.fecha_nacimiento}
            onChange={handleChange}
          />

          <label className="form-label">Género</label>
          <select
            className="form-input"
            name="genero"
            value={form.genero}
            onChange={handleChange}
          >
            <option value="M">Masculino</option>
            <option value="F">Femenino</option>
            <option value="O">Otro</option>
          </select>

          <label className="form-label">Biografía</label>
          <textarea
            ref={bioRef}
            className="form-input"
            name="biografia"
            value={form.biografia}
            onChange={handleChange}
          />

          <button
            type="button"
            className="btn btn-secondary form-button"
            onClick={() => navigate(`/perfil/${id}/cambiar-password`)}
          >
            Cambiar contraseña
          </button>

          <button
            type="submit"
            className="btn btn-primary form-button"
            disabled={saving}
          >
            {saving ? "Guardando..." : "Guardar cambios"}
          </button>

          {error && <p className="form-error">{error}</p>}
        </form>
      </div>
    </div>
  );
}
