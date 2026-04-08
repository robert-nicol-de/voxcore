

"use client";
import { useEffect, useState } from "react";
import StatusStack from "@/components/StatusStack";
import { buildStatusStack } from "@/utils/buildStatusStack";

function sortTasks(tasks: any[]) {
  const priority = {
    blocked: 4,
    "in-progress": 3,
    "not-started": 2,
    done: 1,
  };
  return [...tasks].sort((a, b) => priority[b.status] - priority[a.status]);
}

function TaskDrawer({ task, onClose }: any) {
  if (!task) return null;
  return (
    <div className="fixed right-0 top-0 w-[400px] h-full bg-zinc-900 p-6 z-50 shadow-xl">
      <button onClick={onClose} className="mb-4 text-sm text-gray-400">Close</button>
      <h2 className="text-xl font-bold mt-4">{task.description}</h2>
      <div className="mt-4">
        <p>Status: {task.status}</p>
        <p>Owner: {task.owner || "human"}</p>
      </div>
      {task.definition_of_done && (
        <div className="mt-4">
          <h3 className="font-semibold mb-1">Definition of Done</h3>
          <ul className="list-disc ml-4">
            {task.definition_of_done.map((d: string, i: number) => (
              <li key={i}>{d}</li>
            ))}
          </ul>
        </div>
      )}
      {task.owner === "ai" && task.reason && (
        <div className="text-xs text-purple-300 mt-4">
          🧠 {task.reason}
        </div>
      )}
    </div>
  );
}

export default function Dashboard() {
  const [phases, setPhases] = useState<any[]>([]);
  const [selectedTask, setSelectedTask] = useState<any>(null);

  const fetchStatus = async () => {
    const res = await fetch("/api/build/status");
    const data = await res.json();
    setPhases(data.phases);
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const tasks = sortTasks(buildStatusStack(phases));
  const blockedCount = tasks.filter((t) => t.status === "blocked").length;

  return (
    <div className="p-6 bg-black text-white min-h-screen">
      <h1 className="text-3xl font-bold mb-6">VoxCore Build OS</h1>

      {/* 🚨 Alerts */}
      {blockedCount > 0 && (
        <div className="bg-red-900 p-3 rounded mb-4">
          🚨 {blockedCount} blocked tasks need attention
        </div>
      )}

      <StatusStack
        tasks={tasks}
        onSelectTask={setSelectedTask}
      />

      {selectedTask && (
        <TaskDrawer
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
        />
      )}
    </div>
  );
}
