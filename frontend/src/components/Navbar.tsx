import { Link, useLocation } from "react-router-dom";
import "../styles/Navbar.css";
import LoginButton from "./LoginButton";
import LogoutButton from "./LogoutButton";
import CreateAccountButton from "./CreateAccountButton";
import CreateQuejaButton from "./CreateQuejaButton";
import MiPerfilButton from "./MiPerfilButton";
import { useAuth } from "../context/AuthContext";
import QuejasButton from "./QuejasButton";
import StatsButton from "./StatsButton";
import NotificacionesButton from "./NotificacionesButton";

const Navbar: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();

  const isLoginPage = location.pathname === "/login";

  return (
    <nav className="navbar">
      <div className="logo">
        <Link to="/">ALCALDE ESCUCHAME</Link>
      </div>

      <ul className="nav-links">
        <StatsButton />
        <QuejasButton />
        <CreateQuejaButton />
        {user && <NotificacionesButton />
        }


        {user ? (
          <li>
            <LogoutButton />

          </li>
        ) : (
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