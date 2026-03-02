// src/api/quejas.ts

import axios from "../utils/axios";

export const createQuejaRequest = (formData: FormData) => {
  return axios.post("/quejas/create/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};
