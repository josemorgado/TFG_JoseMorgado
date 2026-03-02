// Login.tsx
import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useLocation, useNavigate } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import TextField from "../components/TextField";
import PasswordField from "../components/PasswordField";
import SubmitButton from "../components/SubmitButton";
import ErrorMessage from "../components/ErrorMessage";

type LoginState = {
  reason?: "create-queja";
  from?: { pathname?: string };
};

const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // ⬅️ ESTA es la forma correcta (solo casteas .state)
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

      // Si venía de Crear Queja ➝ redirige allí
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
    <AuthLayout title="Iniciar sesión">
      {/* Mensaje especial si venía por crear queja */}
      {reason === "create-queja" && (
        <p style={{ color: "crimson", marginBottom: 12 }}>
          Debes iniciar sesión para poder crear una queja.
        </p>
      )}

      <form onSubmit={onSubmit} noValidate>
        <TextField
          name="username"
          className="auth-field"
          placeholder="Username"
          autoComplete="username"
          value={form.username}
          onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
          required
          disabled={loading}
        />

        <PasswordField
          name="password"
          className="auth-field"
          type="password"
          placeholder="Password"
          autoComplete="password"
          value={form.password}
          onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
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

        <SubmitButton loading={loading}>Entrar</SubmitButton>

        <ErrorMessage message={error} />
      </form>

      <p style={{ marginTop: 12 }}>
        ¿No tienes cuenta?{" "}
        <button
          type="button"
          className="link"
          onClick={() => navigate("/register")}
        >
          Crear cuenta
        </button>
      </p>
    </AuthLayout>
  );
};

export default Login;