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

// Parámetros generales para stats
interface StatsParams {
    user_id?: number;
    limit?: number;
    desde?: string;
    hasta?: string;
    estado?: "PEN" | "ENP" | "RES" | "REC";
    distrito_id?: number;
    categoria_id?: number;
    include_zero?: boolean;
    ordering?: "-total" | "total" | "nombre";
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