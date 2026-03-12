import { useEffect, useState, useMemo } from "react";
import { getQuejas } from "../api/quejas";
import type { Queja } from "../types/queja";
import "../styles/home.css";

import QuejaCard from "../components/QuejaCard";

import {
  useCategorias,
  useDistritos,
} from "../modules/catalogos/catalogos.queries";

import HeroImg from "../assets/icons/ImagenHome1.png";
import CreateQuejaButton from "../components/CreateQuejaButton";
import { useNavigate } from "react-router-dom";

export default function Home() {
  const [quejas, setQuejas] = useState<Queja[]>([]);
  const [loading, setLoading] = useState(true);

  // Filtros básicos de Home (más simples que la página de listado completo)
  const [filters, setFilters] = useState({
    texto: "",
    categoria: "",
    distrito: "",
  });
  const navigate = useNavigate();

  const handleClickVerMas = () => {
    navigate("/quejas");
  };
  // Carga de categorías y distritos (TU SISTEMA REAL)
  const { data: categorias } = useCategorias();
  const { data: distritos } = useDistritos();

  useEffect(() => {
    (async () => {
      const data = await getQuejas();
      setQuejas(data);
      setLoading(false);
    })();
  }, []);

  // Filtrado
  const filteredQuejas = useMemo(() => {
    return quejas
      .filter((q) => {
        if (filters.texto) {
          const text = filters.texto.toLowerCase();
          if (
            !q.titulo.toLowerCase().includes(text) &&
            !q.descripcion.toLowerCase().includes(text)
          ) {
            return false;
          }
        }

        if (filters.categoria && q.categoria_nombre !== filters.categoria)
          return false;

        if (filters.distrito && q.distrito_nombre !== filters.distrito)
          return false;

        return true;
      })
      .sort(
        (a, b) =>
          new Date(b.fecha_creacion_iso).getTime() -
          new Date(a.fecha_creacion_iso).getTime(),
      );
  }, [quejas, filters]);

  const handleFilterChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>,
  ) => {
    setFilters({
      ...filters,
      [e.target.name]: e.target.value,
    });
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

  {loading ? (
    <p>Cargando...</p>
  ) : (
    <div className="quejas-grid-home">
      {filteredQuejas.slice(0, 9).map((q) => (
        <QuejaCard key={q.id} q={q} />
      ))}

      {filteredQuejas.length > 9 && (
        <div className="grid-cta">
          <button className="auth-button" onClick={handleClickVerMas}>
            Ver más
          </button>
        </div>
      )}
    </div>
  )}
</section>
    </div>
  );
}
