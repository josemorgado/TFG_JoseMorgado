// src/api/megusta.ts
import axiosInstance from "../utils/axios";

export async function toggleLike(objectId: number, contentType: number) {
  try {
    const body = { content_type: contentType, object_id: objectId };
    const res = await axiosInstance.post("/megusta/toggle/", body);
    return res.data;
  } catch (err: any) {
    // Log detallado
    if (err.response) {
      console.error("toggleLike error:", err.response.status, err.response.data);
    } else {
      console.error("toggleLike network/error:", err.message || err);
    }
    throw err;
  }
}