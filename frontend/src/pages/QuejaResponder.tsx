import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import axiosInstance from "../utils/axios";
import type { Queja } from "../types/queja";
import type { Imagen } from "../types/imagen";
import type { Video } from "../types/video";
import "../styles/QuejaDetail.css";
import { mediaUrl } from "../utils/media";

function QuejaResponder() {
    const { quejaId } = useParams();

    const [queja, setQueja] = useState<Queja | null>(null);
    const [imagenes, setImagenes] = useState<Imagen[]>([]);
    const [videos, setVideos] = useState<Video[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);

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
                <div className="sections-row">                {/* IMÁGENES */}
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

            </div>
        </main>
    );
}

export default QuejaResponder;