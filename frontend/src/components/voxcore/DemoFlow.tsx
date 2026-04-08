import React from "react";

interface DemoFlowStep {
  id: number;
  title: string;
  description: string;
  completed: boolean;
}

interface DemoFlowProps {
  steps: DemoFlowStep[];
}

export const DemoFlow = ({ steps }: DemoFlowProps) => {
  return (
    <div className="space-y-6">
      {steps.map((step, index) => (
        <div key={step.id} className="flex gap-4">
          {/* Step indicator */}
          <div className="flex flex-col items-center">
            <div
              className={`
              w-10 h-10 rounded-full flex items-center justify-center font-semibold
              ${
                step.completed
                  ? "bg-green-500/20 text-green-400 border border-green-500/30"
                  : "bg-blue-500/20 text-blue-400 border border-blue-500/30"
              }
            `}
            >
              {step.completed ? "✓" : step.id}
            </div>
            {index < steps.length - 1 && (
              <div className="w-1 h-12 bg-gray-700 my-2" />
            )}
          </div>

          {/* Step content */}
          <div className="flex-1 pt-1">
            <h4 className="font-semibold text-white">{step.title}</h4>
            <p className="text-gray-400 text-sm mt-1">{step.description}</p>
          </div>
        </div>
      ))}
    </div>
  );
};
