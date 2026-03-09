import React, { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

import "../styles/form-layout.css";

type LoginState = {
  reason?: "create-queja";
  from?: { pathname?: string };
};

const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const state = location.state as LoginState | undefined;

  const reason = state?.reason;
  const from = state?.from?.pathname ?? "/";

  const [form, setForm] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(form);

      if (reason === "create-queja") {
        navigate("/create-queja", { replace: true });
      } else {
        navigate(from, { replace: true });
      }
    } catch (err: any) {
      if (err?.response?.status === 401) {
        setError("Usuario o contraseña incorrectos");
      } else {
        setError("Error del servidor, inténtalo más tarde");
      }
      setForm((f) => ({ ...f, password: "" }));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card">
          {reason === "create-queja" && (
            <p className="form-error" style={{ marginBottom: 12 }}>
              Debes iniciar sesión para poder crear una queja.
            </p>
          )}
        <h1 className="form-title">Iniciar sesión</h1>

        <form onSubmit={onSubmit} noValidate className="form-container">
          <label className="form-label">Username</label>
          <input
            className="form-input"
            value={form.username}
            onChange={(e) =>
              setForm((f) => ({ ...f, username: e.target.value }))
            }
            required
            disabled={loading}
          />

          <label className="form-label">Password</label>
          <input
            className="form-input"
            type="password"
            value={form.password}
            onChange={(e) =>
              setForm((f) => ({ ...f, password: e.target.value }))
            }
            required
            disabled={loading}
          />

          <p style={{ marginTop: 8 }}>
            <button
              type="button"
              className="link"
              onClick={() => navigate("/forgot-password")}
            >
              ¿Has olvidado tu contraseña?
            </button>
          </p>

          <button
            type="submit"
            className="btn btn-primary form-button"
            disabled={loading}
          >
            {loading ? "Entrando..." : "Entrar"}
          </button>

          {error && <p className="form-error">{error}</p>}
        </form>

        <p className="form-link-center" style={{ marginTop: 12 }}>
          ¿No tienes cuenta?{" "}
          <button
            type="button"
            className="link"
            onClick={() => navigate("/register")}
          >
            Crear cuenta
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;
