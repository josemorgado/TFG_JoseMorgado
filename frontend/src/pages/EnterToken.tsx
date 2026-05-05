import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import PageError from "../components/PageError";

export default function EnterToken() {
  const navigate = useNavigate();
  const location = useLocation();

  const email = (location.state as { email?: string } | null)?.email;

  const [uid, setUid] = useState("");
  const [token, setToken] = useState("");
  const [errorFormulario, setErrorFormulario] = useState<string | null>(null);

  if (!email) {
    return (
      <PageError message="No se ha proporcionado un email válido. Vuelve a iniciar el proceso de recuperación." />
    );
  }

  const handleValidarCodigo = () => {
    setErrorFormulario(null);

    const uidLimpio = uid.trim();
    const tokenLimpio = token.trim();

    if (!uidLimpio || !tokenLimpio) {
      setErrorFormulario("Debes introducir el UID y el token.");
      return;
    }

    navigate("/new-password", {
      state: {
        uid: uidLimpio,
        token: tokenLimpio,
        email,
      },
    });
  };

  return (
    <div className="form-page">
      <div className="form-card">
        <h2 className="form-title">Pegar código de recuperación</h2>

        <div className="form-container">
          <label className="form-label">UID</label>
          <input
            type="text"
            className="form-input"
            placeholder="Ej.: MQ"
            value={uid}
            onChange={(e) => setUid(e.target.value)}
          />

          <label className="form-label">Token</label>
          <input
            type="text"
            className="form-input"
            placeholder="Ej.: d5bpjh-..."
            value={token}
            onChange={(e) => setToken(e.target.value)}
          />

          {errorFormulario && (
            <p className="form-error">{errorFormulario}</p>
          )}

          <button className="form-button" onClick={handleValidarCodigo}>
            Validar código
          </button>
        </div>
      </div>
    </div>
  );
}