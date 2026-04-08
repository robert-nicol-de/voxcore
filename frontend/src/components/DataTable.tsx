type Props = {
  data: any[];
};

export default function DataTable({ data }: Props) {
  if (!data || data.length === 0) return null;

  const columns = Object.keys(data[0]);

  return (
    <div style={{ overflowX: "auto", marginTop: "16px" }}>
      <table style={{ width: "100%", borderCollapse: "collapse" }}>
        <thead>
          <tr>
            {columns.map((col) => (
              <th
                key={col}
                style={{
                  textAlign: "left",
                  padding: "8px",
                  borderBottom: "1px solid #333",
                }}
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={i}>
              {columns.map((col) => (
                <td
                  key={col}
                  style={{
                    padding: "8px",
                    borderBottom: "1px solid #222",
                  }}
                >
                  {row[col]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
