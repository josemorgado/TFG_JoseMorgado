// src/api/quejas.ts

import axios from "../utils/axios";
import type {Queja} from "../types/queja"
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
