import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginRequest, registerRequest } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import { storage } from "../utils/storage";
import "../styles/form-layout.css";

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { login: authLogin } = useAuth();

  const [form, setForm] = useState({
    username: "",
    password: "",
    confirmPassword: "",
    email: "",
    firstName: "",
    lastName: "",
    genero: "",
    fechaNacimiento: "",
    biografia: "",
    telefono: "",
    direccion: "",
    foto: null as File | null,
  });

  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (form.password !== form.confirmPassword) {
      setError("Las contraseñas no coinciden");
      return;
    }

    const required = [
      ["fecha de nacimiento", form.fechaNacimiento],
      ["teléfono", form.telefono],
      ["dirección", form.direccion],
    ];

    for (const [label, value] of required) {
      if (!String(value).trim()) {
        setError(`El campo ${label} es obligatorio`);
        return;
      }
    }

    const fd = new FormData();
    fd.append("username", form.username.trim());
    fd.append("email", form.email.trim());
    fd.append("first_name", form.firstName.trim());
    fd.append("last_name", form.lastName.trim());
    fd.append("password", form.password);
    fd.append("telefono", form.telefono.trim());
    fd.append("direccion", form.direccion.trim());
    fd.append("fecha_nacimiento", form.fechaNacimiento);

    if (form.genero) fd.append("genero", form.genero);
    if (form.biografia) fd.append("biografia", form.biografia.trim());
    if (form.foto) fd.append("foto_perfil", form.foto);

    try {
      await registerRequest(fd);

      const tokens = await loginRequest({
        username: form.username,
        password: form.password,
      });

      storage.setAccess(tokens.access);
      if (tokens.refresh) storage.setRefresh(tokens.refresh);

      await authLogin({
        username: form.username,
        password: form.password,
      });

      navigate("/");
    } catch (err: any) {
      const data = err?.response?.data?.error?.details || err?.response?.data;
      if (!data) {
        setError("No se pudo conectar con el servidor.");
        return;
      }

      const messages: string[] = [];

      for (const key of Object.keys(data)) {
        const value = data[key];
        if (Array.isArray(value)) {
          messages.push(`${key}: ${value.join(" ")}`);
        } else if (typeof value === "object") {
          for (const sub of Object.keys(value)) {
            messages.push(`${sub}: ${value[sub].join(" ")}`);
          }
        }
      }

      setError(messages.join(" · ") || "No se puede crear la cuenta.");
    }
  };

  return (
    <div className="form-page">
      <div className="form-card">
        <h1 className="form-title">Crear cuenta</h1>

        <form onSubmit={handleSubmit} className="form-container">

          <label className="form-label">Nombre</label>
          <input
            className="form-input"
            value={form.firstName}
            onChange={(e) => setForm({ ...form, firstName: e.target.value })}
            required
          />

          <label className="form-label">Apellidos</label>
          <input
            className="form-input"
            value={form.lastName}
            onChange={(e) => setForm({ ...form, lastName: e.target.value })}
            required
          />

          <label className="form-label">Nombre de usuario</label>
          <input
            className="form-input"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            required
          />

          <label className="form-label">Correo electrónico</label>
          <input
            className="form-input"
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            required
          />

          <label className="form-label">Género</label>
          <select
            className="form-input"
            value={form.genero}
            onChange={(e) => setForm({ ...form, genero: e.target.value })}
          >
            <option value="">Selecciona una opción</option>
            <option value="M">Hombre</option>
            <option value="F">Mujer</option>
            <option value="O">Otro</option>
          </select>

          <label className="form-label">Fecha de nacimiento</label>
          <input
            className="form-input"
            type="date"
            value={form.fechaNacimiento}
            onChange={(e) => setForm({ ...form, fechaNacimiento: e.target.value })}
            required
          />

          <label className="form-label">Teléfono</label>
          <input
            className="form-input"
            type="tel"
            pattern="^\+?\d{7,15}$"
            value={form.telefono}
            onChange={(e) => setForm({ ...form, telefono: e.target.value })}
            required
          />

          <label className="form-label">Dirección</label>
          <input
            className="form-input"
            value={form.direccion}
            onChange={(e) => setForm({ ...form, direccion: e.target.value })}
            required
          />

          <label className="form-label">Biografía (opcional)</label>
          <textarea
            className="form-input"
            value={form.biografia}
            onChange={(e) => setForm({ ...form, biografia: e.target.value })}
            rows={4}
          />

          <label className="form-label">Foto de perfil (opcional)</label>
          <input
            className="form-input"
            type="file"
            accept="image/*"
            onChange={(e) =>
              setForm({ ...form, foto: e.target.files?.[0] || null })
            }
          />

          <label className="form-label">Contraseña</label>
          <input
            className="form-input"
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            required
          />

          <label className="form-label">Confirmar contraseña</label>
          <input
            className="form-input"
            type="password"
            value={form.confirmPassword}
            onChange={(e) =>
              setForm({ ...form, confirmPassword: e.target.value })
            }
            required
          />

          <button className="btn btn-primary form-button">
            Crear cuenta
          </button>

          {error && <p className="form-error">{error}</p>}
        </form>
        <p className="form-link-center" style={{ marginTop: 12 }}>
          ¿Ya tienes una cuenta?
          <button className="link" onClick={() => navigate("/login")}>
            Inicia sesión aquí
          </button>
        </p>
      </div>
    </div>
  );
};

export default Register;