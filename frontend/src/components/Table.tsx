import SkeletonTable from "./SkeletonTable";

interface TableProps {
  data: Array<Record<string, any>>;
  loading?: boolean;
}

export default function Table({ data, loading }: TableProps) {
  if (loading || !data || data.length === 0) return <SkeletonTable />;
  const columns = Object.keys(data[0] || {});
  return (
    <div className="overflow-x-auto rounded-xl border border-[var(--border-default)] bg-[var(--bg-surface)] mb-4">
      <table className="min-w-full text-sm">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col} className="sticky top-0 bg-[var(--bg-elevated)] text-left px-4 py-2 font-semibold text-[var(--text-primary)]">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i} className="hover:bg-[var(--bg-hover)] transition">
              {columns.map((col) => (
                <td key={col} className="px-4 py-2 border-t border-[var(--border-default)]">{String(row[col] ?? "")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
