import { useNavigate, useLocation } from "react-router-dom";
import "../styles/rutaProhibida.css";

export default function RutaProhibida() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="ruta-prohibida-page">
      <div className="ruta-prohibida-card card">

        <h1 className="ruta-prohibida-title">Acceso no permitido</h1>

        <p className="ruta-prohibida-msg">
          No tienes permiso para acceder a esta página.
        </p>

        {location.state?.attemptedId && (
          <p className="ruta-prohibida-sub">
            ID bloqueada: {location.state.attemptedId}
          </p>
        )}

        <button
          className="btn btn-primary ruta-prohibida-btn"
          onClick={() => navigate(-1)}
        >
          Volver atrás
        </button>

      </div>
    </div>
  );
}