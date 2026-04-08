import {
  LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar
} from "recharts";

export function InsightChart({ data, config }: { data: any[]; config: any }) {
  if (!config || !data || data.length === 0) return null;

  if (config.chart === "line") {
    return (
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data}>
          <XAxis dataKey={config.x_axis} />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey={config.y_axis} stroke="#2563eb" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    );
  }
  if (config.chart === "bar") {
    return (
      <ResponsiveContainer width="100%" height={180}>
        <BarChart data={data}>
          <XAxis dataKey={config.x_axis} />
          <YAxis />
          <Tooltip />
          <Bar dataKey={config.y_axis} fill="#f59e42" />
        </BarChart>
      </ResponsiveContainer>
    );
  }
  // Add grouped_bar and other chart types as needed
  return null;
}
