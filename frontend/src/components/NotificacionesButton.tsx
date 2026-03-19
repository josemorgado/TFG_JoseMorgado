import { useNavigate } from "react-router-dom";

export default function LoginButton() {
  const navigate = useNavigate();
  const handleLogout = async () => {
      navigate("/notificaciones");
  };

  return (
    <button className="auth-button"onClick={handleLogout}>
      Notificaciones
    </button>
  );
}
