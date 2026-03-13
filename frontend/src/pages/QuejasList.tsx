import { useEffect, useState, useMemo } from "react";
import { getQuejas } from "../api/quejas";
import type { Queja } from "../types/queja";
import "../styles/quejasList.css";
import QuejaCard from "../components/QuejaCard";

import {
  useCategorias,
  useDistritos,
} from "../modules/catalogos/catalogos.queries";

export default function QuejasList() {
  const [quejas, setQuejas] = useState<Queja[]>([]);
  const [loading, setLoading] = useState(true);
  const [isFiltersOpen, setIsFiltersOpen] = useState(false);
  const [isSortOpen, setIsSortOpen] = useState(false);

  // Estado de todos los filtros (un único select para multimedia)
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
    media: "", // "", "con", "sin", "videos", "imagenes"
  });

  const handleFilter = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    const { name, value, type } = e.target;

    if (type === "number") {
      const num = Number(value);
      if (num < 0) {
        setFilters({ ...filters, [name]: "" });
        return;
      }
    }

    let updated = { ...filters, [name]: value };

    if (name === "votosMin" && Number(value) > Number(filters.votosMax)) {
      updated.votosMax = "";
    }
    if (name === "votosMax" && Number(value) < Number(filters.votosMin)) {
      updated.votosMin = "";
    }
    if (
      name === "comentariosMin" &&
      Number(value) > Number(filters.comentariosMax)
    ) {
      updated.comentariosMax = "";
    }
    if (
      name === "comentariosMax" &&
      Number(value) < Number(filters.comentariosMin)
    ) {
      updated.comentariosMin = "";
    }
    if (name === "fechaDesde") {
      const desde = new Date(value);
      const hasta = new Date(filters.fechaHasta);
      const hoy = new Date();
      if (desde > hoy) {
        updated.fechaDesde = hoy.toISOString().slice(0, 10);
      }
      if (filters.fechaHasta && desde > hasta) {
        updated.fechaHasta = value;
      }
    }
    if (name === "fechaHasta") {
      const hasta = new Date(value);
      const desde = new Date(filters.fechaDesde);
      const hoy = new Date();
      if (hasta > hoy) {
        updated.fechaHasta = hoy.toISOString().slice(0, 10);
      }
      if (filters.fechaDesde && hasta < desde) {
        updated.fechaDesde = value;
      }
    }

    setFilters(updated);
  };

  const toggleFilters = () => setIsFiltersOpen((prev) => !prev);
  const toggleSort = () => setIsSortOpen((prev) => !prev);

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

  // Cargar quejas
  useEffect(() => {
    (async () => {
      const data = await getQuejas();
      setQuejas(data);
      setLoading(false);
    })();
  }, []);

  const [sortBy, setSortBy] = useState("");

  // Filtrado avanzado
  const filteredQuejas = useMemo(() => {
    const filtradas = quejas.filter((q) => {
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

      // ---------- FILTRO MULTIMEDIA ÚNICO ----------
      const img = Number(q.imagenes_count ?? 0);
      const vid = Number(q.videos_count ?? 0);
      const totalMedia = img + vid;

      switch (filters.media) {
        case "con": // con media (imágenes o vídeos)
          if (totalMedia === 0) return false;
          break;
        case "sin": // sin media
          if (totalMedia > 0) return false;
          break;
        case "videos": // al menos un vídeo
          if (vid === 0) return false;
          break;
        case "imagenes": // al menos una imagen
          if (img === 0) return false;
          break;
        default:
          // "" → sin filtro
          break;
      }
      // ---------- FIN FILTRO MULTIMEDIA ----------

      return true;
    });

    let ordenadas = [...filtradas];
    switch (sortBy) {
      case "fecha_asc":
        ordenadas.sort(
          (a, b) =>
            new Date(a.fecha_creacion_iso).getTime() -
            new Date(b.fecha_creacion_iso).getTime(),
        );
        break;

      case "fecha_desc":
        ordenadas.sort(
          (a, b) =>
            new Date(b.fecha_creacion_iso).getTime() -
            new Date(a.fecha_creacion_iso).getTime(),
        );
        break;

      case "votos":
        ordenadas.sort((a, b) => b.num_votos - a.num_votos);
        break;

      case "comentarios":
        ordenadas.sort((a, b) => b.num_comentarios - a.num_comentarios);
        break;

      default:
        break;
    }
    return ordenadas;
  }, [quejas, filters, sortBy]);

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
      media: "",
    });
  };

  return (
    <div className="quejas-layout">
      {/* BARRA LATERAL DE FILTROS */}
      <aside className={`sidebar-filtros ${isFiltersOpen ? "open" : "closed"}`}>
        <div className="sidebar-section">
          <div className="sidebar-header">
            <button
              className="sidebar-title-btn"
              onClick={() => setIsSortOpen((p) => !p)}
              aria-expanded={isSortOpen}
              title={isSortOpen ? "Ocultar ordenación" : "Mostrar ordenación"}
            >
              Ordenar por
              <span className={`chevron ${isSortOpen ? "up" : "down"}`} />
            </button>
          </div>

          {isSortOpen && (
            <div className="filtros-panel">
              <div className="options-list">
                <label className="option-item">
                  <input
                    type="radio"
                    name="sort"
                    value="fecha_asc"
                    checked={sortBy === "fecha_asc"}
                    onChange={(e) => setSortBy(e.target.value)}
                  />
                  <span>Fecha (más antiguas primero)</span>
                </label>

                <label className="option-item">
                  <input
                    type="radio"
                    name="sort"
                    value="fecha_desc"
                    checked={sortBy === "fecha_desc"}
                    onChange={(e) => setSortBy(e.target.value)}
                  />
                  <span>Fecha (más recientes primero)</span>
                </label>

                <label className="option-item">
                  <input
                    type="radio"
                    name="sort"
                    value="votos"
                    checked={sortBy === "votos"}
                    onChange={(e) => setSortBy(e.target.value)}
                  />
                  <span>Más votos</span>
                </label>

                <label className="option-item">
                  <input
                    type="radio"
                    name="sort"
                    value="comentarios"
                    checked={sortBy === "comentarios"}
                    onChange={(e) => setSortBy(e.target.value)}
                  />
                  <span>Más comentarios</span>
                </label>
              </div>
            </div>
          )}
        </div>

        <div className="sidebar-section">
          <div className="sidebar-header">
            <button
              className="sidebar-title-btn"
              onClick={() => setIsFiltersOpen((p) => !p)}
              aria-expanded={isFiltersOpen}
              aria-controls="filtros-panel"
              title={isFiltersOpen ? "Ocultar filtros" : "Mostrar filtros"}
            >
              Filtros
              <span className={`chevron ${isFiltersOpen ? "up" : "down"}`} />
            </button>

            <button
              className="btn btn-secondary btn-small btn-filter"
              onClick={resetFilters}
              style={{ marginTop: "10px" }}
              title="Reiniciar filtros"
            >
              Reiniciar filtros
            </button>
          </div>

          {isFiltersOpen && (
            <div id="filtros-panel" className="filtros-panel">
              {/* TEXTO */}
              <div className="filtro-item">
                <label>Texto</label>
                <input
                  className="input"
                  name="texto"
                  onChange={handleFilter}
                  placeholder="Buscar…"
                  value={filters.texto}
                />
              </div>

              {/* MULTIMEDIA (todas las opciones en el mismo select) */}
              <div className="filtro-item">
                <label>Multimedia</label>
                <select
                  className="input"
                  name="media"
                  onChange={handleFilter}
                  value={filters.media}
                >
                  <option value="">Todas</option>
                  <option value="con">Con media</option>
                  <option value="sin">Sin media</option>
                  <option value="videos">Con vídeos</option>
                  <option value="imagenes">Con imágenes</option>
                </select>
              </div>

              {/* ESTADO */}
              <div className="filtro-item">
                <label>Estado</label>
                <select
                  className="input"
                  name="estado"
                  onChange={handleFilter}
                  value={filters.estado}
                >
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
                <select
                  className="input"
                  name="categoria"
                  onChange={handleFilter}
                  value={filters.categoria}
                >
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
                <select
                  className="input"
                  name="distrito"
                  onChange={handleFilter}
                  value={filters.distrito}
                >
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
                  value={filters.autor}
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
                  value={filters.ubicacion}
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
                  value={filters.fechaDesde}
                />
              </div>

              <div className="filtro-item">
                <label>Hasta</label>
                <input
                  type="date"
                  className="input"
                  name="fechaHasta"
                  onChange={handleFilter}
                  value={filters.fechaHasta}
                />
              </div>

              {/* VOTOS */}
              <div className="filtro-item">
                <label>Votos min</label>
                <input
                  type="number"
                  className="input"
                  name="votosMin"
                  min="0"
                  onChange={handleFilter}
                  value={filters.votosMin}
                />
              </div>

              <div className="filtro-item">
                <label>Votos max</label>
                <input
                  type="number"
                  className="input"
                  name="votosMax"
                  min="0"
                  onChange={handleFilter}
                  value={filters.votosMax}
                />
              </div>

              {/* COMENTARIOS */}
              <div className="filtro-item">
                <label>Com. min</label>
                <input
                  type="number"
                  className="input"
                  name="comentariosMin"
                  min="0"
                  onChange={handleFilter}
                  value={filters.comentariosMin}
                />
              </div>

              <div className="filtro-item">
                <label>Com. max</label>
                <input
                  type="number"
                  className="input"
                  name="comentariosMax"
                  min="0"
                  onChange={handleFilter}
                  value={filters.comentariosMax}
                />
              </div>
            </div>
          )}
        </div>
      </aside>

      {/* LISTA DE QUEJAS */}
      <div className="quejas-content">
        <h2 className="quejas-header">
          Listado de Quejas ({filteredQuejas.length})
        </h2>

        <div className="quejas-grid">
          {filteredQuejas.map((q) => (
            <QuejaCard key={q.id} q={q} />
          ))}
        </div>
      </div>
    </div>
  );
}
