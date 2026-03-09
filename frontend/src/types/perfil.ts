export interface Perfil {
  genero: "M" | "F" | "O";
  biografia: string;
  moderator: boolean;
  telefono: string;
  direccion: string;
  fecha_nacimiento: string;
  fecha_actualizacion: string;
  foto_perfil: string | null;
  edad: number;
}

export interface Usuario {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  date_joined: string;
  last_login: string | null;
  perfil: Perfil;
}

// Tipos para la actualización (parcial) del usuario + perfil

export type Genero = "M" | "F" | "O";

export interface PerfilUpdateInput {
  telefono?: string;
  direccion?: string;
  fecha_nacimiento?: string;
  genero?: Genero;
  biografia?: string;
}

export interface UsuarioUpdateInput {
  username?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  perfil: PerfilUpdateInput;
}

export interface UpdateUsuarioParams {
  id: number | string;
  data: UsuarioUpdateInput;
  file?: File | null;
}
