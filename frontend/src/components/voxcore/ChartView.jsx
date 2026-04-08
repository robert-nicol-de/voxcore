import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import SkeletonChart from "../SkeletonChart";

export default function ChartView({ data, loading, onSelectPoint }) {
  if (loading) return <SkeletonChart />;
  if (!data) return <div className="card">No data</div>;

  const handleBarClick = (entry) => {
    if (onSelectPoint) {
      onSelectPoint(entry);
    }
  };

  return (
    <div className="card">
      <h3>Revenue Trend</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} onClick={(state) => {
          if (state && state.activeTooltipIndex !== undefined) {
            handleBarClick(data[state.activeTooltipIndex]);
          }
        }}>
          <XAxis dataKey="month" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="revenue" stroke="#3b82f6" onClick={handleBarClick} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
