import { X, Database, Table2, Columns, ChevronDown } from 'lucide-react';
import { useState, useEffect } from 'react';
import { apiUrl } from '../lib/api';

interface Column {
  name: string;
  type: string;
}

interface Table {
  schema: string;
  name: string;
  fullName: string;
  columns: Column[];
}

interface ViewItem {
  schema: string;
  name: string;
  fullName: string;
}

interface SchemaExplorerProps {
  onClose: () => void;
}

export default function SchemaExplorer({ onClose }: SchemaExplorerProps) {
  const [databases, setDatabases] = useState<string[]>([]);
  const [selectedDatabase, setSelectedDatabase] = useState('');
  const [tables, setTables] = useState<Table[]>([]);
  const [views, setViews] = useState<ViewItem[]>([]);
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);
  const [loadingDatabase, setLoadingDatabase] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const bootstrap = async () => {
      try {
        setLoading(true);
        setError(null);

        const dbRes = await fetch(apiUrl('/api/v1/schema/databases'));
        if (!dbRes.ok) {
          throw new Error('Failed to fetch databases');
        }

        const dbData = await dbRes.json();
        const availableDatabases: string[] = dbData.databases || [];
        setDatabases(availableDatabases);

        const preferred =
          localStorage.getItem('dbDatabase') ||
          dbData.current_database ||
          (availableDatabases.length > 0 ? availableDatabases[0] : '');

        setSelectedDatabase(preferred);
      } catch (fetchError: any) {
        console.error('Error fetching database list:', fetchError);
        setError(fetchError?.message || 'Failed to load schema explorer');
      } finally {
        setLoading(false);
      }
    };

    bootstrap();
  }, []);

  useEffect(() => {
    const fetchSchemaForDatabase = async () => {
      if (!selectedDatabase) {
        setTables([]);
        setViews([]);
        return;
      }

      try {
        setLoadingDatabase(true);
        setError(null);

        const [tablesRes, columnsRes, viewsRes] = await Promise.all([
          fetch(apiUrl(`/api/v1/schema/tables?database=${encodeURIComponent(selectedDatabase)}`)),
          fetch(apiUrl(`/api/v1/schema/columns?database=${encodeURIComponent(selectedDatabase)}`)),
          fetch(apiUrl(`/api/v1/schema/views?database=${encodeURIComponent(selectedDatabase)}`)),
        ]);

        if (!tablesRes.ok || !columnsRes.ok || !viewsRes.ok) {
          throw new Error('Failed to fetch schema metadata');
        }

        const tablesData = await tablesRes.json();
        const columnsData = await columnsRes.json();
        const viewsData = await viewsRes.json();

        const columnsByTable = new Map<string, Column[]>();
        for (const col of columnsData.columns || []) {
          const fullName = `${col.table_schema}.${col.table_name}`;
          const existing = columnsByTable.get(fullName) || [];
          existing.push({ name: col.column_name, type: col.data_type });
          columnsByTable.set(fullName, existing);
        }

        const discoveredTables: Table[] = (tablesData.tables || []).map((table: any) => ({
          schema: table.table_schema,
          name: table.table_name,
          fullName: table.full_name,
          columns: columnsByTable.get(table.full_name) || [],
        }));

        const discoveredViews: ViewItem[] = (viewsData.views || []).map((view: any) => ({
          schema: view.table_schema,
          name: view.table_name,
          fullName: view.full_name,
        }));

        setTables(discoveredTables);
        setViews(discoveredViews);
        if (discoveredTables.length > 0) {
          setExpandedTables(new Set([discoveredTables[0].fullName]));
        } else {
          setExpandedTables(new Set());
        }
      } catch (fetchError: any) {
        console.error('Error fetching schema details:', fetchError);
        setTables([]);
        setViews([]);
        setError(fetchError?.message || 'Failed to load schema metadata');
      } finally {
        setLoadingDatabase(false);
      }
    };

    fetchSchemaForDatabase();
  }, [selectedDatabase]);

  const toggleTable = (tableFullName: string) => {
    const newExpanded = new Set(expandedTables);
    if (newExpanded.has(tableFullName)) {
      newExpanded.delete(tableFullName);
    } else {
      newExpanded.add(tableFullName);
    }
    setExpandedTables(newExpanded);
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.headerTitle}>
          <Database size={20} style={{ color: '#a78bfa' }} />
          <h2 style={styles.title}>Schema Explorer</h2>
          <span style={styles.tableCount}>({tables.length} tables, {views.length} views)</span>
        </div>
        <button 
          onClick={onClose} 
          style={styles.closeButton}
        >
          <X size={20} />
        </button>
      </div>

      <div style={styles.selectorSection}>
        <label style={styles.selectorLabel}>Database</label>
        <select
          value={selectedDatabase}
          onChange={(event) => setSelectedDatabase(event.target.value)}
          style={styles.selectorInput}
        >
          {databases.map((db) => (
            <option key={db} value={db}>
              {db}
            </option>
          ))}
        </select>
      </div>

      {/* Content */}
      <div style={styles.content}>
        {loading || loadingDatabase ? (
          <div style={styles.loadingText}>Loading schema...</div>
        ) : error ? (
          <div style={styles.errorText}>{error}</div>
        ) : tables.length === 0 ? (
          <div style={styles.loadingText}>No tables found for this database</div>
        ) : (
          <>
            <h3 style={styles.sectionTitle}>Tables</h3>
            {tables.map((table) => (
            <div key={table.fullName} style={styles.tableGroup}>
              {/* Table Header */}
              <button
                onClick={() => toggleTable(table.fullName)}
                style={styles.tableButton}
              >
                <ChevronDown
                  size={16}
                  style={{
                    transform: expandedTables.has(table.fullName) ? 'rotate(0deg)' : 'rotate(-90deg)',
                    transition: 'transform 0.2s',
                    color: '#a78bfa',
                  }}
                />
                <Table2 size={16} style={{ color: '#a78bfa' }} />
                <h3 style={styles.tableName}>{table.fullName}</h3>
                <span style={styles.columnCount}>({table.columns.length})</span>
              </button>

              {/* Columns */}
              {expandedTables.has(table.fullName) && (
                <div style={styles.columnsContainer}>
                  {table.columns.map((col) => (
                    <div
                      key={col.name}
                      style={styles.columnRow}
                    >
                      <div style={styles.columnLeft}>
                        <Columns size={12} style={{ color: '#64748b', flexShrink: 0 }} />
                        <span style={styles.columnName}>{col.name}</span>
                      </div>
                      <div style={styles.columnRight}>
                        <span style={styles.columnType}>{col.type}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}

            <h3 style={styles.sectionTitle}>Views</h3>
            {views.length === 0 ? (
              <div style={styles.loadingText}>No views found</div>
            ) : (
              views.map((view) => (
                <div key={view.fullName} style={styles.viewRow}>
                  <Table2 size={14} style={{ color: '#94a3b8' }} />
                  <span style={styles.viewText}>{view.fullName}</span>
                </div>
              ))
            )}
          </>
        )}
      </div>
    </div>
  );
}

const styles: { [key: string]: React.CSSProperties } = {
  container: {
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    background: '#0f172a',
    borderLeft: '1px solid #1e293b',
  },
  
  header: {
    padding: '16px',
    borderBottom: '1px solid #1e293b',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexShrink: 0,
  },
  
  headerTitle: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
  },
  
  title: {
    fontWeight: '600',
    fontSize: '18px',
    margin: 0,
  },
  
  tableCount: {
    fontSize: '12px',
    color: '#64748b',
  },
  
  closeButton: {
    background: 'transparent',
    border: 'none',
    color: '#94a3b8',
    cursor: 'pointer',
    padding: '4px',
    borderRadius: '4px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.2s',
  },
  
  content: {
    flex: 1,
    overflowY: 'auto',
    padding: '16px',
  },

  selectorSection: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px',
    padding: '12px 16px',
    borderBottom: '1px solid #1e293b',
  },

  selectorLabel: {
    color: '#94a3b8',
    fontSize: '12px',
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    fontWeight: 700,
  },

  selectorInput: {
    background: '#111827',
    color: '#e5e7eb',
    border: '1px solid #334155',
    borderRadius: '6px',
    padding: '8px 10px',
    fontSize: '13px',
  },

  sectionTitle: {
    margin: '6px 0 10px',
    color: '#cbd5e1',
    fontSize: '13px',
    textTransform: 'uppercase',
    letterSpacing: '0.08em',
  },
  
  loadingText: {
    color: '#94a3b8',
    fontSize: '14px',
  },

  errorText: {
    color: '#fca5a5',
    fontSize: '14px',
  },
  
  tableGroup: {
    marginBottom: '12px',
  },
  
  tableButton: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    color: '#a78bfa',
    background: 'transparent',
    border: 'none',
    cursor: 'pointer',
    padding: '8px 0',
    fontSize: '14px',
    transition: 'all 0.2s',
  },
  
  tableName: {
    fontWeight: '500',
    fontSize: '14px',
    margin: 0,
  },
  
  columnCount: {
    fontSize: '12px',
    color: '#64748b',
  },
  
  columnsContainer: {
    paddingLeft: '24px',
  },
  
  columnRow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    color: '#cbd5e1',
    fontSize: '13px',
    padding: '4px 8px',
    borderRadius: '4px',
    transition: 'all 0.2s',
    marginBottom: '4px',
  },
  
  columnLeft: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    minWidth: 0,
  },
  
  columnName: {
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  
  columnRight: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginLeft: '8px',
    flexShrink: 0,
  },
  
  columnType: {
    color: '#94a3b8',
    fontSize: '12px',
  },
  
  viewRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '6px 8px',
    borderRadius: '4px',
    color: '#94a3b8',
    fontSize: '13px',
    marginBottom: '4px',
  },

  viewText: {
    color: '#cbd5e1',
  },
};
