export interface Imagen {
  id: number;
  content_type: number;
  object_id: number;
  imagen: string;
  orden: number | null;
  fecha_creacion: string;
  content_object_text: string | null;
}
