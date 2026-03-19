import { useState } from "react";
import NotificacionDropdown from "./NotificacionDropdown";

interface Props {
  unread: number;
  onClick?: () => void;
}

export default function NotificacionBell({ unread }: Props) {
  const [open, setOpen] = useState(false);

  return (
    <div className="notification-bell" style={{ position: "relative" }}>
      <button
        aria-label="Notificaciones"
        className="btn-icon"
        onClick={() => setOpen((o) => !o)}
      >
        {/* Icono simple de campana (SVG) */}
        <svg width="24" height="24" viewBox="0 0 24 24" aria-hidden>
          <path
            fill="currentColor"
            d="M12 22a2 2 0 0 0 2-2h-4a2 2 0 0 0 2 2m6-6v-5a6 6 0 0 0-5-5.91V4a1 1 0 0 0-2 0v1.09A6 6 0 0 0 6 11v5l-2 2v1h16v-1z"
          />
        </svg>
        {unread > 0 && (
          <span
            className="badge"
            style={{
              position: "absolute",
              top: -4,
              right: -4,
              minWidth: 18,
              height: 18,
              padding: "0 6px",
              borderRadius: 9,
              fontSize: 12,
              background: "#e11d48",
              color: "white",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            {unread}
          </span>
        )}
      </button>

      {open && (
        <div
          className="dropdown"
          style={{
            position: "absolute",
            right: 0,
            marginTop: 8,
            width: 360,
            maxWidth: "90vw",
            background: "white",
            border: "1px solid #e5e7eb",
            borderRadius: 8,
            boxShadow: "0 10px 25px rgba(0,0,0,0.08)",
            zIndex: 50,
          }}
        >
          <NotificacionDropdown onClose={() => setOpen(false)} />
        </div>
      )}
    </div>
  );
}