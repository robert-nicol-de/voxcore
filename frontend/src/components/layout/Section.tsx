import React from "react";

interface SectionProps {
  children: React.ReactNode;
  className?: string;
}

export const Section = ({ children, className = "" }: SectionProps) => {
  return (
    <section className={`py-24 ${className}`}>
      {children}
    </section>
  );
};
