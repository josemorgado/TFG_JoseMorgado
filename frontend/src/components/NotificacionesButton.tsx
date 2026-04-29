import { useNavigate } from "react-router-dom";

interface Props {
  unreadNCount: number;
  onClick?: () => void;
}

export default function NotificacionesButton({
  unreadNCount,
  onClick,
}: Props) {
  const navigate = useNavigate();

  const handleClick = () => {
    onClick?.();
    navigate("/notificaciones");
  };

  return (
    <div className="notification-wrapper">
      <button className="auth-button" onClick={handleClick}>
        Notificaciones
      </button>

      {unreadNCount > 0 && (
        <span className="notification-badge">
          {unreadNCount > 99 ? "99+" : unreadNCount}
        </span>
      )}
    </div>
  );
}