import axios from "../utils/axios";

export const crearImagenQueja = async (
    contentTypeId: number,
    quejaId: number,
    file: File
) => {
    const formData = new FormData();
    formData.append("content_type", String(contentTypeId));
    formData.append("object_id",String(quejaId));
    formData.append("imagen",file);
    for (const [k, v] of formData.entries()) {
        console.log("FD", k, v);
    }

    return axios.post("/imagenes/create/", formData,{
        headers: {"Content-Type": "multipart/form-data"
        },
    });
};