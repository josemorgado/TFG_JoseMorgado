import type { ListState } from "../types/storage";

const ACCESS_KEY = "jwt_access";
const REFRESH_KEY = "jwt_refresh";

const KEY = "quejasListState";

export const storage = {
  getAccess: () => localStorage.getItem(ACCESS_KEY),
  setAccess: (token: string) => localStorage.setItem(ACCESS_KEY, token),
  clearAccess: () => localStorage.removeItem(ACCESS_KEY),

  getRefresh: () => localStorage.getItem(REFRESH_KEY),
  setRefresh: (token: string) => localStorage.setItem(REFRESH_KEY, token),
  clearRefresh: () => localStorage.removeItem(REFRESH_KEY),

  clearAll: () => {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
  },
};

export function loadListState<TFilters, TSort extends string = string>(): ListState<TFilters, TSort> | null {
  try {
    const raw = sessionStorage.getItem(KEY);
    if (!raw) return null;
    return JSON.parse(raw) as ListState<TFilters,TSort>;
  } catch {
    return null;
  }
}

export function saveListState<TFilters, TSort extends string = string>(state: ListState<TFilters, TSort>) {
  try {
    sessionStorage.setItem(KEY, JSON.stringify(state));
  } catch {}
}

export function clearListState() {
  try {
    sessionStorage.removeItem(KEY);
  } catch {}
}
