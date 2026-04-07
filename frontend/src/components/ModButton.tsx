import { useAuth } from "../context/AuthContext";
import { toggleModerator } from "../api/perfil";

type ModButtonProps = {
  targetUserId: number;
  targetIsModerator: boolean;
  onUpdated?: (updatedUser: any) => void;
};

export default function ModButton({
  targetUserId,
  targetIsModerator,
  onUpdated,
}: ModButtonProps) {
  const { user: userActivo } = useAuth();

  if (!userActivo?.perfil?.moderator) return null;

  const handleToggleModerator = async () => {
    const actionText = targetIsModerator
      ? "quitar el rol de moderador"
      : "asignar el rol de moderador";

    const confirmed = window.confirm(
      `¿Estás seguro de que deseas ${actionText} a este usuario?`
    );

    if (!confirmed) return;

    try {
      const updatedUser = await toggleModerator(
        targetUserId,
        targetIsModerator
      );

      // Permite refrescar el perfil mostrado
      onUpdated?.(updatedUser);
    } catch (error) {
      console.error("Error al cambiar moderador", error);
      alert("No se pudo cambiar el rol de moderador");
    }
  };

  return (
    <button className="auth-button" onClick={handleToggleModerator}>
      {targetIsModerator ? "Quitar moderador" : "Hacer moderador"}
    </button>
  );
}