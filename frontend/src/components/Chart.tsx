import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";

export default function Chart({ data }) {
  return (
    <BarChart width={600} height={300} data={data}>
      <XAxis dataKey="region" />
      <YAxis />
      <Tooltip />
      <Bar dataKey="value" />
    </BarChart>
  );
}
