import React from "react";
import { useNavigate } from "react-router-dom";

interface Queja {
  id: number;
  titulo: string;
  categoria_nombre: string;
  distrito_nombre: string;
  estado: string;
  fecha_creacion: string;
  descripcion: string;
  num_votos: number;
  num_comentarios: number;
  autor_nombre:string;
}

interface Props {
  q: Queja;
}

const QuejaCard: React.FC<Props> = ({ q }) => {
  const navigate = useNavigate();

  return (
    <div
      className="queja-card"
      onClick={() => navigate(`/quejas/${q.id}`)}
    >
      <h3 className="queja-title">{q.titulo}</h3>
      <h6 className="queja-author">{q.autor_nombre}</h6>

      <p className="queja-meta">
        {q.categoria_nombre} · {q.distrito_nombre} · {q.estado} · {q.fecha_creacion}
      </p>

      <p className="queja-descripcion">
        {q.descripcion.slice(0, 120)}…
      </p>

      <div className="queja-footer">
        <div className="queja-stat">
          <svg
            viewBox="0 0 24 24"
            className="queja-stat__icon"
            aria-hidden="true"
          >
            <path
              d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5
               5.5 0 00-7.78 7.78L12 21.23l8.84-8.84a5.5
               5.5 0 000-7.78z"
            />
          </svg>
          <span className="queja-stat__count">{q.num_votos}</span>

        <div className="queja-stat" aria-label={`${q.num_comentarios} comentarios`}>
          <svg viewBox="0 0 24 24" className="queja-stat__icon" aria-hidden="true">
            <path d="M21 6.5a3.5 3.5 0 00-3.5-3.5h-11A3.5 3.5 0 003 6.5v7A3.5 3.5 0 006.5 17H7v3.25a.75.75 0 001.23.58L12.1 17h5.4A3.5 3.5 0 0021 13.5v-7z"/>
          </svg>
          <span className="queja-stat__count">{q.num_comentarios}</span>
        </div>

        </div>
      </div>
    </div>
  );
};

export default QuejaCard;