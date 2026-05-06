import { useState } from "react";
import { useLocation, useNavigate, useParams } from "react-router-dom";
import { Navigate } from "react-router-dom";
import { changePassword } from "../api/perfil";
import PageError from "../components/PageError";
import { useAuth } from "../context/AuthContext";

export default function ChangePassword() {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const {user} = useAuth();
  if (!id) {
    return <PageError message="Falta la ID del usuario en la URL." />;
  }

  const idUsuario = Number(id);
  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  if (user?.id !== Number(id)) {
    return <Navigate to="/ruta-prohibida" replace />;
  }

  if (Number.isNaN(idUsuario)) {
    return <PageError message="La ID del usuario no es válida." />;
  }

  const formularioAnterior = location.state?.formData || null;

  const [contrasenaActual, setContrasenaActual] = useState("");
  const [nuevaContrasena, setNuevaContrasena] = useState("");
  const [repetirContrasena, setRepetirContrasena] = useState("");

  const [errorFormulario, setErrorFormulario] = useState<string | null>(null);
  const [guardando, setGuardando] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorFormulario(null);

    if (nuevaContrasena !== repetirContrasena) {
      setErrorFormulario("Las nuevas contraseñas no coinciden.");
      return;
    }

    const confirmado = window.confirm(
      "¿Estás seguro de que quieres cambiar la contraseña?",
    );
    if (!confirmado) return;

    try {
      setGuardando(true);
      await changePassword(idUsuario, contrasenaActual, nuevaContrasena);

      navigate(`/perfil/${idUsuario}/update`, {
        state: { formData: formularioAnterior },
      });
    } catch (err: any) {
      const mensajeBackend =
        err?.response?.data?.detail || "Error al cambiar la contraseña.";
      setErrorFormulario(mensajeBackend);
    } finally {
      setGuardando(false);
    }
  };

  const handleDescartar = () => {
    navigate(`/perfil/${idUsuario}/update`, {
      state: { formData: formularioAnterior },
    });
  };

  return (
    <div className="form-page">
      <div className="form-card">
        <h1 className="form-title">Cambiar contraseña</h1>

        <form className="form-container" onSubmit={handleSubmit}>
          <label className="form-label">Contraseña actual</label>
          <input
            type="password"
            className="form-input"
            value={contrasenaActual}
            onChange={(e) => setContrasenaActual(e.target.value)}
            required
          />

          <label className="form-label">Nueva contraseña</label>
          <input
            type="password"
            className="form-input"
            value={nuevaContrasena}
            onChange={(e) => setNuevaContrasena(e.target.value)}
            required
          />

          <label className="form-label">Repite la nueva contraseña</label>
          <input
            type="password"
            className="form-input"
            value={repetirContrasena}
            onChange={(e) => setRepetirContrasena(e.target.value)}
            required
          />

          {errorFormulario && (
            <p className="form-error">{errorFormulario}</p>
          )}

          <button
            type="button"
            className="btn btn-secondary form-button"
            onClick={handleDescartar}
            disabled={guardando}
          >
            Descartar cambios
          </button>

          <button
            type="submit"
            className="btn btn-primary form-button"
            disabled={guardando}
          >
            {guardando ? "Guardando..." : "Guardar cambios"}
          </button>
        </form>
      </div>
    </div>
  );
}