// src/api/respuestas.ts
import api from "../utils/axios";
import { isAxiosError } from "axios";
import type {Paginated,RespuestaDTO, CreateRespuestaPayload, UpdateRespuestaPayload} from "../types/respuestas"

/* =========================
 * Endpoints
 * ========================= */
export const RESPUESTAS_ENDPOINTS = {
  listarPorQueja: (quejaId: number | string) => `/quejas/${quejaId}/respuestas/`,
  crear: (quejaId: number | string) => `/quejas/${quejaId}/respuestas/crear/`,
  detallePublico: (respuestaId: number | string) => `/respuestas/${respuestaId}/`,
  admin: (respuestaId: number | string) => `/respuestas/${respuestaId}/admin/`,
} as const;

/* =========================
 * Errores
 * ========================= */
export type ValidationErrors = Record<string, string[] | string>;
export class ApiError extends Error {
  status?: number;
  details?: unknown;
  constructor(message: string, status?: number, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

function wrapError(err: unknown): never {
  if (isAxiosError(err)) {
    const status = err.response?.status;
    const details = err.response?.data;
    const msg =
      (typeof details === "string" && details) ||
      (details?.detail as string) ||
      err.message ||
      "Error de API";
    throw new ApiError(msg, status, details);
  }
  throw err instanceof Error ? err : new Error(String(err));
}

/* =========================
 * API
 * ========================= */

export async function listarRespuestasPorQueja(
  quejaId: number | string,
  params?: { page?: number; page_size?: number }
): Promise<Paginated<RespuestaDTO>> {
  try {
    const { data } = await api.get<Paginated<RespuestaDTO>>(
      RESPUESTAS_ENDPOINTS.listarPorQueja(quejaId),
      { params }
    );
    return data;
  } catch (err) {
    wrapError(err);
  }
}

export async function crearRespuesta(
  quejaId: number | string,
  payload: CreateRespuestaPayload
): Promise<RespuestaDTO> {
  try {
    const { data } = await api.post<RespuestaDTO>(
      RESPUESTAS_ENDPOINTS.crear(quejaId),
      payload
    );
    return data;
  } catch (err) {
    wrapError(err);
  }
}

export async function obtenerRespuestaPublica(
  respuestaId: number | string
): Promise<RespuestaDTO> {
  try {
    const { data } = await api.get<RespuestaDTO>(
      RESPUESTAS_ENDPOINTS.detallePublico(respuestaId)
    );
    return data;
  } catch (err) {
    wrapError(err);
  }
}

export async function actualizarRespuesta(
  respuestaId: number | string,
  payload: UpdateRespuestaPayload,
  options?: { method?: "PATCH" | "PUT" }
): Promise<RespuestaDTO> {
  try {
    const method = options?.method ?? "PATCH";
    const url = RESPUESTAS_ENDPOINTS.admin(respuestaId);
    const { data } =
      method === "PUT"
        ? await api.put<RespuestaDTO>(url, payload)
        : await api.patch<RespuestaDTO>(url, payload);
    return data;
  } catch (err) {
    wrapError(err);
  }
}

export async function eliminarRespuesta(respuestaId: number | string): Promise<void> {
  try {
    await api.delete(RESPUESTAS_ENDPOINTS.admin(respuestaId));
  } catch (err) {
    wrapError(err);
  }
}