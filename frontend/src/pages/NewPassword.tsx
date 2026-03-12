import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { confirmPasswordReset } from "../api/auth";

export default function NewPassword() {
  const navigate = useNavigate();
  const location = useLocation();

  const { uid, token, email } = (location.state || {}) as {
    uid: string;
    token: string;
    email: string;
  };

  const [password, setPassword] = useState("");
  const [password2, setPassword2] = useState("");
  const [error, setError] = useState("");

  if (!uid || !token) {
    return <p className="form-error">Error: Faltan datos. Vuelve a solicitar el código.</p>;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== password2) {
      setError("Las contraseñas no coinciden.");
      return;
    }

    try {
      await confirmPasswordReset(uid, token, password);

      alert("Contraseña actualizada correctamente");
      navigate("/login");

    } catch (err: any) {
      const backendError =
        err.response?.data?.detail ||
        err.response?.data?.message ||
        "Token inválido o expirado.";
      setError(backendError);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card">
        <h2 className="form-title">Nueva contraseña</h2>
        <p style={{ marginBottom: 14 }}>Cuenta: {email}</p>

        <form className="form-container" onSubmit={handleSubmit}>

          <label className="form-label">Nueva contraseña</label>
          <input
            type="password"
            className="form-input"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <label className="form-label">Repite la contraseña</label>
          <input
            type="password"
            className="form-input"
            value={password2}
            onChange={(e) => setPassword2(e.target.value)}
          />

          {error && <p className="form-error">{error}</p>}

          <button type="submit" className="form-button">
            Cambiar contraseña
          </button>
        </form>
      </div>
    </div>
  );
}