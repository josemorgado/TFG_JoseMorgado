import React, { useState } from "react";
import { useNavigate } from "react-router-dom";

import { loginRequest, registerRequest } from "../api/auth";
import { useAuth } from "../context/AuthContext";
import { storage } from "../utils/storage";

import "../styles/form-layout.css";

const Register: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [formulario, setFormulario] = useState({
    usuario: "",
    contraseña: "",
    confirmarContraseña: "",
    email: "",
    nombre: "",
    apellidos: "",
    genero: "",
    fechaNacimiento: "",
    biografia: "",
    telefono: "",
    direccion: "",
    foto: null as File | null,
  });

  const [errorFormulario, setErrorFormulario] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorFormulario(null);

    if (formulario.contraseña !== formulario.confirmarContraseña) {
      setErrorFormulario("Las contraseñas no coinciden");
      return;
    }

    const camposObligatorios: [string, string][] = [
      ["fecha de nacimiento", formulario.fechaNacimiento],
      ["teléfono", formulario.telefono],
      ["dirección", formulario.direccion],
    ];

    for (const [etiqueta, valor] of camposObligatorios) {
      if (!valor.trim()) {
        setErrorFormulario(`El campo ${etiqueta} es obligatorio`);
        return;
      }
    }

    const formData = new FormData();
    formData.append("username", formulario.usuario.trim());
    formData.append("email", formulario.email.trim());
    formData.append("first_name", formulario.nombre.trim());
    formData.append("last_name", formulario.apellidos.trim());
    formData.append("password", formulario.contraseña);
    formData.append("telefono", formulario.telefono.trim());
    formData.append("direccion", formulario.direccion.trim());
    formData.append("fecha_nacimiento", formulario.fechaNacimiento);

    if (formulario.genero) {
      formData.append("genero", formulario.genero);
    }

    if (formulario.biografia) {
      formData.append("biografia", formulario.biografia.trim());
    }

    if (formulario.foto) {
      formData.append("foto_perfil", formulario.foto);
    }

    try {
      await registerRequest(formData);

      const tokens = await loginRequest({
        username: formulario.usuario,
        password: formulario.contraseña,
      });

      storage.setAccess(tokens.access);
      if (tokens.refresh) {
        storage.setRefresh(tokens.refresh);
      }

      await login({
        username: formulario.usuario,
        password: formulario.contraseña,
      });

      navigate("/");
    } catch (err: any) {
      const datosError =
        err?.response?.data?.error?.details || err?.response?.data;

      if (!datosError) {
        setErrorFormulario("No se pudo conectar con el servidor.");
        return;
      }

      const mensajes: string[] = [];

      for (const clave of Object.keys(datosError)) {
        const valor = datosError[clave];

        if (Array.isArray(valor)) {
          mensajes.push(`${clave}: ${valor.join(" ")}`);
        } else if (typeof valor === "object") {
          for (const subclave of Object.keys(valor)) {
            mensajes.push(`${subclave}: ${valor[subclave].join(" ")}`);
          }
        }
      }

      setErrorFormulario(mensajes.join(" · ") || "No se puede crear la cuenta.");
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
            value={formulario.nombre}
            onChange={(e) =>
              setFormulario({ ...formulario, nombre: e.target.value })
            }
            required
          />

          <label className="form-label">Apellidos</label>
          <input
            className="form-input"
            value={formulario.apellidos}
            onChange={(e) =>
              setFormulario({ ...formulario, apellidos: e.target.value })
            }
            required
          />

          <label className="form-label">Nombre de usuario</label>
          <input
            className="form-input"
            value={formulario.usuario}
            onChange={(e) =>
              setFormulario({ ...formulario, usuario: e.target.value })
            }
            required
          />

          <label className="form-label">Correo electrónico</label>
          <input
            className="form-input"
            type="email"
            value={formulario.email}
            onChange={(e) =>
              setFormulario({ ...formulario, email: e.target.value })
            }
            required
          />

          <label className="form-label">Género</label>
          <select
            className="form-input"
            value={formulario.genero}
            onChange={(e) =>
              setFormulario({ ...formulario, genero: e.target.value })
            }
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
            value={formulario.fechaNacimiento}
            onChange={(e) =>
              setFormulario({
                ...formulario,
                fechaNacimiento: e.target.value,
              })
            }
            required
          />

          <label className="form-label">Teléfono</label>
          <input
            className="form-input"
            type="tel"
            pattern="^\+?\d{7,15}$"
            value={formulario.telefono}
            onChange={(e) =>
              setFormulario({ ...formulario, telefono: e.target.value })
            }
            required
          />

          <label className="form-label">Dirección</label>
          <input
            className="form-input"
            value={formulario.direccion}
            onChange={(e) =>
              setFormulario({ ...formulario, direccion: e.target.value })
            }
            required
          />

          <label className="form-label">Biografía (opcional)</label>
          <textarea
            className="form-input"
            rows={4}
            value={formulario.biografia}
            onChange={(e) =>
              setFormulario({ ...formulario, biografia: e.target.value })
            }
          />

          <label className="form-label">Foto de perfil (opcional)</label>
          <input
            className="form-input"
            type="file"
            accept="image/*"
            onChange={(e) =>
              setFormulario({
                ...formulario,
                foto: e.target.files?.[0] || null,
              })
            }
          />

          <label className="form-label">Contraseña</label>
          <input
            className="form-input"
            type="password"
            value={formulario.contraseña}
            onChange={(e) =>
              setFormulario({ ...formulario, contraseña: e.target.value })
            }
            required
          />

          <label className="form-label">Confirmar contraseña</label>
          <input
            className="form-input"
            type="password"
            value={formulario.confirmarContraseña}
            onChange={(e) =>
              setFormulario({
                ...formulario,
                confirmarContraseña: e.target.value,
              })
            }
            required
          />

          <button className="btn btn-primary form-button">
            Crear cuenta
          </button>

          {errorFormulario && (
            <p className="form-error">{errorFormulario}</p>
          )}
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