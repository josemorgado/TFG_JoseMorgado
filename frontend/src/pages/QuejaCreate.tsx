import { useState } from "react";
import { useNavigate } from "react-router-dom";

import { createQuejaRequest } from "../api/quejas";
import { crearImagenQueja } from "../api/imagenes";
import { crearVideoQueja } from "../api/videos";

import {
  useCategorias,
  useDistritos,
} from "../modules/catalogos/catalogos.queries";

import "../styles/form-layout.css";

export default function QuejaCreate() {
  const navigate = useNavigate();

  const {
    data: categorias,
    isLoading: categoriasCargando,
    error: errorCategorias,
  } = useCategorias();

  const {
    data: distritos,
    isLoading: distritosCargando,
    error: errorDistritos,
  } = useDistritos();

  const [formulario, setFormulario] = useState({
    titulo: "",
    descripcion: "",
    categoria: "",
    distrito: "",
    ubicacion: "",
    imagenes: [] as File[],
    videos: [] as File[],
  });

  const [errorFormulario, setErrorFormulario] = useState<string | null>(null);
  const [errorImagenes, setErrorImagenes] = useState<string | null>(null);
  const [errorVideos, setErrorVideos] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorFormulario(null);

    const titulo = formulario.titulo.trim();
    const descripcion = formulario.descripcion.trim();

    if (!titulo || titulo.length < 5) {
      setErrorFormulario("El título debe tener al menos 5 caracteres.");
      return;
    }

    if (!descripcion || descripcion.length < 10) {
      setErrorFormulario("La descripción debe tener al menos 10 caracteres.");
      return;
    }

    if (!formulario.categoria) {
      setErrorFormulario("Debes seleccionar una categoría.");
      return;
    }

    if (!formulario.distrito) {
      setErrorFormulario("Debes seleccionar un distrito.");
      return;
    }

    if (formulario.imagenes.length > 5) {
      setErrorFormulario("Solo puedes subir un máximo de 5 imágenes.");
      return;
    }

    if (formulario.videos.length > 1) {
      setErrorFormulario("Solo puedes subir un máximo de 1 vídeo.");
      return;
    }

    const datos = new FormData();
    datos.append("titulo", titulo);
    datos.append("descripcion", descripcion);
    datos.append("categoria", String(Number(formulario.categoria)));
    datos.append("distrito", String(Number(formulario.distrito)));

    if (formulario.ubicacion.trim()) {
      datos.append("ubicacion", formulario.ubicacion.trim());
    }

    try {
      setEnviando(true);

      const respuesta = await createQuejaRequest(datos);
      const idQueja = respuesta?.data?.id;
      const contentType = respuesta?.data?.content_type;

      for (const imagen of formulario.imagenes) {
        await crearImagenQueja(contentType, idQueja, imagen);
      }

      for (const video of formulario.videos) {
        await crearVideoQueja(contentType, idQueja, video);
      }

      navigate(idQueja ? `/quejas/${idQueja}` : "/quejas");
    } catch (err: any) {
      if (err?.response?.data) {
        const data = err.response.data;
        const mensajes: string[] = [];

        if (typeof data === "string") {
          setErrorFormulario(data);
          return;
        }

        if (data.titulo) mensajes.push(`Título: ${data.titulo.join(" ")}`);
        if (data.descripcion)
          mensajes.push(`Descripción: ${data.descripcion.join(" ")}`);
        if (data.categoria)
          mensajes.push(`Categoría: ${data.categoria.join(" ")}`);
        if (data.distrito)
          mensajes.push(`Distrito: ${data.distrito.join(" ")}`);
        if (data.ubicacion)
          mensajes.push(`Ubicación: ${data.ubicacion.join(" ")}`);

        setErrorFormulario(
          mensajes.join(" · ") || "Error al crear la queja."
        );
      } else {
        setErrorFormulario("No se pudo conectar con el servidor.");
      }
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="form-page">
      <div className="form-card">
        <h1 className="form-title">Crear queja</h1>

        <form onSubmit={handleSubmit} className="form-container">
          <label className="form-label">Título</label>
          <input
            className="form-input"
            value={formulario.titulo}
            onChange={(e) =>
              setFormulario({ ...formulario, titulo: e.target.value })
            }
          />

          <label className="form-label">Descripción</label>
          <textarea
            className="form-input"
            rows={4}
            value={formulario.descripcion}
            onChange={(e) =>
              setFormulario({ ...formulario, descripcion: e.target.value })
            }
          />

          <label className="form-label">Categoría</label>
          <select
            className="form-input"
            value={formulario.categoria}
            onChange={(e) =>
              setFormulario({ ...formulario, categoria: e.target.value })
            }
            disabled={categoriasCargando || !!errorCategorias}
          >
            <option value="" disabled>
              {categoriasCargando
                ? "Cargando categorías…"
                : "Selecciona una categoría"}
            </option>
            {errorCategorias && (
              <option disabled>⚠️ Error cargando categorías</option>
            )}
            {categorias?.map((c) => (
              <option key={c.id} value={String(c.id)}>
                {c.nombre}
              </option>
            ))}
          </select>

          <label className="form-label">Distrito</label>
          <select
            className="form-input"
            value={formulario.distrito}
            onChange={(e) =>
              setFormulario({ ...formulario, distrito: e.target.value })
            }
            disabled={distritosCargando || !!errorDistritos}
          >
            <option value="" disabled>
              {distritosCargando
                ? "Cargando distritos…"
                : "Selecciona un distrito"}
            </option>
            {errorDistritos && (
              <option disabled>⚠️ Error cargando distritos</option>
            )}
            {distritos?.map((d) => (
              <option key={d.id} value={String(d.id)}>
                {d.nombre}
              </option>
            ))}
          </select>

          <label className="form-label">Ubicación (opcional)</label>
          <input
            className="form-input"
            value={formulario.ubicacion}
            onChange={(e) =>
              setFormulario({ ...formulario, ubicacion: e.target.value })
            }
          />

          <label className="form-label">Imágenes (máx. 5)</label>
          <input
            className="form-input"
            type="file"
            accept="image/*"
            multiple
            onChange={(e) => {
              const archivos = Array.from(e.target.files || []);
              if (archivos.length > 5) {
                setErrorImagenes("El máximo permitido es 5 imágenes.");
                return;
              }
              setErrorImagenes(null);
              setFormulario({ ...formulario, imagenes: archivos });
            }}
          />
          {errorImagenes && (
            <p className="form-error">{errorImagenes}</p>
          )}

          <label className="form-label">Vídeo (máx. 1)</label>
          <input
            className="form-input"
            type="file"
            accept="video/*"
            multiple
            onChange={(e) => {
              const archivos = Array.from(e.target.files || []);
              if (archivos.length > 1) {
                setErrorVideos("Solo se permite un vídeo.");
                return;
              }
              setErrorVideos(null);
              setFormulario({ ...formulario, videos: archivos });
            }}
          />
          {errorVideos && <p className="form-error">{errorVideos}</p>}

          <button
            type="submit"
            className="btn btn-primary form-button"
            disabled={
              enviando || !!errorImagenes || !!errorVideos
            }
          >
            {enviando ? "Creando…" : "Crear queja"}
          </button>

          {errorFormulario && (
            <p className="form-error">{errorFormulario}</p>
          )}
        </form>
      </div>
    </div>
  );
}
