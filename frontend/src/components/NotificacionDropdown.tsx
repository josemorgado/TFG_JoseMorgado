// src/components/notifications/NotificationDropdown.tsx
import { useNavigate } from "react-router-dom";
import { useNotificaciones } from "../hooks/useNotificaciones";

interface Props {
  onClose: () => void;
}

export default function NotificacionDropdown({ onClose }: Props) {
  const navigate = useNavigate();
  const {
    data,
    unread,
    loading,
    onMarkAllRead,
    onMarkRead,
    onDelete,
    refresh,
  } = useNotificaciones({ initialPageSize: 10 });

  const handleOpen = async (id: number, url: string | null) => {
    // marca como leída y navega
    await onMarkRead(id);
    if (url) navigate(url);
    onClose();
  };

  return (
    <div style={{ padding: 12 }}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 8,
          justifyContent: "space-between",
          marginBottom: 8,
        }}
      >
        <strong>Notificaciones</strong>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn-link" onClick={refresh}>Actualizar</button>
          {unread > 0 && (
            <button className="btn-link" onClick={onMarkAllRead}>
              Marcar todas como leídas
            </button>
          )}
        </div>
      </div>

      {loading && <p>Cargando…</p>}
      {!loading && (!data || data.results.length === 0) && (
        <p style={{ color: "#6b7280" }}>No tienes notificaciones.</p>
      )}

      <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
        {data?.results.slice(0, 10).map((n) => (
          <li
            key={n.id}
            style={{
              padding: "8px 6px",
              borderRadius: 6,
              background: n.is_read ? "transparent" : "#f1f5f9",
              border: "1px solid #e5e7eb",
              marginBottom: 6,
              cursor: "pointer",
            }}
          >
            <div
              onClick={() => handleOpen(n.id, n.url)}
              style={{ display: "flex", flexDirection: "column", gap: 6 }}
            >
              <div style={{ display: "flex", justifyContent: "space-between" }}>
                <span style={{ fontWeight: 600 }}>{n.title}</span>
                <small style={{ color: "#6b7280" }}>{(n.created_at)}</small>
              </div>
              <span style={{ color: "#374151" }}>{n.message}</span>
            </div>

            <div style={{ marginTop: 6, display: "flex", gap: 8 }}>
              {!n.is_read && (
                <button className="btn-link" onClick={() => onMarkRead(n.id)}>
                  Marcar leída
                </button>
              )}
              {n.is_read && (
                <button className="btn-link" onClick={() => onMarkRead(n.id)}>
                  Volver a abrir
                </button>
              )}
              <button
                className="btn-link danger"
                onClick={() => onDelete(n.id)}
                style={{ color: "#b91c1c" }}
              >
                Eliminar
              </button>
            </div>
          </li>
        ))}
      </ul>

      <div style={{ textAlign: "right", marginTop: 8 }}>
        <button
          className="btn-link"
          onClick={() => {
            onClose();
            navigate("/notificaciones");
          }}
        >
          Ver todas
        </button>
      </div>
    </div>
  );
}
