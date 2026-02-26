import { api } from './client';

const AUTH_LOGIN = import.meta.env.VITE_AUTH_LOGIN ?? '/token/';
const AUTH_ME = import.meta.env.VITE_AUTH_ME ?? '/usuarios/me/';

export type LoginRequest = { username: string; password: string };
export type TokenPair = { access: string; refresh?: string };

export async function loginRequest(data: LoginRequest) {
  // SimpleJWT responde { access, refresh }
  const res = await api.post<TokenPair>(AUTH_LOGIN, data);
  return res.data;
}

export async function fetchMe(accessToken: string) {
  const res = await api.get(AUTH_ME, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data;
}