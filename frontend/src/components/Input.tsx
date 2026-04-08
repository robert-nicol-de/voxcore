import React from "react";
import "./Input.css";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
}

export const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, className, ...props }, ref) => {
    return (
      <div className="input-wrapper">
        {label && <label className="input-label">{label}</label>}
        <input
          ref={ref}
          className={`input ${error ? "input-error" : ""} ${className || ""}`}
          {...props}
        />
        {error && <span className="input-error-text">{error}</span>}
        {helperText && <span className="input-helper-text">{helperText}</span>}
      </div>
    );
  }
);

Input.displayName = "Input";
