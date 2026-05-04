// src/api/quejas.ts

import axios from "../utils/axios";
import type { Queja } from "../types/queja"
export const createQuejaRequest = (formData: FormData) => {
  for (const [k, v] of formData.entries()) {
    console.log("FD", k, v);
  }

  return axios.post("/quejas/create/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export async function getQuejasByUser(userId: number): Promise<Queja[]> {
  const response = await axios.get(`/quejas/autor/${userId}`);
  return response.data;
}

export async function deleteQueja(id: number) {
  return axios.delete(`/quejas/${id}/delete/`);
}

export async function getQuejas(params?: {
  page?: number;
  page_size?: number;
}): Promise<{ results: Queja[]; count: number }> {
  const response = await axios.get(`/quejas/`, { params });
  return response.data;
}

export type GetQuejasParams = {
  page?: number;
  page_size?: number;

  estado?: string;
  categoria?: string;
  distrito?: string;

  autor?: string;
  ubicacion?: string;
  texto?: string;

  votosMin?: number | "";
  votosMax?: number | "";

  comentariosMin?: number | "";
  comentariosMax?: number | "";

  media?: string;
  ordering?: string;
};

export async function getQuejasFiltered(params: GetQuejasParams) {
  const response = await axios.get(`/quejas/`, {
    params,
  });

  return response.data;
}
