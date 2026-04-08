import React from "react";
import { Badge } from "./Badge";
import "./SchemaTrustBadge.css";

interface SchemaTrustBadgeProps {
  grade: string;
  score: number;
  warnings?: string[];
}

const gradeToVariant = (grade: string) => {
  switch (grade) {
    case "A": return "safe";
    case "B": return "info";
    case "C": return "warning";
    case "D": return "danger";
    default: return "info";
  }
};

const SchemaTrustBadge: React.FC<SchemaTrustBadgeProps> = ({ grade, score, warnings = [] }) => (
  <div className="schema-trust-badge">
    <Badge variant={gradeToVariant(grade)}>
      Trust: {grade} ({score})
    </Badge>
    {grade === "D" && warnings.length > 0 && (
      <div className="trust-warnings">
        {warnings.map((w, i) => (
          <div className="trust-warning" key={i}>{w}</div>
        ))}
      </div>
    )}
  </div>
);

export default SchemaTrustBadge;
