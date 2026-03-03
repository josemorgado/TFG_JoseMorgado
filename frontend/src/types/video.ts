export interface Video {
  id: number;
  content_type: number;
  object_id: number;
  video: string;
  orden: number | null;
  fecha_creacion: string;
  content_object_text: string | null;
}