import { Link, useLocation } from "react-router-dom";
import "../styles/Navbar.css";
import LoginButton from "./LoginButton";
import CreateAccountButton from "./CreateAccountButton";
import MiPerfilButton from "./MiPerfilButton";
import { useAuth } from "../context/AuthContext";
import QuejasButton from "./QuejasButton";
import StatsButton from "./StatsButton";
import NotificacionesButton from "./NotificacionesButton";
import { getUnreadCount } from "../api/notificaciones";
import { useState, useEffect } from "react";
const Navbar: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();

  const [unreadCount, setUnreadCount] = useState(0);
  const isLoginPage = location.pathname === "/login";


useEffect(() => {
  if (!user) return;

  const loadCount = async () => {
    try {
      const count = await getUnreadCount();
      setUnreadCount(count);
    } catch (error) {
      console.error("Error obteniendo notificaciones:", error);
    }
  };

  // 1. Cargar al entrar por primera vez
  loadCount();

  // 2. Función que se ejecutará cuando se dispare el evento
  const handleUpdate = () => {
    loadCount();
  };

  // 3. Escuchar el evento personalizado
  window.addEventListener("notificaciones-actualizadas", handleUpdate);

  // 4. Cleanup
  return () => {
    window.removeEventListener("notificaciones-actualizadas", handleUpdate);
  };

}, [user]);


  return (
    <nav className="navbar">
      <div className="logo">
        <Link to="/">ALCALDE ESCUCHAME</Link>
      </div>

      <ul className="nav-links">
        <StatsButton />
        <QuejasButton />
        {user && <NotificacionesButton unreadNCount={unreadCount} />}


        {!user && (
          <li>
            {isLoginPage ? (
              <CreateAccountButton />
            ) : (
              <LoginButton />
            )}
          </li>
        )}
        {user && <MiPerfilButton />}

      </ul>
    </nav>
  );
};

export default Navbar;