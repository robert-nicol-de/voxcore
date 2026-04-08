import { useEffect, useState } from "react";

export default function AlertsPanel({ userId }: { userId: string }) {
  const [alerts, setAlerts] = useState<any[]>([]);

  const fetchAlerts = async () => {
    const res = await fetch(`/api/alerts/${userId}`);
    const data = await res.json();
    setAlerts(data.alerts || []);
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 30000);
    return () => clearInterval(interval);
  }, [userId]);

  return (
    <div className="mt-6">
      <h3 className="font-bold mt-4 text-lg">🚨 Alerts</h3>
      {alerts.length === 0 ? (
        <div className="text-sm text-gray-400 mt-2">No alerts.</div>
      ) : (
        alerts.map((alert, i) => (
          <div key={i} className="border p-3 rounded mb-2 bg-red-50">
            <p className="font-semibold">
              {alert.insight.insight}
            </p>
            <p>Type: {alert.insight.type}</p>
            <p>Confidence: {alert.insight.confidence}</p>
            {alert.insight.confidence > 0.9 && (
              <span className="text-red-600 font-bold">🔥 High Priority</span>
            )}
          </div>
        ))
      )}
    </div>
  );
}
