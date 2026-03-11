// src/pages/QuejasList.tsx
import { useEffect, useState } from "react";
import { getQuejas } from "../api/quejas";
import type { Queja } from "../types/queja";
import { useNavigate } from "react-router-dom";
import "../styles/QuejasList.css";

export default function QuejasList() {
  const [quejas, setQuejas] = useState<Queja[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const navigate = useNavigate();

  useEffect(() => {
    (async () => {
      try {
        const data = await getQuejas();
        setQuejas(data);
      } catch (e) {
        setError("No se pudieron cargar las quejas.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const estadoCompleto: Record<string, string> = {
    PEN: "Pendiente",
    ENP: "En Progreso",
    RES: "Resuelta",
    REC: "Rechazada",
  };

  if (loading) return <p className="loading">Cargando quejas...</p>;
  if (error) return <p className="error">{error}</p>;

  return (
    <div className="quejas-page">
      <h2 className="quejas-header">Listado de Quejas</h2>

      {quejas.length > 0 ? (
        <div className="quejas-grid">
          {quejas.map((q) => (
            <div
              key={q.id}
              className="queja-card"
              onClick={() => navigate(`/quejas/${q.id}`)}
            >
              <h3 className="queja-title">{q.titulo}</h3>

              <p className="queja-meta">
                <strong>Estado:</strong> {estadoCompleto[q.estado] || q.estado}
              </p>

              <p className="queja-meta">
                <strong>Fecha:</strong> {q.fecha_creacion}
              </p>

              <p className="queja-descripcion">
                {q.descripcion.length > 120
                  ? q.descripcion.slice(0, 120) + "..."
                  : q.descripcion}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <div className="empty-state">
          Todavía no hay quejas registradas.
        </div>
      )}
    </div>
  );
}