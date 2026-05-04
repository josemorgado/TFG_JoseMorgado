import { useEffect, useState, useRef } from "react";
import { useSearchParams } from "react-router-dom";

import { getQuejasFiltered } from "../api/quejas";
import type { Queja } from "../types/queja";

import "../styles/QuejasList.css";
import QuejaCard from "../components/QuejaCard";

import type { FiltersShape, SortBy } from "../types/filters";
import { defaultFilters } from "../types/filters";
import {
  loadListState,
  saveListState,
  clearListState,
} from "../utils/storage";

import {
  useCategorias,
  useDistritos,
} from "../modules/catalogos/catalogos.queries";

export default function QuejasList() {
  const topRef = useRef<HTMLDivElement>(null);
  const [searchParams] = useSearchParams();

  const saved = loadListState<FiltersShape, SortBy>();

  const [items, setItems] = useState<Queja[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);

  const [filters, setFilters] = useState<FiltersShape>(
    saved?.filters ?? defaultFilters
  );
  const [sortBy, setSortBy] = useState<SortBy>(saved?.sortBy ?? "");

  const [isFiltersOpen, setIsFiltersOpen] = useState(
    saved?.isFiltersOpen ?? false
  );
  const [isSortOpen, setIsSortOpen] = useState(
    saved?.isSortOpen ?? false
  );

  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 12;

  const [textoDraft, setTextoDraft] = useState(filters.texto);
  const [autorDraft, setAutorDraft] = useState(filters.autor);
  const [ubicacionDraft, setUbicacionDraft] = useState(filters.ubicacion);

  const { data: categorias, isLoading: catLoading, error: catError } =
    useCategorias();
  const { data: distritos, isLoading: disLoading, error: disError } =
    useDistritos();

  const buildApiFilters = (f: FiltersShape) => ({
    ...f,
    votosMin: f.votosMin ? Number(f.votosMin) : undefined,
    votosMax: f.votosMax ? Number(f.votosMax) : undefined,
    comentariosMin: f.comentariosMin
      ? Number(f.comentariosMin)
      : undefined,
    comentariosMax: f.comentariosMax
      ? Number(f.comentariosMax)
      : undefined,
  });

  const handleFilterChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
  };

  const handleEnterApply = (
    e: React.KeyboardEvent<HTMLInputElement>,
    field: "texto" | "autor" | "ubicacion"
  ) => {
    if (e.key === "Enter") {
      setFilters((prev) => ({
        ...prev,
        ...(field === "texto" && { texto: textoDraft }),
        ...(field === "autor" && { autor: autorDraft }),
        ...(field === "ubicacion" && { ubicacion: ubicacionDraft }),
      }));
    }
  };

  useEffect(() => {
    setTextoDraft(filters.texto);
    setAutorDraft(filters.autor);
    setUbicacionDraft(filters.ubicacion);
  }, [filters.texto, filters.autor, filters.ubicacion]);

  useEffect(() => {
    const categoria = searchParams.get("categoria");
    const distrito = searchParams.get("distrito");
    const estado = searchParams.get("estado");

    if (categoria || distrito || estado) {
      clearListState();
      setFilters({
        ...defaultFilters,
        categoria: categoria ?? "",
        distrito: distrito ?? "",
        estado: estado ?? "",
      });
      setSortBy("");
      setIsFiltersOpen(true);
      setIsSortOpen(false);
      setCurrentPage(1);
    }
  }, []);

  useEffect(() => {
    saveListState<FiltersShape, SortBy>({
      filters,
      sortBy,
      isFiltersOpen,
      isSortOpen,
    });
    setCurrentPage(1);
  }, [filters, sortBy, isFiltersOpen, isSortOpen]);

  useEffect(() => {
    setIsLoading(true);

    getQuejasFiltered({
      page: currentPage,
      page_size: itemsPerPage,
      ordering: sortBy || undefined,
      ...buildApiFilters(filters),
    }).then((data) => {
      setItems(data.results);
      setTotalCount(data.count);
      setIsLoading(false);
    });
  }, [filters, sortBy, currentPage]);

  useEffect(() => {
    topRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [currentPage]);

  const totalPages = Math.ceil(totalCount / itemsPerPage);

  const resetFilters = () => {
    setFilters(defaultFilters);
    setIsFiltersOpen(false);
    clearListState();
  };

  const resetSort = () => {
    setSortBy("");
    setIsSortOpen(false);
    clearListState();
  };

  if (isLoading) return <p className="loading">Cargando...</p>;

  return (
    <div ref={topRef} className="quejas-layout">
      <aside className={`sidebar-filtros ${isFiltersOpen ? "open" : "closed"}`}>
        <div className="sidebar-section">
          <div className="sidebar-header">
            <button
              className="sidebar-title-btn"
              onClick={() => setIsSortOpen((p) => !p)}
            >
              Ordenar por
              <span className={`chevron ${isSortOpen ? "up" : "down"}`} />
            </button>
            <button
              className="btn btn-secondary btn-small btn-filter"
              onClick={resetSort}
              style={{ marginTop: "10px" }}
            >
              Reiniciar
            </button>
          </div>

          {isSortOpen && (
            <div className="filtros-panel options-list">
              {[
                ["fecha_desc", "Fecha (más recientes primero)"],
                ["fecha_asc", "Fecha (más antiguas primero)"],
                ["votos", "Más votos"],
                ["comentarios", "Más comentarios"],
                ["respuestas", "Más respuestas"],
              ].map(([value, label]) => (
                <label className="option-item" key={value}>
                  <input
                    type="radio"
                    value={value}
                    checked={sortBy === value}
                    onChange={(e) =>
                      setSortBy(e.target.value as SortBy)
                    }
                  />
                  <span>{label}</span>
                </label>
              ))}
            </div>
          )}
        </div>

        <div className="sidebar-section">
          <div className="sidebar-header">
            <button
              className="sidebar-title-btn"
              onClick={() => setIsFiltersOpen((p) => !p)}
            >
              Filtros
              <span className={`chevron ${isFiltersOpen ? "up" : "down"}`} />
            </button>
            <button
              className="btn btn-secondary btn-small btn-filter"
              onClick={resetFilters}
              style={{ marginTop: "10px" }}
            >
              Reiniciar
            </button>
          </div>

          {isFiltersOpen && (
            <div className="filtros-panel">
              <div className="filtro-item">
                <label>Texto</label>
                <input
                  className="input"
                  placeholder="Pulsa Enter para buscar"
                  value={textoDraft}
                  onChange={(e) => setTextoDraft(e.target.value)}
                  onKeyDown={(e) => handleEnterApply(e, "texto")}
                />
              </div>
              <div className="filtro-item">
                <label>Estado</label>
                <select
                  className="input"
                  name="estado"
                  value={filters.estado}
                  onChange={handleFilterChange}
                >
                  <option value="">Todos</option>
                  <option value="PEN">Pendiente</option>
                  <option value="ENP">En progreso</option>
                  <option value="RES">Resuelta</option>
                  <option value="REC">Rechazada</option>
                </select>
              </div>

              <div className="filtro-item">
                <label>Categoría</label>
                <select
                  className="input"
                  name="categoria"
                  value={filters.categoria}
                  onChange={handleFilterChange}
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

              <div className="filtro-item">
                <label>Distrito</label>
                <select
                  className="input"
                  name="distrito"
                  value={filters.distrito}
                  onChange={handleFilterChange}
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

              <div className="filtro-item">
                <label>Autor</label>
                <input
                  className="input"
                  placeholder="Pulsa Enter para buscar"
                  value={autorDraft}
                  onChange={(e) => setAutorDraft(e.target.value)}
                  onKeyDown={(e) => handleEnterApply(e, "autor")}
                />
              </div>

              <div className="filtro-item">
                <label>Ubicación</label>
                <input
                  className="input"
                  placeholder="Pulsa Enter para buscar"
                  value={ubicacionDraft}
                  onChange={(e) => setUbicacionDraft(e.target.value)}
                  onKeyDown={(e) => handleEnterApply(e, "ubicacion")}
                />
              </div>

              <div className="filtro-item">
                <label>Desde</label>
                <input
                  type="date"
                  className="input"
                  name="fechaDesde"
                  value={filters.fechaDesde}
                  onChange={handleFilterChange}
                />
              </div>

              <div className="filtro-item">
                <label>Hasta</label>
                <input
                  type="date"
                  className="input"
                  name="fechaHasta"
                  value={filters.fechaHasta}
                  onChange={handleFilterChange}
                />
              </div>

              <div className="filtro-item">
                <label>Votos min</label>
                <input
                  type="number"
                  className="input"
                  name="votosMin"
                  value={filters.votosMin}
                  onChange={handleFilterChange}
                />
              </div>

              <div className="filtro-item">
                <label>Votos max</label>
                <input
                  type="number"
                  className="input"
                  name="votosMax"
                  value={filters.votosMax}
                  onChange={handleFilterChange}
                />
              </div>

              <div className="filtro-item">
                <label>Com. min</label>
                <input
                  type="number"
                  className="input"
                  name="comentariosMin"
                  value={filters.comentariosMin}
                  onChange={handleFilterChange}
                />
              </div>

              <div className="filtro-item">
                <label>Com. max</label>
                <input
                  type="number"
                  className="input"
                  name="comentariosMax"
                  value={filters.comentariosMax}
                  onChange={handleFilterChange}
                />
              </div>
            </div>
          )}
        </div>
      </aside>

      <div className="quejas-content">
        <h2 className="quejas-header">
          Listado de Quejas ({totalCount})
        </h2>

        <div className="quejas-grid">
          {items.map((q) => (
            <QuejaCard key={q.id} q={q} />
          ))}
        </div>

        {totalPages > 1 && (
          <div className="pagination">
            <button
              className="btn"
              disabled={currentPage === 1}
              onClick={() => setCurrentPage((p) => p - 1)}
            >
              ← Anterior
            </button>
            <span className="page-indicator">
              {currentPage} / {totalPages}
            </span>
            <button
              className="btn"
              disabled={currentPage === totalPages}
              onClick={() => setCurrentPage((p) => p + 1)}
            >
              Siguiente →
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
