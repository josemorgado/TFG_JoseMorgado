import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { getUsuarioById, updateUsuario } from "../api/perfil";
import "../styles/perfilUpdate.css";

export default function PerfilUpdate() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

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

  // ---------------- CARGAR DATOS DEL USUARIO ----------------
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
      } catch (e) {
        setError("No se pudieron cargar los datos.");
      } finally {
        setLoading(false);
      }
    })();
  }, [id]);

  // ---------------- HANDLERS ----------------
  const handleChange = (e: any) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const handleFile = (e: any) =>
    setForm({ ...form, foto_perfil: e.target.files?.[0] || null });

  // ---------------- ENVIAR FORMULARIO ----------------
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
    } catch (err) {
      console.log(err);
      setError("Error al guardar los cambios.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <p className="loading">Cargando...</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <div className="perfil-update-page">
      <div className="card perfil-update-card">
        <h1 className="perfil-update-title">Actualizar Perfil</h1>

        <form onSubmit={handleSubmit} className="perfil-update-form">
          <h3 className="form-section-title">Información del Usuario</h3>

          <label>Nombre de usuario</label>
          <input
            className="input"
            name="username"
            value={form.username}
            onChange={handleChange}
          />

          <label>Email</label>
          <input
            className="input"
            name="email"
            value={form.email}
            onChange={handleChange}
          />

          <label>Nombre</label>
          <input
            className="input"
            name="first_name"
            value={form.first_name}
            onChange={handleChange}
          />

          <label>Apellidos</label>
          <input
            className="input"
            name="last_name"
            value={form.last_name}
            onChange={handleChange}
          />

          <h3 className="form-section-title">Datos del Perfil</h3>

          <label>Teléfono</label>
          <input
            className="input"
            name="telefono"
            value={form.telefono}
            onChange={handleChange}
          />

          <label>Dirección</label>
          <input
            className="input"
            name="direccion"
            value={form.direccion}
            onChange={handleChange}
          />

          <label>Fecha de nacimiento</label>
          <input
            type="date"
            className="input"
            name="fecha_nacimiento"
            value={form.fecha_nacimiento}
            onChange={handleChange}
          />

          <label>Género</label>
          <select
            className="input"
            name="genero"
            value={form.genero}
            onChange={handleChange}
          >
            <option value="M">Masculino</option>
            <option value="F">Femenino</option>
            <option value="O">Otro</option>
          </select>

          <label>Biografía</label>
          <textarea
            className="input"
            name="biografia"
            value={form.biografia}
            onChange={handleChange}
          />

          <label>Foto de perfil</label>
          <input type="file" className="input" onChange={handleFile} />

          <button
            type="button"
            className="btn btn-secondary change-password-btn"
            onClick={() => navigate(`/perfil/${id}/cambiar-password`)}
          >
            Cambiar contraseña
          </button>

          <button type="submit" className="btn btn-primary" disabled={saving}>
            {saving ? "Guardando..." : "Guardar cambios"}
          </button>
        </form>
      </div>
    </div>
  );
}
