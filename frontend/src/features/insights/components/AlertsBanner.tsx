import { Alert } from "../types/insight";

export const AlertsBanner = ({ alerts }: { alerts: Alert[] }) => (
  <div className="w-full mb-6">
    {alerts.map((alert, i) => {
      const isCritical = alert.insight.confidence > 0.9 || alert.insight.type === "anomaly" || alert.insight.type === "anomaly_detection";
      return (
        <div
          key={i}
          className={`bg-red-600 text-white font-bold py-3 px-4 rounded-xl shadow-lg mb-2 flex items-center gap-2 ${isCritical ? "animate-pulse ring-4 ring-red-300" : ""}`}
        >
          <span className="text-2xl">🚨</span>
          <span>{alert.insight.insight}</span>
          {isCritical && <span className="ml-2 text-yellow-200 animate-bounce">HIGH PRIORITY</span>}
        </div>
      );
    })}
  </div>
);
