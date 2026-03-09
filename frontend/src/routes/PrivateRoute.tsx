import { Navigate, Outlet, useParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function PrivateRoutePerfil() {
  const { user } = useAuth();
  const { id } = useParams();

  if (!user) {
    return (
      <Navigate
        to="/login"
        state={{ reason: "auth-required" }}
        replace
      />
    );
  }

  if (id && Number(id) !== user.id) {
    return (
      <Navigate
        to="/ruta-prohibida"
        state={{ attemptedId: id }}
        replace
      />
    );
  }

  return <Outlet />;
}
