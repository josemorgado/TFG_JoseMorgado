// src/pages/NotificationsPage.tsx
import { useEffect, useMemo } from "react";
import { useNotificaciones } from "../hooks/useNotificaciones";
import { useSearchParams, useNavigate } from "react-router-dom";
import "../styles/Notificaciones.css";

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

  const totalPages = useMemo(() => {
    if (!data?.count) return 1;
    return Math.ceil(data.count / pageSize);
  }, [data, pageSize]);

  useEffect(() => {
    if (page !== pageParam) {
      setPage(pageParam);
    }
  }, [pageParam, page, setPage]);

  const goTo = (p: number) => {
    setParams({ page: String(p) });
    setPage(p);
  };

  const hasUnread = useMemo(
    () => Boolean(data?.results?.some(n => !n.is_read)),
    [data]
  );

  return (
    <div className="notifications-page">
      {/* Header */}
      <div className="notifications-header">
        <h1 className="notifications-title">Notificaciones</h1>

        <div className="notifications-actions">
          <button className="btn btn-secondary" onClick={refresh}>
            Actualizar
          </button>
          {hasUnread && (
            <button className="btn btn-primary" onClick={onMarkAllRead}>
              Marcar todas como leídas
            </button>)}

        </div>
      </div>

      {/* Estados */}
      {loading && <p>Cargando…</p>}
      {error && <p style={{ color: "var(--color-danger)" }}>{error}</p>}

      {!loading && !error && data?.results?.length === 0 && (
        <div className="notifications-empty">
          No hay notificaciones por mostrar
        </div>
      )}

      {/* Lista */}
      <ul className="notifications-list">
        {data?.results.map((n) => (
          <li
            key={n.id}
            className={`notification-item ${!n.is_read ? "is-unread" : ""}`}
          >
            {/* Área principal clicable */}
            <div
              className="notification-main"
              onClick={async () => {
                // Evitar llamadas redundantes si ya está leída
                if (!n.is_read) await onMarkRead(n.id);
                if (n.url) navigate(n.url);
              }}
            >
              <div className="notification-head">
                <strong className="notification-title">{n.title}</strong>
                <small className="notification-meta">
                  {n.created_at}
                </small>
              </div>

              <p className="notification-message">{n.message}</p>
            </div>

            {/* Acciones secundarias */}
            <div className="notification-actions">
              {!n.is_read ? (
                <button className="btn-sm" onClick={() => onMarkRead(n.id)}>
                  Marcar leída
                </button>
              ) : (
                <button className="btn-sm" onClick={() => onMarkUnread(n.id)}>
                  Marcar no leída
                </button>
              )}

              <button
                className="btn-sm danger"
                onClick={() => onDelete(n.id)}
              >
                Eliminar
              </button>
            </div>
          </li>
        ))}
      </ul>

      {/* Paginación */}
      {data && data.count > pageSize && (
        <div className="notifications-pagination">
          <button
            className="btn btn-secondary"
            disabled={!data.previous}
            onClick={() => goTo(Math.max(1, page - 1))}
          >
            Anterior
          </button>

          <span className="page-label">{page}/{totalPages}</span>

          <button
            className="btn btn-secondary"
            disabled={!data.next}
            onClick={() => goTo(page + 1)}
          >
            Siguiente
          </button>
        </div>
      )}
    </div>
  );
}