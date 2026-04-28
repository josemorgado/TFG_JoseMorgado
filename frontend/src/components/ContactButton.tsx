import { useNavigate } from "react-router-dom";

type LogoutButtonProps = {
  onClick?: () => void;
};

export default function LogoutButton({ onClick }: LogoutButtonProps) {
  const navigate = useNavigate();

  const handleContact = () => {
    onClick?.();
    navigate("/contact");
  };

  return (
    <button className="auth-button" onClick={handleContact}>
      Contacto
    </button>
  );
}