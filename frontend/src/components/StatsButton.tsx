import { useNavigate } from "react-router-dom";

export default function LoginButton() {
  const navigate = useNavigate();
  const handleLogout = async () => {
      navigate("/stats");
  };

  return (
    <button className="auth-button"onClick={handleLogout}>
      Estadisticas
    </button>
  );
}
