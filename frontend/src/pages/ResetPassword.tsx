import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { requestPasswordReset } from "../api/auth";

export default function ResetPassword() {
  const navigate = useNavigate();

  const [correoElectronico, setCorreoElectronico] = useState("");
  const [errorFormulario, setErrorFormulario] = useState<string | null>(null);
  const [codigoEnviado, setCodigoEnviado] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorFormulario(null);

    try {
      await requestPasswordReset(correoElectronico);
      setCodigoEnviado(true);

      setTimeout(() => {
        navigate("/enter-token", {
          state: { email: correoElectronico },
        });
      }, 1500);
    } catch (err: any) {
      const mensajeBackend =
        err?.response?.data?.email?.[0] ||
        err?.response?.data?.detail ||
        "Error inesperado al solicitar el código.";

      setErrorFormulario(mensajeBackend);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card">
        <h2 className="form-title">Recuperar contraseña</h2>

        {!codigoEnviado ? (
          <form className="form-container" onSubmit={handleSubmit}>
            <label className="form-label">Correo electrónico</label>
            <input
              type="email"
              className="form-input"
              placeholder="Tu email"
              value={correoElectronico}
              onChange={(e) => setCorreoElectronico(e.target.value)}
            />

            {errorFormulario && (
              <p className="form-error">{errorFormulario}</p>
            )}

            <button type="submit" className="form-button">
              Enviar código
            </button>
          </form>
        ) : (
          <p className="form-link-center">
            Código enviado. Revisa tu correo.
          </p>
        )}
      </div>
    </div>
  );
}