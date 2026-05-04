import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import axiosInstance from "../utils/axios";

import type { Queja } from "../types/queja";
import type { Imagen } from "../types/imagen";
import type { Video } from "../types/video";
import type { EstadoQuejaCode } from "../types/respuestas";

import { crearRespuesta } from "../api/respuestas";
import { mediaUrl } from "../utils/media";

import "../styles/QuejaDetail.css";

function QuejaResponder() {
  const { quejaId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [item, setItem] = useState<Queja | null>(null);
  const [images, setImages] = useState<Imagen[]>([]);
  const [videos, setVideos] = useState<Video[]>([]);

  const [text, setText] = useState("");
  const [newState, setNewState] = useState<EstadoQuejaCode | "">("");

  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);

  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [okMsg, setOkMsg] = useState<string | null>(null);

  const ESTADO_VALUES: Record<string, EstadoQuejaCode> = {
    PEN: "PEN",
    ENP: "ENP",
    RES: "RES",
    REC: "REC",
  };

  const canRespond = Boolean(
    user?.is_staff ||
      user?.is_superuser ||
      user?.is_moderator ||
      (user?.groups || []).some((g: any) =>
        String(g?.name ?? g).toLowerCase().includes("moderador")
      )
  );

  useEffect(() => {
    if (!quejaId) {
      setErrorMsg("ID inválido");
      setIsLoading(false);
      return;
    }

    let cancelled = false;

    async function fetchData() {
      try {
        setIsLoading(true);
        setErrorMsg(null);

        const [quejaRes, imgRes, videoRes] = await Promise.all([
          axiosInstance.get<Queja>(`/quejas/${quejaId}/`),
          axiosInstance.get<Imagen[]>(`/imagenes/queja/${quejaId}/`),
          axiosInstance.get<Video[]>(`/videos/queja/${quejaId}/`),
        ]);

        if (!cancelled) {
          setItem(quejaRes.data);
          setImages(imgRes.data);
          setVideos(videoRes.data);
        }
      } catch {
        if (!cancelled) {
          setErrorMsg("Error al cargar la información de la queja.");
        }
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    fetchData();
    return () => {
      cancelled = true;
    };
  }, [quejaId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg(null);
    setOkMsg(null);

    if (!item || !quejaId) {
      setErrorMsg("Queja no válida.");
      return;
    }

    const content = text.trim();
    if (content.length < 3) {
      setErrorMsg("El contenido es demasiado corto (mín. 3 caracteres).");
      return;
    }

    try {
      setIsSending(true);

      await crearRespuesta(quejaId, {
        contenido: content,
        nuevo_estado: newState || ESTADO_VALUES[item.estado],
      });

      setOkMsg("Respuesta enviada correctamente.");
      navigate(`/quejas/${quejaId}/respuestas`, { replace: true });
    } catch (err: any) {
      const data = err?.response?.data || err?.details;
      const firstKey =
        data && typeof data === "object" ? Object.keys(data)[0] : null;
      const firstError = firstKey ? data[firstKey]?.[0] : null;

      setErrorMsg(
        firstError || data?.detail || err?.message || "No se pudo enviar la respuesta."
      );
    } finally {
      setIsSending(false);
    }
  };

  if (isLoading) {
    return (
      <div className="detail-page">
        <div className="detail">
          <div className="alert alert--loading">Cargando…</div>
        </div>
      </div>
    );
  }

  if (errorMsg || !item) {
    return (
      <div className="detail-page">
        <div className="detail">
          <div className="alert alert--error">
            {errorMsg ?? "No hay datos."}
          </div>
        </div>
      </div>
    );
  }

  return (
    <main className="detail-page responder-page">
      <div className="detail">
        <header className="detail__header card">
          <h1 className="detail__title">{item.titulo}</h1>

          <div className="detail__meta">
            <span className="pill">
              <strong>Autor:</strong> {item.autor_nombre}
            </span>

            <span className="meta__group">
              <span className="meta__label">Estado:</span>
              <span className="pill pill--neutral">{item.estado}</span>
            </span>

            <span className="meta__group">
              <span className="meta__label">Categoría:</span>
              <span className="pill pill--neutral">
                {item.categoria_nombre}
              </span>
            </span>

            <span className="meta__group">
              <span className="meta__label">Distrito:</span>
              <span className="pill pill--neutral">
                {item.distrito_nombre}
              </span>
            </span>
          </div>

          <div className="detail_content">
            {item.descripcion && (
              <p className="detail__desc">
                <strong>Descripción: </strong>
                {item.descripcion}
              </p>
            )}

            {item.ubicacion && (
              <p className="detail__desc">
                <strong>Ubicación: </strong>
                {item.ubicacion}
              </p>
            )}
          </div>
        </header>

        <div className="sections-row">
          <section className="section_media">
            <h2 className="section__title">
              Imágenes ({images.length})
            </h2>

            {images.length === 0 ? (
              <p className="empty-state">No hay imágenes.</p>
            ) : (
              <div className="media-grid">
                {images.map((img) => (
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

          <section className="section_media">
            <h2 className="section__title">Vídeos</h2>

            {videos.length === 0 ? (
              <p className="empty-state">No hay vídeos.</p>
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

        {canRespond && (
          <div className="form-resp">
            <section className="section" style={{ marginTop: 8 }}>
              <h2 className="section__title">Responder queja</h2>

              {errorMsg && (
                <div className="alert alert--error">{errorMsg}</div>
              )}
              {okMsg && (
                <div className="alert alert--loading">{okMsg}</div>
              )}

              <form onSubmit={handleSubmit} className="comment-form">
                <div
                  className="comment-form__row"
                  style={{ marginBottom: 12 }}
                >
                  <textarea
                    className="comment-textarea"
                    placeholder="Escribe la respuesta a la queja."
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    minLength={3}
                    required
                  />

                  <div className="comment-form__buttons">
                    <button
                      type="submit"
                      className="btn btn-primary btn-small"
                      disabled={isSending || text.trim().length < 3}
                    >
                      {isSending ? "Enviando…" : "Enviar"}
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

                <div className="mt-12">
                  <div className="form-field-inline form-field-inline--compact state">
                    <label
                      htmlFor="nuevo-estado"
                      className="meta__label"
                    >
                      Cambiar estado de la queja:
                    </label>

                    <select
                      id="nuevo-estado"
                      className="select-pill"
                      value={newState}
                      onChange={(e) =>
                        setNewState(
                          (e.target.value || "") as EstadoQuejaCode | ""
                        )
                      }
                    >
                      <option value={ESTADO_VALUES[item.estado]}>
                        — Mantener estado —
                      </option>
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
        )}
      </div>
    </main>
  );
}

export default QuejaResponder;
