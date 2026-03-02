import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerRequest, loginRequest, fetchMe } from "../api/auth";
import { storage } from "../utils/storage";

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
    <div style={{ maxWidth: 420, margin: "6rem auto" }}>
      <h1>Crear cuenta</h1>
      <form onSubmit={handleSubmit}>
        <label style={{ display: "block", marginTop: 8 }}>
          First Name:
          <input
            value={form.firstName}
            onChange={(e) => setForm({ ...form, firstName: e.target.value })}
            autoComplete="given-name"
            required
          />
        </label>

        <label style={{ display: "block", marginTop: 8 }}>
          Last Name:
          <input
            value={form.lastName}
            onChange={(e) => setForm({ ...form, lastName: e.target.value })}
            autoComplete="family-name"
            required
          />
        </label>

        <label style={{ display: "block", marginTop: 8 }}>
          Username:
          <input
            value={form.username}
            onChange={(e) => setForm({ ...form, username: e.target.value })}
            autoComplete="username"
            required
          />
        </label>

        <label style={{ display: "block", marginTop: 8 }}>
          Email:
          <input
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
            autoComplete="email"
            required
          />
        </label>

        <label style={{ display: "block", marginTop: 8 }}>
          Género:
          <select
            value={form.genero}
            onChange={(e) => setForm({ ...form, genero: e.target.value })}
            style={{ width: "60%", padding: "4px" }}
          >
            <option value="">Selecciona una opción</option>
            <option value="M">Hombre</option>
            <option value="F">Mujer</option>
            <option value="O">Otro</option>
          </select>
        </label>

        <label style={{ display: "block", marginTop: 8 }}>
          Password:
          <input
            type="password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
            autoComplete="new-password"
            required
          />
        </label>

        <label style={{ display: "block", marginTop: 8 }}>
          Confirm Password:
          <input
            type="password"
            value={form.confirmPassword}
            onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
            autoComplete="new-password"
            required
          />
        </label>

        <label style={{ display: "block", marginTop: 8 }}>
          Fecha de Nacimiento:
          <input
            type="date"
            value={form.fechaNacimiento}
            onChange={(e) => setForm({ ...form, fechaNacimiento: e.target.value })}
            autoComplete="bday"
            required
          />
        </label>

        <label style={{ display: "block", marginTop: 8 }}>
          Biografía:
          <textarea
            value={form.biografia}
            onChange={(e) => setForm({ ...form, biografia: e.target.value })}
          />
        </label>

        <label style={{ display: "block", marginTop: 8 }}>
          Teléfono:
          <input
            type="tel"
            value={form.telefono}
            onChange={(e) => setForm({ ...form, telefono: e.target.value })}
            autoComplete="tel"
            pattern='^\+?\d{7,15}$'
            required
          />
        </label>

        <label style={{ display: "block", marginTop: 8 }}>
          Dirección:
          <input
            value={form.direccion}
            onChange={(e) => setForm({ ...form, direccion: e.target.value })}
            autoComplete="street-address"
            required
          />
        </label>
        <label style={{ display: "block", marginTop: 8 }}>
          Foto de perfil:
          <input
            type="file"
            accept="image/*"
            onChange={(e) => {
              const file = e.target.files?.[0] || null;
              setForm({ ...form, foto: file });
            }}
          />
        </label>

        <button type="submit" style={{ marginTop: 12 }}>
          Crear cuenta
        </button>
        {error && <p style={{ color: "crimson" }}>{error}</p>}
      </form>
        <p style={{ marginTop: 12 }}>
        ¿No tienes cuenta?{" "}
            <button
            type="button"
            onClick={() => navigate("/login")}
            style={{
                background: "none",
                border: "none",
                padding: 0,
                color: "#007bff",
                textDecoration: "underline",
                cursor: "pointer"
            }}
            >
            Crear cuenta
            </button>
        </p>
    </div>
  );
};

export default Register;