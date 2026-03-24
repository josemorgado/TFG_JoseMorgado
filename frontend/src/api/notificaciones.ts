// src/api/notifications.ts
import axios from "../utils/axios";
import type { Notificacion, Paginated } from "../types/notificaciones";

export async function getNotifications(params?: {
  page?: number;
  page_size?: number;
  is_read?: boolean;
}): Promise<Paginated<Notificacion>> {
  const { page, page_size, is_read } = params || {};
  const resp = await axios.get<Paginated<Notificacion>>("/notificaciones/", {
    params: {
      page,
      page_size,
      is_read: typeof is_read === "boolean" ? (is_read ? "true" : "false") : undefined,
    },
  });
  return resp.data;
}

export async function getUnreadCount(): Promise<number> {
  const resp = await axios.get<{ unread: number }>("/notificaciones/unread-count/");
  return resp.data.unread;
}

export async function markRead(id: number): Promise<void> {
  window.dispatchEvent(new Event("notificaciones-actualizadas"));
  await axios.patch(`/notificaciones/${id}/read/`);
}

export async function markUnread(id: number): Promise<void> {
  window.dispatchEvent(new Event("notificaciones-actualizadas"));
  await axios.patch(`/notificaciones/${id}/unread/`);
}

export async function markAllRead(): Promise<void> {
  window.dispatchEvent(new Event("notificaciones-actualizadas"));
  await axios.patch("/notificaciones/read-all/");
}

export async function deleteNotification(id: number): Promise<void> {
  window.dispatchEvent(new Event("notificaciones-actualizadas"));
  await axios.delete(`/notificaciones/${id}/`);
}