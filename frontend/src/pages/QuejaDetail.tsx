import { useEffect, useMemo, useState } from "react";
import axiosInstance from "../utils/axios";
import axios from "axios";
import { useParams } from "react-router-dom";
import type { Queja } from "../types/queja";
import type { Comentario } from "../types/comentario";
import type { Imagen } from "../types/imagen";
import type { Video } from "../types/video";
import { mediaUrl } from "../utils/media";
import "../styles/detail.css"; // <-- importa el CSS reutilizable

/** ---- Comentarios: árbol + tipos ---- */
type CommentNode = Comentario & { children: CommentNode[] };

function buildCommentTree(comments: Comentario[]): CommentNode[] {
  const map = new Map<number, CommentNode>();
  const roots: CommentNode[] = [];

  // Crear nodos
  comments.forEach((c) => map.set(c.id, { ...c, children: [] }));

  // Enlazar hijos
  map.forEach((node) => {
    if (node.parent) {
      const parent = map.get(node.parent);
      if (parent) parent.children.push(node);
      else roots.push(node); // fallback si no existe el parent
    } else {
      roots.push(node);
    }
  });

  // Orden por fecha (opcional)
  const sortByDate = (arr: CommentNode[]) => {
    arr.sort(
      (a, b) =>
        new Date(a.fecha_creacion).getTime() -
        new Date(b.fecha_creacion).getTime()
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

  // Imágenes: preview + desplegable
  const [showAllImages, setShowAllImages] = useState(false);
  const firstTwo = imagenes.slice(0, 2);
  const rest = imagenes.slice(2);
  const remaining = rest.length;

  // Estado completo del estado :)
  const estadoCompleto: Record<string, string> = {
    PEN: "Pendiente",
    ENP: "En Progreso",
    RES: "Resuelta",
    REC: "Rechazada",
  };

  // Comentarios: árbol + toggles por id
  const tree = useMemo(() => buildCommentTree(comentarios), [comentarios]);
  const [expanded, setExpanded] = useState<Set<number>>(new Set());
  const toggleReplies = (id: number) =>
    setExpanded((prev) => {
      const next = new Set(prev);
      next.has(id) ? next.delete(id) : next.add(id);
      return next;
    });

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

  /** --- Componente recursivo para un comentario --- */
  function CommentItem({ node, level = 0 }: { node: CommentNode; level?: number }) {
    const isOpen = expanded.has(node.id);
    const repliesCount = node.children.length;

    return (
      <li className="comment" style={{ marginLeft: level ? 16 : 0 }}>
        <p className="comment__content">{node.contenido}</p>


        <div className="comment__footer">
        <div className="comment__meta">
            <span>ID autor: {node.autor}</span>
            <span>Fecha: {node.fecha_creacion}</span>
            <span>Votos: {node.num_votos}</span>
        </div>

        {repliesCount > 0 && (
            <button
            type="button"
            className="toggle-replies btn btn-secondary"
            onClick={() => toggleReplies(node.id)}
            aria-expanded={isOpen}
            >
            {isOpen ? "Ocultar" : "Ver"} {repliesCount} respuesta{repliesCount !== 1 ? "s" : ""}
            </button>
        )}
        </div>



        {isOpen && repliesCount > 0 && (
          <ul id={`replies-${node.id}`} className="comment-list replies">
            {node.children.map((child) => (
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
          <h1 className="detail__title">{queja.titulo}</h1>
          {queja.descripcion && (
            <p className="detail__desc">{queja.descripcion}</p>
          )}

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
                        <img className="media media--image" src={mediaUrl(img.imagen)} alt="" />
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

                {/* DESPLEGABLE: solo resto (sin duplicar) */}
                {showAllImages && remaining > 0 && (
                  <div className="media-grid">
                    {rest.map((img, i) => (
                      <div key={i} className="media-card">
                        <div className="media-card__visual">
                          <img className="media media--image" src={mediaUrl(img.imagen)} alt="" />
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
                      {/* Clase específica para centrar y ajustar video */}
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
          <h2 className="section__title">Comentarios ({comentarios.length})</h2>

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