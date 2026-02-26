const ACCESS_KEY = 'jwt_access';
const REFRESH_KEY = 'jwt_refresh';

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