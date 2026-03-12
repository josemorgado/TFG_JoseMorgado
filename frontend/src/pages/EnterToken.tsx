import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";

export default function EnterToken() {
  const navigate = useNavigate();
  const location = useLocation();
  const email = (location.state as any)?.email;

  const [uid, setUid] = useState("");
  const [token, setToken] = useState("");
  const [error, setError] = useState("");

  if (!email) {
    return <p className="form-error">Error: No se ha proporcionado email.</p>;
  }

  const handleNext = () => {
    setError("");

    if (!uid.trim() || !token.trim()) {
      setError("Debes introducir UID y Token.");
      return;
    }

    navigate("/new-password", {
      state: { uid: uid.trim(), token: token.trim(), email }
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

          {error && <p className="form-error">{error}</p>}

          <button className="form-button" onClick={handleNext}>
            Validar código
          </button>
        </div>
      </div>
    </div>
  );
}