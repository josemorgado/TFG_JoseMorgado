import { useNavigate } from "react-router-dom";

export default function ModeratorButton() {
  const navigate = useNavigate();

  const handleModeratorPanel = () => {
    navigate("/moderador");
  };

  return (
    <button
      className="auth-button"
      onClick={handleModeratorPanel}
    >
      Panel de moderación
    </button>
  );
}
