import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
    fetchDistrito,
    updateDistrito,
    deleteDistrito,
} from "../api/moderacion";

import PageError from "../components/PageError";
import PageInfo from "../components/PageInfo";

export default function EditarDistrito() {
    const { id } = useParams();
    const navigate = useNavigate();

    if (!id) {
        return <PageError message="Falta la ID del distrito en la URL." />;
    }

    const idDistrito = Number(id);

    if (Number.isNaN(idDistrito)) {
        return <PageError message="La ID del distrito no es válida." />;
    }

    const [nombreDistrito, setNombreDistrito] = useState("");
    const [codigoDistrito, setCodigoDistrito] = useState("");

    const [cargando, setCargando] = useState(true);
    const [guardando, setGuardando] = useState(false);
    const [errorPagina, setErrorPagina] = useState<string | null>(null);
    const [errorFormulario, setErrorFormulario] = useState<string | null>(null);

    useEffect(() => {
        (async () => {
            try {
                const datos = await fetchDistrito(idDistrito);
                setNombreDistrito(datos.nombre);
                setCodigoDistrito(datos.codigo);
            } catch {
                setErrorPagina("No se pudo cargar el distrito.");
            } finally {
                setCargando(false);
            }
        })();
    }, [idDistrito]);

    if (cargando) {
        return <PageInfo message="Cargando distrito..." />;
    }

    if (errorPagina) {
        return <PageError message={errorPagina} />;
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setErrorFormulario(null);

        const nombreLimpio = nombreDistrito.trim();
        const codigoLimpio = codigoDistrito.trim();

        if (!nombreLimpio) {
            setErrorFormulario("El nombre del distrito es obligatorio.");
            return;
        }

        if (nombreLimpio.length < 3) {
            setErrorFormulario("El nombre debe tener al menos 3 caracteres.");
            return;
        }

        if (nombreLimpio.length > 100) {
            setErrorFormulario("El nombre no puede tener más de 100 caracteres.");
            return;
        }

        if (!codigoLimpio) {
            setErrorFormulario("El código del distrito es obligatorio.");
            return;
        }

        if (codigoLimpio.length < 2) {
            setErrorFormulario("El código debe tener al menos 2 caracteres.");
            return;
        }

        if (codigoLimpio.length > 10) {
            setErrorFormulario("El código no puede tener más de 10 caracteres.");
            return;
        }

        try {
            setGuardando(true);
            await updateDistrito(idDistrito, {
                nombre: nombreLimpio,
                codigo: codigoLimpio,
            });
            navigate("/moderador");
        } catch (err: any) {
            const mensajeBackend =
                err?.response?.data?.codigo?.[0] ||
                err?.response?.data?.detail ||
                "Error al actualizar el distrito.";

            setErrorFormulario(mensajeBackend);
        } finally {
            setGuardando(false);
        }
    };

    const handleEliminar = async () => {
        const confirmado = window.confirm(
            "¿Seguro que quieres eliminar este distrito? Esta acción no se puede deshacer. Al eliminarlo, se borrarán todas las quejas asociadas.",
        );
        if (!confirmado) return;

        try {
            setGuardando(true);
            await deleteDistrito(idDistrito);
            navigate("/moderador");
        } catch {
            setErrorFormulario("No se pudo eliminar el distrito.");
        } finally {
            setGuardando(false);
        }
    };

    const handleDescartar = () => navigate(-1);

    return (
        <div className="form-page">
            <div className="form-card">
                <h1 className="form-title">Editar distrito</h1>

                <form className="form-container" onSubmit={handleSubmit}>
                    <label className="form-label">Nombre</label>
                    <input
                        className="form-input"
                        value={nombreDistrito}
                        onChange={(e) => setNombreDistrito(e.target.value)}
                        required
                    />

                    <label className="form-label">Código</label>
                    <input
                        className="form-input"
                        value={codigoDistrito}
                        onChange={(e) => setCodigoDistrito(e.target.value)}
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