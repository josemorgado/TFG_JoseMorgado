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
