import React from "react";
import { useQuery, useMutation } from "react-query";
import axios from "axios";

export function AFHSStatusBadge({ state }) {
  const color =
    state === "GREEN"
      ? "#4caf50"
      : state === "YELLOW"
      ? "#ffeb3b"
      : state === "ORANGE"
      ? "#ff9800"
      : state === "RED"
      ? "#f44336"
      : "#bdbdbd";
  return (
    <span
      style={{
        background: color,
        color: "#222",
        borderRadius: 6,
        padding: "2px 8px",
        fontWeight: 600,
        marginLeft: 8,
      }}
    >
      {state || "UNKNOWN"}
    </span>
  );
}

export function InvestigateMyBusinessButton({ onResult }) {
  const mutation = useMutation(
    () =>
      axios.post("/api/agent/investigate", { mode: "auto" }).then((r) => r.data),
    {
      onSuccess: onResult,
    }
  );
  return (
    <button
      onClick={() => mutation.mutate()}
      disabled={mutation.isLoading}
      style={{ fontSize: 18, padding: "10px 24px", margin: 12 }}
    >
      {mutation.isLoading ? "Investigating..." : "Investigate My Business"}
    </button>
  );
}

export function InvestigationReport({ report }) {
  if (!report) return null;
  return (
    <div style={{ margin: 24, padding: 24, border: "1px solid #ccc", borderRadius: 8 }}>
      <h2>VoxCore Investigation</h2>
      <div>
        <b>AFHS State:</b> <AFHSStatusBadge state={report.afhs_state?.afhs_state_level} />
      </div>
      <div style={{ margin: "12px 0" }}>
        <b>Insights:</b>
        <ul>
          {report.insights?.map((i, idx) => (
            <li key={idx}>{i}</li>
          ))}
        </ul>
      </div>
      <div>
        <b>Drivers:</b>
        <ul>
          {report.drivers?.map((d, idx) => (
            <li key={idx}>
              {d.metric} in {d.region}: {d.change_pct}%
            </li>
          ))}
        </ul>
      </div>
      <div>
        <b>Recommendations:</b>
        <ul>
          {report.recommendations?.map((r, idx) => (
            <li key={idx}>{r}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default function BusinessInvestigationDemo() {
  const [report, setReport] = React.useState(null);
  return (
    <div>
      <InvestigateMyBusinessButton onResult={setReport} />
      <InvestigationReport report={report} />
    </div>
  );
}
