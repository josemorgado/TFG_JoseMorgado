// src/utils/axios.ts
import axios from "axios";
import { storage } from "./storage";

const instance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api",
});

instance.interceptors.request.use((config) => {
  const access = storage.getAccess?.();
  if (access) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${access}`;
  }
  return config;
});

export default instance;
