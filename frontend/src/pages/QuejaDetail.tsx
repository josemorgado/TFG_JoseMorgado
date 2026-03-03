import { useEffect, useState } from "react";
import axiosInstance from "../utils/axios"
import axios from "axios"
import { useParams } from "react-router-dom";
import type { Queja } from "../types/queja";
import type { Comentario } from "../types/comentario";
import type { Imagen } from "../types/imagen";
import type { Video } from "../types/video";
import { mediaUrl } from "../utils/media";

function QuejaDetail() {
    const { id } = useParams();
    const [queja, setQueja] = useState<Queja | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [imagenes, setImagenes] = useState<Imagen[]>([]);
    const [videos, setVideos] = useState<Video[]>([]);
    const [comentarios, setComentarios] = useState<Comentario[]>([]);
    imagenes.forEach(img => console.log("IMG URL =", img.imagen));


  useEffect(() => {
    if (!id) return;

    let cancel = false;


    async function fetchAll() {
    try {
        setLoading(true);
        setError(null);

        // 1. Queja
        const quejaRes = await axiosInstance.get<Queja>(`/quejas/${id}/`);
        if (!cancel) setQueja(quejaRes.data);

        // 2. Imágenes
        const imagenesRes = await axiosInstance.get<Imagen[]>(`/imagenes/queja/${id}/`);
        if (!cancel) setImagenes(imagenesRes.data);

        // 3. Videos
        const videosRes = await axiosInstance.get<Video[]>(`/videos/queja/${id}/`);
        if (!cancel) setVideos(videosRes.data);

        // 4. Comentarios
        const comentarioRes = await axiosInstance.get<Comentario[]>(`/comentarios/queja/${id}/`);
        if (!cancel) setComentarios(comentarioRes.data);

        console.log("QUEJA:", quejaRes.data);


        console.log("IMAGENES:", imagenesRes.data);
        console.log("VIDEOS:", videosRes.data);
        console.log("COMENTARIOS:", comentarioRes.data);


    } catch (err) {
        if (axios.isAxiosError(err)) {
        setError("Error cargando los datos de la queja.");
        } else {
        setError("Error inesperado");
        }
    } finally {
        if (!cancel) setLoading(false);
    }
    }

    fetchAll();
    return () => {
      cancel = true;
    };
  }, [id]);

  if (loading) return <p>Cargando…</p>;
  if (error) return <p style={{ color: "crimson" }}>{error}</p>;
  if (!queja) return <p>No hay datos.</p>;

  return (
    <div>
        <h1>{queja.titulo}</h1>
        <p>{queja.descripcion}</p>
        <small>
            Estado: {queja.estado} · Categoría: {queja.categoria_nombre} · Distrito: {queja.distrito_nombre} · Imágenes: {imagenes.length} · Videos: {videos.length} · Comentarios: {comentarios.length}
        </small>

        <div style={{ marginTop: 16 }}>
        <h2>Imágenes</h2>

        {imagenes.length === 0 ? (
            <p>No hay imágenes.</p>
        ) : (
            <div>
            {imagenes.map((img) => (
                <div key={img.id} style={{ marginBottom: 12 }}>
                <img
                    src={mediaUrl(img.imagen)}
                    alt={`Imagen ${img.id}`}
                    style={{ maxWidth: "300px", display: "block" }}
                />
                <small>Subida: {img.fecha_creacion}</small>
                </div>
            ))}
            </div>
        )}
        </div>


        <div style={{ marginTop: 16 }}>
        <h2>Videos</h2>

        {videos.length === 0 ? (
            <p>No hay videos.</p>
        ) : (
            <div>
            {videos.map((v) => (
                <div key={v.id} style={{ marginBottom: 12 }}>
                <video
                    src={mediaUrl(v.video)}
                    controls
                    style={{ maxWidth: "320px", display: "block" }}
                />
                <small>Subido: {v.fecha_creacion}</small>
                </div>
            ))}
            </div>
        )}
        </div>
        <div style={{ marginTop: 16 }}>
        <h2>Comentarios</h2>
        {comentarios.length === 0 ? (
            <p>No hay comentarios.</p>
        ) : (
            <ul>
            {comentarios.map((c) => (
                <li key={c.id}>
                <p>{c.contenido}</p>
                <small>
                    ID autor: {c.autor} · Fecha: {c.fecha_creacion} · Votos: {c.num_votos}
                </small>
                {c.parent && <div><small>Respuesta a #{c.parent}</small></div>}
                </li>
            ))}
            </ul>
        )}
        </div>

    </div>
  );
}

export default QuejaDetail;