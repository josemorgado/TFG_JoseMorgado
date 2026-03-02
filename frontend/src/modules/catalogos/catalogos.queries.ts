// src/modules/catalogos/catalogos.queries.ts
import { useQuery } from "@tanstack/react-query";
import { fetchCategorias, fetchDistritos } from "../../api/catalogos";
import type { OpcionBasica } from "../../api/catalogos";

export const catalogoKeys = {
  categorias: ["catalogos", "categorias"] as const,
  distritos: ["catalogos", "distritos"] as const,
};

export function useCategorias() {
  return useQuery<OpcionBasica[]>({
    queryKey: catalogoKeys.categorias,
    queryFn: fetchCategorias,
    staleTime: 1000 * 60 * 5,
  });
}

export function useDistritos() {
  return useQuery<OpcionBasica[]>({
    queryKey: catalogoKeys.distritos,
    queryFn: fetchDistritos,
    staleTime: 1000 * 60 * 5,
  });
}