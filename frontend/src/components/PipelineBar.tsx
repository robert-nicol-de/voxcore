// Step 3: PipelineBar (static, contract-ready)
import React from "react";

export type PipelineStage = {
  label: string;
  status: "pending" | "active" | "complete" | "error";
};

interface PipelineBarProps {
  stages: PipelineStage[];
}

export default function PipelineBar({ stages }: PipelineBarProps) {
  return (
    <div className="flex gap-24 items-center w-full justify-center">
      {stages.map((stage, idx) => (
        <div key={stage.label} className="flex flex-col items-center">
          <div
            className={
              "w-8 h-8 flex items-center justify-center rounded-full text-sm font-bold " +
              (stage.status === "active"
                ? "bg-[var(--accent-blue)] text-white shadow-[var(--glow-blue)]"
                : stage.status === "complete"
                ? "bg-[var(--accent-green)] text-white shadow-[var(--glow-green)]"
                : stage.status === "error"
                ? "bg-red-600 text-white shadow-[0_0_12px_rgba(239,68,68,0.6)]"
                : "bg-[var(--bg-secondary)] text-[var(--text-secondary)] border border-[var(--text-secondary)]")
            }
            style={{ boxShadow: stage.status === "active"
                ? "var(--glow-blue)"
                : stage.status === "complete"
                ? "var(--glow-green)"
                : stage.status === "error"
                ? "0 0 12px rgba(239,68,68,0.6)"
                : undefined }}
          >
            {idx + 1}
          </div>
          <span className="mt-2 text-xs font-medium tracking-wide text-center" style={{ color: stage.status === "pending" ? "var(--text-secondary)" : undefined }}>{stage.label}</span>
        </div>
      ))}
    </div>
  );
}
