import { useState, useEffect } from "react";

interface DemoFlowProps {
  className?: string;
}

export function DemoFlow({ className = "" }: DemoFlowProps) {
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveStep((prev) => (prev + 1) % 4);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const steps = [
    {
      icon: "🤖",
      label: "AI Parser",
      description: "Natural language → SQL",
      color: "from-blue-600 to-blue-400",
    },
    {
      icon: "📝",
      label: "SQL Generation",
      description: "Semantic SQL created",
      color: "from-purple-600 to-purple-400",
    },
    {
      icon: "🛡️",
      label: "VoxCore Analysis",
      description: "Risk score calculated",
      color: "from-pink-600 to-pink-400",
    },
    {
      icon: "✅",
      label: "Safe Execution",
      description: "Query executed safely",
      color: "from-green-600 to-green-400",
    },
  ];

  return (
    <div className={`${className}`}>
      {/* Pipeline Visualization */}
      <div className="bg-gradient-to-b from-blue-600/5 to-transparent border border-white/10 rounded-2xl p-8 mb-8">
        <div className="grid grid-cols-4 gap-4">
          {steps.map((step, idx) => (
            <div key={idx} className="relative">
              {/* Connection Line */}
              {idx < steps.length - 1 && (
                <div
                  className={`absolute top-12 left-1/2 w-12 h-0.5 bg-gradient-to-r opacity-30 transition-opacity duration-1000 ${
                    activeStep >= idx ? "opacity-100" : "opacity-30"
                  }`}
                  style={{
                    backgroundImage: "linear-gradient(to right, rgb(59, 130, 246), transparent)",
                  }}
                />
              )}

              {/* Step Circle */}
              <div
                className={`relative h-24 flex flex-col items-center justify-center rounded-2xl border transition-all duration-500 ${
                  activeStep === idx
                    ? `bg-gradient-to-b ${step.color} bg-opacity-20 border-white/30 shadow-lg shadow-blue-500/20`
                    : "bg-white/5 border-white/10"
                }`}
              >
                <div className="text-4xl mb-1">{step.icon}</div>
                <div className="text-xs font-semibold text-center">{step.label}</div>
              </div>

              {/* Description */}
              <div className="mt-3 text-center">
                <p className="text-xs text-gray-400">{step.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Live Example */}
      <div className="space-y-4">
        <div className="bg-[#111827] border border-white/10 rounded-2xl p-6">
          <div className="text-xs uppercase text-gray-500 tracking-wider mb-2">Input</div>
          <p className="text-gray-300">
            "Show me the top 5 customers by revenue from the last quarter"
          </p>
        </div>

        {activeStep === 1 && (
          <div className="bg-[#111827] border border-white/10 rounded-2xl p-6">
            <div className="text-xs uppercase text-gray-500 tracking-wider mb-2">SQL Generated</div>
            <pre className="text-green-400 text-xs overflow-x-auto">
              <code>{`SELECT customer_id, SUM(amount) as revenue
FROM orders
WHERE order_date >= DATE_TRUNC('quarter', CURRENT_DATE)
GROUP BY customer_id
ORDER BY revenue DESC
LIMIT 5`}</code>
            </pre>
          </div>
        )}

        {activeStep === 2 && (
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-red-500/10 border border-red-500/30 rounded-2xl p-4">
              <div className="text-xs text-gray-500 uppercase mb-2">Risk Score</div>
              <div className="text-3xl font-bold text-red-400">28</div>
            </div>
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-2xl p-4">
              <div className="text-xs text-gray-500 uppercase mb-2">Policy Check</div>
              <div className="text-sm text-blue-400">No violations</div>
            </div>
            <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-2xl p-4">
              <div className="text-xs text-gray-500 uppercase mb-2">Sensitivity</div>
              <div className="text-sm text-yellow-400">Customer data</div>
            </div>
          </div>
        )}

        {activeStep === 3 && (
          <div className="bg-green-500/10 border border-green-500/30 rounded-2xl p-6">
            <div className="text-xs uppercase text-gray-500 tracking-wider mb-2">Result</div>
            <div className="space-y-2 text-sm text-gray-300">
              <p>✓ Query passed all security policies</p>
              <p>✓ Risk score 28 is within safe limits</p>
              <p>✓ Executing on primary database...</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
