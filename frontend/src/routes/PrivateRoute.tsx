import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

type PrivateRouteProps = {
  reason?: string;
};

export default function PrivateRoute({ reason }: PrivateRouteProps) {
  const { user, loading } = useAuth();
  const location = useLocation();

  // ⏳ Esperar a que se cargue la sesión
  if (loading) {
    return null;
  }

  // ❌ No logueado
  if (!user) {
    return (
      <Navigate
        to="/login"
        state={{
          reason,
          from: location.pathname,
        }}
        replace
      />
    );
  }

  // ✅ Logueado
  return <Outlet />;
}