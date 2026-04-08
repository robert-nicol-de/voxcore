import {
  Bar,
  BarChart,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from "recharts";

export function ResultChartCard({
  chart,
  data,
  onSelectPoint,
}) {
  if (!chart || !data?.length) {
    return (
      <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
          Visualization
        </p>
        <div className="mt-4 flex min-h-[320px] items-center justify-center rounded-2xl border border-dashed border-white/10 bg-black/20">
          <p className="text-sm text-slate-400">
            No chart available for this response yet.
          </p>
        </div>
      </div>
    );
  }

  const handleClick = (entry) => {
    onSelectPoint?.(entry);
  };

  const COLORS = [
    "#3b82f6", // blue
    "#06b6d4", // cyan
    "#10b981", // emerald
    "#f59e0b", // amber
    "#ef4444", // red
    "#8b5cf6", // violet
  ];

  return (
    <div className="rounded-3xl border border-white/10 bg-white/5 p-5">
      <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
        Visualization
      </p>
      <h3 className="mt-2 text-lg font-semibold text-white">
        {chart.title || "Query Results"}
      </h3>

      <div className="mt-6 h-[350px] rounded-2xl border border-white/5 bg-black/20 p-4">
        <ResponsiveContainer width="100%" height="100%">
          {chart.type === "line" ? (
            <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
              <XAxis
                dataKey={chart.xKey || Object.keys(data[0])[0]}
                stroke="#94a3b8"
                tickLine={false}
                axisLine={false}
              />
              <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #475569",
                  borderRadius: "8px",
                  color: "#f1f5f9",
                }}
                cursor={{ stroke: "#0087ff" }}
              />
              <Line
                type="monotone"
                dataKey={chart.yKey || Object.keys(data[0])[1]}
                stroke="#0087ff"
                dot={false}
                isAnimationActive
                strokeWidth={2}
              />
            </LineChart>
          ) : chart.type === "pie" ? (
            <PieChart>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #475569",
                  borderRadius: "8px",
                  color: "#f1f5f9",
                }}
              />
              <Pie
                data={data}
                dataKey={chart.yKey || Object.keys(data[0])[1]}
                nameKey={chart.xKey || Object.keys(data[0])[0]}
                cx="50%"
                cy="50%"
                outerRadius={100}
                onClick={({ payload }) => handleClick(payload)}
                isAnimationActive
              >
                {data.map((entry, idx) => (
                  <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          ) : (
            // Default: bar chart
            <BarChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
              <XAxis
                dataKey={chart.xKey || Object.keys(data[0])[0]}
                stroke="#94a3b8"
                tickLine={false}
                axisLine={false}
              />
              <YAxis stroke="#94a3b8" tickLine={false} axisLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#1e293b",
                  border: "1px solid #475569",
                  borderRadius: "8px",
                  color: "#f1f5f9",
                }}
                cursor={{ fill: "rgba(0, 135, 255, 0.1)" }}
              />
              <Bar
                dataKey={chart.yKey || Object.keys(data[0])[1]}
                fill="#0087ff"
                radius={[8, 8, 0, 0]}
                onClick={({ payload }) => handleClick(payload)}
                isAnimationActive
              />
            </BarChart>
          )}
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default ResultChartCard;
