// src/api/catalogos.ts
import { api } from "./client";

export type OpcionBasica = {
  id: number;
  nombre: string;
};

function unwrap<T>(data: any): T[] {
  return Array.isArray(data?.results) ? data.results : data;
}

export async function fetchCategorias(): Promise<OpcionBasica[]> {
  const { data } = await api.get("/categorias/");
  return unwrap<OpcionBasica>(data);
}

export async function fetchDistritos(): Promise<OpcionBasica[]> {
  const { data } = await api.get("/distritos/");
  return unwrap<OpcionBasica>(data);
}
