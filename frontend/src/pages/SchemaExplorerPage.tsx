import { useEffect, useState } from 'react';
import { apiUrl } from '../lib/api';
import PageHeader from '../components/PageHeader';

type TableMeta = { name: string; schema: string };
type ColumnMeta = {
  name: string;
  type: string;
  nullable: boolean;
  primary_key: boolean;
  sensitive?: string | null;
};

const SENSITIVE_RULES: Array<{ pattern: RegExp; label: string }> = [
  { pattern: /email|e_?mail/i,                                   label: '⚠ PII' },
  { pattern: /phone|mobile|cell/i,                               label: '⚠ PII' },
  { pattern: /address|postal|zip|city/i,                         label: '⚠ PII' },
  { pattern: /dob|birth|date_of_birth/i,                         label: '⚠ PII' },
  { pattern: /first_?name|last_?name|full_?name/i,               label: '⚠ PII' },
  { pattern: /ssn|social_?security|national_?id|passport/i,      label: '⚠ sensitive' },
  { pattern: /credit_?card|card_?number|cvv|ccv/i,               label: '⚠ sensitive' },
  { pattern: /password|passwd/i,                                  label: '⚠ sensitive' },
  { pattern: /api_?key|secret|token|private_?key/i,              label: '⚠ sensitive' },
];

function getSensitiveLabel(col: ColumnMeta): string | null {
  if (col.sensitive) return col.sensitive.includes('PII') ? '⚠ PII' : '⚠ sensitive';
  for (const { pattern, label } of SENSITIVE_RULES) {
    if (pattern.test(col.name)) return label;
  }
  return null;
}

function detectLikelyForeignKey(colName: string, allTables: TableMeta[]): string | null {
  const lower = colName.toLowerCase();
  for (const table of allTables) {
    const tName = table.name.toLowerCase();
    if (lower === `${tName}_id` || lower === `${tName}id`) {
      return table.name;
    }
  }
  return null;
}

