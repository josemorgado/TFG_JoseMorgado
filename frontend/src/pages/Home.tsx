import { useEffect, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";

import { getQuejas } from "../api/quejas";
import { getTopCategorias, getTopDistritos } from "../api/stats";

import type { Queja } from "../types/queja";

import QuejaCard from "../components/QuejaCard";
import CreateQuejaButton from "../components/CreateQuejaButton";

import {
  useCategorias,
  useDistritos,
} from "../modules/catalogos/catalogos.queries";

import HeroImg from "../assets/icons/ImagenHome1.png";
import "../styles/home.css";

export default function Home() {
  const navigate = useNavigate();

  const [items, setItems] = useState<Queja[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [totalCount, setTotalCount] = useState(0);
  const [topCategory, setTopCategory] = useState("");
  const [topDistrict, setTopDistrict] = useState("");

  const [filters, setFilters] = useState({
    texto: "",
    categoria: "",
    distrito: "",
  });

  const { data: categorias } = useCategorias();
  const { data: distritos } = useDistritos();

  useEffect(() => {
    (async () => {
      const data = await getQuejas({ page: 1, page_size: 9 });

      setItems(data.results);
      setTotalCount(data.count);

      const topCat = await getTopCategorias({ limit: 1 });
      setTopCategory(topCat.length ? topCat[0].nombre : "Sin datos");

      const topDist = await getTopDistritos({ limit: 1 });
      setTopDistrict(topDist.length ? topDist[0].nombre : "Sin datos");

      setIsLoading(false);
    })();
  }, []);

  const visibleItems = useMemo(() => {
    return items.filter((q) => {
      if (filters.texto) {
        const text = filters.texto.toLowerCase();
        if (
          !q.titulo.toLowerCase().includes(text) &&
          !q.descripcion.toLowerCase().includes(text)
        ) {
          return false;
        }
      }

      if (filters.categoria && q.categoria_nombre !== filters.categoria) {
        return false;
      }

      if (filters.distrito && q.distrito_nombre !== filters.distrito) {
        return false;
      }

      return true;
    });
  }, [items, filters]);

  const handleFilterChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFilters((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  const handleGoToList = () => {
    navigate("/quejas");
  };

  return (
    <div className="home">
      <section className="card hero">
        <div className="hero-grid">
          <div className="hero-titles">
            <h1 className="hero-title">Tu voz cuenta.</h1>
            <p className="hero-subtitle">
              Publica tus quejas y mejora tu ciudad.
            </p>
            <CreateQuejaButton />
          </div>

          <div className="hero-image-wrapper">
            <img
              src={HeroImg}
              alt="Ciudadano megáfono"
              className="hero-image"
            />
          </div>
        </div>
      </section>

      <section className="card home-filtros">
        <div className="filters-row">
          <input
            name="texto"
            className="input"
            placeholder="Buscar…"
            value={filters.texto}
            onChange={handleFilterChange}
          />

          <select
            name="categoria"
            className="input"
            value={filters.categoria}
            onChange={handleFilterChange}
          >
            <option value="">Todas las categorías</option>
            {categorias?.map((c) => (
              <option key={c.id} value={c.nombre}>
                {c.nombre}
              </option>
            ))}
          </select>

          <select
            name="distrito"
            className="input"
            value={filters.distrito}
            onChange={handleFilterChange}
          >
            <option value="">Todos los distritos</option>
            {distritos?.map((d) => (
              <option key={d.id} value={d.nombre}>
                {d.nombre}
              </option>
            ))}
          </select>
        </div>
      </section>

      <section className="card">
        <h2 className="home-section-title">Últimas quejas</h2>

        {isLoading ? (
          <p>Cargando...</p>
        ) : (
          <>
            <div className="quejas-grid-home">
              {visibleItems.map((q) => (
                <QuejaCard key={q.id} q={q} />
              ))}

              {totalCount > 9 && (
                <div className="grid-cta">
                  <button
                    className="auth-button"
                    onClick={handleGoToList}
                  >
                    Ver todas
                  </button>
                </div>
              )}
            </div>

            <div className="stats-card-home">
              <div className="stats-item">
                <div className="stats-number">
                  {topCategory || "Sin datos"}
                </div>
                <div className="stats-label">Categoría más activa</div>
              </div>

              <div className="stats-item">
                <div className="stats-number">{totalCount}</div>
                <div className="stats-label">Total de quejas</div>
              </div>

              <div className="stats-item">
                <div className="stats-number">
                  {topDistrict || "Sin datos"}
                </div>
                <div className="stats-label">Distrito más activo</div>
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  );
}
