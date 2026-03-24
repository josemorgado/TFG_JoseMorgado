export interface Queja{
    id: number;
    titulo: string;
    descripcion: string;
    categoria: number | null;
    categoria_nombre: string;
    distrito: number | null;
    distrito_nombre: string;
    estado: string;
    ubicacion: string | null;
    autor: number | null;
    autor_nombre: string;
    fecha_creacion: string;
    fecha_creacion_iso: string;
    fecha_actualizacion: string;
    num_votos: number;
    num_comentarios: number;
    num_respuestas:number;
    num_comentarios_top_level: number;
    content_type: string;
    is_liked: boolean;
    imagenes_count: number;
    videos_count: number;
}