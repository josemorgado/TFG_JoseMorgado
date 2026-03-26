import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function MiPerfilButton() {
  const { user } = useAuth();
  const navigate = useNavigate();

  const goToProfile = () => {
    if (!user?.id) return;
    navigate(`/perfil/${user.id}`);
  };

  const iniciales = (() => {
    if (!user) return "";
    const nombre = `${user.first_name || ""} ${user.last_name || ""}`.trim();
    if (nombre) {
      const partes = nombre.split(/\s+/).filter(Boolean);
      return partes.slice(0, 2).map(p => p[0]?.toUpperCase()).join("");
    }
    return user.username?.slice(0, 2).toUpperCase() ?? "";
  })();

  return (
    <div
      onClick={goToProfile}
      style={{
        width: 40,
        height: 40,
        borderRadius: "50%",
        cursor: "pointer",
        overflow: "hidden",
        border: "2px solid var(--color-primary)",
        boxShadow: "var(--shadow-soft)",
        background: "var(--color-light)",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        userSelect: "none",
        fontWeight: "bold",
        fontSize: "0.9rem",
      }}
    >
      {iniciales}
    </div>
  );
}