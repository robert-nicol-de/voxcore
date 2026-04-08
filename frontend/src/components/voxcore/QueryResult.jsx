import InsightPanel from "./InsightPanel";
import ChartView from "./ChartView";
import Table from "../Table";

export default function QueryResult({ data, loading }) {
  if (!data) {
    // Show skeletons for chart and table while loading
    return (
      <div style={{ marginTop: 20 }}>
        <ChartView data={null} loading={true} />
        <Table data={[]} loading={true} />
      </div>
    );
  }

  // Step-by-step rendering: Chart loads first, then Table, then Insights
  return (
    <div style={{ marginTop: 20 }}>
      <ChartView data={data.result} loading={loading} />
      <Table data={data.table || []} loading={loading} />
      <InsightPanel insights={data.insight} />
    </div>
  );
}
