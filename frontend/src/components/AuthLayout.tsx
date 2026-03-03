import React from "react";
import "../styles/AuthLayout.css";

type AuthLayoutProps = {
  title: string;
  children: React.ReactNode;
  maxWidth?: number;
};

const AuthLayout: React.FC<AuthLayoutProps> = ({ title, children }) => {
  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">{title}</h1>
        {children}
      </div>
    </div>
  );
};

export default AuthLayout;