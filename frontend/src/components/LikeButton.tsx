// src/components/LikeButton.tsx
import { useState } from "react";
import { toggleLike } from "../api/megusta";

interface Props {
  initialLiked: boolean;
  initialCount: number;
  objectId: number;
  contentType: number;
}

export default function LikeButton({
  initialLiked,
  initialCount,
  objectId,
  contentType,
}: Props) {
  const [liked, setLiked] = useState<boolean>(initialLiked);
  const [count, setCount] = useState<number>(initialCount);
  const [loading, setLoading] = useState<boolean>(false);

  const handleToggle = async () => {
    if (loading) return;
    setLoading(true);

    const prevLiked = liked;
    const prevCount = count;
    setLiked(!prevLiked);
    setCount(prevCount + (prevLiked ? -1 : 1));

    try {
      const res = await toggleLike(objectId, contentType);
      setLiked(res.liked);
      if (typeof res.count === "number") setCount(res.count);
    } catch (e) {
      setLiked(prevLiked);
      setCount(prevCount);
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
                 5.5 0 000-7.78z"/>
      </svg>
      <span className="like-count">{count}</span>
    </button>
  );
}
``