import { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import axiosInstance from "../utils/axios";
import axios from "axios";
import { useAuth } from "../context/AuthContext";
import type { Queja } from "../types/queja";
import {config} from "../config"
/** Tipos mínimos para selects */
interface Categoria {
  id: number;
  nombre: string;
}
interface Distrito {
  id: number;
  nombre: string;
}

const LIMITE_UPDATE_TIME = config.LIMIT_TIME_UPDATE_QUEJA;//declarado en config.ts

export default function QuejaUpdate() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Datos base
  const [queja, setQueja] = useState<Queja | null>(null);
  const [categorias, setCategorias] = useState<Categoria[]>([]);
  const [distritos, setDistritos] = useState<Distrito[]>([]);

  // Form state
  const [titulo, setTitulo] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [categoria, setCategoria] = useState<number | "">("");
  const [distrito, setDistrito] = useState<number | "">("");
  const [ubicacion, setUbicacion] = useState("");

  // Errores del form (cliente/servidor)
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // --------- Guards de acceso (autor + 5 minutos) ----------
  const puedeActualizar = useMemo(() => {
    if (!queja?.fecha_creacion_iso) return false;
    if (!(user && queja.autor === user.id)) return false;

    const fecha = new Date(queja.fecha_creacion_iso);
    const ahora = new Date();
    const diffMin = (ahora.getTime() - fecha.getTime()) / 60000;
    return diffMin <= LIMITE_UPDATE_TIME;
  }, [queja, user]);

  // --------- Carga inicial ----------
  useEffect(() => {
    let cancel = false;
    async function fetchAll() {
      if (!id) return;
      try {
        setLoading(true);
        setError(null);

        // Carga en paralelo
        const [quejaRes, catsRes, distRes] = await Promise.all([
          axiosInstance.get<Queja>(`/quejas/${id}/`),
          axiosInstance.get<Categoria[]>(`/categorias/`),
          axiosInstance.get<Distrito[]>(`/distritos/`),
        ]);

        if (cancel) return;

        setQueja(quejaRes.data);
        setCategorias(catsRes.data);
        setDistritos(distRes.data);

        // Inicializa form
        setTitulo(quejaRes.data.titulo || "");
        setDescripcion(quejaRes.data.descripcion || "");
        setCategoria(quejaRes.data.categoria ?? "");
        setDistrito(quejaRes.data.distrito ?? "");
        setUbicacion(quejaRes.data.ubicacion || "");
      } catch (err) {
        console.error(err);
        setError("No se pudo cargar la queja o los catálogos.");
      } finally {
        if (!cancel) setLoading(false);
      }
    }

    fetchAll();
    return () => {
      cancel = true;
    };
  }, [id]);

  // --------- Validación cliente ----------
  function validateClient(): boolean {
    const errs: Record<string, string> = {};

    const t = titulo.trim();
    const d = descripcion.trim();

    if (t.length < 5 || t.length > 200) {
      errs.titulo = "El título debe tener entre 5 y 200 caracteres.";
    }
    if (d.length < 10 || d.length > 5000) {
      errs.descripcion =
        "La descripción debe tener entre 10 y 5000 caracteres.";
    }
    if (!categoria) {
      errs.categoria = "Selecciona una categoría.";
    }
    if (!distrito) {
      errs.distrito = "Selecciona un distrito.";
    }

    setFormErrors(errs);
    return Object.keys(errs).length === 0;
  }

  // --------- Submit ----------
  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!id) return;

    // Guardias en cliente
    if (!queja) return;
    if (!puedeActualizar) {
      setError(
        "No puedes actualizar esta queja (autor o tiempo mínimo no cumplido).",
      );
      return;
    }
    if (!validateClient()) return;

    try {
      setSaving(true);
      setError(null);

      const payload = {
        titulo: titulo.trim(),
        descripcion: descripcion.trim(),
        categoria: Number(categoria),
        distrito: Number(distrito),
        ubicacion: ubicacion.trim() || null,
      };

      await axiosInstance.put(`/quejas/${id}/update/`, payload);
      navigate(`/quejas/${id}`);
    } catch (err) {
      if (axios.isAxiosError(err)) {
        const data = err.response?.data as any;
        const apiErrs: Record<string, string> = {};
        if (data) {
          Object.keys(data).forEach((k) => {
            const v = data[k];
            if (Array.isArray(v)) apiErrs[k] = v.join(" ");
            else if (typeof v === "string") apiErrs[k] = v;
          });
        }
        setFormErrors((prev) => ({ ...prev, ...apiErrs }));
        setError(apiErrs.non_field_errors || "No se pudo actualizar la queja.");
      } else {
        setError("Error inesperado al actualizar.");
      }
    } finally {
      setSaving(false);
    }
  }

  // --------- Estados de carga/errores ----------
  if (loading) {
    return (
      <div className="form-page">
        <div className="form-card">
          <h1 className="form-title">Editar queja</h1>
          <div className="form-error">Cargando…</div>
        </div>
      </div>
    );
  }

  if (error && !queja) {
    return (
      <div className="form-page">
        <div className="form-card">
          <h1 className="form-title">Editar queja</h1>
          <div className="form-error">{error}</div>
          <div className="form-link-center">
            <Link to={`/quejas/${id}`} className="btn btn-secondary">
              Volver
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // Si no cumple guardias, mostramos mensaje y salimos
  const noAutor = user && queja && queja.autor !== user.id;
  if (queja && (!puedeActualizar || noAutor)) {
    return (
      <div className="form-page">
        <div className="form-card">
          <h1 className="form-title">Editar queja</h1>
          <div className="form-error" style={{ textAlign: "center" }}>
            {noAutor
              ? "Solo el autor puede editar esta queja."
              : `Solo se puede editar a partir de ${LIMITE_UPDATE_TIME} minutos tras su creación.`}
          </div>
          <div className="form-link-center">
            <Link to={`/quejas/${id}`} className="btn btn-secondary">
              Volver
            </Link>
          </div>
        </div>
      </div>
    );
  }

  // --------- Formulario ----------
  return (
    <div className="form-page">
      <div className="form-card">
        <h1 className="form-title">Editar queja</h1>

        <form className="form-container" onSubmit={handleSubmit} noValidate>
          {/* Título */}
          <label className="form-label" htmlFor="titulo">
            Título
          </label>
          <input
            id="titulo"
            type="text"
            className="form-input"
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
            placeholder="Título breve y descriptivo…"
          />
          {formErrors.titulo && (
            <div className="form-error">{formErrors.titulo}</div>
          )}

          {/* Descripción */}
          <label className="form-label" htmlFor="descripcion">
            Descripción
          </label>
          <textarea
            id="descripcion"
            className="form-input"
            value={descripcion}
            rows={5}
            onChange={(e) => setDescripcion(e.target.value)}
            placeholder="Describe la incidencia con detalle…"
          />
          {formErrors.descripcion && (
            <div className="form-error">{formErrors.descripcion}</div>
          )}

          {/* Categoría */}
          <label className="form-label" htmlFor="categoria">
            Categoría
          </label>
          <select
            id="categoria"
            className="form-input"
            value={categoria}
            onChange={(e) =>
              setCategoria(e.target.value ? Number(e.target.value) : "")
            }
          >
            <option value="">Selecciona una categoría…</option>
            {categorias.map((c) => (
              <option key={c.id} value={c.id}>
                {c.nombre}
              </option>
            ))}
          </select>
          {formErrors.categoria && (
            <div className="form-error">{formErrors.categoria}</div>
          )}

          {/* Distrito */}
          <label className="form-label" htmlFor="distrito">
            Distrito
          </label>
          <select
            id="distrito"
            className="form-input"
            value={distrito}
            onChange={(e) =>
              setDistrito(e.target.value ? Number(e.target.value) : "")
            }
          >
            <option value="">Selecciona un distrito…</option>
            {distritos.map((d) => (
              <option key={d.id} value={d.id}>
                {d.nombre}
              </option>
            ))}
          </select>
          {formErrors.distrito && (
            <div className="form-error">{formErrors.distrito}</div>
          )}

          {/* Ubicación (opcional) */}
          <label className="form-label" htmlFor="ubicacion">
            Ubicación (opcional)
          </label>
          <input
            id="ubicacion"
            type="text"
            className="form-input"
            value={ubicacion}
            onChange={(e) => setUbicacion(e.target.value)}
            placeholder="Ej. Calle Falsa 123…"
          />
          {formErrors.ubicacion && (
            <div className="form-error">{formErrors.ubicacion}</div>
          )}

          {/* Info de estado (solo lectura) */}
          {queja?.estado && (
            <>
              <div className="form-section-title">Estado actual</div>
              <input
                className="form-input"
                value={queja.estado}
                disabled
                aria-label="Estado actual"
              />
            </>
          )}

          {/* Acciones */}
          <button className="btn btn-secondary form-button" onClick={()=>navigate(`/quejas/${id}`)} >
            Descartar cambios
          </button>
          <button
            type="submit"
            className="btn btn-primary form-button"
            disabled={saving}
          >
            {saving ? "Guardando…" : "Guardar cambios"}
          </button>

          {/* Error general */}
          {error && <div className="form-error">{error}</div>}

          {/* Ayuda */}
          {queja?.fecha_creacion_iso && (
            <div
              className="form-link-center"
              style={{ color: "var(--color-primary)" }}
            >
              Creada el {new Date(queja.fecha_creacion_iso).toLocaleString()}
            </div>
          )}
        </form>
      </div>
    </div>
  );
}
