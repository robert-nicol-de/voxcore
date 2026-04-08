import React, { useEffect, useState } from "react";

// ImpactSummary: Shows total impact, successful/failed actions for the week
export function ImpactSummary() {
  const [summary, setSummary] = useState<{
    totalImpact: number;
    successCount: number;
    failCount: number;
  }>({ totalImpact: 0, successCount: 0, failCount: 0 });

  useEffect(() => {
    fetch("/api/actions/impact-summary")
      .then(res => res.json())
      .then(data => {
        setSummary({
          totalImpact: data.total_impact || 0,
          successCount: data.success_count || 0,
          failCount: data.fail_count || 0,
        });
      });
  }, []);

  return (
    <div className="mb-6 p-4 bg-blue-50 rounded-xl flex items-center gap-8 shadow">
      <div className="text-2xl font-bold text-blue-700">
        +{summary.totalImpact.toFixed(1)}% revenue recovered
      </div>
      <div className="text-md text-green-700">
        {summary.successCount} successful actions
      </div>
      <div className="text-md text-red-600">
        {summary.failCount} failed action{summary.failCount !== 1 ? "s" : ""}
      </div>
    </div>
  );
}
