export type EstadoQuejaCode = "PEN" | "ENP" | "RES" | "REC";

export interface RespuestaDTO {
    id: number;
    queja: number;
    moderador: number | null;
    contenido: string;
    nuevo_estado: EstadoQuejaCode | null;
    fecha_respuesta: string;
    moderador_username: string | null;
    fecha_actualizacion: string;
}

export interface CreateRespuestaPayload {
    contenido: string;
    nuevo_estado?: EstadoQuejaCode | null;
}

export interface UpdateRespuestaPayload {
    contenido?: string;
    nuevo_estado?: EstadoQuejaCode | null;
}

export interface Paginated<T> {
    count: number;
    next: string | null;
    previous: string | null;
    results: T[];
}