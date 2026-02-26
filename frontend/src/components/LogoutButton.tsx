import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function LogoutButton() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
      logout();            // limpia tokens y user
      navigate("/");
  };

  return (
    <button onClick={handleLogout}>
      Cerrar sesión
    </button>
  );
}
