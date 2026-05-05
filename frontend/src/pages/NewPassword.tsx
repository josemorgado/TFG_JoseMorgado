import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { confirmPasswordReset } from "../api/auth";
import PageError from "../components/PageError";

export default function NewPassword() {
  const navigate = useNavigate();
  const location = useLocation();

  const datosRuta = (location.state || {}) as {
    uid?: string;
    token?: string;
    email?: string;
  };

  const { uid, token, email } = datosRuta;

  const [nuevaContrasena, setNuevaContrasena] = useState("");
  const [repetirContrasena, setRepetirContrasena] = useState("");
  const [errorFormulario, setErrorFormulario] = useState<string | null>(null);

  if (!uid || !token) {
    return (
      <PageError message="Faltan datos para restablecer la contraseña. Vuelve a solicitar el código." />
    );
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorFormulario(null);

    if (nuevaContrasena !== repetirContrasena) {
      setErrorFormulario("Las contraseñas no coinciden.");
      return;
    }

    try {
      await confirmPasswordReset(uid, token, nuevaContrasena);
      window.alert("Contraseña actualizada correctamente");
      navigate("/login");
    } catch (err: any) {
      const mensajeBackend =
        err?.response?.data?.detail ||
        err?.response?.data?.message ||
        "El enlace no es válido o ha expirado.";
      setErrorFormulario(mensajeBackend);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card">
        <h2 className="form-title">Nueva contraseña</h2>

        {email && <p style={{ marginBottom: 14 }}>Cuenta: {email}</p>}

        <form className="form-container" onSubmit={handleSubmit}>
          <label className="form-label">Nueva contraseña</label>
          <input
            type="password"
            className="form-input"
            value={nuevaContrasena}
            onChange={(e) => setNuevaContrasena(e.target.value)}
          />

          <label className="form-label">Repite la contraseña</label>
          <input
            type="password"
            className="form-input"
            value={repetirContrasena}
            onChange={(e) => setRepetirContrasena(e.target.value)}
          />

          {errorFormulario && (
            <p className="form-error">{errorFormulario}</p>
          )}

          <button type="submit" className="form-button">
            Cambiar contraseña
          </button>
        </form>
      </div>
    </div>
  );
}