// CreateQuejaButton.tsx
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

type LoginState = {
  reason?: "create-queja";
  from?: { pathname?: string };
};

export default function CreateQuejaButton() {
  const navigate = useNavigate();
  const location = useLocation();
  const { user } = useAuth();

  const handleClick = () => {
    if (!user) {
      const state: LoginState = {
        reason: "create-queja",
        from: { pathname: location.pathname },
      };
      navigate("/login", { state });
      return;
    }
    navigate("/create-queja");
  };

  return (
    <button className="auth-button" onClick={handleClick}>
      Crear Queja
    </button>
  );
}