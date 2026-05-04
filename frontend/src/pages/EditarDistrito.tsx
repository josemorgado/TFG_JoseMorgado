import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { fetchDistrito, updateDistrito } from "../api/moderacion";
import { deleteDistrito } from "../api/moderacion";

export default function EditarDistrito() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [nombre, setNombre] = useState("");
    const [codigo, setCodigo] = useState("");
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        (async () => {
            try {
                const data = await fetchDistrito(Number(id));
                setNombre(data.nombre);
                setCodigo(data.codigo);
            } catch {
                setError("No se pudo cargar el distrito");
            }
        })();
    }, [id]);
    const handleDiscard = () => {
        navigate(-1);
    };
    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await updateDistrito(Number(id), { nombre, codigo });
            navigate("/moderador");
        } catch {
            setError("Error al actualizar el distrito");
        }
    };

    const handleDelete = async () => {
        const ok = window.confirm(
            "¿Seguro que quieres eliminar este distrito? Esta acción no se puede deshacer. Si lo eleimna, se eliminaran todas las quejas asociadas a este distrito."
        );
        if (!ok) return;

        try {
            await deleteDistrito(Number(id));
            navigate("/moderador");
        } catch {
            setError("No se pudo eliminar el distrito");
        }
    };

    return (
        <div className="form-page">
            <div className="form-card">
                <h1 className="form-title">Editar distrito</h1>

                {error && <p className="form-error">{error}</p>}

                <form className="form-container" onSubmit={handleSubmit}>
                    <label className="form-label">Nombre</label>
                    <input
                        className="form-input"
                        value={nombre}
                        onChange={(e) => setNombre(e.target.value)}
                        required
                    />

                    <label className="form-label">Código</label>
                    <input
                        className="form-input"
                        value={codigo}
                        onChange={(e) => setCodigo(e.target.value)}
                        required
                    />
                    <div className="form-actions">


                        <button
                            type="button"
                            className="form-button"
                            onClick={handleDiscard}
                        >
                            Descartar cambios
                        </button>

                        <button className="form-button form-button-secondary" type="submit">
                            Guardar cambios
                        </button>
                        <button
                            type="button"
                            className="form-button form-button-danger"
                            onClick={handleDelete}
                        >
                            Eliminar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}