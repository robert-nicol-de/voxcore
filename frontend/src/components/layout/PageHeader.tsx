import React from "react";

interface PageHeaderProps {
  title: string;
  description?: string;
}

export default function PageHeader({ title, description }: PageHeaderProps) {
  return (
    <div style={{ marginBottom: "24px" }}>
      <h1 style={{ fontSize: "24px", fontWeight: "600" }}>{title}</h1>
      {description && (
        <p style={{ color: "#666", marginTop: "4px" }}>{description}</p>
      )}
    </div>
  );
}
