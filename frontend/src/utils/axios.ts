import axios from "axios";
import { storage } from "./storage";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
});

// --- (1) Añadir el access token a cada request ---
api.interceptors.request.use((config) => {
  const access = storage.getAccess?.();
  if (access) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

// --- (2) REFRESCAR TOKEN AUTOMÁTICAMENTE SI EXPIRA ---
api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const original = error.config;

    // Solo entramos aquí si: (1) es 401, (2) no se ha reintentado antes
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      const refresh = storage.getRefresh?.();
      if (!refresh) {
        return Promise.reject(error);
      }

      try {
        const res = await axios.post(
          `${api.defaults.baseURL}/token/refresh/`,
          { refresh }
        );

        // Guardar el nuevo access token
        storage.setAccess(res.data.access);

        // Repetir la petición original con el nuevo access
        original.headers.Authorization = `Bearer ${res.data.access}`;
        return api(original);

      } catch (refreshError) {
        // Si el refresh también expira → cerrar sesión
        storage.clearAll?.();
      }
    }

    return Promise.reject(error);
  }
);

export default api;
export { api };