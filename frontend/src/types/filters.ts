export type MediaFilter = "" | "con" | "sin" | "imagenes" | "videos" | "ambos";

export type FiltersShape = {
  texto: string;
  estado: string;
  categoria: string;
  distrito: string;
  autor: string;
  ubicacion: string;
  fechaDesde: string;
  fechaHasta: string;
  votosMin: string;
  votosMax: string;
  comentariosMin: string;
  comentariosMax: string;
  media: MediaFilter;
};

export type SortBy = "" | "fecha_asc" | "fecha_desc" | "votos" | "comentarios" | "respuestas";


export const defaultFilters: FiltersShape = {
  texto: "",
  estado: "",
  categoria: "",
  distrito: "",
  autor: "",
  ubicacion: "",
  fechaDesde: "",
  fechaHasta: "",
  votosMin: "",
  votosMax: "",
  comentariosMin: "",
  comentariosMax: "",
  media: "",
};

