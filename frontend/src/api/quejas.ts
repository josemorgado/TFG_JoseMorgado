// src/api/quejas.ts

import axios from "../utils/axios";

export const createQuejaRequest = (formData: FormData) => {
  for (const [k, v] of formData.entries()) {
    console.log("FD", k, v);
  }

  return axios.post("/quejas/create/", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};
