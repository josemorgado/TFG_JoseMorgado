import axios from "../utils/axios";
import type { Usuario } from "../types/perfil";

export async function getUsuarioById(id: number | string): Promise<Usuario> {
  const response = await axios.get(`/usuarios/${id}/`);
  return response.data;
}

export async function updateUsuario(
  id: number | string,
  data: any,
  file?: File | null,
) {
  try {
    if (file) {
      const formData = new FormData();

      // Campos user
      if (data.username !== undefined)
        formData.append("username", data.username);
      if (data.email !== undefined) formData.append("email", data.email);
      if (data.first_name !== undefined)
        formData.append("first_name", data.first_name);
      if (data.last_name !== undefined)
        formData.append("last_name", data.last_name);

      if (data.perfil) {
        formData.append("perfil", JSON.stringify(data.perfil));
      }

      if (file) formData.append("perfil.foto_perfil", file);

      const res = await axios.patch(
        `/usuarios/${id}/partial-update/`,
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        },
      );
      return res.data;
    }

    const res = await axios.patch(`/usuarios/${id}/partial-update/`, data);
    return res.data;
  } catch (err: any) {
    throw err.response?.data || err;
  }
}

export const changePassword = async (
  userId: number | string,
  oldPassword: string,
  newPassword: string
) => {
  return axios.post(`/usuarios/${userId}/change-password/`, {
    old_password: oldPassword,
    new_password: newPassword
  });
};

export async function deleteUsuario(id: number | string) {
  try {
    // 1) Coger el refresh token
    const refresh = localStorage.getItem("refresh");

    // 2) Invalidar refresh token en backend
    if (refresh) {
      try {
        await axios.post(`/usuarios/logout/`, { refresh });
      } catch {
        // aunque falle, seguimos; no bloquea el borrado
      }
    }

    // 3) Borrar tokens locales
    try {
      localStorage.removeItem("access");
      localStorage.removeItem("refresh");
    } catch { }

    // 4) Eliminar usuario definitivamente
    const res = await axios.delete(`/usuarios/${id}/delete/`);
    return res.data; // normalmente será undefined (204)

  } catch (err: any) {
    throw err.response?.data || err;
  }
}

export async function toggleModerator(
  id: number | string,
  currentValue: boolean
) {
  const res = await axios.patch(`/usuarios/${id}/partial-update/`, {
    perfil: {
      moderator: !currentValue,
    },
  });
  return res.data;
}
