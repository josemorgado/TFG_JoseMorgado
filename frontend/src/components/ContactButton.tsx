import { useNavigate } from "react-router-dom";

export default function ContactButton() {
  const navigate = useNavigate();

  const handleContact = async () => {
    try {
      navigate("/contact");
    }catch (error) {
      console.error("Error al navegar a contacto", error);
      alert("No se pudo navegar a contacto");
    }

  };

  return (
    <button className="auth-button" onClick={handleContact}>
      Contacto
    </button>
  );
}
