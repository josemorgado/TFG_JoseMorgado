// src/components/MiPerfilButton.tsx

import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import perfilIcon from "../assets/icons/perfil-icon.png"; // ✅ Importar imagen

export default function MiPerfilButton() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const goToProfile = () => {
    if (!user || !user.id) return;
    navigate(`/perfil/${user.id}`);
  };

  return (
    <img
      src={perfilIcon}
      alt="Mi perfil"
      onClick={goToProfile}
      style={{
        width: 40,
        height: 40,
        cursor: "pointer",
        objectFit: "cover",
        borderRadius: "50%",
        border: "2px solid var(--color-primary)",
        boxShadow: "var(--shadow-soft)",
      }}
    />
  );
}
