import React, { createContext, useContext, useEffect, useState } from "react";
import { loginRequest, fetchMe } from "../api/auth";
import type { LoginRequest } from "../api/auth";
import { storage } from "../utils/storage";

type AuthUser = { id: number; username: string;[k: string]: any };


type AuthContextType = {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => void;
  setUser: React.Dispatch<React.SetStateAction<AuthUser | null>>;
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  login: async () => { },
  logout: () => { },
  setUser: () => { },
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<AuthUser | null>(null);

  // Restaurar sesión en carga inicial
  useEffect(() => {
    const access = storage.getAccess();

    if (!access) return;

    const restore = async () => {
      try {
        const me = await fetchMe(access); // Axios renovará token si está expirado
        setUser(me);
      } catch {
        storage.clearAll();
        setUser(null);
      }
    };

    restore();
  }, []);

  // Login
  const login = async (credentials: LoginRequest) => {
    try {
      const tokens = await loginRequest(credentials);

      storage.setAccess(tokens.access);
      if (tokens.refresh) storage.setRefresh(tokens.refresh);

      const me = await fetchMe(tokens.access);
      setUser(me);
    } catch (err) {
      throw err;
    }
  };


  // Logout
  const logout = () => {
    storage.clearAll();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{ user, isAuthenticated: !!user, login, logout, setUser }}
    >
      {children}
    </AuthContext.Provider>
  );
};