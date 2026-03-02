import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerRequest, loginRequest, fetchMe } from "../api/auth";
import { storage } from "../utils/storage";
import AuthLayout from "../components/AuthLayout";

const Register: React.FC = () => {
    const navigate = useNavigate();

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
        setError("El telefono es obligatorio");
        return;
    }

    if (!form.direccion.trim()) {
        setError("La dirección es obligatoria.");
        return;
    }

    console.log("Formulario válido. Datos preparados:");

const formData = new FormData();

formData.append("username", form.username.trim());
formData.append("email", form.email.trim());
formData.append("first_name", form.firstName.trim());
formData.append("last_name", form.lastName.trim());
formData.append("password", form.password.trim());

// 🔥 CAMPOS PLANOS (NO perfil.xxx)
formData.append("telefono", form.telefono.trim());
formData.append("direccion", form.direccion.trim());
formData.append("fecha_nacimiento", form.fechaNacimiento.trim());

if (form.genero) {
  formData.append("genero", form.genero);
}

if (form.biografia) {
  formData.append("biografia", form.biografia.trim());
}

if (form.foto) {
  formData.append("foto_perfil", form.foto);
}
    try {

      console.log("[Register] calling registerRequest", formData);
      await registerRequest(formData);
      console.log("[Register] register OK, about to login");


      const tokens = await loginRequest({username: form.username, password: form.password});

      if (tokens.refresh) storage.setRefresh(tokens.refresh);
      storage.setAccess(tokens.access)

      navigate("/")
    } catch (err: any) {
      if (err.response?.data){
        const data= err.response.data;

        if (typeof data == "string") {
          setError(data);
          return;
        }

        const messages: string[] = [];

        if (data.username) messages.push(`username: ${data.username.join(" ")}`);
        if (data.email) messages.push(`email: ${data.email.join(" ")}`);
        if (data.first_name) messages.push(`nombre: ${data.first_name.join(" ")}`);
        if (data.last_name) messages.push(`apellidos: ${data.last_name.join(" ")}`);
        if (data.password) messages.push(`password: ${data.password.join(" ")}`);

        if (data.perfil) {
          const p = data.perfil;
          if (p.telefono) messages.push(`teléfono: ${p.telefono.join(" ")}`);
          if (p.direccion) messages.push(`dirección: ${p.direccion.join(" ")}`);
          if (p.fecha_nacimiento) messages.push(`fecha de nacimiento: ${p.fecha_nacimiento.join(" ")}`);
          if (p.genero) messages.push(`género: ${p.genero.join(" ")}`);
          if (p.biografia) messages.push(`biografía: ${p.biografia.join(" ")}`);
        }

        setError(messages.join(" . ") || "No se puede crear la cuenta o error de login.")
      } else {
        setError("No se pudo conectar con el servidor. Intentalo de nuevo mas tarde.")
      }
    }

    console.log(form);

};

return (
      <AuthLayout title="Crear cuenta">
        <form onSubmit={handleSubmit}>
          {/* Nombre */}
          <label htmlFor="firstName">Nombre</label>
          <input
            id="firstName"
            className="auth-field"
            type="text"
            placeholder="Tu nombre"
            value={form.firstName}
            onChange={(e) => setForm({ ...form, firstName: e.target.value })}
            autoComplete="given-name"
            required
          />

          {/* Apellidos */}
          <label htmlFor="lastName">Apellidos</label>
          <input
            id="lastName"
            className="auth-field"
            type="text"
            placeholder="Tus apellidos"
            value={form.lastName}
            onChange={(e) => setForm({ ...form, lastName: e.target.value })}
            autoComplete="family-name"
            required
          />

          {/* Username */}
          <label htmlFor="username">Nombre de usuario</label>
          <input
            id="username"
            className="auth-field"
            type="text"
            placeholder="Ej: josemaria"
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            autoComplete="username"
            required
          />

          {/* Email */}
          <label htmlFor="email">Correo electrónico</label>
          <input
            id="email"
            className="auth-field"
            type="email"
            placeholder="correo@ejemplo.com"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            autoComplete="email"
            required
          />

          {/* Género */}
          <label htmlFor="genero">Género</label>
          <select
            id="genero"
            className="auth-field"
            value={form.genero}
            onChange={(e) => setForm({ ...form, genero: e.target.value })}
          >
            <option value="">Selecciona una opción</option>
            <option value="M">Hombre</option>
            <option value="F">Mujer</option>
            <option value="O">Otro</option>
          </select>

          {/* Fecha de nacimiento */}
          <label htmlFor="fechaNacimiento">Fecha de nacimiento</label>
          <input
            id="fechaNacimiento"
            className="auth-field"
            type="date"
            value={form.fechaNacimiento}
            onChange={(e) => setForm({ ...form, fechaNacimiento: e.target.value })}
            autoComplete="bday"
            required
          />

          {/* Teléfono */}
          <label htmlFor="telefono">Teléfono</label>
          <input
            id="telefono"
            className="auth-field"
            type="tel"
            placeholder="+34 600 111 222"
            value={form.telefono}
            onChange={(e) => setForm({ ...form, telefono: e.target.value })}
            autoComplete="tel"
            pattern="^\+?\d{7,15}$"
            required
          />

          {/* Dirección */}
          <label htmlFor="direccion">Dirección</label>
          <input
            id="direccion"
            className="auth-field"
            type="text"
            placeholder="Calle, número, ciudad"
            value={form.direccion}
            onChange={(e) => setForm({ ...form, direccion: e.target.value })}
            autoComplete="street-address"
            required
          />

          {/* Biografía */}
          <label htmlFor="biografia">Biografía (opcional)</label>
          <textarea
            id="biografia"
            className="auth-field"
            placeholder="Cuéntanos algo sobre ti..."
            value={form.biografia}
            onChange={(e) => setForm({ ...form, biografia: e.target.value })}
            rows={4}
          />

          {/* Foto de perfil */}
          <label htmlFor="foto">Foto de perfil (opcional)</label>
          <input
            id="foto"
            className="auth-field"
            type="file"
            accept="image/*"
            onChange={(e) => {
              const file = e.target.files?.[0] || null;
              setForm({ ...form, foto: file });
            }}
          />

          {/* Contraseña */}
          <label htmlFor="password">Contraseña</label>
          <input
            id="password"
            className="auth-field"
            type="password"
            placeholder="Mínimo 8 caracteres"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            autoComplete="new-password"
            required
          />

          {/* Confirmar contraseña */}
          <label htmlFor="confirmPassword">Confirmar contraseña</label>
          <input
            id="confirmPassword"
            className="auth-field"
            type="password"
            placeholder="Repite la contraseña"
            value={form.confirmPassword}
            onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
            autoComplete="new-password"
            required
          />

          <button className="submit-button" style={{ marginTop: 12 }}>
            Crear cuenta
          </button>
          {error && <p style={{ color: "crimson" }}>{error}</p>}
        </form>
          <p style={{ marginTop: 12 }}>
          ¿Ya tienes una cuenta?{" "}
              <button
              type="button"
              className="link"
              onClick={() => navigate("/login")}
              >
              Inicia sesion aqui
              </button>
          </p>
        </AuthLayout>
  );
};

export default Register;