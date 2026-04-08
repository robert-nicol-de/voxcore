import React from "react";
import ColumnList from "./ColumnList";

type ColumnMeta = {
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
  sensitive?: string | null;
};

type Summary = {
  description?: string;
  primary_key?: string;
  relationships?: string[];
  metrics?: string[];
};

type Props = {
  tableName: string | null;
  columns: ColumnMeta[];
  summary: Summary | null;
};

export default function TableViewer({ tableName, columns, summary }: Props) {
  if (!tableName) {
    return (
      <div className="table-details">
        <h3 style={{ color: "#e8f1ff" }}>Table Details</h3>
        <p style={{ color: "#9ab3cf" }}>Select a table from the schema tree.</p>
      </div>
    );
  }

  return (
    <div className="table-details">
      <h3 style={{ color: "#e8f1ff", marginBottom: 8 }}>Table: {tableName}</h3>

      <h4 style={{ color: "#9ec3ff", margin: "16px 0 10px" }}>Columns</h4>
      <ColumnList columns={columns} />

      <h4 style={{ color: "#9ec3ff", margin: "18px 0 10px" }}>AI Summary</h4>
      <div style={{ color: "#cfe0f5", lineHeight: 1.6, fontSize: 13 }}>
        <div>{summary?.description || "No summary available."}</div>
        {summary?.primary_key && <div>Primary key: {summary.primary_key}</div>}
        {summary?.relationships && summary.relationships.length > 0 && (
          <div>Relationships: {summary.relationships.join(", ")}</div>
        )}
        {summary?.metrics && summary.metrics.length > 0 && (
          <div>Metrics: {summary.metrics.join(", ")}</div>
        )}
      </div>
    </div>
  );
}
