import React, { createContext, useContext, useEffect, useState } from "react";
import { loginRequest, fetchMe } from "../api/auth";
import type { LoginRequest } from "../api/auth";
import { storage } from "../utils/storage";

type AuthUser = {
  id: number;
  username: string;
  perfil?: {
    moderator: boolean;
  };
  [k: string]: any;
};

type AuthContextType = {
  user: AuthUser | null;
  loading: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => void;
  setUser: React.Dispatch<React.SetStateAction<AuthUser | null>>;
};

const AuthContext = createContext<AuthContextType>({
  user: null,
  loading: true,
  isAuthenticated: false,
  login: async () => {},
  logout: () => {},
  setUser: () => {},
});

export const useAuth = () => useContext(AuthContext);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  // 🔄 Restaurar sesión al cargar la app
  useEffect(() => {
    const access = storage.getAccess();

    if (!access) {
      setLoading(false);
      return;
    }

    const restore = async () => {
      try {
        const me = await fetchMe(access);
        setUser(me);
      } catch {
        storage.clearAll();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    restore();
  }, []);

  // 🔐 Login
  const login = async (credentials: LoginRequest) => {
    const tokens = await loginRequest(credentials);

    storage.setAccess(tokens.access);
    if (tokens.refresh) storage.setRefresh(tokens.refresh);

    const me = await fetchMe(tokens.access);
    setUser(me);
  };

  // 🚪 Logout
  const logout = () => {
    storage.clearAll();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        logout,
        setUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
