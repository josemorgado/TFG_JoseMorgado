import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import AuthLayout from "../components/AuthLayout";
import { createQuejaRequest } from "../api/quejas";
import { useCategorias, useDistritos } from "../modules/catalogos/catalogos.queries";
import { crearImagenQueja } from "../api/imagenes";

const CreateQueja: React.FC = () => {
  const navigate = useNavigate();

  // Cargar catálogos (IMPORTANTE: hooks dentro del componente)
  const { data: categorias, isLoading: catLoading, error: catError } = useCategorias();
  const { data: distritos,  isLoading: disLoading, error: disError } = useDistritos();

  const [form, setForm] = useState({
    titulo: "",
    descripcion: "",
    categoria: "", // select guarda string; luego convertimos a number al enviar
    distrito: "",
    ubicacion: "",
    imagenes: [] as File[],
    videos: [] as File[],
  });

  const [error, setError] = useState<string | null>(null);
  const [errorImagenes, setErrorImagenes] = useState<string | null>(null);
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Validaciones rápidas en cliente
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


    // Construir FormData (conversión a number -> string)
    const formData = new FormData();
    formData.append("titulo", form.titulo.trim());
    formData.append("descripcion", form.descripcion.trim());
    formData.append("categoria", String(Number(form.categoria)));
    formData.append("distrito", String(Number(form.distrito)));

    if (form.ubicacion.trim()) {
      formData.append("ubicacion", form.ubicacion.trim());
    }

    try {
      const res = await createQuejaRequest(formData); // POST /quejas/create/ (multipart)
      // Si el backend devuelve el objeto con id:
      const id = res?.data?.id;
      const ctId = res?.data?.content_type;



      for (const file of form.imagenes) {
        await crearImagenQueja(ctId,id,file)
      }

      if (id) {
        navigate(`/quejas/${id}`);
      } else {
        // Fallback si no llega id
        navigate("/quejas");
      }
    } catch (err: any) {
      if (err.response?.data) {
        const data = err.response.data;
        console.log("error response", data);

        const messages: string[] = [];

        if (typeof data === "string") {
          setError(data);
          return;
        }

        if (data.titulo) messages.push(`Título: ${Array.isArray(data.titulo) ? data.titulo.join(" ") : String(data.titulo)}`);
        if (data.descripcion) messages.push(`Descripción: ${Array.isArray(data.descripcion) ? data.descripcion.join(" ") : String(data.descripcion)}`);
        if (data.categoria) messages.push(`Categoría: ${Array.isArray(data.categoria) ? data.categoria.join(" ") : String(data.categoria)}`);
        if (data.distrito) messages.push(`Distrito: ${Array.isArray(data.distrito) ? data.distrito.join(" ") : String(data.distrito)}`);
        if (data.ubicacion) messages.push(`Ubicación: ${Array.isArray(data.ubicacion) ? data.ubicacion.join(" ") : String(data.ubicacion)}`);

        setError(messages.join(" • ") || "Error al crear la queja");
      } else {
        setError("No se pudo conectar con el servidor.");
      }
    }
  };

  return (
    <AuthLayout title="Crear Queja">
      <form onSubmit={handleSubmit} className="grid gap-3">
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
        <label htmlFor="categoria">Categoría</label>
        <select
          id="categoria"
          className="auth-field"
          value={form.categoria}
          onChange={(e) => setForm({ ...form, categoria: e.target.value })}
          required
          disabled={catLoading || !!catError}
        >
          <option value="" disabled>
            {catLoading ? "Cargando categorías…" : "Selecciona una categoría"}
          </option>
          {catError && <option value="" disabled>⚠️ Error cargando categorías</option>}
          {categorias?.map((c) => (
            <option key={c.id} value={String(c.id)}>
              {c.nombre}
            </option>
          ))}
        </select>

        {/* Distrito */}
        <label htmlFor="distrito">Distrito</label>
        <select
          id="distrito"
          className="auth-field"
          value={form.distrito}
          onChange={(e) => setForm({ ...form, distrito: e.target.value })}
          required
          disabled={disLoading || !!disError}
        >
          <option value="" disabled>
            {disLoading ? "Cargando distritos…" : "Selecciona un distrito"}
          </option>
          {disError && <option value="" disabled>⚠️ Error cargando distritos</option>}
          {distritos?.map((d) => (
            <option key={d.id} value={String(d.id)}>
              {d.nombre}
            </option>
          ))}
        </select>

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
          onChange={(e) =>{
            const files = Array.from(e.target.files || []);
            const MAX = 5;
            if (files.length > MAX) {
              setErrorImagenes("El maximo de imagenes es 5.");
              return;
            }
            setErrorImagenes(null)
            setForm({
              ...form,
              imagenes: Array.from(e.target.files || []),
            });
          }}
        />
        {errorImagenes && (
          <p style={{ color: "crimson", fontSize: "0.9rem" }}>
            {errorImagenes}
          </p>
        )}
        {/* Videos */}
        <label htmlFor="videos">Videos (opcional)</label>
        <input
          id="videos"
          className="auth-field"
          type="file"
          accept="video/*"
          multiple
          onChange={(e) =>{
            const files = Array.from(e.target.files || []);
            const MAX = 1;
            if (files.length > MAX) {
              setError("El maximo de videos es 1.");
              setForm({...form, imagenes: []});
              return;
            }
            setForm({
              ...form,
              videos: Array.from(e.target.files || []),
            })
          }}
        />

        <button className="submit-button" style={{ marginTop: 12 }} disabled={errorImagenes}>
          Crear Queja
        </button>

        {error && <p style={{ color: "crimson" }}>{error}</p>}
      </form>
    </AuthLayout>
  );
};

export default CreateQueja;