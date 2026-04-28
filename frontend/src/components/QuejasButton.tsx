// QuejasButton.tsx
import { useNavigate } from "react-router-dom";

type QuejasButtonProps = {
  onClick?: () => void;
};

export default function QuejasButton({ onClick }: QuejasButtonProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    onClick?.();
    navigate("/quejas");
  };

  return (
    <button className="auth-button" onClick={handleClick}>
      Quejas
    </button>
  );
}