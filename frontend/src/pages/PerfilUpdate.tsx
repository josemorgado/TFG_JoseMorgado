import { useEffect, useState, useRef, useLayoutEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getUsuarioById, updateUsuario } from "../api/perfil";
import "../styles/form-layout.css";

export default function PerfilUpdate() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const bioRef = useRef<HTMLTextAreaElement | null>(null);

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
    foto_perfil: null as File | null,
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
          foto_perfil: null,
        });
      } catch {
        setError("No se pudieron cargar los datos.");
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

  const handleFile = (e: any) =>
    setForm({ ...form, foto_perfil: e.target.files?.[0] || null });

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

          <h3 className="form-section-title">Información del Usuario</h3>

          <label className="form-label">Nombre de usuario</label>
          <input className="form-input" name="username" value={form.username} onChange={handleChange} />

          <label className="form-label">Email</label>
          <input className="form-input" name="email" value={form.email} onChange={handleChange} />

          <label className="form-label">Nombre</label>
          <input className="form-input" name="first_name" value={form.first_name} onChange={handleChange} />

          <label className="form-label">Apellidos</label>
          <input className="form-input" name="last_name" value={form.last_name} onChange={handleChange} />

          <h3 className="form-section-title">Datos del Perfil</h3>

          <label className="form-label">Teléfono</label>
          <input className="form-input" name="telefono" value={form.telefono} onChange={handleChange} />

          <label className="form-label">Dirección</label>
          <input className="form-input" name="direccion" value={form.direccion} onChange={handleChange} />

          <label className="form-label">Fecha de nacimiento</label>
          <input type="date" className="form-input" name="fecha_nacimiento" value={form.fecha_nacimiento} onChange={handleChange} />

          <label className="form-label">Género</label>
          <select className="form-input" name="genero" value={form.genero} onChange={handleChange}>
            <option value="M">Masculino</option>
            <option value="F">Femenino</option>
            <option value="O">Otro</option>
          </select>

          <label className="form-label">Biografía</label>
          <textarea ref={bioRef} className="form-input" name="biografia" value={form.biografia} onChange={handleChange} />

          <label className="form-label">Foto de perfil</label>
          <input type="file" className="form-input" onChange={handleFile} />

          <button type="button" className="btn btn-secondary form-button" onClick={() => navigate(`/perfil/${id}/cambiar-password`)}>
            Cambiar contraseña
          </button>

          <button type="submit" className="btn btn-primary form-button" disabled={saving}>
            {saving ? "Guardando..." : "Guardar cambios"}
          </button>

          {error && <p className="form-error">{error}</p>}
        </form>
      </div>
    </div>
  );
}