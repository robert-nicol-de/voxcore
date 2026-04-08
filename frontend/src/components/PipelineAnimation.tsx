
import React from "react";
import "./PipelineAnimation.css";

const steps = [
  "User Prompt",
  "AI Generated SQL",
  "VoxCore Query Inspector",
  "Risk Engine",
  "Policy Engine",
  "Sandbox Execution",
  "Production Database"
];

export default function PipelineAnimation({ activeStep = 0 }: { activeStep?: number }) {
  return (
    <div className="pipeline-animation">
      {steps.map((step, idx) => (
        <div className="pipeline-step" key={step}>
          <div className={`step-circle${activeStep === idx ? " active" : ""}`}></div>
          <div className="step-label">{step}</div>
          {idx < steps.length - 1 && <div className="step-arrow">↓</div>}
        </div>
      ))}
      <div className="pipeline-glow" style={{ top: `${activeStep * 64}px` }}></div>
    </div>
  );
}
