import { useState } from "react";
import { WorkflowReplay } from "./WorkflowReplay";

export function SimulationRunner({ workflow }) {
  const [events, setEvents] = useState([]);
  const [running, setRunning] = useState(false);

  const runSimulation = async () => {
    setRunning(true);
    setEvents([]);
    const res = await fetch("/api/workflows/simulate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(workflow)
    });
    const data = await res.json();
    setEvents(data.events);
  };

  return (
    <div>
      <button
        onClick={runSimulation}
        className="px-4 py-2 bg-blue-600 text-white rounded-lg"
      >
        ▶ Run Simulation
      </button>
      {running && <WorkflowReplay events={events} />}
    </div>
  );
}
