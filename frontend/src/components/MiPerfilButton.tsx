import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function miPerfilButton() {
    const {user} = useAuth();
    const navigate = useNavigate();

    const goToProfile = () => {
        if (!user || !user.id) return;
        navigate(`/perfil/${user.id}`);
    }


    return (
        <button className="auth-button" onClick={goToProfile}>
            Mi Perfil
        </button>
    );
}
