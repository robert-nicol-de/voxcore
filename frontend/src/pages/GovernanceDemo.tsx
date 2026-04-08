// Step 6: Demo page to wire up layout and components (static pipeline)
import React from "react";
import GovernanceLayout from "../layouts/GovernanceLayout";
import PipelineBar, { PipelineStage } from "../components/PipelineBar";
import StatusStack from "../components/StatusStack";
import RiskBadge from "../components/RiskBadge";

// Static pipeline object for demo
const pipeline = {
  validated: true,
  rewritten: true,
  risk_score: 18,
  status: "success",
};

function mapPipeline(pipeline: any): PipelineStage[] {
  return [
    { label: "Question", status: "complete" },
    { label: "Validation", status: pipeline.validated ? "complete" : "pending" },
    { label: "Risk", status: "complete" },
    {
      label: "Execution",
      status: pipeline.status === "blocked" ? "error" : "complete",
    },
    { label: "Insight", status: "complete" },
  ];
}

function buildStatusStack(pipeline: any): string[] {
  const items = [];
  if (pipeline.validated) items.push("Validated");
  if (pipeline.rewritten) items.push("Rewritten");
  if (pipeline.status === "blocked") {
    items.push("Blocked");
  } else {
    items.push("Governed");
  }
  return items;
}

export default function GovernanceDemo() {
  return (
    <GovernanceLayout>
      <PipelineBar stages={mapPipeline(pipeline)} />
      <StatusStack items={buildStatusStack(pipeline)} />
      <RiskBadge riskScore={pipeline.risk_score} />
      {/* Insight placeholder (after governance) */}
      <div className="mt-16 text-center text-lg text-[var(--text-secondary)]">Insight will appear here after governance.</div>
    </GovernanceLayout>
  );
}
