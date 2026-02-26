import React, { useState } from "react";

type PasswordFieldProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  name: string;
};

const PasswordField: React.FC<PasswordFieldProps> = ({ label, name, style, ...props }) => {
  const [show, setShow] = useState(false);
  const id = props.id ?? name;

  return (
    <label htmlFor={id} style={{ display: "block", marginTop: 8, ...style }}>
      {label}
      <div style={{ display: "flex", alignItems: "center" }}>
        <input
          id={id}
          name={name}
          type={show ? "text" : "password"}
          autoComplete="current-password"
          {...props}
        />
        <button
          type="button"
          onClick={() => setShow(v => !v)}
          aria-label={show ? "Ocultar contraseña" : "Mostrar contraseña"}
          title={show ? "Ocultar contraseña" : "Mostrar contraseña"}
          style={{ marginLeft: 8 }}
          disabled={props.disabled}
        >
          {show ? "🙈" : "👁️"}
        </button>
      </div>
    </label>
  );
};

export default PasswordField;