import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../utils/axios";
import axios from "axios";
import { useParams } from "react-router-dom";
import type { Queja } from "../types/queja";
import type { Comentario } from "../types/comentario";
import type { Imagen } from "../types/imagen";
import type { Video } from "../types/video";
import { mediaUrl } from "../utils/media";
import "../styles/QuejaDetail.css";
import LikeButton from "../components/LikeButton";
import CommentButton from "../components/CommentButton";
import { useAuth } from "../context/AuthContext";
import { config } from "../config";
/** ---- Comentarios: árbol + tipos ---- */
type CommentNode = Comentario & { children: CommentNode[] };

const LIMITE_UPDATE_TIME = config.LIMIT_TIME_UPDATE_QUEJA;//declarado en config.ts
function buildCommentTree(comments: Comentario[]): CommentNode[] {
  const map = new Map<number, CommentNode>();
  const roots: CommentNode[] = [];

  comments.forEach((c) => map.set(c.id, { ...c, children: [] }));

  map.forEach((node) => {
    if (node.parent) {
      const parent = map.get(node.parent);
      if (parent) parent.children.push(node);
      else roots.push(node);
    } else {
      roots.push(node);
    }
  });

  const sortByDate = (arr: CommentNode[]) => {
    arr.sort(
      (a, b) =>
        new Date(a.fecha_creacion).getTime() -
        new Date(b.fecha_creacion).getTime(),
    );
    arr.forEach((n) => sortByDate(n.children));
  };
  sortByDate(roots);

  return roots;
}

