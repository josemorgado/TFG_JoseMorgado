// src/components/CommentButton.tsx

export default function CommentButton({onClick}:{onClick: ()=>void}) {
  return (
    <button
      type="button"
      className="heart-btn"
      aria-label="Responder comentario"
      onClick={() => {
        console.log("Click en CommentButton (sin funcionalidad)");
        onClick();
      }}
    >
      <svg
        viewBox="0 0 24 24"
        className="heart-icon"
        aria-hidden="true"
      >
        <path
          d="M4 4h16v10H7l-3 3V4z"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>

      <span
        style={{
          marginLeft: 6,
          fontSize: 12,
          color: "var(--color-primary)",
        }}
      >
        Comentar
      </span>
    </button>
  );
}