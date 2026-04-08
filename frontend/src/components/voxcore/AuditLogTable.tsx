import React from "react";

interface AuditLogEntry {
  id: string;
  timestamp: string;
  user: string;
  action: string;
  result: "approved" | "blocked" | "pending";
}

interface AuditLogTableProps {
  entries: AuditLogEntry[];
}

export const AuditLogTable = ({ entries }: AuditLogTableProps) => {
  const resultColor = {
    approved: "text-green-400",
    blocked: "text-red-400",
    pending: "text-yellow-400",
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/10">
            <th className="text-left py-2 px-4 text-gray-400">Timestamp</th>
            <th className="text-left py-2 px-4 text-gray-400">User</th>
            <th className="text-left py-2 px-4 text-gray-400">Action</th>
            <th className="text-left py-2 px-4 text-gray-400">Result</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((entry) => (
            <tr key={entry.id} className="border-b border-white/5">
              <td className="py-2 px-4 text-gray-400">{entry.timestamp}</td>
              <td className="py-2 px-4">{entry.user}</td>
              <td className="py-2 px-4">{entry.action}</td>
              <td className={`py-2 px-4 font-semibold ${resultColor[entry.result]}`}>
                {entry.result.charAt(0).toUpperCase() + entry.result.slice(1)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
