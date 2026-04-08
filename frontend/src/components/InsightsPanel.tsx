import QueryInspector from "./QueryInspector";
import Chart from "./Chart";
import Suggestions from "./Suggestions";

export default function InsightsPanel({ response }) {
  if (!response) return <div>No data yet</div>;
  return (
    <div className="space-y-6">
      {/* QUERY INSPECTOR */}
      <QueryInspector data={response.query_inspector} />
      {/* CHART */}
      <Chart data={response.data} config={response.chart} />
      {/* SUGGESTIONS */}
      <Suggestions suggestions={response.suggestions} />
    </div>
  );
}
