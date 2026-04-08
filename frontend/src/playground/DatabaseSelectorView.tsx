import { Database, Plus, Settings } from 'lucide-react';

interface DatabaseConfig {
  id: string;
  name: string;
  type: 'sql' | 'warehouse' | 'analytics';
  status: 'active' | 'inactive';
  tables?: number;
  lastSync?: string;
}

interface DatabaseSelectorViewProps {
  onSelectDatabase?: (id: string) => void;
  onAddDatabase?: () => void;
}

const mockDatabases: DatabaseConfig[] = [
  {
    id: 'db1',
    name: 'Production Analytics DB',
    type: 'warehouse',
    status: 'active',
    tables: 47,
    lastSync: '2 minutes ago',
  },
  {
    id: 'db2',
    name: 'Data Lake (Parquet)',
    type: 'analytics',
    status: 'active',
    tables: 156,
    lastSync: '30 minutes ago',
  },
  {
    id: 'db3',
    name: 'Legacy System',
    type: 'sql',
    status: 'inactive',
    tables: 23,
  },
];

export function DatabaseSelectorView({
  onSelectDatabase,
  onAddDatabase,
}: DatabaseSelectorViewProps) {
  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="border-b border-white/10 px-4 py-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-white">Connected Databases</h3>
          <button
            onClick={onAddDatabase}
            className="inline-flex items-center gap-2 px-2 py-1 rounded text-xs font-medium text-sky-200 hover:text-sky-100 hover:bg-sky-500/10 transition"
          >
            <Plus className="w-4 h-4" />
            Add Database
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <div className="space-y-2 px-4 py-3">
          {mockDatabases.map((db) => (
            <div
              key={db.id}
              onClick={() => onSelectDatabase?.(db.id)}
              className="rounded-lg border border-slate-500/20 bg-slate-900/40 p-3 hover:bg-slate-900/70 cursor-pointer transition group"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3 flex-1">
                  <div className="p-2 rounded bg-sky-500/10 flex-shrink-0">
                    <Database className="w-4 h-4 text-sky-300" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="text-sm font-medium text-slate-100 group-hover:text-sky-200 transition">
                      {db.name}
                    </h4>
                    <div className="flex items-center gap-2 mt-1">
                      <span className="text-xs px-2 py-0.5 rounded bg-white/5 text-slate-300">
                        {db.type}
                      </span>
                      <span
                        className={`text-xs px-2 py-0.5 rounded ${
                          db.status === 'active'
                            ? 'bg-green-500/10 text-green-200'
                            : 'bg-gray-500/10 text-gray-300'
                        }`}
                      >
                        {db.status}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {(db.tables || db.lastSync) && (
                <div className="ml-11 mt-2 space-y-1 text-xs text-slate-400">
                  {db.tables && <p>{db.tables} tables available</p>}
                  {db.lastSync && <p>Synced {db.lastSync}</p>}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      <div className="border-t border-white/10 px-4 py-3">
        <button className="w-full inline-flex items-center justify-center gap-2 px-3 py-2 rounded-lg bg-sky-500/10 hover:bg-sky-500/15 border border-sky-500/30 text-sky-200 text-sm font-medium transition">
          <Settings className="w-4 h-4" />
          Configure Connection Settings
        </button>
      </div>
    </div>
  );
}
