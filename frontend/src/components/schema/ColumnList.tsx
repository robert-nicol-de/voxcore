import React from "react";

type ColumnMeta = {
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
  sensitive?: string | null;
};

type Props = {
  columns: ColumnMeta[];
};

function fkHint(columnName: string): boolean {
  return /_id$/i.test(columnName) && !/^id$/i.test(columnName);
}

export default function ColumnList({ columns }: Props) {
  return (
    <div>
      {columns.map((c) => (
        <div key={c.name} className="column-row">
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <span style={{ color: "#e8f1ff", fontFamily: "monospace" }}>{c.name}</span>
            {c.primary_key && <span className="schema-badge">PK</span>}
            {!c.primary_key && fkHint(c.name) && <span className="schema-badge">FK</span>}
            {c.sensitive && <span className="schema-badge">Sensitive</span>}
          </div>
          <span style={{ color: "#9ab3cf", fontFamily: "monospace" }}>{c.type.toUpperCase()}</span>
        </div>
      ))}
    </div>
  );
}
