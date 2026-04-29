import { Link, useLocation } from "react-router-dom";
import { useEffect, useState } from "react";
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

const Navbar: React.FC = () => {
  const { user } = useAuth();
  const { unreadCount } = useNotifications();
  const location = useLocation();

  const [menuOpen, setMenuOpen] = useState(false);

  const isLoginPage = location.pathname === "/login";

  const closeMenu = () => setMenuOpen(false);

  useEffect(() => {
    setMenuOpen(false);
  }, [location.pathname]);

  return (
    <nav className="navbar">
      <div className="logo">
        <Link to="/" onClick={closeMenu}>
          ALCALDE ESCÚCHAME
        </Link>
      </div>

      {/* HAMBURGER */}
      <button
        className="menu-toggle"
        onClick={() => setMenuOpen((prev) => !prev)}
        aria-label="Abrir menú"
        aria-expanded={menuOpen}
      >
        ☰
      </button>

      <ul className={`nav-links ${menuOpen ? "open" : ""}`}>
        <QuejasButton onClick={closeMenu} />
        <StatsButton onClick={closeMenu} />
        <ContactButton onClick={closeMenu} />

        {user && (
          <NotificacionesButton
            unreadNCount={unreadCount}
            onClick={closeMenu}
          />
        )}

        {!user && (
          <li onClick={closeMenu}>
            {isLoginPage ? (
              <CreateAccountButton />
            ) : (
              <LoginButton />
            )}
          </li>
        )}

        {user && <MiPerfilButton onClick={closeMenu} />}
      </ul>
    </nav>
  );
};

export default Navbar;
