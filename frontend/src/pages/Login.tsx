import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

import "../styles/form-layout.css";

type EstadoLogin = {
  reason?: "create-queja";
  from?: { pathname?: string };
};

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const estado = location.state as EstadoLogin | undefined;

  const motivoRedireccion = estado?.reason;
  const rutaDestino = estado?.from?.pathname ?? "/";

  const [credenciales, setCredenciales] = useState({
    username: "",
    password: "",
  });

  const [cargando, setCargando] = useState(false);
  const [errorFormulario, setErrorFormulario] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorFormulario(null);

    if (!credenciales.username.trim() || !credenciales.password) {
      setErrorFormulario("Debes introducir usuario y contraseña.");
      return;
    }

    try {
      setCargando(true);
      await login(credenciales);

      if (motivoRedireccion === "create-queja") {
        navigate("/create-queja", { replace: true });
      } else {
        navigate(rutaDestino, { replace: true });
      }
    } catch (err: any) {
      const mensajeBruto =
        err?.normalized?.message ||
        err?.response?.data?.error?.message ||
        "";

      if (
        mensajeBruto.toLowerCase().includes("account") ||
        mensajeBruto.toLowerCase().includes("credential")
      ) {
        setErrorFormulario("Usuario o contraseña incorrectos.");
      } else {
        setErrorFormulario(
          "Error del servidor. Inténtalo de nuevo más tarde."
        );
      }

      setCredenciales((prev) => ({
        ...prev,
        password: "",
      }));
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card">
        {motivoRedireccion === "create-queja" && (
          <p className="form-error" style={{ marginBottom: 12 }}>
            Debes iniciar sesión para poder crear una queja.
          </p>
        )}

        <h1 className="form-title">Iniciar sesión</h1>

        <form onSubmit={handleSubmit} noValidate className="form-container">
          <label className="form-label">Usuario</label>
          <input
            className="form-input"
            value={credenciales.username}
            onChange={(e) =>
              setCredenciales((prev) => ({
                ...prev,
                username: e.target.value,
              }))
            }
            required
            disabled={cargando}
          />

          <label className="form-label">Contraseña</label>
          <input
            className="form-input"
            type="password"
            value={credenciales.password}
            onChange={(e) =>
              setCredenciales((prev) => ({
                ...prev,
                password: e.target.value,
              }))
            }
            required
            disabled={cargando}
          />

          <p className="form-link-center" style={{ marginTop: 8 }}>
            <button
              type="button"
              className="link"
              onClick={() => navigate("/reset-password")}
            >
              ¿Has olvidado tu contraseña?
            </button>
          </p>

          <button
            type="submit"
            className="btn btn-primary form-button"
            disabled={cargando}
          >
            {cargando ? "Entrando..." : "Entrar"}
          </button>

          {errorFormulario && (
            <p className="form-error">{errorFormulario}</p>
          )}
        </form>

        <p className="form-link-center" style={{ marginTop: 12 }}>
          ¿No tienes cuenta?
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
}