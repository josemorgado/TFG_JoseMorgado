import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "https://alcalde-escuchame-backend.onrender.com";

export const api = axios.create({
  baseURL: API_BASE_URL,
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    console.error("API Error:", err.response || err);
    throw err;
  }
);