import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useLocation, useNavigate } from "react-router-dom";
import AuthLayout from "../components/AuthLayout.tsx";
import TextField from "../components/TextField";
import PasswordField from "../components/PasswordField";
import SubmitButton from "../components/SubmitButton.tsx";
import ErrorMessage from "../components/ErrorMessage";

type LocationState = { from?: { pathname?: string } } | null;

const Login: React.FC = () => {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation() as unknown as { state: LocationState };

  const [form, setForm] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const from = location?.state?.from?.pathname ?? "/";

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await login(form);
      navigate(from, { replace: true });
    } catch (err: any) {
      if (err?.response?.status === 401) {
        setError("Usuario o contraseña incorrectos");
      } else {
        setError("Error del servidor, inténtalo de nuevo más tarde");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout title="Iniciar sesión">
      <form onSubmit={onSubmit} noValidate>
        <TextField
          label="Usuario"
          name="username"
          value={form.username}
          onChange={(e) => setForm((f) => ({ ...f, username: e.target.value }))}
          autoComplete="username"
          required
          disabled={loading}
        />

        <PasswordField
          label="Contraseña"
          name="password"
          value={form.password}
          onChange={(e) => setForm((f) => ({ ...f, password: e.target.value }))}
          required
          disabled={loading}
        />

        <SubmitButton loading={loading}>Entrar</SubmitButton>
        <ErrorMessage message={error} />
      </form>
        <p style={{ marginTop: 12 }}>
        ¿No tienes cuenta?{" "}
          <button
            type="button"
            onClick={() => navigate("/register")}
            style={{
              background: "none",
              border: "none",
              padding: 0,
              color: "#007bff",
              textDecoration: "underline",
              cursor: "pointer"
            }}
          >
            Crear cuenta
          </button>
      </p>
    </AuthLayout>

  );
};

export default Login;