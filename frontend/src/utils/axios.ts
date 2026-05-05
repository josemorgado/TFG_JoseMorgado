import axios from "axios";
import { storage } from "./storage";

const BASE_URL = import.meta.env.VITE_API_BASE_URL;

if (!BASE_URL) {
  throw new Error("VITE_API_BASE_URL no está definida");
}

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
});

api.interceptors.request.use((config) => {
  const access = storage.getAccess?.();
  if (access) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original?._retry) {
      original._retry = true;

      const refresh = storage.getRefresh?.();
      if (!refresh) {
        storage.clearAll?.();
        return Promise.reject(error);
      }

      try {
        const res = await axios.post(
          `${BASE_URL}/api/token/refresh/`,
          { refresh }
        );

        storage.setAccess(res.data.access);
        original.headers.Authorization = `Bearer ${res.data.access}`;
        return api(original);

      } catch {
        storage.clearAll?.();
        return Promise.reject(error);
      }
    }

    const data = error.response?.data;

    error.normalized = {
      status: error.response?.status,
      message:
        data?.error?.message ||
        data?.detail ||
        "Se ha producido un error inesperado",
      details: data?.error?.details || data || null,
    };

    return Promise.reject(error);
  }
);

export default api;
