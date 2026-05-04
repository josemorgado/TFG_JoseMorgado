
import api from "../utils/axios";
import type { Categoria } from "../types/categoria";
import type { Distrito } from "../types/distrito";

export async function fetchCategoriasFull(): Promise<Categoria[]> {
    const { data } = await api.get("/categorias/");
    return data;
}

export async function fetchDistritosFull(): Promise<Distrito[]> {
    const { data } = await api.get("/distritos/");
    return data;
}
export type CreateCategoriaPayload = {
    nombre: string;
    descripcion: string;
};

export async function createCategoria(
    payload: CreateCategoriaPayload
): Promise<Categoria> {
    console.log("TOKEN:", localStorage.getItem("access"));
    const { data } = await api.post("/categorias/create/", payload);
    return data;
}

export type CreateDistritoPayload = {
    nombre: string;
    codigo: string;
};

export async function createDistrito(
    payload: CreateDistritoPayload
): Promise<Distrito> {
    const { data } = await api.post("/distritos/create/", payload);
    return data;
}
export async function fetchCategoria(id: number) {
  const { data } = await api.get(`/categorias/${id}/`);
  return data;
}

export async function updateCategoria(id: number, payload: any) {
  const { data } = await api.put(`/categorias/${id}/update/`, payload);
  return data;
}

export async function fetchDistrito(id: number) {
  const { data } = await api.get(`/distritos/${id}/`);
  return data;
}

export async function updateDistrito(id: number, payload: any) {
  const { data } = await api.put(`/distritos/${id}/update`, payload);
  return data;
}

export async function deleteCategoria(id: number) {
  await api.delete(`/categorias/${id}/delete/`);
}

export async function deleteDistrito(id: number) {
  await api.delete(`/distritos/${id}/delete/`);
}
