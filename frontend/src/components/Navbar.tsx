import { Link, useLocation } from "react-router-dom";
import "../styles/Navbar.css";
import LoginButton from "./LoginButton";
import LogoutButton from "./LogoutButton";
import CreateAccountButton from "./CreateAccountButton";
import CreateQuejaButton from "./CreateQuejaButton";
import { useAuth } from "../context/AuthContext";

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
        <li>
          <Link to="/">Inicio</Link>
        </li>

        <CreateQuejaButton />

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
      </ul>
    </nav>
  );
};

export default Navbar;