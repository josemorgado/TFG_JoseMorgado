// src/utils/axios.ts
import axios from "axios";
import { storage } from "./storage";

const BASE_URL = import.meta.env.VITE_API_BASE_URL+"/api";

if (!BASE_URL) {
  throw new Error("VITE_API_BASE_URL no está definida");
}

const api = axios.create({
  baseURL: `${BASE_URL}/api`,
});

// 3️⃣ Interceptor: añadir access token a cada request
api.interceptors.request.use((config) => {
  const access = storage.getAccess?.();
  if (access) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

// 4️⃣ Interceptor: refresh automático del token
api.interceptors.response.use(
  (response) => response,

  async (error) => {
    const original = error.config;

    if (error.response?.status === 401 && !original._retry) {
      original._retry = true;

      const refresh = storage.getRefresh?.();
      if (!refresh) {
        storage.clearAll?.();
        return Promise.reject(error);
      }

      try {
        // OJO: aquí NO se pone /api otra vez
        const res = await axios.post(
          `${BASE_URL}/api/token/refresh/`,
          { refresh }
        );

        storage.setAccess(res.data.access);

        original.headers.Authorization = `Bearer ${res.data.access}`;
        return api(original);

      } catch (refreshError) {
        storage.clearAll?.();
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;