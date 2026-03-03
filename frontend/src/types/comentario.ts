export interface Comentario {
  id: number;
  queja: number;
  autor: number;
  contenido: string;
  fecha_creacion: string;
  num_votos: number;
  parent: number | null;
}