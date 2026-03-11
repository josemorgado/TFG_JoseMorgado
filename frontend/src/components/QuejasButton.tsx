// QuejasButton.tsx
import { useNavigate } from "react-router-dom";

export default function QuejasButton() {
  const navigate = useNavigate();
  const handleClick = () => {
    navigate("/quejas");
  };

  return (
    <button className="auth-button" onClick={handleClick}>
      Quejas
    </button>
  );
}