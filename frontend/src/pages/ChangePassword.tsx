import { useLocation, useNavigate, useParams } from "react-router-dom";
import { useState } from "react";
import { changePassword } from "../api/perfil";
export default function ChangePassword() {
  const { id } = useParams();
  const navigate = useNavigate();

  // Recuperamos los datos del formulario de update perfil
  const location = useLocation();
  const previousFormData = location.state?.formData || null;

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [repeatPassword, setRepeatPassword] = useState("");

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (newPassword !== repeatPassword) {
      setError("Las nuevas contraseñas no coinciden.");
      return;
    }
    if (! window.confirm("¿Estas seguro de que quieres cambiar la contraseña?")){
        return;
    }
    setLoading(true);

    try {
      await changePassword(id!, currentPassword, newPassword);

      navigate(`/perfil/${id}/update`, {
        state: { formData: previousFormData },
      });
    } catch (err: any) {
      setError(err.response?.data?.detail || "Error al cambiar la contraseña.");
    } finally {
      setLoading(false);
    }
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
            value={currentPassword}
            onChange={(e) => setCurrentPassword(e.target.value)}
            required
          />

          <label className="form-label">Nueva contraseña</label>
          <input
            type="password"
            className="form-input"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            required
          />

          <label className="form-label">Repite la nueva contraseña</label>
          <input
            type="password"
            className="form-input"
            value={repeatPassword}
            onChange={(e) => setRepeatPassword(e.target.value)}
            required
          />

          {error && <p className="form-error">{error}</p>}
          <button
            type="button"
            className="btn btn-secondary form-button"
            onClick={() =>
              navigate(`/perfil/${id}/update`, {
                state: { formData: previousFormData },
              })
            }
          >
            Descartar cambios
          </button>
          <button
            type="submit"
            className="btn btn-primary form-button"
            disabled={loading}
          >
            {loading ? "Guardando..." : "Guardar cambios"}
          </button>
        </form>
      </div>
    </div>
  );
}
