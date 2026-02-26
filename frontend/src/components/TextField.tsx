import React from "react";

type TextFieldProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label: string;
  name: string;
};

const TextField: React.FC<TextFieldProps> = ({ label, name, style, ...props }) => {
  const id = props.id ?? name;
  return (
    <label htmlFor={id} style={{ display: "block", marginTop: 8, ...style }}>
      {label}
      <input id={id} name={name} {...props} />
    </label>
  );
};

export default TextField;