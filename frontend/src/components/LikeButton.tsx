import { useEffect, useState } from "react";
import { toggleLike } from "../api/megusta";

interface Props {
  initialLiked: boolean;
  initialCount: number;
  objectId: number;
  contentType: number;
  onChange?: (liked: boolean, count: number) => void;
  onUnauthorized?: () => void;
}

export default function LikeButton({
  initialLiked,
  initialCount,
  objectId,
  contentType,
  onChange,
  onUnauthorized,
}: Props) {
  const [liked, setLiked] = useState<boolean>(!!initialLiked);
  const [count, setCount] = useState<number>(initialCount ?? 0);
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => setLiked(!!initialLiked), [initialLiked]);
  useEffect(() => setCount(initialCount ?? 0), [initialCount]);

  const handleToggle = async () => {
    if (loading) return;
    setLoading(true);

    const prevLiked = liked;
    const prevCount = count;

    const optimisticLiked = !prevLiked;
    const optimisticCount = prevCount + (prevLiked ? -1 : 1);

    setLiked(optimisticLiked);
    setCount(optimisticCount);
    onChange?.(optimisticLiked, optimisticCount);

    try {
      const res = await toggleLike(objectId, contentType);

      const serverLiked = !!res.liked;
      const serverCount =
        typeof res.count === "number" ? res.count : optimisticCount;

      setLiked(serverLiked);
      setCount(serverCount);
      onChange?.(serverLiked, serverCount);
    } catch (err: any) {
      setLiked(prevLiked);
      setCount(prevCount);
      onChange?.(prevLiked, prevCount);

      if (err?.response?.status === 401) {
        onUnauthorized?.();
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <button
      className={`heart-btn ${liked ? "active" : ""}`}
      onClick={handleToggle}
      aria-label={liked ? "Quitar me gusta" : "Dar me gusta"}
      disabled={loading}
      type="button"
    >
      <svg viewBox="0 0 24 24" className="heart-icon" aria-hidden="true">
        <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5
                 5.5 0 00-7.78 7.78L12 21.23l8.84-8.84a5.5
                 5.5 0 000-7.78z" />
      </svg>
      <span className="like-count" style={{ marginLeft: 6 }}>
        {count}
      </span>
    </button>
  );
}