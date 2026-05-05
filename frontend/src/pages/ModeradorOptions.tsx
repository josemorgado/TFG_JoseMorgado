import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import {
  fetchCategoriasFull,
  fetchDistritosFull,
  createCategoria,
  createDistrito,
} from "../api/moderacion";

import type { Categoria } from "../types/categoria";
import type { Distrito } from "../types/distrito";

import PageError from "../components/PageError";
import PageInfo from "../components/PageInfo";

export default function ModeradorOptions() {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [distritos, setDistritos] = useState<Distrito[]>([]);

  const [nombreCategoria, setNombreCategoria] = useState("");
  const [descripcionCategoria, setDescripcionCategoria] = useState("");

  const [nombreDistrito, setNombreDistrito] = useState("");
  const [codigoDistrito, setCodigoDistrito] = useState("");

  const [cargando, setCargando] = useState(true);
  const [errorPagina, setErrorPagina] = useState<string | null>(null);
  const [errorFormulario, setErrorFormulario] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [cats, dists] = await Promise.all([
          fetchCategoriasFull(),
          fetchDistritosFull(),
        ]);
        setCategorias(cats);
        setDistritos(dists);
      } catch {
        setErrorPagina(
          "No se pudieron cargar los datos de moderación. Inténtalo más tarde."
        );
      } finally {
        setCargando(false);
      }
    })();
  }, []);

  if (cargando) {
    return <PageInfo message="Cargando datos de moderación..." />;
  }

  if (errorPagina) {
    return <PageError message={errorPagina} />;
  }

  const handleCrearCategoria = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorFormulario(null);

    const nombre = nombreCategoria.trim();
    const descripcion = descripcionCategoria.trim();

    if (!nombre || nombre.length < 3) {
      setErrorFormulario(
        "El nombre de la categoría debe tener al menos 3 caracteres."
      );
      return;
    }

    if (!descripcion || descripcion.length < 10) {
      setErrorFormulario(
        "La descripción debe tener al menos 10 caracteres."
      );
      return;
    }

    try {
      const nueva = await createCategoria({ nombre, descripcion });
      setCategorias((prev) => [...prev, nueva]);
      setNombreCategoria("");
      setDescripcionCategoria("");
    } catch (err: any) {
      const mensaje =
        err?.response?.data?.nombre?.[0] ||
        err?.response?.data?.detail ||
        "No se pudo crear la categoría.";

      setErrorFormulario(mensaje);
    }
  };

  const handleCrearDistrito = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorFormulario(null);

    const nombre = nombreDistrito.trim();
    const codigo = codigoDistrito.trim().toUpperCase();

    if (!nombre || nombre.length < 3) {
      setErrorFormulario(
        "El nombre del distrito debe tener al menos 3 caracteres."
      );
      return;
    }

    if (!codigo || codigo.length < 2) {
      setErrorFormulario(
        "El código del distrito debe tener al menos 2 caracteres."
      );
      return;
    }

    if (codigo.length > 10) {
      setErrorFormulario(
        "El código del distrito no puede tener más de 10 caracteres."
      );
      return;
    }

    try {
      const nuevo = await createDistrito({ nombre, codigo });
      setDistritos((prev) => [...prev, nuevo]);
      setNombreDistrito("");
      setCodigoDistrito("");
    } catch (err: any) {
      const mensaje =
        err?.response?.data?.codigo?.[0] ||
        err?.response?.data?.detail ||
        "No se pudo crear el distrito.";

      setErrorFormulario(mensaje);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card moderador-panel">
        <h1 className="form-title">Panel de moderación</h1>

        {errorFormulario && (
          <p className="form-error">{errorFormulario}</p>
        )}

        {/* ===================== */}
        {/* CATEGORÍAS */}
        {/* ===================== */}
        <section className="moderador-section">
          <h2 className="form-section-title">Categorías</h2>

          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Descripción</th>
                  <th>Activa</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {categorias.map((c) => (
                  <tr key={c.id}>
                    <td>{c.id}</td>
                    <td>{c.nombre}</td>
                    <td>{c.descripcion}</td>
                    <td>{c.activo ? "Sí" : "No"}</td>
                    <td>
                      <Link
                        to={`/moderador/categorias/${c.id}/editar`}
                        className="table-edit-btn"
                      >
                        Editar
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <form
            onSubmit={handleCrearCategoria}
            className="form-container moderador-form"
          >
            <label className="form-label">Nombre</label>
            <input
              className="form-input"
              value={nombreCategoria}
              onChange={(e) => setNombreCategoria(e.target.value)}
            />

            <label className="form-label">Descripción</label>
            <textarea
              className="form-input"
              value={descripcionCategoria}
              onChange={(e) => setDescripcionCategoria(e.target.value)}
            />

            <button type="submit" className="form-button">
              Crear categoría
            </button>
          </form>
        </section>

        {/* ===================== */}
        {/* DISTRITOS */}
        {/* ===================== */}
        <section className="moderador-section">
          <h2 className="form-section-title">Distritos</h2>

          <div className="table-wrapper">
            <table className="data-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Código</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {distritos.map((d) => (
                  <tr key={d.id}>
                    <td>{d.id}</td>
                    <td>{d.nombre}</td>
                    <td>{d.codigo}</td>
                    <td>
                      <Link
                        to={`/moderador/distritos/${d.id}/editar`}
                        className="table-edit-btn"
                      >
                        Editar
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <form
            onSubmit={handleCrearDistrito}
            className="form-container moderador-form"
          >
            <label className="form-label">Nombre</label>
            <input
              className="form-input"
              value={nombreDistrito}
              onChange={(e) => setNombreDistrito(e.target.value)}
            />

            <label className="form-label">Código</label>
            <input
              className="form-input"
              value={codigoDistrito}
              onChange={(e) =>
                setCodigoDistrito(e.target.value.toUpperCase())
              }
            />

            <button type="submit" className="form-button">
              Crear distrito
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}