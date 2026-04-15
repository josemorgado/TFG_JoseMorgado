const API_ORIGIN = "https://alcalde-escuchame-backend.onrender.com";

export function mediaUrl(url: string): string {
  if (!url) return "";

  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }

  return `${API_ORIGIN}${url}`;
}