import { useEffect, useState, useMemo } from "react";
import { getQuejas } from "../api/quejas";
import type { Queja } from "../types/queja";
import { useNavigate } from "react-router-dom";
import "../styles/quejasList.css";

import {
  useCategorias,
  useDistritos,
} from "../modules/catalogos/catalogos.queries";

export default function QuejasList() {
  const navigate = useNavigate();

  const [quejas, setQuejas] = useState<Queja[]>([]);
  const [loading, setLoading] = useState(true);

  // =========================================
  // 🔥 Estado de todos los filtros
  // =========================================
  const [filters, setFilters] = useState({
    texto: "",
    estado: "",
    categoria: "",
    distrito: "",
    autor: "",
    ubicacion: "",
    fechaDesde: "",
    fechaHasta: "",
    votosMin: "",
    votosMax: "",
    comentariosMin: "",
    comentariosMax: "",
  });

  const handleFilter = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    setFilters({ ...filters, [e.target.name]: e.target.value });
  };

  const {
    data: categorias,
    isLoading: catLoading,
    error: catError,
  } = useCategorias();

  const {
    data: distritos,
    isLoading: disLoading,
    error: disError,
  } = useDistritos();

  // =========================================
  // 🔥 Cargar quejas
  // =========================================
  useEffect(() => {
    (async () => {
      const data = await getQuejas();
      setQuejas(data);
      setLoading(false);
    })();
  }, []);

  // =========================================
  // 🔍 Filtrado avanzado (useMemo)
  // =========================================
  const filteredQuejas = useMemo(() => {
    return quejas.filter((q) => {
      if (filters.estado && q.estado !== filters.estado) return false;

      if (filters.categoria && q.categoria_nombre !== filters.categoria)
        return false;

      if (filters.distrito && q.distrito_nombre !== filters.distrito)
        return false;

      if (filters.autor) {
        const autor = q.autor_nombre?.toLowerCase() || "";
        if (!autor.includes(filters.autor.toLowerCase())) return false;
      }

      if (filters.ubicacion) {
        if (
          !q.ubicacion ||
          !q.ubicacion.toLowerCase().includes(filters.ubicacion.toLowerCase())
        )
          return false;
      }

      if (filters.texto) {
        const txt = filters.texto.toLowerCase();
        if (
          !q.titulo.toLowerCase().includes(txt) &&
          !q.descripcion.toLowerCase().includes(txt)
        )
          return false;
      }

      if (filters.fechaDesde) {
        if (new Date(q.fecha_creacion) < new Date(filters.fechaDesde))
          return false;
      }

      if (filters.fechaHasta) {
        if (new Date(q.fecha_creacion) > new Date(filters.fechaHasta))
          return false;
      }

      if (filters.votosMin && q.num_votos < Number(filters.votosMin))
        return false;
      if (filters.votosMax && q.num_votos > Number(filters.votosMax))
        return false;

      if (
        filters.comentariosMin &&
        q.num_comentarios < Number(filters.comentariosMin)
      )
        return false;
      if (
        filters.comentariosMax &&
        q.num_comentarios > Number(filters.comentariosMax)
      )
        return false;

      return true;
    });
  }, [quejas, filters]);

  if (loading) return <p className="loading">Cargando...</p>;

  const resetFilters = () => {
    setFilters({
      texto: "",
      estado: "",
      categoria: "",
      distrito: "",
      autor: "",
      ubicacion: "",
      fechaDesde: "",
      fechaHasta: "",
      votosMin: "",
      votosMax: "",
      comentariosMin: "",
      comentariosMax: "",
    });
  };

  return (
    <div className="quejas-layout">
      {/* ========================== */}
      {/* 🔥 BARRA LATERAL DE FILTROS */}
      {/* ========================== */}
      <div className="sidebar-filtros">
        <h3 className="sidebar-title">Filtros</h3>

<button
  className="btn btn-secondary btn-small"
  onClick={resetFilters}
  style={{ marginTop: "10px" }}
>
  Reiniciar filtros
</button>

        {/* TEXTO */}
        <div className="filtro-item">
          <label>Texto</label>
          <input
            className="input"
            name="texto"
            onChange={handleFilter}
            placeholder="Buscar…"
          />
        </div>

        {/* ESTADO */}
        <div className="filtro-item">
          <label>Estado</label>
          <select className="input" name="estado" onChange={handleFilter}>
            <option value="">Todos</option>
            <option value="PEN">Pendiente</option>
            <option value="ENP">En Progreso</option>
            <option value="RES">Resuelta</option>
            <option value="REC">Rechazada</option>
          </select>
        </div>

        {/* CATEGORÍA */}
        <div className="filtro-item">
          <label>Categoría</label>
          <select className="input" name="categoria" onChange={handleFilter}>
            <option value="">Todas</option>

            {catLoading && <option>Cargando…</option>}
            {catError && <option>Error</option>}

            {categorias?.map((c) => (
              <option key={c.id} value={c.nombre}>
                {c.nombre}
              </option>
            ))}
          </select>
        </div>

        {/* DISTRITO */}
        <div className="filtro-item">
          <label>Distrito</label>
          <select className="input" name="distrito" onChange={handleFilter}>
            <option value="">Todos</option>

            {disLoading && <option>Cargando…</option>}
            {disError && <option>Error</option>}

            {distritos?.map((d) => (
              <option key={d.id} value={d.nombre}>
                {d.nombre}
              </option>
            ))}
          </select>
        </div>

        {/* AUTOR */}
        <div className="filtro-item">
          <label>Autor</label>
          <input
            className="input"
            name="autor"
            onChange={handleFilter}
            placeholder="Nombre del autor"
          />
        </div>

        {/* UBICACIÓN */}
        <div className="filtro-item">
          <label>Ubicación</label>
          <input
            className="input"
            name="ubicacion"
            onChange={handleFilter}
            placeholder="Ej: Calle Real"
          />
        </div>

        {/* FECHAS */}
        <div className="filtro-item">
          <label>Desde</label>
          <input
            type="date"
            className="input"
            name="fechaDesde"
            onChange={handleFilter}
          />
        </div>

        <div className="filtro-item">
          <label>Hasta</label>
          <input
            type="date"
            className="input"
            name="fechaHasta"
            onChange={handleFilter}
          />
        </div>

        {/* VOTOS */}
        <div className="filtro-item">
          <label>Votos min</label>
          <input
            type="number"
            className="input"
            name="votosMin"
            onChange={handleFilter}
          />
        </div>

        <div className="filtro-item">
          <label>Votos max</label>
          <input
            type="number"
            className="input"
            name="votosMax"
            onChange={handleFilter}
          />
        </div>

        {/* COMENTARIOS */}
        <div className="filtro-item">
          <label>Com. min</label>
          <input
            type="number"
            className="input"
            name="comentariosMin"
            onChange={handleFilter}
          />
        </div>

        <div className="filtro-item">
          <label>Com. max</label>
          <input
            type="number"
            className="input"
            name="comentariosMax"
            onChange={handleFilter}
          />
        </div>
      </div>
      {/* ========================== */}
      {/* 🔥 LISTA DE QUEJAS */}
      {/* ========================== */}
      <div className="quejas-content">
        <h2 className="quejas-header">Listado de Quejas</h2>

        <div className="quejas-grid">
          {filteredQuejas.map((q) => (
            <div
              className="queja-card"
              key={q.id}
              onClick={() => navigate(`/quejas/${q.id}`)}
            >
              <h3 className="queja-title">{q.titulo}</h3>

              <p className="queja-meta">
                {q.categoria_nombre} · {q.distrito_nombre} · {q.estado}
              </p>

              <p className="queja-descripcion">
                {q.descripcion.slice(0, 120)}…
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
