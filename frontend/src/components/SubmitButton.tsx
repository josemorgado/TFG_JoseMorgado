import React from "react";

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
      disabled={disabled || loading}
      style={{ marginTop: 12, ...style }}
      aria-busy={loading || undefined}
    >
      {loading ? "Entrando…" : children ?? "Entrar"}
    </button>
  );
};

export default SubmitButton;