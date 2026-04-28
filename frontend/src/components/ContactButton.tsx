import { useNavigate } from "react-router-dom";

type ContactButtonProps = {
  onClick?: () => void;
};

export default function ContactButton({ onClick }: ContactButtonProps) {
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