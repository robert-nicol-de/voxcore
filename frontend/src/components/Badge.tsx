import React from "react";
import "./Badge.css";

interface BadgeProps {
  children: React.ReactNode;
  variant?: "safe" | "warning" | "danger" | "info";
  className?: string;
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = "info",
  className = "",
}) => {
  return (
    <span className={`badge badge-${variant} ${className}`}>
      {children}
    </span>
  );
};