export default function SchemaExplorerPage() {
  const companyId   = localStorage.getItem('voxcore_company_id')   || 'default';
  const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';

  const [connections,       setConnections]       = useState<string[]>([]);
  const [selectedConn,      setSelectedConn]      = useState('');
  const [dbName,            setDbName]            = useState('');
  const [tables,            setTables]            = useState<TableMeta[]>([]);
  const [search,            setSearch]            = useState('');
  const [selectedTable,     setSelectedTable]     = useState<string | null>(null);
  const [columns,           setColumns]           = useState<ColumnMeta[]>([]);
  const [selectedCol,       setSelectedCol]       = useState<string | null>(null);
  const [loadingTables,     setLoadingTables]     = useState(false);
  const [loadingCols,       setLoadingCols]       = useState(false);
  const [errorMsg,          setErrorMsg]          = useState('');

  useEffect(() => {
    const load = async () => {
      try {
        const params = new URLSearchParams({ company_id: companyId, workspace_id: workspaceId });
        const res = await fetch(apiUrl(`/api/v1/schema/databases?${params}`));
        if (res.ok) {
          const data = await res.json() as { databases: string[] };
          const list = data.databases || [];
          setConnections(list);
          if (list.length > 0) setSelectedConn(list[0]);
        }
      } catch {
        setErrorMsg('Failed to load connections');
      }
    };
    void load();
  }, [companyId, workspaceId]);

  useEffect(() => {
    if (!selectedConn) return;
    setLoadingTables(true);
    setTables([]);
    setSelectedTable(null);
    setColumns([]);
    setSelectedCol(null);
    setErrorMsg('');

    const load = async () => {
      try {
        const params = new URLSearchParams({
          company_id:      companyId,
          workspace_id:    workspaceId,
          connection_name: selectedConn,
        });
        const res = await fetch(apiUrl(`/api/v1/schema/tables?${params}`));
        if (res.ok) {
          const data = await res.json() as { tables: TableMeta[]; database: string };
          setTables(data.tables || []);
          setDbName(data.database || selectedConn);
        } else {
          const body = await res.json().catch(() => ({})) as { detail?: string };
          setErrorMsg(body.detail || 'Failed to load tables');
        }
      } catch {
        setErrorMsg('Network error loading tables');
      } finally {
        setLoadingTables(false);
      }
    };
    void load();
  }, [selectedConn, companyId, workspaceId]);

  const loadColumns = async (tableName: string) => {
    setSelectedTable(tableName);
    setSelectedCol(null);
    setLoadingCols(true);
    setColumns([]);
    try {
      const params = new URLSearchParams({
        company_id:      companyId,
        workspace_id:    workspaceId,
        connection_name: selectedConn,
      });
      const res = await fetch(apiUrl(`/api/v1/schema/table/${encodeURIComponent(tableName)}?${params}`));
      if (res.ok) {
        const data = await res.json() as { columns: ColumnMeta[] };
        setColumns(data.columns || []);
      }
    } catch {
      setColumns([]);
    } finally {
      setLoadingCols(false);
    }
  };

  const filteredTables = search
    ? tables.filter(t => t.name.toLowerCase().includes(search.toLowerCase()))
    : tables;

  const selectedColumn = columns.find(c => c.name === selectedCol);
  const likelyForeignKey = selectedColumn ? detectLikelyForeignKey(selectedColumn.name, tables) : null;

  return (
    <div>
      <PageHeader
        title="Schema Explorer"
        subtitle="Browse database structure safely — reads system metadata only, never touches user data"
      />

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16, flexWrap: 'wrap' }}>
        <select
          value={selectedConn}
          onChange={e => setSelectedConn(e.target.value)}
          style={{
            background: 'var(--platform-card-bg)',
            border: '1px solid var(--platform-border)',
            borderRadius: 8,
            color: '#fff',
            padding: '8px 14px',
            fontSize: 13,
            minWidth: 200,
            cursor: 'pointer',
          }}
        >
          {connections.length === 0 && <option value="">No connections</option>}
          {connections.map(c => <option key={c} value={c}>{c}</option>)}
        </select>

        {dbName && (
          <span style={{ fontSize: 12, color: 'var(--platform-muted)' }}>
            Database: <strong style={{ color: '#4f8cff', fontFamily: 'monospace' }}>{dbName}</strong>
          </span>
        )}

        {tables.length > 0 && (
          <span style={{ fontSize: 12, color: 'var(--platform-muted)', marginLeft: 'auto' }}>
            {tables.length} table{tables.length !== 1 ? 's' : ''} • {columns.length} column{columns.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      {errorMsg && (
        <div style={{
          background: 'rgba(255,80,80,0.1)',
          border: '1px solid rgba(255,80,80,0.3)',
          borderRadius: 8,
          padding: '10px 16px',
          color: '#ff5050',
          fontSize: 13,
          marginBottom: 16,
        }}>
          {errorMsg}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '240px 1fr 300px', gap: 16, alignItems: 'start' }}>

        {/* LEFT PANEL: Tables */}
        <div style={{
          background: 'var(--platform-card-bg)',
          border: '1px solid var(--platform-border)',
          borderRadius: 12,
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <div style={{ padding: '16px', borderBottom: '1px solid var(--platform-border)' }}>
            <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: 'var(--platform-muted)', marginBottom: 8, letterSpacing: '0.08em' }}>
              Tables
            </div>
            <input
              type="text"
              placeholder="Search…"
              value={search}
              onChange={e => setSearch(e.target.value)}
              style={{
                width: '100%',
                background: 'rgba(255,255,255,0.05)',
                border: '1px solid var(--platform-border)',
                borderRadius: 6,
                color: '#fff',
                padding: '6px 10px',
                fontSize: 12,
                boxSizing: 'border-box',
                outline: 'none',
              }}
            />
          </div>

          <div style={{ flex: 1, overflowY: 'auto', maxHeight: 600 }}>
            {loadingTables && <div style={{ padding: '16px', color: 'var(--platform-muted)', fontSize: 12 }}>Loading…</div>}
            {!loadingTables && connections.length === 0 && <div style={{ padding: '16px', color: 'var(--platform-muted)', fontSize: 12 }}>Connect a database first</div>}

            {filteredTables.map(t => {
              const isActive = selectedTable === t.name;
              return (
                <button
                  key={t.name}
                  onClick={() => void loadColumns(t.name)}
                  style={{
                    display: 'block',
                    width: '100%',
                    textAlign: 'left',
                    padding: '8px 14px',
                    borderLeft: isActive ? '3px solid #4f8cff' : '3px solid transparent',
                    background: isActive ? 'rgba(79,140,255,0.08)' : 'transparent',
                    color: isActive ? '#4f8cff' : '#e2e8f0',
                    border: 'none',
                    fontSize: 13,
                    fontFamily: 'monospace',
                    cursor: 'pointer',
                    borderBottom: '1px solid rgba(255,255,255,0.03)',
                    fontWeight: isActive ? 600 : 400,
                  }}
                >
                  {isActive && <span style={{ marginRight: 6, fontSize: 10 }}>▸</span>}
                  {t.name}
                </button>
              );
            })}

            {!loadingTables && filteredTables.length === 0 && search && (
              <div style={{ padding: '16px', color: 'var(--platform-muted)', fontSize: 12 }}>
                No tables match "{search}"
              </div>
            )}
          </div>
        </div>

        {/* MIDDLE PANEL: Columns */}
        <div style={{
          background: 'var(--platform-card-bg)',
          border: '1px solid var(--platform-border)',
          borderRadius: 12,
          padding: '16px',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}>
          {!selectedTable ? (
            <div style={{ textAlign: 'center', color: 'var(--platform-muted)', fontSize: 13, padding: '40px 20px' }}>
              ← Select a table
            </div>
          ) : (
            <>
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontWeight: 700, fontSize: 15, fontFamily: 'monospace', color: '#4f8cff', marginBottom: 4 }}>
                  {selectedTable}
                </div>
                <div style={{ fontSize: 11, color: 'var(--platform-muted)' }}>
                  {loadingCols ? '⏳ Loading…' : `${columns.length} column${columns.length !== 1 ? 's' : ''}`}
                </div>
              </div>

              {!loadingCols && columns.length > 0 && (
                <div style={{ overflowX: 'auto', flex: 1 }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                    <thead>
                      <tr style={{ borderBottom: '1px solid var(--platform-border)' }}>
                        {['Column', 'Type', 'PK', 'Null', 'Risk'].map(h => (
                          <th
                            key={h}
                            style={{
                              textAlign: 'left',
                              padding: '6px 10px',
                              color: 'var(--platform-muted)',
                              fontWeight: 600,
                              fontSize: 10,
                              textTransform: 'uppercase',
                              letterSpacing: '0.05em',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {h}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {columns.map(col => {
                        const isSelectedCol = selectedCol === col.name;
                        const flag = getSensitiveLabel(col);
                        return (
                          <tr
                            key={col.name}
                            onClick={() => setSelectedCol(col.name)}
                            style={{
                              borderBottom: '1px solid rgba(255,255,255,0.04)',
                              background: isSelectedCol ? 'rgba(79,140,255,0.08)' : 'transparent',
                              cursor: 'pointer',
                            }}
                          >
                            <td style={{
                              padding: '8px 10px',
                              fontFamily: 'monospace',
                              fontWeight: col.primary_key ? 700 : 400,
                              color: col.primary_key ? '#4f8cff' : '#e2e8f0',
                              maxWidth: 120,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}>
                              {col.name}
                            </td>
                            <td style={{
                              padding: '8px 10px',
                              fontFamily: 'monospace',
                              color: '#a0c4ff',
                              fontSize: 11,
                              maxWidth: 80,
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}>
                              {col.type.toUpperCase()}
                            </td>
                            <td style={{ padding: '8px 10px', textAlign: 'center' }}>
                              {col.primary_key && <span style={{ color: '#4f8cff', fontWeight: 700 }}>✓</span>}
                            </td>
                            <td style={{ padding: '8px 10px', color: col.nullable ? 'var(--platform-muted)' : '#5ccbff' }}>
                              {col.nullable ? '✓' : '✗'}
                            </td>
                            <td style={{ padding: '8px 10px' }}>
                              {flag && (
                                <span style={{
                                  background: flag.includes('PII') ? 'rgba(255,196,0,0.15)' : 'rgba(255,80,80,0.15)',
                                  color: flag.includes('PII') ? '#ffc400' : '#ff5050',
                                  borderRadius: 4,
                                  padding: '2px 6px',
                                  fontSize: 9,
                                  fontWeight: 600,
                                }}>
                                  {flag.replace('⚠ ', '')}
                                </span>
                              )}
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              )}
            </>
          )}
        </div>

        {/* RIGHT PANEL: Column details */}
        <div style={{
          background: 'var(--platform-card-bg)',
          border: '1px solid var(--platform-border)',
          borderRadius: 12,
          padding: '16px',
          overflow: 'auto',
          maxHeight: 700,
        }}>
          {!selectedCol || !selectedColumn ? (
            <div style={{ color: 'var(--platform-muted)', fontSize: 12, textAlign: 'center', padding: '20px 0' }}>
              ← Click column
            </div>
          ) : (
            <>
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: 11, color: 'var(--platform-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 6, letterSpacing: '0.08em' }}>
                  Column
                </div>
                <div style={{ fontFamily: 'monospace', fontSize: 15, fontWeight: 700, color: '#4f8cff', wordBreak: 'break-all' }}>
                  {selectedColumn.name}
                </div>
              </div>

              <div style={{ marginBottom: 16 }}>
                <div style={{ fontSize: 11, color: 'var(--platform-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 4, letterSpacing: '0.08em' }}>
                  Data Type
                </div>
                <div style={{ fontFamily: 'monospace', fontSize: 13, color: '#a0c4ff' }}>
                  {selectedColumn.type.toUpperCase()}
                </div>
              </div>

              <div style={{ marginBottom: 16 }}>
                <div style={{ fontSize: 11, color: 'var(--platform-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 8, letterSpacing: '0.08em' }}>
                  Properties
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {selectedColumn.primary_key && (
                    <span style={{ background: 'rgba(79,140,255,0.2)', color: '#4f8cff', borderRadius: 6, padding: '4px 10px', fontSize: 11, fontWeight: 600 }}>
                      Primary Key
                    </span>
                  )}
                  {selectedColumn.nullable && (
                    <span style={{ background: 'rgba(100,200,255,0.15)', color: '#5ccbff', borderRadius: 6, padding: '4px 10px', fontSize: 11 }}>
                      Nullable
                    </span>
                  )}
                  {!selectedColumn.nullable && (
                    <span style={{ background: 'rgba(255,150,0,0.15)', color: '#ffa500', borderRadius: 6, padding: '4px 10px', fontSize: 11 }}>
                      Not Null
                    </span>
                  )}
                </div>
              </div>

              {getSensitiveLabel(selectedColumn) && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 11, color: 'var(--platform-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 8, letterSpacing: '0.08em' }}>
                    Data Classification
                  </div>
                  <span style={{
                    background: getSensitiveLabel(selectedColumn)?.includes('PII') ? 'rgba(255,196,0,0.15)' : 'rgba(255,80,80,0.15)',
                    color: getSensitiveLabel(selectedColumn)?.includes('PII') ? '#ffc400' : '#ff5050',
                    borderRadius: 6,
                    padding: '6px 12px',
                    fontSize: 12,
                    fontWeight: 600,
                    display: 'inline-block',
                  }}>
                    {getSensitiveLabel(selectedColumn)}
                  </span>
                </div>
              )}

              {likelyForeignKey && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: 11, color: 'var(--platform-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 8, letterSpacing: '0.08em' }}>
                    Likely FK
                  </div>
                  <button
                    onClick={() => void loadColumns(likelyForeignKey)}
                    style={{
                      display: 'block',
                      width: '100%',
                      background: 'rgba(79,140,255,0.2)',
                      border: '1px solid rgba(79,140,255,0.4)',
                      color: '#4f8cff',
                      borderRadius: 6,
                      padding: '8px',
                      fontSize: 12,
                      cursor: 'pointer',
                      fontFamily: 'monospace',
                      fontWeight: 600,
                    }}
                  >
                    → {likelyForeignKey}
                  </button>
                </div>
              )}

              <div>
                <div style={{ fontSize: 11, color: 'var(--platform-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: 8, letterSpacing: '0.08em' }}>
                  AI Context
                </div>
                <code style={{
                  background: 'rgba(0,0,0,0.3)',
                  borderRadius: 6,
                  padding: '8px',
                  display: 'block',
                  fontSize: 11,
                  color: '#a0c4ff',
                  fontFamily: 'monospace',
                  wordBreak: 'break-all',
                }}>
                  {selectedTable}({selectedColumn.name}: {selectedColumn.type})
                </code>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
