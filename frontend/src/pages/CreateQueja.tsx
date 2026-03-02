import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import { createQuejaRequest } from "../api/quejas.ts";

const CreateQueja: React.FC = () => {
  const navigate = useNavigate();

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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!form.titulo.trim() || form.titulo.length < 5) {
      setError("El título debe tener mínimo 5 caracteres");
      return;
    }

    if (!form.descripcion.trim() || form.descripcion.length < 10) {
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

    const formData = new FormData();
    formData.append("titulo", form.titulo.trim());
    formData.append("descripcion", form.descripcion.trim());
    formData.append("categoria", form.categoria);
    formData.append("distrito", form.distrito);

    if (form.ubicacion.trim()) {
      formData.append("ubicacion", form.ubicacion.trim());
    }

    form.imagenes.forEach((img) => formData.append("imagenes", img));
    form.videos.forEach((vid) => formData.append("videos", vid));

    try {
      const res = await createQuejaRequest(formData);
      console.log("Queja creada:", res.data);
      navigate(`/quejas/${res.data.id}`);
    } catch (err: any) {
      if (err.response?.data) {
        const data = err.response.data;
        console.log("error response", data);

        const messages: string[] = [];

        if (typeof data === "string") {
          setError(data);
          return;
        }

        if (data.titulo) messages.push(`Título: ${data.titulo.join(" ")}`);
        if (data.descripcion) messages.push(`Descripción: ${data.descripcion.join(" ")}`);
        if (data.categoria) messages.push(`Categoría: ${data.categoria.join(" ")}`);
        if (data.distrito) messages.push(`Distrito: ${data.distrito.join(" ")}`);
        if (data.ubicacion) messages.push(`Ubicación: ${data.ubicacion.join(" ")}`);

        setError(messages.join(" • ") || "Error al crear la queja");
      } else {
        setError("No se pudo conectar con el servidor.");
      }
    }
  };

  return (
    <AuthLayout title="Crear Queja">
      <form onSubmit={handleSubmit}>
        {/* Título */}
        <label htmlFor="titulo">Título</label>
        <input
          id="titulo"
          className="auth-field"
          type="text"
          value={form.titulo}
          onChange={(e) => setForm({ ...form, titulo: e.target.value })}
          required
        />

        {/* Descripción */}
        <label htmlFor="descripcion">Descripción</label>
        <textarea
          id="descripcion"
          className="auth-field"
          value={form.descripcion}
          onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
          rows={4}
          required
        />

        {/* Categoría */}
        <label htmlFor="categoria">ID Categoría</label>
        <input
          id="categoria"
          className="auth-field"
          type="number"
          value={form.categoria}
          onChange={(e) => setForm({ ...form, categoria: e.target.value })}
          required
        />

        {/* Distrito */}
        <label htmlFor="distrito">ID Distrito</label>
        <input
          id="distrito"
          className="auth-field"
          type="number"
          value={form.distrito}
          onChange={(e) => setForm({ ...form, distrito: e.target.value })}
          required
        />

        {/* Ubicación */}
        <label htmlFor="ubicacion">Ubicación (opcional)</label>
        <input
          id="ubicacion"
          className="auth-field"
          type="text"
          value={form.ubicacion}
          onChange={(e) => setForm({ ...form, ubicacion: e.target.value })}
        />

        {/* Imágenes */}
        <label htmlFor="imagenes">Imágenes (opcional)</label>
        <input
          id="imagenes"
          className="auth-field"
          type="file"
          accept="image/*"
          multiple
          onChange={(e) =>
            setForm({
              ...form,
              imagenes: Array.from(e.target.files || []),
            })
          }
        />

        {/* Videos */}
        <label htmlFor="videos">Videos (opcional)</label>
        <input
          id="videos"
          className="auth-field"
          type="file"
          accept="video/*"
          multiple
          onChange={(e) =>
            setForm({
              ...form,
              videos: Array.from(e.target.files || []),
            })
          }
        />

        <button className="submit-button" style={{ marginTop: 12 }}>
          Crear Queja
        </button>

        {error && <p style={{ color: "crimson" }}>{error}</p>}
      </form>
    </AuthLayout>
  );
};

export default CreateQueja;