import React from "react";

type PasswordFieldProps = React.InputHTMLAttributes<HTMLInputElement> & {
  name: string;
  label?: string;
};

const PasswordField: React.FC<PasswordFieldProps> = ({
  name,
  label,
  id,
  className = "",
  ...props
}) => {
  const inputId = id ?? name;

  return (
    <label htmlFor={inputId} style={{ display: "block", marginTop: 8 }}>
      {label && <div>{label}</div>}
      <input
        id={inputId}
        name={name}
        type="password"
        className={`auth-field`}
        autoComplete="current-password"
        {...props}
      />
    </label>
  );
};

export default PasswordField;