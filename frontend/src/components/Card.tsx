import React from "react";
import "./Card.css";

interface CardProps {
  children: React.ReactNode;
  elevation?: "sm" | "md" | "lg";
  className?: string;
}

export const Card: React.FC<CardProps> = ({
  children,
  elevation = "sm",
  className = "",
}) => {
  return (
    <div className={`card card-${elevation} ${className}`}>
      {children}
    </div>
  );
};
