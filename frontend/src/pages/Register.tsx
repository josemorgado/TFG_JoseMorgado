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
    if (!form.fechaNacimiento) {
      setError("La fecha de nacimiento es obligatoria");
      return;
    }
    if (!form.telefono.trim()) {
      setError("El teléfono es obligatorio");
      return;
    }
    if (!form.direccion.trim()) {
      setError("La dirección es obligatoria.");
      return;
    }

    const formData = new FormData();
    formData.append("username", form.username.trim());
    formData.append("email", form.email.trim());
    formData.append("first_name", form.firstName.trim());
    formData.append("last_name", form.lastName.trim());
    formData.append("password", form.password.trim());
    formData.append("telefono", form.telefono.trim());
    formData.append("direccion", form.direccion.trim());
    formData.append("fecha_nacimiento", form.fechaNacimiento.trim());

    if (form.genero) formData.append("genero", form.genero);
    if (form.biografia) formData.append("biografia", form.biografia.trim());
    if (form.foto) formData.append("foto_perfil", form.foto);

    try {
      await registerRequest(formData);

      const tokens = await loginRequest({
        username: form.username,
        password: form.password,
      });

      if (tokens.refresh) storage.setRefresh(tokens.refresh);
      storage.setAccess(tokens.access);

      await authLogin({
        username: form.username,
        password: form.password,
      });

      navigate("/");
    } catch (err: any) {
      if (err.response?.data) {
        const data = err.response.data;
        const messages: string[] = [];

        if (typeof data == "string") {
          setError(data);
          return;
        }

        if (data.username) messages.push(`username: ${data.username.join(" ")}`);
        if (data.email) messages.push(`email: ${data.email.join(" ")}`);
        if (data.first_name) messages.push(`nombre: ${data.first_name.join(" ")}`);
        if (data.last_name) messages.push(`apellidos: ${data.last_name.join(" ")}`);
        if (data.password) messages.push(`password: ${data.password.join(" ")}`);

        if (data.perfil) {
          const p = data.perfil;
          if (p.telefono) messages.push(`teléfono: ${p.telefono.join(" ")}`);
          if (p.direccion) messages.push(`dirección: ${p.direccion.join(" ")}`);
          if (p.fecha_nacimiento) messages.push(`fecha nacimiento: ${p.fecha_nacimiento.join(" ")}`);
          if (p.genero) messages.push(`género: ${p.genero.join(" ")}`);
          if (p.biografia) messages.push(`biografía: ${p.biografia.join(" ")}`);
        }

        setError(messages.join(" . ") || "No se puede crear la cuenta.");
      } else {
        setError("No se pudo conectar con el servidor.");
      }
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

          <p className="form-link-center"style={{ marginTop: 12 }}>
            ¿Ya tienes una cuenta?{" "}
            <button type="button" className="link" onClick={() => navigate("/login")}>
              Inicia sesión aquí
            </button>
          </p>
        </div>
      </div>
  );
};

export default Register;