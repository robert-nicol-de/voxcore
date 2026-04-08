import { useState } from "react";

export default function QueryReplay() {
  const steps = [
    {
      stage: "User Question",
      content: "Show revenue by region"
    },
    {
      stage: "Intent Detection",
      content: "Metric: revenue | Dimension: region"
    },
    {
      stage: "Table Selection",
      content: "sales table selected"
    },
    {
      stage: "SQL Construction",
      content: "SELECT region, SUM(revenue) FROM sales GROUP BY region"
    },
    {
      stage: "Firewall Analysis",
      content: "Risk score: 0.12 | Query allowed"
    },
    {
      stage: "Execution",
      content: "Query executed successfully"
    }
  ];

  const [currentStep, setCurrentStep] = useState(0);

  function nextStep() {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  }

  function prevStep() {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  }

  return (
    <div className="query-replay">
      <h2>AI Query Replay</h2>

      <div className="replay-stage">
        <h3>{steps[currentStep].stage}</h3>
        <pre>{steps[currentStep].content}</pre>
      </div>

      <div className="replay-controls">
        <button onClick={prevStep}>◀ Prev</button>
        <span>
          Step {currentStep + 1} / {steps.length}
        </span>
        <button onClick={nextStep}>Next ▶</button>
      </div>
    </div>
  );
}
