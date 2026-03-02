import React from "react";
import "./AuthLayout.css";

type TextFieldProps = React.InputHTMLAttributes<HTMLInputElement> & {
  name: string;
};

const TextField: React.FC<TextFieldProps> = ({ name, style, ...props }) => {
  const id = props.id ?? name;
  return (
    <label htmlFor={id} style={{ display: "block", marginTop: 8, ...style }}>
      <input className="auth-field" id={id} name={name} {...props} />
    </label>
  );
};

export default TextField;