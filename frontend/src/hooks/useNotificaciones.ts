import { useCallback, useEffect, useRef, useState } from "react";
import type { Notificacion, Paginated } from "../types/notificaciones";
import {
  deleteNotification,
  getNotifications,
  getUnreadCount,
  markAllRead,
  markRead,
  markUnread,
} from "../api/notificaciones";

export function useNotificaciones(options?: {
  initialPageSize?: number;
  pollIntervalMs?: number;
}) {
  const pageSize = options?.initialPageSize ?? 10;
  const pollIntervalMs = options?.pollIntervalMs ?? 0;

  const [page, setPage] = useState(1);
  const [data, setData] = useState<Paginated<Notificacion> | null>(null);
  const [loading, setLoading] = useState(false);
  const [unread, setUnread] = useState<number>(0);
  const [error, setError] = useState<string | null>(null);

  const isMounted = useRef(true);

  const fetchUnread = useCallback(async () => {
    try {
      const count = await getUnreadCount();
      if (!isMounted.current) return;
      setUnread(count);
    } catch (err) {
    }
  }, []);

  const fetchPage = useCallback(
    async (newPage?: number) => {
      setLoading(true);
      setError(null);
      try {
        const p = newPage ?? page;
        const resp = await getNotifications({ page: p, page_size: pageSize });
        if (!isMounted.current) return;
        setData(resp);
      } catch (err: any) {
        if (!isMounted.current) return;
        setError(err?.message ?? "Error al cargar notificaciones");
      } finally {
        if (isMounted.current) setLoading(false);
      }
    },
    [page, pageSize]
  );

  const refresh = useCallback(async () => {
    await Promise.all([fetchUnread(), fetchPage()]);
  }, [fetchUnread, fetchPage]);

  useEffect(() => {
    isMounted.current = true;
    refresh();
    let timer: number | undefined;
    if (pollIntervalMs > 0) {
      timer = window.setInterval(refresh, pollIntervalMs);
    }
    return () => {
      isMounted.current = false;
      if (timer) window.clearInterval(timer);
    };
  }, [pollIntervalMs, refresh]);

  const onMarkRead = useCallback(
    async (id: number) => {
      setData((prev) =>
        prev
          ? {
              ...prev,
              results: prev.results.map((n) =>
                n.id === id ? { ...n, is_read: true } : n
              ),
            }
          : prev
      );
      setUnread((u) => Math.max(0, u - 1));
      try {
        await markRead(id);
      } catch {
        await refresh();
      }
    },
    [refresh]
  );

  const onMarkUnread = useCallback(
    async (id: number) => {
      setData((prev) =>
        prev
          ? {
              ...prev,
              results: prev.results.map((n) =>
                n.id === id ? { ...n, is_read: false } : n
              ),
            }
          : prev
      );
      setUnread((u) => u + 1);
      try {
        await markUnread(id);
      } catch {
        await refresh();
      }
    },
    [refresh]
  );

  const onMarkAllRead = useCallback(async () => {
    setData((prev) =>
      prev
        ? { ...prev, results: prev.results.map((n) => ({ ...n, is_read: true })) }
        : prev
    );
    setUnread(0);
    try {
      await markAllRead();
    } catch {
      await refresh();
    }
  }, [refresh]);

  const onDelete = useCallback(
    async (id: number) => {
      setData((prev) =>
        prev
          ? { ...prev, results: prev.results.filter((n) => n.id !== id) }
          : prev
      );
      try {
        await deleteNotification(id);
        await fetchUnread();
      } catch {
        await refresh();
      }
    },
    [fetchUnread, refresh]
  );

  const setPageAndFetch = useCallback(
    (p: number) => {
      setPage(p);
      fetchPage(p);
    },
    [fetchPage]
  );

  return {
    unread,
    data,
    loading,
    error,
    page,
    pageSize,
    setPage: setPageAndFetch,
    refresh,
    onMarkRead,
    onMarkUnread,
    onMarkAllRead,
    onDelete,
  };
}
