import React, { createContext, useContext, useEffect, useState } from 'react';
import { loginRequest, fetchMe } from '../api/auth';
import type { LoginRequest } from '../api/auth';
import { storage } from '../utils/storage';

type AuthUser = { id: number; username: string; [k: string]: any };

type AuthContextType = {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  isAuthenticated: false,
  login: async () => {},
  logout: () => {},
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    const access = storage.getAccess();
    if (!access) {
      return;
    }

  const restoreSession = async () => {
      try {
        const me = await fetchMe(access);
        setUser(me);
      } catch (err) {
        storage.clearAll();
        setUser(null);
      }
  };

  restoreSession();
  }, []);

  const login = async (credentials: LoginRequest) => {
    // 1) pedir tokens
    const tokens = await loginRequest(credentials);
    // 2) guardar tokens
    storage.setAccess(tokens.access);
    if (tokens.refresh) storage.setRefresh(tokens.refresh);
    // 3) pedir datos de usuario (si tienes /me)
    const me = await fetchMe(tokens.access);
    setUser(me);
    return me;
  };

  const logout = () => {
    storage.clearAll();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated: !!user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};