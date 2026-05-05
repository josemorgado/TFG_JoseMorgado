import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import axiosInstance from "../utils/axios";
import axios from "axios";
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
import { deleteQueja } from "../api/quejas";
import { listarRespuestasPorQueja } from "../api/respuestas";

type NodoComentario = Comentario & { children: NodoComentario[] };

const LIMITE_TIEMPO_ACTUALIZACION = config.LIMIT_TIME_UPDATE_QUEJA;

function construirArbolComentarios(comentarios: Comentario[]): NodoComentario[] {
  const mapa = new Map<number, NodoComentario>();
  const raices: NodoComentario[] = [];

  comentarios.forEach((c) => mapa.set(c.id, { ...c, children: [] }));

  mapa.forEach((nodo) => {
    if (nodo.parent) {
      const padre = mapa.get(nodo.parent);
      if (padre) padre.children.push(nodo);
      else raices.push(nodo);
    } else {
      raices.push(nodo);
    }
  });

  return raices;
}

function QuejaDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [queja, setQueja] = useState<Queja | null>(null);
  const [imagenes, setImagenes] = useState<Imagen[]>([]);
  const [videos, setVideos] = useState<Video[]>([]);
  const [comentarios, setComentarios] = useState<Comentario[]>([]);
  const [cargando, setCargando] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [mostrarTodasLasImagenes, setMostrarTodasLasImagenes] = useState(false);
  const [textoComentario, setTextoComentario] = useState("");
  const [mostrarFormularioComentario, setMostrarFormularioComentario] = useState(false);
  const [enviandoComentario, setEnviandoComentario] = useState(false);
  const [contadorRespuestas, setContadorRespuestas] = useState<number | null>(null);
  const [cargandoRespuestas, setCargandoRespuestas] = useState<boolean>(false);
  const [expandidos, setExpandidos] = useState<Set<number>>(new Set());

  const primerosDos = imagenes.slice(0, 2);
  const restantes = imagenes.slice(2);
  const cantidadRestantes = restantes.length;

  const esModeradorOAdmin = Boolean(
    user?.is_staff ||
    user?.is_superuser ||
    user?.is_moderator ||
    (user?.groups || []).some((g: any) => (typeof g === "string" ? g : g?.name || "").toLowerCase().includes("moderador"))
  );

  const estadoCompleto: Record<string, string> = {
    PEN: "Pendiente",
    ENP: "En Progreso",
    RES: "Resuelta",
    REC: "Rechazada",
  };

  const arbolComentarios = useMemo(() => construirArbolComentarios(comentarios), [comentarios]);

  const puedeActualizar = (() => {
    if (!queja?.fecha_creacion_iso) return false;
    if (!(user && queja.autor === user.id)) return false;

    const fecha = new Date(queja.fecha_creacion_iso);
    const ahora = new Date();
    const diffMs = ahora.getTime() - fecha.getTime();
    const diffMin = diffMs / 60000;
    return diffMin <= LIMITE_TIEMPO_ACTUALIZACION;
  })();

  const alternarRespuestas = useCallback((idComentario: number) => {
    setExpandidos((anterior) => {
      const siguiente = new Set(anterior);
      siguiente.has(idComentario) ? siguiente.delete(idComentario) : siguiente.add(idComentario);
      return siguiente;
    });
  }, []);

  useEffect(() => {
    if (!id) return;
    let cancelado = false;

    async function obtenerDatos() {
      try {
        setCargando(true);
        setError(null);

        const [quejaRes, imagenesRes, videosRes, comentarioRes] = await Promise.all([
          axiosInstance.get<Queja>(`/quejas/${id}/`),
          axiosInstance.get<Imagen[]>(`/imagenes/queja/${id}/`),
          axiosInstance.get<Video[]>(`/videos/queja/${id}/`),
          axiosInstance.get<Comentario[]>(`/comentarios/queja/${id}/`),
        ]);

        if (!cancelado) {
          setQueja(quejaRes.data);
          setImagenes(imagenesRes.data);
          setVideos(videosRes.data);
          setComentarios(comentarioRes.data);
        }
      } catch (err) {
        if (axios.isAxiosError(err)) {
          setError("La queja no existe.");
        } else {
          setError("Error inesperado");
        }
      } finally {
        if (!cancelado) setCargando(false);
      }
    }

    obtenerDatos();
    return () => {
      cancelado = true;
    };
  }, [id]);

  useEffect(() => {
    if (!id) return;
    let cancelado = false;

    (async () => {
      try {
        setCargandoRespuestas(true);
        const qid = Number(id);
        const datos = await listarRespuestasPorQueja(qid, { page: 1, page_size: 1 });
        if (!cancelado) setContadorRespuestas(datos.count);
      } catch {
        if (!cancelado) setContadorRespuestas(0);
      } finally {
        if (!cancelado) setCargandoRespuestas(false);
      }
    })();

    return () => {
      cancelado = true;
    };
  }, [id]);

  function requerirInicioSesion(mensaje: string) {
    const irALogin = window.confirm(`${mensaje}\n\n¿Quieres ir a iniciar sesión ahora?`);
    if (irALogin) {
      navigate("/login");
    }
  }

  function manejadorEliminar() {
    if (!window.confirm("¿Seguro que deseas eliminar esta queja?")) return;

    deleteQueja(Number(id))
      .then(() => navigate("/"))
      .catch((err) => {
        console.error(err);
        alert("No se pudo eliminar la queja.");
      });
  }

  const manejadorCambioMeGustaQueja = useCallback((meGusta: boolean, cantidad: number) => {
    setQueja((anterior) =>
      anterior ? { ...anterior, is_liked: meGusta, num_votos: cantidad } : anterior,
    );
  }, []);

  async function manejadorEnviarComentario() {
    if (!textoComentario.trim() || !id) return;

    try {
      setEnviandoComentario(true);

      const respuesta = await axiosInstance.post("/comentarios/create/", {
        queja: Number(id),
        contenido: textoComentario.trim(),
      });

      setComentarios((anterior) => [...anterior, respuesta.data]);
      setTextoComentario("");
      setMostrarFormularioComentario(false);
    } catch (err: any) {
      if (err?.response?.status === 401) {
        requerirInicioSesion("Debes iniciar sesión para comentar.");
      } else {
        alert("No se pudo enviar el comentario.");
      }
    } finally {
      setEnviandoComentario(false);
    }
  }

  async function manejadorEnviarRespuesta(idPadre: number, texto: string) {
    if (!texto || !id) return;

    try {
      const respuesta = await axiosInstance.post("/comentarios/create/", {
        queja: Number(id),
        contenido: texto,
        parent: idPadre,
      });

      setComentarios((anterior) => [...anterior, respuesta.data]);
    } catch (err: any) {
      if (err?.response?.status === 401) {
        requerirInicioSesion("Debes iniciar sesión para responder.");
      } else {
        alert("Error al enviar la respuesta");
      }
    }
  }

  const manejadorCambioMeGustaComentario = useCallback(
    (idComentario: number, meGusta: boolean, cantidad: number) => {
      setComentarios((anterior) =>
        anterior.map((c) =>
          c.id === idComentario
            ? { ...c, is_liked: meGusta, num_votos: cantidad }
            : c,
        ),
      );
    },
    [],
  );

  if (cargando) {
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

  function ItemComentario({
    nodo,
    nivel = 0,
  }: {
    nodo: NodoComentario;
    nivel?: number;
  }) {
    const [respondiendo, setRespondiendo] = useState(false);
    const [textoRespuesta, setTextoRespuesta] = useState("");

    const abierto = expandidos.has(nodo.id);
    const contadorRespuestasLocales = nodo.children.length;

    const enviarRespuesta = () => {
      manejadorEnviarRespuesta(nodo.id, textoRespuesta);
      setTextoRespuesta("");
      setRespondiendo(false);
    };

    return (
      <li className="comment" style={{ marginLeft: nivel ? 16 : 0 }}>
        <p>
          <strong>
            <Link to={`/perfil/${nodo.autor}`}>{nodo.autor_nombre}</Link>
          </strong>
          :{nodo.contenido}
        </p>
        <div className="comment__footer">
          <div className="comment__meta">
            <span>{nodo.fecha_creacion}</span>
          </div>

          <div className="comment__actions">
            {contadorRespuestasLocales > 0 && (
              <button
                type="button"
                className="toggle-replies btn btn-secondary"
                onClick={() => alternarRespuestas(nodo.id)}
                aria-expanded={abierto}
              >
                {abierto ? "Ocultar" : "Ver"} {contadorRespuestasLocales} respuesta
                {contadorRespuestasLocales !== 1 ? "s" : ""}
              </button>
            )}

            <button
              type="button"
              className="reply-btn btn btn-secondary"
              onClick={() => setRespondiendo(!respondiendo)}
            >
              Responder
            </button>

            <LikeButton
              initialLiked={!!nodo.is_liked}
              initialCount={nodo.num_votos ?? 0}
              objectId={nodo.id}
              contentType={Number(nodo.content_type)}
              onChange={manejadorCambioMeGustaComentario.bind(null, nodo.id)}
              onUnauthorized={() =>
                requerirInicioSesion("Debes iniciar sesión para dar Me gusta.")
              }
            />
          </div>
        </div>

        {respondiendo && (
          <div className="reply-form">
            <div className="reply-form__row">
              <textarea
                value={textoRespuesta}
                onChange={(e) => setTextoRespuesta(e.target.value)}
                placeholder={`Responder a ${nodo.autor_nombre}…`}
                className="reply-textarea"
              />

              <div className="reply-form__buttons">
                <button
                  className="btn btn-primary btn-small"
                  disabled={textoRespuesta.trim().length < 3}
                  onClick={enviarRespuesta}
                >
                  Enviar
                </button>

                <button
                  className="btn btn-secondary btn-small"
                  onClick={() => setRespondiendo(false)}
                >
                  Cancelar
                </button>
              </div>
            </div>
          </div>
        )}

        {abierto && contadorRespuestasLocales > 0 && (
          <ul className="comment-list replies">
            {nodo.children.map((hijo: NodoComentario) => (
              <ItemComentario key={hijo.id} nodo={hijo} nivel={nivel + 1} />
            ))}
          </ul>
        )}
      </li>
    );
  }

  return (
    <main className="detail-page">
      <div className="detail">
        <header className="detail__header card">
          <div className="header_grid">
            <div className="like-title">
              <LikeButton
                initialLiked={!!queja.is_liked}
                initialCount={queja.num_votos ?? 0}
                objectId={queja.id}
                contentType={Number(queja.content_type)}
                onChange={manejadorCambioMeGustaQueja}
                onUnauthorized={() =>
                  requerirInicioSesion("Debes iniciar sesión para dar Me gusta.")
                }
              />
              <h1 className="detail__title">{queja.titulo}</h1>
            </div>
            <div>
              {puedeActualizar && (
                <button
                  type="button"
                  className="update-btn btn btn-secondary btn-small"
                  onClick={() => navigate(`update`)}
                >
                  Actualizar
                </button>
              )}
              {!cargandoRespuestas &&
                contadorRespuestas !== null &&
                contadorRespuestas > 0 &&
                (
                  <Link
                    to={`/quejas/${id}/respuestas`}
                    className="btn btn-secondary btn-small"
                    style={{ marginLeft: 8 }}
                  >
                    Ver respuestas ({contadorRespuestas})
                  </Link>
                )}

              {esModeradorOAdmin && (
                <button
                  type="button"
                  onClick={() => navigate(`/quejas/${id}/responder`)}
                  className="btn btn-primary btn-small"
                >
                  Responder queja
                </button>
              )}

              {user && queja.autor === user.id && (
                <button
                  type="button"
                  className="delete-btn btn btn-primary btn-small"
                  onClick={manejadorEliminar}
                >
                  Eliminar
                </button>
              )}
            </div>
          </div>
          <div className="detail__meta">
            <span className="meta__label">Usuario:</span>
            <span className="pill" title="User">
              <strong>
                <Link to={`/perfil/${queja.autor}`}>{queja.autor_nombre}</Link>
              </strong>
            </span>

            <span className="meta__group">
              <span className="meta__label">Estado:</span>
              <Link
                to={`/quejas?estado=${queja.estado}`}
                className="pill pill--neutral pill--link"
              >
                {estadoCompleto[queja.estado] || queja.estado}
              </Link>
            </span>

            <span className="meta__group">
              <span className="meta__label">Categoría:</span>
              <Link
                to={`/quejas?categoria=${encodeURIComponent(queja.categoria_nombre)}`}
                className="pill pill--neutral pill--link"
              >
                {queja.categoria_nombre}
              </Link>
            </span>

            <span className="meta__group">
              <span className="meta__label">Distrito:</span>
              <Link
                to={`/quejas?distrito=${encodeURIComponent(queja.distrito_nombre)}`}
                className="pill pill--neutral pill--link"
              >
                {queja.distrito_nombre}
              </Link>
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
          <section className="section_media">
            <h2 className="section__title">Imágenes ({imagenes.length})</h2>

            {imagenes.length > 0 ? (
              <>
                <div className="media-grid-2">
                  {primerosDos.map((img, indice) => (
                    <div key={img.id} className="media-card">
                      <div className="media-card__visual">
                        <img
                          className="media media--image"
                          src={mediaUrl(img.imagen)}
                          alt=""
                        />

                        {indice === 1 && cantidadRestantes > 0 && !mostrarTodasLasImagenes && (
                          <div
                            className="overlay-more"
                            onClick={() => setMostrarTodasLasImagenes(true)}
                          >
                            +{cantidadRestantes}
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {mostrarTodasLasImagenes && cantidadRestantes > 0 && (
                  <div className="media-grid">
                    {restantes.map((img, i) => (
                      <div key={i} className="media-card">
                        <div className="media-card__visual">
                          <img
                            className="media media--image"
                            src={mediaUrl(img.imagen)}
                            alt=""
                          />

                          {i === restantes.length - 1 && (
                            <div
                              className="overlay-more"
                              onClick={() => setMostrarTodasLasImagenes(false)}
                            >
                              -{cantidadRestantes}
                            </div>
                          )}
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

        <section className="section">
          <div className="section_title_header">
            <h2 className="section__title">
              Comentarios ({comentarios.length})
            </h2>
            <CommentButton
              onClick={() => {
                setMostrarFormularioComentario(true);
              }}
            />
          </div>

          {mostrarFormularioComentario && (
            <div className="comment-form">
              <div className="comment-form__row">
                <textarea
                  value={textoComentario}
                  onChange={(e) => setTextoComentario(e.target.value)}
                  placeholder="Escribe tu comentario…"
                  className="comment-textarea"
                />

                <div className="comment-form__buttons">
                  <button
                    className="btn btn-primary btn-small"
                    disabled={enviandoComentario || textoComentario.trim().length < 3}
                    onClick={manejadorEnviarComentario}
                  >
                    {enviandoComentario ? "..." : "Enviar"}
                  </button>

                  <button
                    className="btn btn-secondary btn-small"
                    onClick={() => {
                      setMostrarFormularioComentario(false);
                      setTextoComentario("");
                    }}
                  >
                    Cancelar
                  </button>
                </div>
              </div>
            </div>
          )}
          {arbolComentarios.length === 0 ? (
            <div className="empty-state">No hay comentarios.</div>
          ) : (
            <ul className="comment-list">
              {arbolComentarios.map((raiz) => (
                <ItemComentario key={raiz.id} nodo={raiz} />
              ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}

export default QuejaDetail;
