import { useEffect, useState } from "react";
import { apiUrl } from "../lib/api";

type SchemaExplorerProps = {
  connectionName?: string;
};

type SchemaPayload = {
  schema?: Array<{ table?: string }>;
  tables?: string[];
};

export default function SchemaExplorer({ connectionName }: SchemaExplorerProps) {
  const [tables, setTables] = useState<string[]>([]);

  useEffect(() => {
    const loadSchema = async () => {
      const companyId = localStorage.getItem("voxcore_company_id") || "default";
      const workspaceId = localStorage.getItem("voxcore_workspace_id") || "default";
      const params = new URLSearchParams({ company_id: companyId, workspace_id: workspaceId });
      if (connectionName) {
        params.set("connection_name", connectionName);
      }

      try {
        const response = await fetch(apiUrl(`/api/v1/schema/discover?${params.toString()}`));
        if (!response.ok) {
          setTables([]);
          return;
        }

        const data: SchemaPayload = await response.json();
        if (Array.isArray(data.tables)) {
          setTables(data.tables.filter(Boolean));
          return;
        }

        setTables((data.schema || []).map((item) => item.table || "").filter(Boolean));
      } catch {
        setTables([]);
      }
    };

    loadSchema();
  }, [connectionName]);

  return (
    <div className="card">
      <h3>Schema Explorer</h3>
      <ul className="schema-list">
        {tables.length === 0 ? (
          <li className="schema-empty">No schema discovered yet.</li>
        ) : (
          tables.map((table) => <li key={table}>{table}</li>)
        )}
      </ul>
    </div>
  );
}
