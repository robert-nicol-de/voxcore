import React from "react";

type Props = {
  metrics: {
    totalActions: number;
    autoActions: number;
    automationRate: number;
    successRate: number;
    totalImpact: number;
  };
};

export function AutoActionMetricsPanel({ metrics }: Props) {
  return (
    <div className="p-5 bg-white rounded-2xl shadow-sm border space-y-4">
      <div className="text-sm text-gray-500">⚡ Automation Overview</div>
      <div className="grid grid-cols-3 gap-4">
        {/* Automation Rate */}
        <div>
          <div
            className={`text-xl font-semibold ${
              metrics.automationRate > 0.7
                ? "text-green-600"
                : metrics.automationRate > 0.4
                ? "text-yellow-600"
                : "text-red-600"
            }`}
          >
            {(metrics.automationRate * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500">Automated</div>
        </div>
        {/* Success Rate */}
        <div>
          <div className="text-xl font-semibold">
            {(metrics.successRate * 100).toFixed(0)}%
          </div>
          <div className="text-xs text-gray-500">Success Rate</div>
        </div>
        {/* Impact */}
        <div>
          <div className="text-xl font-semibold text-green-600">
            +{(metrics.totalImpact * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">Total Impact</div>
        </div>
      </div>
      <div className="text-xs text-gray-400">
        {metrics.autoActions} of {metrics.totalActions} actions automated
      </div>
      <div className="text-xs text-gray-500">
        VoxCore is automatically resolving {Math.round(metrics.automationRate * 100)}% of detected issues
      </div>
    </div>
  );
}
