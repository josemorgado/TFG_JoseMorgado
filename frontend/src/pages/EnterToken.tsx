import { useEffect, useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";

export default function EnterToken() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();

  const [uid, setUid] = useState("");
  const [token, setToken] = useState("");
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const uidParam = searchParams.get("uid");
    const tokenParam = searchParams.get("token");

    if (uidParam) setUid(uidParam);
    if (tokenParam) setToken(tokenParam);
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!uid || !token) {
      setError("UID y token son obligatorios.");
      return;
    }

    navigate("/new-password", {
      state: { uid, token },
    });
  };

  return (
    <div className="form-page">
      <div className="form-card">
        <h1 className="form-title">Pegar código de recuperación</h1>

        <form onSubmit={handleSubmit} className="form-container">
          <label className="form-label">UID</label>
          <input
            className="form-input"
            value={uid}
            onChange={(e) => setUid(e.target.value)}
            disabled={!!searchParams.get("uid")}
          />

          <label className="form-label">Token</label>
          <input
            className="form-input"
            value={token}
            onChange={(e) => setToken(e.target.value)}
            disabled={!!searchParams.get("token")}
          />

          {error && <p className="form-error">{error}</p>}

          <button type="submit" className="btn btn-primary form-button">
            Validar código
          </button>
        </form>
      </div>
    </div>
  );
}
