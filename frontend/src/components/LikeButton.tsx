
import { useState } from "react";

export default function LikeButton() {
  const [active, setActive] = useState(false);

  return (
    <button
      className={`heart-btn ${active ? "active" : ""}`}
      onClick={() => setActive(prev => !prev)}
      aria-label="Me gusta"
    >
      <svg
        viewBox="0 0 24 24"
        className="heart-icon"
        aria-hidden="true"
      >
        <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5
                 5.5 0 00-7.78 7.78L12 21.23l8.84-8.84a5.5
                 5.5 0 000-7.78z"/>
      </svg>
    </button>
  );
}
