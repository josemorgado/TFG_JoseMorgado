import React from "react";

type AuthLayoutProps = {
  title: string;
  children: React.ReactNode;
  maxWidth?: number;
};

const AuthLayout: React.FC<AuthLayoutProps> = ({ title, children, maxWidth = 420 }) => {
  return (
    <div style={{ maxWidth, margin: "6rem auto" }}>
      <h1>{title}</h1>
      {children}
    </div>
  );
};

export default AuthLayout;