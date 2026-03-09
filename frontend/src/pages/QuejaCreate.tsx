import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { crearImagenQueja } from "../api/imagenes";
import { createQuejaRequest } from "../api/quejas";
import { crearVideoQueja } from "../api/videos";
import {
  useCategorias,
  useDistritos,
} from "../modules/catalogos/catalogos.queries";

import "../styles/form-layout.css";

const QuejaCreate: React.FC = () => {
  const navigate = useNavigate();

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

  const [form, setForm] = useState({
    titulo: "",
    descripcion: "",
    categoria: "",
    distrito: "",
    ubicacion: "",
    imagenes: [] as File[],
    videos: [] as File[],
  });

  const [error, setError] = useState<string | null>(null);
  const [errorImagenes, setErrorImagenes] = useState<string | null>(null);
  const [errorVideos, setErrorVideos] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validaciones
    if (!form.titulo.trim() || form.titulo.trim().length < 5) {
      setError("El título debe tener mínimo 5 caracteres");
      return;
    }
    if (!form.descripcion.trim() || form.descripcion.trim().length < 10) {
      setError("La descripción debe tener mínimo 10 caracteres");
      return;
    }
    if (!form.categoria) {
      setError("Debes seleccionar una categoría");
      return;
    }
    if (!form.distrito) {
      setError("Debes seleccionar un distrito");
      return;
    }
    if (form.imagenes.length > 5) {
      setError("Solo puedes subir un máximo de 5 imágenes.");
      return;
    }
    if (form.videos.length > 1) {
      setError("Solo puedes subir un máximo de 1 video.");
      return;
    }

    const formData = new FormData();
    formData.append("titulo", form.titulo.trim());
    formData.append("descripcion", form.descripcion.trim());
    formData.append("categoria", String(Number(form.categoria)));
    formData.append("distrito", String(Number(form.distrito)));

    if (form.ubicacion.trim()) {
      formData.append("ubicacion", form.ubicacion.trim());
    }

    try {
      const res = await createQuejaRequest(formData);
      const id = res?.data?.id;
      const ctId = res?.data?.content_type;

      for (const file of form.imagenes) {
        await crearImagenQueja(ctId, id, file);
      }
      for (const file of form.videos) {
        await crearVideoQueja(ctId, id, file);
      }

      navigate(id ? `/quejas/${id}` : "/quejas");
    } catch (err: any) {
      if (err.response?.data) {
        const data = err.response.data;
        const messages: string[] = [];

        if (typeof data === "string") {
          setError(data);
          return;
        }

        if (data.titulo) messages.push(`Título: ${data.titulo.join(" ")}`);
        if (data.descripcion)
          messages.push(`Descripción: ${data.descripcion.join(" ")}`);
        if (data.categoria)
          messages.push(`Categoría: ${data.categoria.join(" ")}`);
        if (data.distrito)
          messages.push(`Distrito: ${data.distrito.join(" ")}`);
        if (data.ubicacion)
          messages.push(`Ubicación: ${data.ubicacion.join(" ")}`);

        setError(messages.join(" • ") || "Error al crear la queja");
      } else {
        setError("No se pudo conectar con el servidor.");
      }
    }
  };

  return (
    <div className="form-page">
      <div className="form-card">
        <h1 className="form-title">Crear Queja</h1>

        <form onSubmit={handleSubmit} className="form-container">
          {/* TÍTULO */}
          <label className="form-label">Título</label>
          <input
            className="form-input"
            type="text"
            value={form.titulo}
            onChange={(e) => setForm({ ...form, titulo: e.target.value })}
          />

          {/* DESCRIPCIÓN */}
          <label className="form-label">Descripción</label>
          <textarea
            className="form-input"
            value={form.descripcion}
            onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
            rows={4}
          />

          {/* CATEGORÍA */}
          <label className="form-label">Categoría</label>
          <select
            className="form-input"
            value={form.categoria}
            onChange={(e) => setForm({ ...form, categoria: e.target.value })}
            disabled={catLoading || !!catError}
          >
            <option value="" disabled>
              {catLoading ? "Cargando categorías…" : "Selecciona una categoría"}
            </option>
            {catError && <option disabled>⚠️ Error cargando categorías</option>}
            {categorias?.map((c) => (
              <option key={c.id} value={String(c.id)}>
                {c.nombre}
              </option>
            ))}
          </select>

          {/* DISTRITO */}
          <label className="form-label">Distrito</label>
          <select
            className="form-input"
            value={form.distrito}
            onChange={(e) => setForm({ ...form, distrito: e.target.value })}
            disabled={disLoading || !!disError}
          >
            <option value="" disabled>
              {disLoading ? "Cargando distritos…" : "Selecciona un distrito"}
            </option>
            {disError && <option disabled>⚠️ Error cargando distritos</option>}
            {distritos?.map((d) => (
              <option key={d.id} value={String(d.id)}>
                {d.nombre}
              </option>
            ))}
          </select>

          {/* UBICACIÓN */}
          <label className="form-label">Ubicación (opcional)</label>
          <input
            className="form-input"
            type="text"
            value={form.ubicacion}
            onChange={(e) => setForm({ ...form, ubicacion: e.target.value })}
          />

          {/* IMÁGENES */}
          <label className="form-label">Imágenes (máx 5)</label>
          <input
            className="form-input"
            type="file"
            accept="image/*"
            multiple
            onChange={(e) => {
              const files = Array.from(e.target.files || []);
              if (files.length > 5) {
                setErrorImagenes("El máximo de imágenes es 5.");
                return;
              }
              setErrorImagenes(null);
              setForm({ ...form, imagenes: files });
            }}
          />
          {errorImagenes && <p className="form-error">{errorImagenes}</p>}

          {/* VIDEOS */}
          <label className="form-label">Video (máx 1)</label>
          <input
            className="form-input"
            type="file"
            accept="video/*"
            multiple
            onChange={(e) => {
              const files = Array.from(e.target.files || []);
              if (files.length > 1) {
                setErrorVideos("Solo se permite 1 video.");
                return;
              }
              setErrorVideos(null);
              setForm({ ...form, videos: files });
            }}
          />
          {errorVideos && <p className="form-error">{errorVideos}</p>}

          {/* BOTÓN FINAL */}
          <button
            type="submit"
            className="btn btn-primary form-button"
            disabled={!!errorImagenes || !!errorVideos}
          >
            Crear Queja
          </button>

          {error && <p className="form-error">{error}</p>}
        </form>
      </div>
    </div>
  );
};

export default QuejaCreate;
