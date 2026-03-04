
import axios from "../utils/axios";
import type { Usuario } from "../types/perfil";

export async function getUsuarioById(id:number|string): Promise<Usuario> {
  const response = await axios.get(`/usuarios/${id}/`);
  return response.data;
}
