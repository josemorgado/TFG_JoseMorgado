import React, { useState } from "react";

const Register: React.FC = () => {
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
  });

  return (
    <div style={{ maxWidth: 420, margin: "6rem auto" }}>
      <h1>Crear cuenta</h1>
      <form>
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

        <button type="submit" style={{ marginTop: 12 }}>
          Crear cuenta
        </button>
      </form>
    </div>
  );
};

export default Register;