import { useNavigate } from "react-router-dom";

type LoginButtonProps = {
  onClick?: () => void;
};

export default function LoginButton({ onClick }: LoginButtonProps) {
  const navigate = useNavigate();

  const handleClick = () => {
    onClick?.();
    navigate("/stats");
  };

  return (
    <button className="auth-button" onClick={handleClick}>
      Estadísticas
    </button>
  );
}