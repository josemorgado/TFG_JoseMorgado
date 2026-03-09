import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function PrivateRouteCrearQueja() {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return (
      <Navigate
        to="/login"
        state={{
          reason: "create-queja",
          from: { pathname: location.pathname },
        }}
        replace
      />
    );
  }

  return <Outlet />;
}