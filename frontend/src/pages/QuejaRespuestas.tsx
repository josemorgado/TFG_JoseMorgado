import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { listarRespuestasPorQueja } from "../api/respuestas";
import type { Paginated, RespuestaDTO } from "../types/respuestas";
import { ESTADO_LABEL } from "../types/estadosQueja";

// Importa el CSS SÓLO para esta página
import "../styles/QuejaRespuesta.css";



export default function QuejaRespuestasPage() {
  const { quejaId } = useParams<{ quejaId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();
  const page = Number(searchParams.get("page") || 1);
  const pageSize = Number(searchParams.get("page_size") || 10);

  const [loading, setLoading] = useState(true);
  const [data, setData] = useState<Paginated<RespuestaDTO> | null>(null);
  const [error, setError] = useState<string | null>(null);

  const qs = useMemo(() => ({ page, page_size: pageSize }), [page, pageSize]);

  useEffect(() => {
    if (!quejaId) return;
    let cancel = false;
    setLoading(true);
    setError(null);

    listarRespuestasPorQueja(quejaId, qs)
      .then((d) => !cancel && setData(d))
      .catch((e) => !cancel && setError(e?.message ?? "No se pudieron cargar las respuestas."))
      .finally(() => !cancel && setLoading(false));

    return () => {
      cancel = true;
    };
  }, [quejaId, qs]);

  if (!quejaId)
    return <p className="respuestas-page__pad">Falta el ID de la queja.</p>;

  // SKELETON LOADER (opcional y encapsulado)
  if (loading) {
    return (
      <div className="respuestas-page">
        <div className="respuestas-page__container">
          <div className="respuestas-page__header">
            <div
              className="respuestas-page__skeleton"
              style={{ width: 320, height: 30, borderRadius: 8 }}
            />
            <div
              className="respuestas-page__skeleton"
              style={{ width: 180, height: 40, borderRadius: 10 }}
            />
          </div>

          <ul className="respuestas-page__list">
            {Array.from({ length: 3 }).map((_, i) => (
              <li key={i} className="respuestas-page__card respuestas-page__skeleton">
                <div
                  className="respuestas-page__skeleton-line respuestas-page__skeleton-line--lg"
                  style={{ width: "55%" }}
                />
                <div className="respuestas-page__skeleton-line" style={{ width: "95%" }} />
                <div className="respuestas-page__skeleton-line" style={{ width: "88%" }} />
                <div
                  className="respuestas-page__skeleton-line respuestas-page__skeleton-line--sm"
                  style={{ width: "40%" }}
                />
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }

  if (error)
    return <div className="respuestas-page__alert respuestas-page__alert--error">{error}</div>;

  return (
    <div className="respuestas-page">
      <div className="respuestas-page__container">
        <div className="respuestas-page__header">
          <h1 className="respuestas-page__title">Respuestas de la queja #{quejaId}</h1>

          <Link to={`/quejas/${quejaId}`} className="btn btn-secondary">
            Volver a la queja
          </Link>
        </div>

        {data && data.results.length === 0 && (
          <div className="respuestas-page__empty">No hay respuestas aún.</div>
        )}

        <ul className="respuestas-page__list">
          {data?.results.map((r) => (
            <li key={r.id} className="respuestas-page__card">
              <div className="respuestas-page__row respuestas-page__row--between">
                <div>
                  <strong>Respuesta #{r.id}</strong>{" "}
                </div>

                {r.nuevo_estado && (
                  <span className={`respuestas-page__tag respuestas-page__tag--${r.nuevo_estado}`}>
                    {ESTADO_LABEL[r.nuevo_estado]} ({r.nuevo_estado})
                  </span>
                )}
              </div>

              <p className="respuestas-page__texto">{r.contenido}</p>

              <div className="respuestas-page__muted respuestas-page__small">
                Moderador: {r.moderador_username ?? r.moderador ?? "N/D"} •{" "}
                Fecha: {r.fecha_actualizacion}
              </div>
            </li>
          ))}
        </ul>

        {data && (data.next || data.previous) && (
          <div className="respuestas-page__pager">
            <button
              className="btn btn-secondary"
              disabled={!data.previous}
              onClick={() =>
                setSearchParams({
                  page: String(Math.max(1, page - 1)),
                  page_size: String(pageSize),
                })
              }
            >
              ← Anterior
            </button>

            <span className="respuestas-page__muted">
              Página {page} • Total: {data.count}
            </span>

            <button
              className="btn btn-secondary"
              disabled={!data.next}
              onClick={() =>
                setSearchParams({
                  page: String(page + 1),
                  page_size: String(pageSize),
                })
              }
            >
              Siguiente →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}