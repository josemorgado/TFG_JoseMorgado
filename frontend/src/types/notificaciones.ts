export interface Notificacion {
  id: number;
  user: number;
  title: string;
  message: string;
  created_at: string; // ISO string
  is_read: boolean;
  url: string | null;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}