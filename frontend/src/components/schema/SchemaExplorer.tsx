import React, { useEffect, useMemo, useState } from 'react';
import { apiUrl } from '../../lib/api';
import SchemaTree from './SchemaTree';
import TableViewer from './TableViewer';

type TableEntry = { name: string; schema: string };
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

export default function SchemaExplorer() {
  const companyId = localStorage.getItem('voxcore_company_id') || 'default';
  const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';
  const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token') || '';

  const [connectionName, setConnectionName] = useState('');
  const [connections, setConnections] = useState<string[]>([]);
  const [tables, setTables] = useState<TableEntry[]>([]);
  const [selectedSchema, setSelectedSchema] = useState<string>('');
  const [selectedTable, setSelectedTable] = useState<string | null>(null);
  const [columns, setColumns] = useState<ColumnMeta[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [dbLabel, setDbLabel] = useState('');

  useEffect(() => {
    const loadConnections = async () => {
      const params = new URLSearchParams({ company_id: companyId, workspace_id: workspaceId });
      const res = await fetch(apiUrl(`/api/v1/schema/databases?${params}`), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const data = (await res.json()) as { databases: string[] };
      const list = data.databases || [];
      setConnections(list);
      if (list.length > 0) setConnectionName(list[0]);
    };
    void loadConnections();
  }, [companyId, workspaceId, token]);

  useEffect(() => {
    if (!connectionName) return;
    const loadTables = async () => {
      const params = new URLSearchParams({
        company_id: companyId,
        workspace_id: workspaceId,
        connection_name: connectionName,
      });
      const res = await fetch(apiUrl(`/api/v1/schema/tables?${params}`), {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) return;
      const data = (await res.json()) as { tables: TableEntry[]; database?: string };
      setTables(data.tables || []);
      setDbLabel(data.database || connectionName);
      setSelectedTable(null);
      setColumns([]);
      setSummary(null);
    };
    void loadTables();
  }, [companyId, workspaceId, connectionName, token]);

  const schemaTree = useMemo(() => {
    const m = new Map<string, string[]>();
    for (const t of tables) {
      const schema = t.schema || 'public';
      if (!m.has(schema)) m.set(schema, []);
      m.get(schema)!.push(t.name);
    }
    return Array.from(m.entries()).map(([name, list]) => ({ name, tables: list.sort() }));
  }, [tables]);

  const onSelectTable = async (schema: string, table: string) => {
    setSelectedSchema(schema);
    setSelectedTable(table);

    const params = new URLSearchParams({
      company_id: companyId,
      workspace_id: workspaceId,
      connection_name: connectionName,
    });

    const [columnsRes, summaryRes] = await Promise.all([
      fetch(apiUrl(`/api/v1/schema/table/${encodeURIComponent(table)}?${params}`), {
        headers: { Authorization: `Bearer ${token}` },
      }),
      fetch(apiUrl(`/api/v1/schema/table-summary?table_name=${encodeURIComponent(table)}&${params}`), {
        headers: { Authorization: `Bearer ${token}` },
      }),
    ]);

    if (columnsRes.ok) {
      const cData = (await columnsRes.json()) as { columns: ColumnMeta[] };
      setColumns(cData.columns || []);
    }

    if (summaryRes.ok) {
      const sData = (await summaryRes.json()) as Summary;
      setSummary(sData);
    } else {
      setSummary(null);
    }
  };

  return (
    <div>
      <div style={{ display: 'flex', gap: 12, marginBottom: 12, alignItems: 'center', flexWrap: 'wrap' }}>
        <div style={{ color: '#9ab3cf', fontSize: 13 }}>Database: <strong style={{ color: '#e8f1ff' }}>{dbLabel || '—'}</strong></div>
        <div style={{ color: '#9ab3cf', fontSize: 13 }}>Workspace: <strong style={{ color: '#e8f1ff' }}>{localStorage.getItem('voxcore_workspace_name') || 'Default'}</strong></div>
        <select
          value={connectionName}
          onChange={(e) => setConnectionName(e.target.value)}
          style={{ marginLeft: 'auto', background: '#101826', color: '#e8f1ff', border: '1px solid #24344d', borderRadius: 8, padding: '8px 10px' }}
        >
          {connections.map((c) => (<option key={c} value={c}>{c}</option>))}
        </select>
      </div>

      <div className="schema-layout">
        <SchemaTree schemas={schemaTree} selectedTable={selectedTable} onSelect={onSelectTable} />
        <TableViewer tableName={selectedTable} columns={columns} summary={summary ? {
          ...summary,
          description: summary.description || (selectedTable ? `Contains ${selectedTable} records.` : undefined),
        } : null} />
      </div>

      {selectedSchema && selectedTable && (
        <div style={{ marginTop: 10, color: '#91a8c4', fontSize: 12 }}>
          Selected: {selectedSchema}.{selectedTable}
        </div>
      )}
    </div>
  );
}
