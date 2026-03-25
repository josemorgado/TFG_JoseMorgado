// src/api/stats.ts
import axios from "../utils/axios"

export interface CategoriaStats {
    id: number;
    nombre: string;
    total: number;
}

export interface DistritoStats {
    id: number;
    nombre: string;
    total: number;
}

export type EstadoCode = "PEN" | "ENP" | "RES" | "REC";

// Parámetros generales para stats
export interface StatsParams {
    user_id?: number;
    limit?: number;
    desde?: string;
    hasta?: string;
    estado?: "PEN" | "ENP" | "RES" | "REC" | string;
    distrito_id?: number;
    categoria_id?: number;
    include_zero?: boolean;
    ordering?: "-total" | "total" | "nombre";
}
export interface Overview {
    total: number;
    pen: number;
    enp: number;
    res: number;
    rec: number;
}

export interface EstadosDistrib {
    PEN: number;
    ENP: number;
    RES: number;
    REC: number;
    total: number;
}

export interface TimePoint {
    period: string;          // YYYY-MM, YYYY-Www, YYYY-MM-DD o YYYY
    total: number;
    by_estado?: Partial<Record<EstadoCode, number>>;
}



export async function getTopCategorias(params?: StatsParams) {
    const response = await axios.get<CategoriaStats[]>("/stats/categorias/", {
        params,
    })
    return response.data
}


export async function getTopDistritos(params?: StatsParams) {
    const response = await axios.get<DistritoStats[]>("/stats/distritos/", {
        params,
    })
    return response.data
}

export async function getOverview(params?: Omit<StatsParams, "limit" | "ordering" | "include_zero">) {
    const { data } = await axios.get<Overview>("/stats/overview/", { params });
    return data;
}

export async function getEstados(params?: Omit<StatsParams, "limit" | "ordering" | "include_zero">) {
    const { data } = await axios.get<EstadosDistrib>("/stats/estados/", { params });
    return data;
}

export async function getTimeSeries(params: (Omit<StatsParams, "limit" | "ordering" | "include_zero">) & {
    group_by?: "day" | "week" | "month" | "year";
    stack_by?: "none" | "estado";
}) {
    const { data } = await axios.get<TimePoint[]>("/stats/timeseries/", { params });
    return data;
}
export async function getRespuestasOverview(params?: StatsParams): Promise<any> {
  const res = await axios.get("/stats/respuestas/overview/", { params });
  return res.data;
}

export async function getRespuestasTimeSeries(params?: any): Promise<TimePoint[]> {
  const res = await axios.get("/stats/respuestas/timeseries/", { params });
  return res.data;
}

export async function getRespuestasCategorias(params?: StatsParams): Promise<CategoriaStats[]> {
  const res = await axios.get("/stats/respuestas/categorias/", { params });
  return res.data;
}

export async function getRespuestasDistritos(params?: StatsParams): Promise<DistritoStats[]> {
  const res = await axios.get("/stats/respuestas/distritos/", { params });
  return res.data;
}