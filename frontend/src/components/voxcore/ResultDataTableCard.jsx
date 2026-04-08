/**
 * Defensive normalization: accept unknown input and normalize to array
 */
function normalizeRows(rows) {
  // Already an array? Return it
  if (Array.isArray(rows)) {
    return rows;
  }

  // Wrapped structure: { rows: [...] }
  if (
    rows &&
    typeof rows === 'object' &&
    'rows' in rows &&
    Array.isArray(rows.rows)
  ) {
    return rows.rows;
  }

  // Wrapped structure: { data: [...] }
  if (
    rows &&
    typeof rows === 'object' &&
    'data' in rows &&
    Array.isArray(rows.data)
  ) {
    return rows.data;
  }

  // Wrapped structure: { result: [...] }
  if (
    rows &&
    typeof rows === 'object' &&
    'result' in rows &&
    Array.isArray(rows.result)
  ) {
    return rows.result;
  }

  // Not an array-like structure? Return empty array
  return [];
}

export function ResultDataTableCard({ rows, columns }) {
  const normalizedRows = normalizeRows(rows);

  if (!normalizedRows || normalizedRows.length === 0) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
          Data
        </p>
        <div className="mt-4 flex min-h-[160px] items-center justify-center rounded-2xl border border-dashed border-white/10 bg-black/20">
          <p className="text-sm text-slate-400">
            No tabular rows available for this response.
          </p>
        </div>
      </div>
    );
  }

  // Auto-generate columns from first row if not provided
  const displayColumns =
    columns ||
    (normalizedRows[0]
      ? Object.keys(normalizedRows[0]).map((key) => ({
          key,
          label: key
            .replace(/([A-Z])/g, ' $1')
            .replace(/^./, (c) => c.toUpperCase()),
        }))
      : []);

  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
      <div className="mb-4 flex items-center justify-between">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
          Data
        </p>
        <p className="text-xs text-slate-500">
          {normalizedRows.length} row{normalizedRows.length === 1 ? '' : 's'}
        </p>
      </div>

      <div className="overflow-hidden rounded-2xl border border-white/10">
        <div className="max-h-[400px] overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            {/* Header */}
            <thead className="bg-white/5">
              <tr>
                {displayColumns.map((col) => (
                  <th
                    key={col.key || col}
                    className="px-4 py-3 font-medium text-slate-300"
                  >
                    {col.label || col.key || col}
                  </th>
                ))}
              </tr>
            </thead>

            {/* Body */}
            <tbody>
              {normalizedRows.map((row, rowIdx) => (
                <tr
                  key={rowIdx}
                  className="border-t border-white/5 bg-black/10 transition hover:bg-white/5"
                >
                  {displayColumns.map((col) => {
                    const colKey = col.key || col;
                    const value = row[colKey];
                    const displayValue =
                      typeof value === 'number'
                        ? new Intl.NumberFormat('en-US', {
                            maximumFractionDigits: 2,
                          }).format(value)
                        : String(value || '—');

                    return (
                      <td
                        key={`${rowIdx}-${colKey}`}
                        className="px-4 py-3 text-slate-200"
                      >
                        {displayValue}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default ResultDataTableCard;
