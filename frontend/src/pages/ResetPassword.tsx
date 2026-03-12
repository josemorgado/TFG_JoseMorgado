import { useState } from "react";
import { requestPasswordReset } from "../api/auth";
import { useNavigate } from "react-router-dom";

export default function ResetPassword() {
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [sent, setSent] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    try {
      await requestPasswordReset(email);
      setSent(true);

      setTimeout(() => {
        navigate("/enter-token", { state: { email } });
      }, 1500);

    } catch (err: any) {
      console.log("ERROR BACKEND:", err.response?.data);
      const backendError =
        err.response?.data?.email?.[0] ||
        err.response?.data?.detail ||
        "Error inesperado";
      setError(backendError);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card">
        <h2 className="form-title">Recuperar contraseña</h2>

        {!sent ? (
          <form className="form-container" onSubmit={handleSubmit}>
            <label className="form-label">Correo electrónico</label>
            <input
              type="email"
              className="form-input"
              placeholder="Tu email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            {error && <p className="form-error">{error}</p>}

            <button type="submit" className="form-button">
              Enviar código
            </button>
          </form>
        ) : (
          <p className="form-link-center">Código enviado. Revisa tu correo.</p>
        )}
      </div>
    </div>
  );
}