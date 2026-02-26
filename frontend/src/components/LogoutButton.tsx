import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { apiLogout } from "../api/auth";

export default function LogoutButton() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await apiLogout(); // Llamada a la API para invalidar el refresh token
    } finally {
      logout();
      navigate("/login");
    }

  };

  return (
    <button onClick={handleLogout}>
      Cerrar sesión
    </button>
  );
}
