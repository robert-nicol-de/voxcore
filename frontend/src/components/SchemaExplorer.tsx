import { X, Database, Table2, Columns, ChevronDown } from 'lucide-react';
import { useState, useEffect } from 'react';

interface Column {
  name: string;
  type: string;
  nullable: boolean;
}

interface Table {
  name: string;
  columns: Column[];
}

interface SchemaExplorerProps {
  onClose: () => void;
}

export default function SchemaExplorer({ onClose }: SchemaExplorerProps) {
  const [tables, setTables] = useState<Table[]>([]);
  const [expandedTables, setExpandedTables] = useState<Set<string>>(new Set());
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSchema = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/schema');
        if (!response.ok) {
          throw new Error('Failed to fetch schema');
        }
        const data = await response.json();
        
        // Transform backend schema to component format
        const transformedTables = data.tables.map((table: any) => ({
          name: table.name,
          columns: table.columns.map((col: any) => ({
            name: col.name,
            type: col.type,
            nullable: col.nullable !== false,
          })),
        }));
        
        setTables(transformedTables);
        if (transformedTables.length > 0) {
          setExpandedTables(new Set([transformedTables[0].name]));
        }
      } catch (error) {
        console.error('Error fetching schema:', error);
        // Fallback to mock data if API fails
        const mockTables = [
          {
            name: 'ACCOUNTS',
            columns: [
              { name: 'ACCOUNT_ID', type: 'VARCHAR', nullable: false },
              { name: 'ACCOUNT_NUMBER', type: 'TEXT', nullable: false },
              { name: 'ACCOUNT_NAME', type: 'TEXT', nullable: true },
              { name: 'BALANCE', type: 'DECIMAL', nullable: true },
              { name: 'OPEN_DATE', type: 'DATE', nullable: true },
              { name: 'STATUS', type: 'VARCHAR', nullable: true },
            ],
          },
          {
            name: 'TRANSACTIONS',
            columns: [
              { name: 'TRANSACTION_ID', type: 'NUMBER', nullable: false },
              { name: 'ACCOUNT_ID', type: 'NUMBER', nullable: false },
              { name: 'TRANSACTION_DATE', type: 'TIMESTAMP', nullable: false },
              { name: 'AMOUNT', type: 'DECIMAL', nullable: false },
              { name: 'DESCRIPTION', type: 'TEXT', nullable: true },
            ],
          },
        ];
        setTables(mockTables);
        setExpandedTables(new Set(['ACCOUNTS']));
      } finally {
        setLoading(false);
      }
    };

    fetchSchema();
  }, []);

  const toggleTable = (tableName: string) => {
    const newExpanded = new Set(expandedTables);
    if (newExpanded.has(tableName)) {
      newExpanded.delete(tableName);
    } else {
      newExpanded.add(tableName);
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
          <span style={styles.tableCount}>({tables.length} tables)</span>
        </div>
        <button 
          onClick={onClose} 
          style={styles.closeButton}
        >
          <X size={20} />
        </button>
      </div>

      {/* Content */}
      <div style={styles.content}>
        {loading ? (
          <div style={styles.loadingText}>Loading schema...</div>
        ) : tables.length === 0 ? (
          <div style={styles.loadingText}>No tables found</div>
        ) : (
          tables.map((table) => (
            <div key={table.name} style={styles.tableGroup}>
              {/* Table Header */}
              <button
                onClick={() => toggleTable(table.name)}
                style={styles.tableButton}
              >
                <ChevronDown
                  size={16}
                  style={{
                    transform: expandedTables.has(table.name) ? 'rotate(0deg)' : 'rotate(-90deg)',
                    transition: 'transform 0.2s',
                    color: '#a78bfa',
                  }}
                />
                <Table2 size={16} style={{ color: '#a78bfa' }} />
                <h3 style={styles.tableName}>{table.name}</h3>
                <span style={styles.columnCount}>({table.columns.length})</span>
              </button>

              {/* Columns */}
              {expandedTables.has(table.name) && (
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
                        {col.nullable && (
                          <span style={styles.nullableBadge}>
                            nullable
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))
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
  
  loadingText: {
    color: '#94a3b8',
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
  
  nullableBadge: {
    color: '#fbbf24',
    background: 'rgba(251, 191, 36, 0.1)',
    padding: '2px 6px',
    borderRadius: '3px',
    fontSize: '11px',
  },
};
