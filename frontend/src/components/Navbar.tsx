import { Link, useLocation, useNavigate } from "react-router-dom";
import "./Navbar.css";
import LoginButton from "./LoginButton";
import LogoutButton from "./LogoutButton";
import CreateAccountButton from "./CreateAccountButton";
import { useAuth } from "../context/AuthContext";

const Navbar: React.FC = () => {
  const { user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

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