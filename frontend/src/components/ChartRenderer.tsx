import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type Props = {
  data: any[];
  config: {
    type: string;
    dimension: string;
    metric: string;
  };
};

export default function ChartRenderer({ data, config }: Props) {
  if (!data || !config) return null;

  const { type, dimension, metric } = config;

  return (
    <div style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        {type === "line" ? (
          <LineChart data={data}>
            <XAxis dataKey={dimension} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey={metric} />
          </LineChart>
        ) : (
          <BarChart data={data}>
            <XAxis dataKey={dimension} />
            <YAxis />
            <Tooltip />
            <Bar dataKey={config.y_axis || metric} fill="#3b82f6" radius={[6, 6, 0, 0]} />
          </BarChart>
        )}
      </ResponsiveContainer>
    </div>
  );
}