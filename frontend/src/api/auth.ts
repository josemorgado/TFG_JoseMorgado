import { api } from './client';
import {storage} from '../utils/storage';

const AUTH_LOGIN = import.meta.env.VITE_AUTH_LOGIN ?? '/token/';
const AUTH_ME = import.meta.env.VITE_AUTH_ME ?? '/usuarios/me/';
const AUTH_REGISTER = import.meta.env.VITE_AUTH_REGISTER ?? '/usuarios/create/';

export type LoginRequest = { username: string; password: string };
export type TokenPair = { access: string; refresh?: string };

export type RegisterPayload = {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  perfil: {
    telefono: string;                // obligatorio
    direccion: string;               // obligatorio
    fecha_nacimiento: string;        // obligatorio, "YYYY-MM-DD"
    genero?: "M" | "F" | "O";        // opcional (default=O)
    biografia?: string;              // opcional
    moderator?: boolean;             // opcional (default=false)
  };


}

// Funcion para login
export async function loginRequest(data: LoginRequest) {
  const res = await api.post<TokenPair>(AUTH_LOGIN, data);
  return res.data;
}

// Funcion para logout
export async function apiLogout() {
  const refresh = storage.getRefresh();
  try {
    await fetch("http://localhost:8000/api/usuarios/logout/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
  } catch {
  }
}

// Funcion para obtener mis datos de usuario
export async function fetchMe(accessToken: string) {
  const res = await api.get(AUTH_ME, {
    headers: { Authorization: `Bearer ${accessToken}` },
  });
  return res.data;
}

// Funcion para crear cuenta
export async function registerRequest(data: FormData) {
  const res = await api.post(AUTH_REGISTER, data);
  return res.data;
}