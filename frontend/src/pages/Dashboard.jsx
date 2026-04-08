import React, { useEffect, useState } from "react";
import Layout from "../components/layout/Layout";
import PageHeader from "../components/PageHeader";
import AnimatedKPI from "../components/AnimatedKPI";
import FirewallStats from "../components/FirewallStats";
import LiveActivity from "../components/LiveActivity";
import LiveQueryFlow from "../components/LiveQueryFlow";
import PipelineAnimation from "../components/PipelineAnimation";
import InsightCard from "../components/InsightCard";
import SmartLoading from "../components/SmartLoading";
import ErrorFeedback from "../components/ErrorFeedback";
import { EMDPanel } from "../components";

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [insights, setInsights] = useState([]);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchDashboard = async () => {
    try {
      // Use correct API base URL
      const API_BASE = "http://127.0.0.1:8000";
      // Only fetch insights for now (others are missing endpoints)
      const [insightsRes] = await Promise.all([
        fetch(`${API_BASE}/api/insights/latest`),
        // fetch(`${API_BASE}/api/metrics`),
        // fetch(`${API_BASE}/api/v1/query/logs`),
      ]);

      // const metricsData = await metricsRes.json();
      const insightsData = await insightsRes.json();
      // const logsData = await logsRes.json();

      // setMetrics(metricsData);
      setInsights(insightsData.insights || []);
      // setLogs(logsData.logs || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
    const interval = setInterval(fetchDashboard, 5000); // polling
    return () => clearInterval(interval);
  }, []);

  if (loading) return <SmartLoading />;


  return (
    <Layout>
      <PageHeader
        title="VoxCore Control Center"
        subtitle="Monitor, protect, and understand your data in real time"
      />

      {/* KPI STRIP */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <AnimatedKPI value={0} />
        <AnimatedKPI value={0} />
        <AnimatedKPI value={0} />
        <AnimatedKPI value={0} />
      </div>

      {/* LIVE SYSTEM */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        <LiveQueryFlow
          stages={[
            { label: "Received", status: "active" },
            { label: "Inspected", status: "safe" },
            { label: "Governed", status: "safe" },
            { label: "Executed", status: "safe" },
          ]}
        />
        <PipelineAnimation />
      </div>

      {/* GOVERNANCE */}
      {/* Commented out FirewallStats until endpoint exists */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* <FirewallStats metrics={metrics} /> */}
        <div className="card">Risk Distribution Chart</div>
      </div>

      {/* INSIGHTS */}
      <div className="grid grid-cols-3 gap-6 mb-8">
        {insights.slice(0, 6).map((insight, i) => (
          <InsightCard key={i} {...insight} />
        ))}
      </div>

      {/* ACTIVITY */}
      {/* Commented out LiveActivity until endpoint exists */}
      <div className="grid grid-cols-2 gap-6 mb-8">
        {/* <LiveActivity logs={logs} /> */}
        <div className="card">Query Timeline</div>
      </div>

      {/* PRIMARY CTA: EXPLAIN MY DATA */}
      <div className="col-span-3">
        <EMDPanel />
      </div>
    </Layout>
  );
}
