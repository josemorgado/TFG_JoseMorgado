// frontend/src/api/videos.ts
import axios from "../utils/axios";

export const crearVideoQueja = async (
    contentTypeId: number,
    quejaId: number,
    file: File
) => {
    const formData = new FormData();
    formData.append("content_type", String(contentTypeId));
    formData.append("object_id", String(quejaId));
    formData.append("video", file);
    for (const [k, v] of formData.entries()) {
        console.log("FD", k, v);
    }

    return axios.post("/videos/create/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
    });
};