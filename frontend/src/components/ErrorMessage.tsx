import React from "react";

const ErrorMessage: React.FC<{ message?: string | null }> = ({ message }) => {
  if (!message) return null;
  return (
    <p role="alert" style={{ color: "crimson", marginTop: 8 }}>
      {message}
    </p>
  );
};

export default ErrorMessage;