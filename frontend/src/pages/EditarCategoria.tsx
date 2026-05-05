import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
    fetchCategoria,
    updateCategoria,
    deleteCategoria,
} from "../api/moderacion";

import PageError from "../components/PageError";
import PageInfo from "../components/PageInfo";

export default function EditarCategoria() {
    const { id } = useParams();
    const navigate = useNavigate();

    if (!id) {
        return <PageError message="Falta la ID de la categoría en la URL." />;
    }

    const idCategoria = Number(id);

    if (Number.isNaN(idCategoria)) {
        return <PageError message="La ID de la categoría no es válida." />;
    }

    const [nombreCategoria, setNombreCategoria] = useState("");
    const [descripcionCategoria, setDescripcionCategoria] = useState("");

    const [cargando, setCargando] = useState(true);
    const [guardando, setGuardando] = useState(false);
    const [errorPagina, setErrorPagina] = useState<string | null>(null);
    const [errorFormulario, setErrorFormulario] = useState<string | null>(null);

    useEffect(() => {
        (async () => {
            try {
                const datos = await fetchCategoria(idCategoria);
                setNombreCategoria(datos.nombre);
                setDescripcionCategoria(datos.descripcion);
            } catch {
                setErrorPagina("No se pudo cargar la categoría.");
            } finally {
                setCargando(false);
            }
        })();
    }, [idCategoria]);

    if (cargando) {
        return <PageInfo message="Cargando categoría..." />;
    }

    if (errorPagina) {
        return <PageError message={errorPagina} />;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrorFormulario(null);

        const nombreLimpio = nombreCategoria.trim();
        const descripcionLimpia = descripcionCategoria.trim();

        if (!nombreLimpio) {
            setErrorFormulario("El nombre de la categoría es obligatorio.");
            return;
        }

        if (nombreLimpio.length < 3) {
            setErrorFormulario("El nombre debe tener al menos 3 caracteres.");
            return;
        }

        if (nombreLimpio.length > 100) {
            setErrorFormulario("El nombre no puede superar los 100 caracteres.");
            return;
        }

        if (!descripcionLimpia) {
            setErrorFormulario("La descripción es obligatoria.");
            return;
        }

        if (descripcionLimpia.length < 10) {
            setErrorFormulario(
                "La descripción debe tener al menos 10 caracteres."
            );
            return;
        }

        try {
            setGuardando(true);
            await updateCategoria(idCategoria, {
                nombre: nombreLimpio,
                descripcion: descripcionLimpia,
            });
            navigate("/moderador");
        } catch (err: any) {
            const mensajeBackend =
                err?.response?.data?.nombre?.[0] ||
                err?.response?.data?.detail ||
                "Error al actualizar la categoría.";

            setErrorFormulario(mensajeBackend);
        } finally {
            setGuardando(false);
        }
    };

    const handleEliminar = async () => {
        const confirmado = window.confirm(
            "¿Seguro que quieres eliminar esta categoría? Esta acción no se puede deshacer. Al eliminarla, se borrarán todas las quejas asociadas.",
        );

        if (!confirmado) return;

        try {
            setGuardando(true);
            await deleteCategoria(idCategoria);
            navigate("/moderador");
        } catch {
            setErrorFormulario("No se pudo eliminar la categoría.");
        } finally {
            setGuardando(false);
        }
    };

    const handleDescartar = () => navigate(-1);

    return (
        <div className="form-page">
            <div className="form-card">
                <h1 className="form-title">Editar categoría</h1>

                <form className="form-container" onSubmit={handleSubmit}>
                    <label className="form-label">Nombre</label>
                    <input
                        className="form-input"
                        value={nombreCategoria}
                        onChange={(e) => setNombreCategoria(e.target.value)}
                        required
                    />

                    <label className="form-label">Descripción</label>
                    <textarea
                        className="form-input"
                        value={descripcionCategoria}
                        onChange={(e) => setDescripcionCategoria(e.target.value)}
                        required
                    />

                    {errorFormulario && (
                        <p className="form-error">{errorFormulario}</p>
                    )}

                    <div className="form-actions">
                        <button
                            type="button"
                            className="form-button"
                            onClick={handleDescartar}
                            disabled={guardando}
                        >
                            Descartar cambios
                        </button>

                        <button
                            type="submit"
                            className="form-button form-button-secondary"
                            disabled={guardando}
                        >
                            Guardar cambios
                        </button>

                        <button
                            type="button"
                            className="form-button form-button-danger"
                            onClick={handleEliminar}
                            disabled={guardando}
                        >
                            Eliminar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}