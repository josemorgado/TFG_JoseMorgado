import api from "../utils/axios";
import { storage } from "../utils/storage";

const AUTH_LOGIN = import.meta.env.VITE_AUTH_LOGIN ?? "/token/";
const AUTH_ME = import.meta.env.VITE_AUTH_ME ?? "/usuarios/me/";
const AUTH_REGISTER = import.meta.env.VITE_AUTH_REGISTER ?? "/usuarios/create/";

export type LoginRequest = { username: string; password: string };
export type TokenPair = { access: string; refresh?: string };

export async function loginRequest(data: LoginRequest): Promise<TokenPair> {
  const res = await api.post<TokenPair>(AUTH_LOGIN, data);
  return res.data;
}

export async function registerRequest(data: FormData) {
  const res = await api.post(AUTH_REGISTER, data);
  return res.data;
}

export async function fetchMe(accessToken: string) {
  const res = await api.get(AUTH_ME, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data;
}

export async function apiLogout() {
  const refresh = storage.getRefresh();
  if (!refresh) return;

  try {
    await api.post("/usuarios/logout/", { refresh });
  } catch {
    /* no-op */
  }
}

export const requestPasswordReset = (email: string) =>
  api.post("/usuarios/reset-password/", { email });

export const confirmPasswordReset = (
  uid: string,
  token: string,
  new_password: string
) => api.post("/usuarios/reset-password-confirm/", { uid, token, new_password });
