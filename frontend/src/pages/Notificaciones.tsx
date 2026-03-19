// src/pages/NotificationsPage.tsx
import { useEffect } from "react";
import { useNotificaciones } from "../hooks/useNotificaciones";
import { formatDateTime } from "../utils/format";
import { useSearchParams, useNavigate } from "react-router-dom";

export default function NotificationsPage() {
  const [params, setParams] = useSearchParams();
  const navigate = useNavigate();

  const pageParam = Number(params.get("page") ?? "1");
  const pageSize = 10;

  const {
    data,
    page,
    setPage,
    loading,
    error,
    onMarkRead,
    onMarkUnread,
    onDelete,
    onMarkAllRead,
    refresh,
  } = useNotificaciones({ initialPageSize: pageSize });

  useEffect(() => {
    if (page !== pageParam) {
      setPage(pageParam);
    }
  }, [pageParam, page, setPage]);

  const goTo = (p: number) => {
    setParams({ page: String(p) });
    setPage(p);
  };

  return (
    <div className="container" style={{ maxWidth: 800, margin: "24px auto", padding: "0 12px" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1 style={{ margin: 0 }}>Notificaciones</h1>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn" onClick={refresh}>Actualizar</button>
          <button className="btn" onClick={onMarkAllRead}>Marcar todas como leídas</button>
        </div>
      </div>

      {loading && <p>Cargando…</p>}
      {error && <p style={{ color: "#b91c1c" }}>{error}</p>}

      <ul style={{ listStyle: "none", padding: 0, marginTop: 16 }}>
        {data?.results.map((n) => (
          <li
            key={n.id}
            style={{
              display: "grid",
              gridTemplateColumns: "1fr auto",
              gap: 8,
              padding: 12,
              border: "1px solid #e5e7eb",
              borderRadius: 8,
              background: n.is_read ? "white" : "#f8fafc",
              marginBottom: 10,
            }}
          >
            <div onClick={async () => {
              await onMarkRead(n.id);
              if (n.url) navigate(n.url);
            }} style={{ cursor: "pointer" }}>
              <div style={{ display: "flex", gap: 8, alignItems: "baseline" }}>
                <strong style={{ fontSize: 16 }}>{n.title}</strong>
                <small style={{ color: "#6b7280" }}>{formatDateTime(n.created_at)}</small>
              </div>
              <p style={{ margin: "6px 0 0 0", color: "#374151" }}>{n.message}</p>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 8, alignItems: "flex-end" }}>
              {!n.is_read ? (
                <button className="btn-sm" onClick={() => onMarkRead(n.id)}>Marcar leída</button>
              ) : (
                <button className="btn-sm" onClick={() => onMarkUnread(n.id)}>Marcar no leída</button>
              )}
              <button className="btn-sm danger" onClick={() => onDelete(n.id)} style={{ color: "#b91c1c" }}>
                Eliminar
              </button>
            </div>
          </li>
        ))}
      </ul>

      {/* Paginación simple */}
      {data && data.count > pageSize && (
        <div style={{ display: "flex", gap: 8, justifyContent: "center", marginTop: 16 }}>
          <button className="btn" disabled={!data.previous} onClick={() => goTo(Math.max(1, page - 1))}>
            Anterior
          </button>
          <span style={{ alignSelf: "center" }}>Página {page}</span>
          <button className="btn" disabled={!data.next} onClick={() => goTo(page + 1)}>
            Siguiente
          </button>
        </div>
      )}
    </div>
  );
}
