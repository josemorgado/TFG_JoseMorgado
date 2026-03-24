import { useNavigate } from "react-router-dom";

interface Props {
  unreadNCount: number;
}

export default function NotificacionesButton({ unreadNCount }: Props) {
  const navigate = useNavigate();

  const handleClick = () => {
    navigate("/notificaciones");
  };

  return (
    <div style={{ position: "relative", display: "inline-block" }}>
      <button className="auth-button" onClick={handleClick}>
        Notificaciones
      </button>

      {unreadNCount > 0 && (
        <span className="notification-badge">
          {unreadNCount}
        </span>
      )}
    </div>
  );
}