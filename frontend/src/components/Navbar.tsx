import { Link, useLocation } from "react-router-dom";
import "../styles/Navbar.css";

import LoginButton from "./LoginButton";
import CreateAccountButton from "./CreateAccountButton";
import MiPerfilButton from "./MiPerfilButton";
import QuejasButton from "./QuejasButton";
import StatsButton from "./StatsButton";
import NotificacionesButton from "./NotificacionesButton";
import ContactButton from "./ContactButton";

import { useAuth } from "../context/AuthContext";
import { useNotifications } from "../context/NotificationsContext";
import LogoutButton from "./LogoutButton";

const Navbar: React.FC = () => {
  const { user } = useAuth();
  const { unreadCount } = useNotifications();
  const location = useLocation();

  const isLoginPage = location.pathname === "/login";

  return (
    <nav className="navbar">
      <div className="logo">
        <Link to="/">ALCALDE ESCÚCHAME</Link>
      </div>

      <ul className="nav-links">
        <QuejasButton />
        <StatsButton />
        <ContactButton />
        <LogoutButton />

        {user && (
          <NotificacionesButton unreadNCount={unreadCount} />
        )}

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