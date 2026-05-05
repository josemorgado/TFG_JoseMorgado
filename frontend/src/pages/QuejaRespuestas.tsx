import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";

import { listarRespuestasPorQueja } from "../api/respuestas";

import type { Paginated, RespuestaDTO } from "../types/respuestas";
import { ESTADO_LABEL } from "../types/estadosQueja";

import PageError from "../components/PageError";
import PageInfo from "../components/PageInfo";
import PageEmpty from "../components/PageEmpty";

import "../styles/QuejaRespuestas.css";

export default function QuejaRespuestasPage() {
  const { quejaId } = useParams<{ quejaId: string }>();
  const [searchParams, setSearchParams] = useSearchParams();

  if (!quejaId) {
    return <PageError message="Falta la ID de la queja en la URL." />;
  }

  const idQueja = Number(quejaId);

  if (Number.isNaN(idQueja)) {
    return <PageError message="La ID de la queja no es válida." />;
  }

  const page = Number(searchParams.get("page") || 1);
  const pageSize = Number(searchParams.get("page_size") || 10);

  const [cargando, setCargando] = useState(true);
  const [datos, setDatos] = useState<Paginated<RespuestaDTO> | null>(null);
  const [errorPagina, setErrorPagina] = useState<string | null>(null);

  const query = useMemo(
    () => ({ page, page_size: pageSize }),
    [page, pageSize]
  );

  useEffect(() => {
    let cancelado = false;
    setCargando(true);
    setErrorPagina(null);

    listarRespuestasPorQueja(idQueja, query)
      .then((res) => {
        if (!cancelado) {
          setDatos(res);
        }
      })
      .catch(() => {
        if (!cancelado) {
          setErrorPagina("No se pudieron cargar las respuestas.");
        }
      })
      .finally(() => {
        if (!cancelado) {
          setCargando(false);
        }
      });

    return () => {
      cancelado = true;
    };
  }, [idQueja, query]);

  if (cargando) {
    return <PageInfo message="Cargando respuestas..." />;
  }

  if (errorPagina) {
    return <PageError message={errorPagina} />;
  }

  if (datos && datos.results.length === 0) {
    return <PageEmpty message="Esta queja aún no tiene respuestas." />;
  }

  return (
    <div className="respuestas-page">
      <div className="respuestas-page__container">
        <div className="respuestas-page__header">
          <h1 className="respuestas-page__title">
            Respuestas de la queja #{idQueja}
          </h1>

          <Link to={`/quejas/${idQueja}`} className="btn btn-secondary">
            Volver a la queja
          </Link>
        </div>

        <ul className="respuestas-page__list">
          {datos?.results.map((r, index) => (
            <li key={r.id} className="respuestas-page__card">
              <div className="respuestas-page__row respuestas-page__row--between">
                <strong>
                  Respuesta #{datos.results.length - index}
                </strong>

                {r.nuevo_estado && (
                  <span
                    className={`respuestas-page__tag respuestas-page__tag--${r.nuevo_estado}`}
                  >
                    {ESTADO_LABEL[r.nuevo_estado]} ({r.nuevo_estado})
                  </span>
                )}
              </div>

              <p className="respuestas-page__texto">{r.contenido}</p>

              <div className="respuestas-page__muted respuestas-page__small">
                Moderador:{" "}
                {r.moderador_username ?? r.moderador ?? "N/D"} • Fecha:{" "}
                {r.fecha_actualizacion}
              </div>
            </li>
          ))}
        </ul>

        {datos && (datos.next || datos.previous) && (
          <div className="respuestas-page__pager">
            <button
              className="btn btn-secondary"
              disabled={!datos.previous}
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
              {page} / {Math.ceil(datos.count / pageSize)}
            </span>

            <button
              className="btn btn-secondary"
              disabled={!datos.next}
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