function QuejaDetail() {
  const { id } = useParams();
  const [queja, setQueja] = useState<Queja | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [imagenes, setImagenes] = useState<Imagen[]>([]);
  const [videos, setVideos] = useState<Video[]>([]);
  const [comentarios, setComentarios] = useState<Comentario[]>([]);
  const { user } = useAuth();
  const navigate = useNavigate();
  // Imágenes: preview + desplegable
  const [showAllImages, setShowAllImages] = useState(false);
  const firstTwo = imagenes.slice(0, 2);
  const rest = imagenes.slice(2);
  const remaining = rest.length;

  // Estado legible del estado
  const estadoCompleto: Record<string, string> = {
    PEN: "Pendiente",
    ENP: "En Progreso",
    RES: "Resuelta",
    REC: "Rechazada",
  };

  // Comentarios: árbol + toggles por id
  const tree = useMemo(() => buildCommentTree(comentarios), [comentarios]);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const toggleReplies = useCallback((cid: number) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(cid) ? next.delete(cid) : next.add(cid);
      return next;
    });
  }, []);

  const [commentText, setCommentText] = useState("");
  const [showCommentBox, setShowCommentBox] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const puedeActualizar = (() => {
    if (!queja?.fecha_creacion_iso) return false;
    if (!(user && queja.autor === user.id)) return false;

    const fecha = new Date(queja.fecha_creacion_iso);
    const ahora = new Date();

    const diffMs = ahora.getTime() - fecha.getTime();
    const diffMin = diffMs / 60000;
    return diffMin <= LIMITE_UPDATE_TIME;
  })();
  useEffect(() => {
    if (!id) return;
    let cancel = false;

    async function fetchAll() {
      try {
        setLoading(true);
        setError(null);

        const [quejaRes, imagenesRes, videosRes, comentarioRes] =
          await Promise.all([
            axiosInstance.get<Queja>(`/quejas/${id}/`),
            axiosInstance.get<Imagen[]>(`/imagenes/queja/${id}/`),
            axiosInstance.get<Video[]>(`/videos/queja/${id}/`),
            axiosInstance.get<Comentario[]>(`/comentarios/queja/${id}/`),
          ]);

        if (!cancel) {
          setQueja(quejaRes.data);
          setImagenes(imagenesRes.data);
          setVideos(videosRes.data);
          setComentarios(comentarioRes.data);
        }
      } catch (err) {
        if (axios.isAxiosError(err)) {
          setError("Error cargando los datos de la queja.");
        } else {
          setError("Error inesperado");
        }
      } finally {
        if (!cancel) setLoading(false);
      }
    }

    fetchAll();
    return () => {
      cancel = true;
    };
  }, [id]);

  const handleQuejaLikeChange = useCallback((liked: boolean, count: number) => {
    setQueja((prev) =>
      prev ? { ...prev, is_liked: liked, num_votos: count } : prev,
    );
  }, []);
  const handleSubmitComment = async () => {
    if (!commentText.trim() || !id) return;

    try {
      setSubmitting(true);

      const response = await axiosInstance.post("/comentarios/create/", {
        queja: Number(id),
        contenido: commentText.trim(),
      });

      setComentarios((prev) => [...prev, response.data]);

      setCommentText("");
      setShowCommentBox(false);
    } catch (err) {
      console.error("Error al enviar comentario", err);
      alert("Error al enviar el comentario");
    } finally {
      setSubmitting(false);
    }
  };
  const handleSubmitReply = async (parentId: number, text: string) => {
    if (!text || !id) return;

    try {
      const response = await axiosInstance.post("/comentarios/create/", {
        queja: Number(id),
        contenido: text,
        parent: parentId,
      });

      // Añadir respuesta a la lista
      setComentarios((prev) => [...prev, response.data]);
    } catch (err) {
      console.error("Error al responder comentario", err);
      alert("Error al enviar la respuesta");
    }
  };
  const handleComentarioLikeChange = useCallback(
    (comentarioId: number, liked: boolean, count: number) => {
      setComentarios((prev) =>
        prev.map((c) =>
          c.id === comentarioId
            ? { ...c, is_liked: liked, num_votos: count }
            : c,
        ),
      );
    },
    [],
  );

  if (loading) {
    return (
      <div className="detail-page">
        <div className="detail">
          <div className="alert alert--loading" role="status">
            Cargando…
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="detail-page">
        <div className="detail">
          <div className="alert alert--error">{error}</div>
        </div>
      </div>
    );
  }

  if (!queja) {
    return (
      <div className="detail-page">
        <div className="detail">
          <div className="empty-state">No hay datos.</div>
        </div>
      </div>
    );
  }

  function CommentItem({
    node,
    level = 0,
  }: {
    node: CommentNode;
    level?: number;
  }) {
    const [isReplying, setIsReplying] = useState(false);
    const [replyText, setReplyText] = useState("");

    const isOpen = expanded.has(node.id);
    const repliesCount = node.children.length;

    const handleSendReply = () => {
      handleSubmitReply(node.id, replyText);
      setReplyText("");
      setIsReplying(false);
    };

    return (
      <li className="comment" style={{ marginLeft: level ? 16 : 0 }}>
        <p className="comment__content">
          <strong>{node.autor_nombre}: </strong>
          {node.contenido}
        </p>

        <div className="comment__footer">
          <div className="comment__meta">
            <span>{node.fecha_creacion}</span>
          </div>

          <div className="comment__actions">
            {repliesCount > 0 && (
              <button
                type="button"
                className="toggle-replies btn btn-secondary"
                onClick={() => toggleReplies(node.id)}
                aria-expanded={isOpen}
              >
                {isOpen ? "Ocultar" : "Ver"} {repliesCount} respuesta
                {repliesCount !== 1 ? "s" : ""}
              </button>
            )}

            <button
              type="button"
              className="reply-btn btn btn-secondary"
              onClick={() => setIsReplying(!isReplying)}
            >
              Responder
            </button>

            <LikeButton
              initialLiked={!!node.is_liked}
              initialCount={node.num_votos ?? 0}
              objectId={node.id}
              contentType={Number(node.content_type)}
              onChange={(liked, count) =>
                handleComentarioLikeChange(node.id, liked, count)
              }
            />
          </div>
        </div>

        {/* FORMULARIO LOCAL - NO PIERDE EL FOCO */}
        {isReplying && (
          <div className="reply-form">
            <div className="reply-form__row">
              <textarea
                value={replyText}
                onChange={(e) => setReplyText(e.target.value)}
                placeholder={`Responder a ${node.autor_nombre}…`}
                className="reply-textarea"
              />

              <div className="reply-form__buttons">
                <button
                  className="btn btn-primary btn-small"
                  disabled={replyText.trim().length < 3}
                  onClick={handleSendReply}
                >
                  Enviar
                </button>

                <button
                  className="btn btn-secondary btn-small"
                  onClick={() => setIsReplying(false)}
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {/* HIJOS */}
        {isOpen && repliesCount > 0 && (
          <ul className="comment-list replies">
            {node.children.map((child: CommentNode) => (
              <CommentItem key={child.id} node={child} level={level + 1} />
            ))}
          </ul>
        )}
      </li>
    );
  }

  return (
    <main className="detail-page">
      <div className="detail">
        {/* Header */}
        <header className="detail__header card">
          <div className="header_grid">
            <div className="like-title">
              <LikeButton
                initialLiked={!!queja.is_liked}
                initialCount={queja.num_votos ?? 0}
                objectId={queja.id}
                contentType={Number(queja.content_type)}
                onChange={handleQuejaLikeChange}
              />
              <h1 className="detail__title">{queja.titulo}</h1>
            </div>
            <div>
              {puedeActualizar && (
                <button
                  type="button"
                  className="update-btn btn btn-secondary btn-small"
                  onClick={()=>navigate(`update`)}
                >
                  Actualizar
                </button>
              )}
            </div>
          </div>
          <div className="detail__meta">
            <span className="pill" title="User">
              <strong>Autor:</strong> {queja.autor_nombre}
            </span>

            <span className="meta__group">
              <span className="meta__label">Estado:</span>
              <span className="pill pill--neutral">
                {estadoCompleto[queja.estado] || queja.estado}
              </span>
            </span>

            <span className="meta__group">
              <span className="meta__label">Categoría:</span>
              <span className="pill pill--neutral">
                {queja.categoria_nombre}
              </span>
            </span>

            <span className="meta__group">
              <span className="meta__label">Distrito:</span>
              <span className="pill pill--neutral">
                {queja.distrito_nombre}
              </span>
            </span>
          </div>
          <div className="detail_content">
            {queja.descripcion && (
              <p className="detail__desc">
                <strong>Descripcion: </strong>
                {queja.descripcion}
              </p>
            )}
            {queja.ubicacion && (
              <p className="detail__desc">
                <strong>Ubicacion: </strong>
                {queja.ubicacion}
              </p>
            )}
          </div>
        </header>

        <div className="sections-row">
          {/* Imágenes */}
          <section className="section_media">
            <h2 className="section__title">Imágenes ({imagenes.length})</h2>

            {imagenes.length > 0 ? (
              <>
                <div className="media-grid-2">
                  {firstTwo.map((img, index) => (
                    <div key={img.id} className="media-card">
                      <div className="media-card__visual">
                        <img
                          className="media media--image"
                          src={mediaUrl(img.imagen)}
                          alt=""
                        />
                        {index === 1 && remaining > 0 && (
                          <div
                            className="overlay-more"
                            onClick={() => setShowAllImages(!showAllImages)}
                          >
                            +{remaining}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {showAllImages && remaining > 0 && (
                  <div className="media-grid">
                    {rest.map((img, i) => (
                      <div key={i} className="media-card">
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
              </>
            ) : (
              <p className="empty-state">No hay imágenes.</p>
            )}
          </section>

          {/* Videos */}
          <section className="section_media">
            <h2 className="section__title">Videos</h2>

            {videos.length === 0 ? (
              <div className="empty-state">No hay videos.</div>
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

        {/* Comentarios */}
        <section className="section">
          <div className="section_title_header">
            <h2 className="section__title">
              Comentarios ({comentarios.length})
            </h2>
            <CommentButton
              onClick={() => {
                setShowCommentBox(true);
              }}
            />
          </div>

          {showCommentBox && (
            <div className="comment-form">
              <div className="comment-form__row">
                {/* TEXTAREA */}
                <textarea
                  value={commentText}
                  onChange={(e) => setCommentText(e.target.value)}
                  placeholder="Escribe tu comentario…"
                  className="comment-textarea"
                />

                {/* BOTONES VERTICALES */}
                <div className="comment-form__buttons">
                  <button
                    className="btn btn-primary btn-small"
                    disabled={submitting || commentText.trim().length < 3}
                    onClick={handleSubmitComment}
                  >
                    {submitting ? "..." : "Enviar"}
                  </button>

                  <button
                    className="btn btn-secondary btn-small"
                    onClick={() => {
                      setShowCommentBox(false);
                      setCommentText("");
                    }}
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          )}
          {tree.length === 0 ? (
            <div className="empty-state">No hay comentarios.</div>
          ) : (
            <ul className="comment-list">
              {tree.map((root) => (
                <CommentItem key={root.id} node={root} />
              ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}

export default QuejaDetail;
