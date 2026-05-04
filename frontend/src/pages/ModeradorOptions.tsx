import { useEffect, useState } from "react";
import {
  fetchCategoriasFull,
  fetchDistritosFull,
  createCategoria,
  createDistrito,
} from "../api/moderacion";
import type { Categoria } from "../types/categoria";
import type { Distrito } from "../types/distrito";
import { Link } from "react-router-dom";

export default function ModeradorOptions() {
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [distritos, setDistritos] = useState<Distrito[]>([]);

  const [catNombre, setCatNombre] = useState("");
  const [catDescripcion, setCatDescripcion] = useState("");

  const [distNombre, setDistNombre] = useState("");
  const [distCodigo, setDistCodigo] = useState("");

  const [error, setError] = useState<string | null>(null);

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
        setError("Error cargando datos de moderación");
      }
    })();
  }, []);

  const handleCreateCategoria = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const nueva = await createCategoria({
        nombre: catNombre,
        descripcion: catDescripcion,
      });
      setCategorias((prev) => [...prev, nueva]);
      setCatNombre("");
      setCatDescripcion("");
    } catch {
      setError("No se pudo crear la categoría");
    }
  };

  const handleCreateDistrito = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const nuevo = await createDistrito({
        nombre: distNombre,
        codigo: distCodigo,
      });
      setDistritos((prev) => [...prev, nuevo]);
      setDistNombre("");
      setDistCodigo("");
    } catch {
      setError("No se pudo crear el distrito");
    }
  };

  return (
    <div className="form-page">
      <div className="form-card moderador-panel">
        <h1 className="form-title">Panel de moderación</h1>

        {error && <p className="form-error">{error}</p>}

        {/* ===================== */}
        {/* CATEGORÍAS */}
        {/* ===================== */}
        <section className="moderador-section">
          <h2 className="form-section-title">Categorías</h2>

<div className="table-wrapper">
  <table className="data-table">
    <thead>
      <tr>
        <th className="col-id">ID</th>
        <th className="col-nombre">Nombre</th>
        <th className="col-descripcion">Descripción</th>
        <th className="col-activa">Activa</th>
        <th className="actions-cell">Acciones</th>
      </tr>
    </thead>
    <tbody>
      {categorias.map((c) => (
        <tr key={c.id}>
          <td className="col-id">{c.id}</td>
          <td className="col-nombre">{c.nombre}</td>
          <td className="col-descripcion">{c.descripcion}</td>
          <td className="col-activa">{c.activo ? "Sí" : "No"}</td>
          <td className="actions-cell">
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
            onSubmit={handleCreateCategoria}
            className="form-container moderador-form"
          >
            <label className="form-label">Nombre</label>
            <input
              className="form-input"
              value={catNombre}
              onChange={(e) => setCatNombre(e.target.value)}
              required
            />

            <label className="form-label">Descripción</label>
            <textarea
              className="form-input"
              value={catDescripcion}
              onChange={(e) => setCatDescripcion(e.target.value)}
              required
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
                  <th className="col-id">ID</th>
                  <th className="col-nombre">Nombre</th>
                  <th className="col-codigo">Código</th>
                  <th className="actions-cell">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {distritos.map((d) => (
                  <tr key={d.id}>
                    <td className="col-id">{d.id}</td>
                    <td className="col-nombre">{d.nombre}</td>
                    <td className="col-codigo code-cell">{d.codigo}</td>
                    <td className="actions-cell">
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
            onSubmit={handleCreateDistrito}
            className="form-container moderador-form"
          >
            <label className="form-label">Nombre</label>
            <input
              className="form-input"
              value={distNombre}
              onChange={(e) => setDistNombre(e.target.value)}
              required
            />

            <label className="form-label">Código</label>
            <input
              className="form-input"
              value={distCodigo}
              onChange={(e) => setDistCodigo(e.target.value)}
              required
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