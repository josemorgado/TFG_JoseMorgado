import React from "react";
import "./SubmitButton.css";

type SubmitButtonProps = {
  loading?: boolean;
  children?: React.ReactNode;
  style?: React.CSSProperties;
  disabled?: boolean;
};

const SubmitButton: React.FC<SubmitButtonProps> = ({ loading, children, style, disabled }) => {
  return (
    <button
      type="submit"
      className="submit-button"
      disabled={disabled || loading}
      style={{ marginTop: 12, ...style }}
      aria-busy={loading || undefined}
    >
      {loading ? "Entrando…" : children ?? "Entrar"}
    </button>
  );
};

export default SubmitButton;