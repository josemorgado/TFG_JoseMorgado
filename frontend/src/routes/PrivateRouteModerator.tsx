import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function PrivateRouteModerador() {
    const { user , loading} = useAuth();
    const location = useLocation();

    if (loading) {
        // Mientras se carga el estado de autenticación, no renderizamos nada
        return null;
    }

    if (!user) {
        return (
            <Navigate
                to="/login"
                state={{ from: location }}
                replace
            />
        );
    }

    if (!user.perfil?.moderator) {
        return <Navigate to="/ruta-prohibida" replace />;
    }

    return <Outlet />;
}