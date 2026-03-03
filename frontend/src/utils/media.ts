const API_ORIGIN = "http://localhost:8000";

export function mediaUrl(url: string): string {
  if (!url) return "";

  if (url.startsWith("http://") || url.startsWith("https://")) {
    return url;
  }

  return `${API_ORIGIN}${url}`;
}