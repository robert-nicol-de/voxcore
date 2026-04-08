import React from "react";
import "./Button.css";

interface ButtonProps {
  children: React.ReactNode;
  variant?: "primary" | "secondary";
  state?: "default" | "hover" | "loading" | "disabled";
  onClick?: () => void;
  className?: string;
  type?: "button" | "submit" | "reset";
}

export const Button: React.FC<ButtonProps> = ({
  children,
  variant = "primary",
  state = "default",
  onClick,
  className = "",
  type = "button",
}) => {
  return (
    <button
      type={type}
      className={`btn btn-${variant} btn-${state} ${className}`}
      onClick={onClick}
      disabled={state === "disabled" || state === "loading"}
    >
      {state === "loading" ? (
        <span className="spinner"></span>
      ) : (
        children
      )}
    </button>
  );
};
