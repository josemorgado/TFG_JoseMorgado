import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useParams, useNavigate } from "react-router-dom";
import axiosInstance from "../utils/axios";
import type { Queja } from "../types/queja";
import type { Imagen } from "../types/imagen";
import type { Video } from "../types/video";
import "../styles/QuejaDetail.css";
import { mediaUrl } from "../utils/media";
import { crearRespuesta } from "../api/respuestas";
import type { EstadoQuejaCode } from "../types/respuestas";


function QuejaResponder() {
    const { quejaId } = useParams();
    const navigate = useNavigate();

    const { user } = useAuth();

    const [contenido, setContenido] = useState("");
    const [nuevoEstado, setNuevoEstado] = useState<EstadoQuejaCode | "">("");
    const [sending, setSending] = useState(false);
    const [formError, setFormError] = useState<string | null>(null);
    const [formOk, setFormOk] = useState<string | null>(null);
    const [queja, setQueja] = useState<Queja | null>(null);
    const [imagenes, setImagenes] = useState<Imagen[]>([]);
    const [videos, setVideos] = useState<Video[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

    const ESTADO_TO_CODE: Record<string, EstadoQuejaCode> = {
        "PEN": "PEN",
        "ENP": "ENP",
        "RES": "RES",
        "REC": "REC",
    };

    const isModeratorOrAdmin = Boolean(
        user?.is_staff ||
        user?.is_superuser ||
        user?.is_moderator ||
        (user?.groups || []).some((g: any) =>
            (typeof g === "string" ? g : g?.name || "")
                .toLowerCase()
                .includes("moderador")
        )
    );

    useEffect(() => {

        if (quejaId === undefined) return;

        if (!quejaId) {
            setError("ID inválido");
            setLoading(false);
            return;
        }

        let cancel = false;

        async function fetchAll() {
            try {
                setLoading(true);
                setError(null);

                const [quejaRes, imagenesRes, videosRes] = await Promise.all([
                    axiosInstance.get<Queja>(`/quejas/${quejaId}/`),
                    axiosInstance.get<Imagen[]>(`/imagenes/queja/${quejaId}/`),
                    axiosInstance.get<Video[]>(`/videos/queja/${quejaId}/`),
                ]);

                if (!cancel) {
                    setQueja(quejaRes.data);
                    setImagenes(imagenesRes.data);
                    setVideos(videosRes.data);
                }
            } catch {
                if (!cancel) setError("Error al cargar la información de la queja.");
            } finally {
                if (!cancel) setLoading(false);
            }
        }

        fetchAll();
        return () => { cancel = true };
    }, [quejaId]);

    if (loading) {
        return (
            <div className="detail-page">
                <div className="detail">
                    <div className="alert alert--loading">Cargando…</div>
                </div>
            </div>
        );
    }

    if (error || !queja) {
        return (
            <div className="detail-page">
                <div className="detail">
                    <div className="alert alert--error">{error ?? "No hay datos."}</div>
                </div>
            </div>
        );
    }

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        setFormError(null);
        setFormOk(null);

        if (!quejaId || !queja?.id) {
            setFormError("Queja no válida.");
            return;
        }

        const text = contenido.trim();
        if (text.length < 3) {
            setFormError("El contenido es demasiado corto (mín. 3 caracteres).");
            return;
        }

        try {
            setSending(true);

            await crearRespuesta(quejaId, {
                contenido: text,
                nuevo_estado: nuevoEstado !== "" ? nuevoEstado : ESTADO_TO_CODE[queja.estado],
            });

            setFormOk("Respuesta enviada correctamente.");
            navigate(`/quejas/${quejaId}/respuestas`, { replace: true });

        } catch (err: any) {
            const data = err?.details || err?.response?.data;
            const firstField = data && typeof data === "object" ? Object.keys(data)[0] : null;
            const firstError = firstField ? data[firstField]?.[0] : null;

            setFormError(
                firstError ||
                data?.detail ||
                err?.message ||
                "No se pudo enviar la respuesta."
            );
        } finally {
            setSending(false);
        }
    }

    return (
        <main className="detail-page responder-page">
            <div className="detail">
                <header className="detail__header card">
                    <h1 className="detail__title">{queja.titulo}</h1>

                    <div className="detail__meta">
                        <span className="pill">
                            <strong>Autor:</strong> {queja.autor_nombre}
                        </span>

                        <span className="meta__group">
                            <span className="meta__label">Estado:</span>
                            <span className="pill pill--neutral">{queja.estado}</span>
                        </span>

                        <span className="meta__group">
                            <span className="meta__label">Categoría:</span>
                            <span className="pill pill--neutral">{queja.categoria_nombre}</span>
                        </span>

                        <span className="meta__group">
                            <span className="meta__label">Distrito:</span>
                            <span className="pill pill--neutral">{queja.distrito_nombre}</span>
                        </span>
                    </div>

                    <div className="detail_content">
                        {queja.descripcion && (
                            <p className="detail__desc">
                                <strong>Descripción: </strong>
                                {queja.descripcion}
                            </p>
                        )}

                        {queja.ubicacion && (
                            <p className="detail__desc">
                                <strong>Ubicación: </strong>
                                {queja.ubicacion}
                            </p>
                        )}
                    </div>
                </header>
                <div className="sections-row">
                    {/* IMÁGENES */}
                    <section className="section_media">
                        <h2 className="section__title">Imágenes ({imagenes.length})</h2>

                        {imagenes.length === 0 ? (
                            <p className="empty-state">No hay imágenes.</p>
                        ) : (
                            <div className="media-grid">
                                {imagenes.map((img) => (
                                    <div key={img.id} className="media-card">
                                        <div className="media-card__visual">
                                            <img
                                                className="media media--image"
                                                src={mediaUrl(img.imagen)}
                                                alt=""
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </section>

                    {/* VIDEOS */}
                    <section className="section_media">
                        <h2 className="section__title">Videos</h2>

                        {videos.length === 0 ? (
                            <p className="empty-state">No hay videos.</p>
                        ) : (
                            <div className="video-grid">
                                {videos.map((v) => (
                                    <figure key={v.id} className="media-card media-card--video">
                                        <div className="media-card__visual">
                                            <video
                                                className="media media--video"
                                                src={mediaUrl(v.video)}
                                                controls
                                            />
                                        </div>
                                    </figure>
                                ))}
                            </div>
                        )}
                    </section>
                </div>
                {isModeratorOrAdmin &&
                    <div className="form-resp">
                        <section className="section" style={{ marginTop: 8 }}>
                            <h2 className="section__title">Responder queja</h2>
                            {formError && <div className="alert alert--error">{formError}</div>}
                            {formOk && <div className="alert alert--loading">{formOk}</div>}

                            <form onSubmit={handleSubmit} className="comment-form">


                                <div className="comment-form__row" style={{ marginBottom: 12 }}>
                                    <textarea
                                        className="comment-textarea"
                                        placeholder="Escribe la respuesta a la queja."
                                        value={contenido}
                                        onChange={(e) => setContenido(e.target.value)}
                                        minLength={3}
                                        required
                                    />

                                    <div className="comment-form__buttons">
                                        <button
                                            type="submit"
                                            className="btn btn-primary btn-small"
                                            disabled={sending || contenido.trim().length < 3}
                                        >
                                            {sending ? "Enviando…" : "Enviar"}
                                        </button>

                                        <button
                                            type="button"
                                            className="btn btn-secondary btn-small"
                                            onClick={() => navigate(-1)}
                                        >
                                            Cancelar
                                        </button>
                                    </div>
                                </div>

                                {/* Select de estado (opcional) */}
                                <div className="mt-12">
                                    <div className="form-field-inline form-field-inline--compact state">
                                        <label htmlFor="nuevo-estado" className="meta__label">
                                            Cambiar estado de la queja:
                                        </label>

                                        <select
                                            id="nuevo-estado"
                                            className="select-pill"
                                            value={nuevoEstado}
                                            onChange={(e) =>
                                                setNuevoEstado((e.target.value || "") as EstadoQuejaCode | "")
                                            }
                                        >
                                            <option value={ESTADO_TO_CODE[queja.estado]}>— Mantener estado —</option>
                                            <option value="PEN">Pendiente</option>
                                            <option value="ENP">En Progreso</option>
                                            <option value="RES">Resuelta</option>
                                            <option value="REC">Rechazada</option>
                                        </select>
                                    </div>
                                </div>
                            </form>
                        </section>

                    </div>
                }
            </div>
        </main>
    );
}

export default QuejaResponder;