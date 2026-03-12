import React from 'react';

type SchemaNode = {
  name: string;
  tables: string[];
};

type Props = {
  schemas: SchemaNode[];
  selectedTable: string | null;
  onSelect: (schema: string, table: string) => void;
};

export default function SchemaTree({ schemas, selectedTable, onSelect }: Props) {
  return (
    <div className="schema-tree">
      {schemas.map((s) => (
        <div key={s.name}>
          <div className="schema-name">{s.name}</div>
          {s.tables.map((t) => (
            <div
              key={`${s.name}.${t}`}
              className="table-name"
              style={selectedTable === t ? { background: '#1b2a3d', color: '#9ec3ff' } : undefined}
              onClick={() => onSelect(s.name, t)}
            >
              {t}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
