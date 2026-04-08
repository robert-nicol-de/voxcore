interface AuditLogEntry {
  id: string;
  queryId: string;
  timestamp: string;
  user: string;
  query: string;
  platform: string;
  action: string;
  status: "blocked" | "allowed" | "reviewed";
  riskScore: number;
  executionTime?: string;
}

interface AuditLogTableProps {
  entries?: AuditLogEntry[];
  className?: string;
}

export function AuditLogTable({ entries, className = "" }: AuditLogTableProps) {
  const defaultEntries: AuditLogEntry[] = [
    {
      id: "1",
      queryId: "QRY-0001",
      timestamp: "2026-04-03 14:23:45",
      user: "alice@company.com",
      query: "DELETE FROM users",
      platform: "GPT-4",
      action: "Destructive operation detected",
      status: "blocked",
      riskScore: 100,
      executionTime: "—",
    },
    {
      id: "2",
      queryId: "QRY-0002",
      timestamp: "2026-04-03 14:15:22",
      user: "bob@company.com",
      query: "SELECT count(*) FROM users WHERE active = true",
      platform: "Claude",
      action: "Routine query",
      status: "allowed",
      riskScore: 8,
      executionTime: "3.2ms",
    },
    {
      id: "3",
      queryId: "QRY-0003",
      timestamp: "2026-04-03 14:08:10",
      user: "charlie@company.com",
      query: "SELECT user_id, email FROM users JOIN orders ON...",
      platform: "GPT-4",
      action: "Requires approval (risk > 60)",
      status: "reviewed",
      riskScore: 67,
      executionTime: "Pending",
    },
    {
      id: "4",
      queryId: "QRY-0004",
      timestamp: "2026-04-03 13:55:33",
      user: "diana@company.com",
      query: "SELECT * INTO '/tmp/backup' FROM employees",
      platform: "Custom Script",
      action: "Unauthorized data export",
      status: "blocked",
      riskScore: 98,
      executionTime: "—",
    },
  ];

  const logs = entries || defaultEntries;

  return (
    <div className={`overflow-x-auto ${className}`}>
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/10">
            <th className="text-left py-4 px-6 text-xs uppercase text-gray-500 font-semibold tracking-wider">Query ID</th>
            <th className="text-left py-4 px-6 text-xs uppercase text-gray-500 font-semibold tracking-wider">Timestamp</th>
            <th className="text-left py-4 px-6 text-xs uppercase text-gray-500 font-semibold tracking-wider">User</th>
            <th className="text-left py-4 px-6 text-xs uppercase text-gray-500 font-semibold tracking-wider">Platform</th>
            <th className="text-left py-4 px-6 text-xs uppercase text-gray-500 font-semibold tracking-wider">Query</th>
            <th className="text-left py-4 px-6 text-xs uppercase text-gray-500 font-semibold tracking-wider">Risk</th>
            <th className="text-left py-4 px-6 text-xs uppercase text-gray-500 font-semibold tracking-wider">Status</th>
            <th className="text-left py-4 px-6 text-xs uppercase text-gray-500 font-semibold tracking-wider">Time</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {logs.map((entry) => (
            <tr key={entry.id} className="hover:bg-white/5 transition-colors">
              <td className="py-4 px-6 text-blue-400 font-mono text-xs">{entry.queryId}</td>
              <td className="py-4 px-6 text-gray-400 text-xs">{entry.timestamp}</td>
              <td className="py-4 px-6 text-gray-300 text-sm">{entry.user}</td>
              <td className="py-4 px-6 text-gray-400 text-xs">{entry.platform}</td>
              <td className="py-4 px-6 text-gray-400 font-mono text-xs max-w-xs truncate">{entry.query}</td>
              <td className="py-4 px-6">
                <span
                  className={`text-xs font-semibold ${
                    entry.riskScore > 70
                      ? "text-red-400"
                      : entry.riskScore > 40
                      ? "text-yellow-400"
                      : "text-green-400"
                  }`}
                >
                  {entry.riskScore}
                </span>
              </td>
              <td className="py-4 px-6">
                <span
                  className={`px-3 py-1 rounded-full text-xs font-semibold ${
                    entry.status === "blocked"
                      ? "bg-red-500/20 text-red-400"
                      : entry.status === "allowed"
                      ? "bg-green-500/20 text-green-400"
                      : "bg-yellow-500/20 text-yellow-400"
                  }`}
                >
                  {entry.status.charAt(0).toUpperCase() + entry.status.slice(1)}
                </span>
              </td>
              <td className="py-4 px-6 text-gray-400 text-xs">{entry.executionTime}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
