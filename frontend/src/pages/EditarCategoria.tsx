import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import {
    fetchCategoria,
    updateCategoria,
    deleteCategoria,
} from "../api/moderacion";

export default function EditarCategoria() {
    const { id } = useParams();
    const navigate = useNavigate();

    const [nombre, setNombre] = useState("");
    const [descripcion, setDescripcion] = useState("");
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        (async () => {
            try {
                const data = await fetchCategoria(Number(id));
                setNombre(data.nombre);
                setDescripcion(data.descripcion);
            } catch {
                setError("No se pudo cargar la categoría");
            }
        })();
    }, [id]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            await updateCategoria(Number(id), { nombre, descripcion });
            navigate("/moderador");
        } catch {
            setError("Error al actualizar la categoría");
        }
    };

    const handleDelete = async () => {
        const ok = window.confirm(
            "¿Seguro que quieres eliminar esta categoría? Esta acción no se puede deshacer."
        );
        if (!ok) return;

        try {
            await deleteCategoria(Number(id));
            navigate("/moderador");
        } catch {
            setError("No se pudo eliminar la categoría");
        }
    };

    const handleDiscard = () => navigate(-1);

    return (
        <div className="form-page">
            <div className="form-card">
                <h1 className="form-title">Editar categoría</h1>

                {error && <p className="form-error">{error}</p>}

                <form className="form-container" onSubmit={handleSubmit}>
                    <label className="form-label">Nombre</label>
                    <input
                        className="form-input"
                        value={nombre}
                        onChange={(e) => setNombre(e.target.value)}
                        required
                    />

                    <label className="form-label">Descripción</label>
                    <textarea
                        className="form-input"
                        value={descripcion}
                        onChange={(e) => setDescripcion(e.target.value)}
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

                        <button type="submit" className="form-button form-button-secondary">
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