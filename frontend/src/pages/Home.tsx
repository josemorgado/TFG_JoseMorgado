import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import { getQuejas } from "../api/quejas";
import { getTopCategorias, getTopDistritos } from "../api/stats";

import type { Queja } from "../types/queja";

import QuejaCard from "../components/QuejaCard";
import CreateQuejaButton from "../components/CreateQuejaButton";
import PageError from "../components/PageError";
import PageInfo from "../components/PageInfo";

import {
  useCategorias,
  useDistritos,
} from "../modules/catalogos/catalogos.queries";

import HeroImg from "../assets/icons/ImagenHome1.png";
import "../styles/home.css";

export default function Home() {
  const navigate = useNavigate();

  const [quejas, setQuejas] = useState<Queja[]>([]);
  const [totalQuejas, setTotalQuejas] = useState(0);
  const [categoriaTop, setCategoriaTop] = useState<string | null>(null);
  const [distritoTop, setDistritoTop] = useState<string | null>(null);

  const [cargando, setCargando] = useState(true);
  const [errorPagina, setErrorPagina] = useState<string | null>(null);

  const [filtros, setFiltros] = useState({
    texto: "",
    categoria: "",
    distrito: "",
  });

  const { data: categorias } = useCategorias();
  const { data: distritos } = useDistritos();

  useEffect(() => {
    (async () => {
      try {
        const datosQuejas = await getQuejas({ page: 1, page_size: 9 });
        setQuejas(datosQuejas.results);
        setTotalQuejas(datosQuejas.count);

        const [topCategorias, topDistritos] = await Promise.all([
          getTopCategorias({ limit: 1 }),
          getTopDistritos({ limit: 1 }),
        ]);

        setCategoriaTop(topCategorias[0]?.nombre ?? "Sin datos");
        setDistritoTop(topDistritos[0]?.nombre ?? "Sin datos");
      } catch {
        setErrorPagina(
          "No se pudo cargar la información principal. Inténtalo más tarde."
        );
      } finally {
        setCargando(false);
      }
    })();
  }, []);


  const quejasVisibles = useMemo(() => {
    if (!Array.isArray(quejas)) return [];

    return quejas.filter((q) => {

      if (filtros.texto) {
        const texto = filtros.texto.toLowerCase();
        if (
          !q.titulo.toLowerCase().includes(texto) &&
          !q.descripcion.toLowerCase().includes(texto)
        ) {
          return false;
        }
      }

      if (
        filtros.categoria &&
        q.categoria_nombre !== filtros.categoria
      ) {
        return false;
      }

      if (
        filtros.distrito &&
        q.distrito_nombre !== filtros.distrito
      ) {
        return false;
      }

      return true;
    });
  }, [quejas, filtros]);

  const handleCambioFiltro = (
    e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
  ) => {
    setFiltros((prev) => ({
      ...prev,
      [e.target.name]: e.target.value,
    }));
  };

  if (cargando) {
    return <PageInfo message="Cargando información principal…" />;
  }

  if (errorPagina) {
    return <PageError message={errorPagina} />;
  }

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
            value={filtros.texto}
            onChange={handleCambioFiltro}
          />

          <select
            name="categoria"
            className="input"
            value={filtros.categoria}
            onChange={handleCambioFiltro}
          >
            <option value="">Todas las categorías</option>

            {Array.isArray(categorias) &&
              categorias.map((c) => (
                <option key={c.id} value={c.nombre}>
                  {c.nombre}
                </option>
              ))}

          </select>

          <select
            name="distrito"
            className="input"
            value={filtros.distrito}
            onChange={handleCambioFiltro}
          >
            <option value="">Todos los distritos</option>

            {Array.isArray(distritos) &&
              distritos.map((d) => (
                <option key={d.id} value={d.nombre}>
                  {d.nombre}
                </option>
              ))}

          </select>
        </div>
      </section>

      <section className="card">
        <h2 className="home-section-title">Últimas quejas</h2>

        {quejasVisibles.length === 0 ? (
          <PageInfo message="No hay quejas para mostrar." />
        ) : (
          <>
            <div className="quejas-grid-home">
              {quejasVisibles.map((q) => (
                <QuejaCard key={q.id} q={q} />
              ))}

              {totalQuejas > 9 && (
                <div className="grid-cta">
                  <button
                    className="auth-button"
                    onClick={() => navigate("/quejas")}
                  >
                    Ver todas
                  </button>
                </div>
              )}
            </div>

            <div className="stats-card-home">
              <div className="stats-item">
                <div className="stats-number">{categoriaTop}</div>
                <div className="stats-label">Categoría más activa</div>
              </div>

              <div className="stats-item">
                <div className="stats-number">{totalQuejas}</div>
                <div className="stats-label">Total de quejas</div>
              </div>

              <div className="stats-item">
                <div className="stats-number">{distritoTop}</div>
                <div className="stats-label">Distrito más activo</div>
              </div>
            </div>
          </>
        )}
      </section>
    </div>
  );
}