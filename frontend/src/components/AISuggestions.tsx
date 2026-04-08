"use client";

import { useState } from "react";
import axios from "axios";
import { useBuildStore } from "@/store/useBuildStore";

export default function AISuggestions() {
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const { fetchStatus } = useBuildStore();

  const generate = async () => {
    const res = await axios.post("/api/build/auto-tasks");
    setSuggestions(res.data.suggestions);
  };

  const approve = async (task: any) => {
    await axios.post("/api/build/approve-task", task);
    fetchStatus();
  };

  return (
    <div className="bg-zinc-900 p-4 rounded mt-6">
      <h2 className="text-lg font-semibold mb-2">AI Suggestions</h2>

      <button
        onClick={generate}
        className="bg-purple-600 px-4 py-2 rounded mb-4"
      >
        🧠 Generate Suggestions
      </button>

      <div className="space-y-3">
        {suggestions.map((task, i) => (
          <div key={i} className="bg-zinc-800 p-3 rounded border border-purple-500">
            <div className="font-semibold flex items-center">
              {task.description}
              <span className="text-xs bg-purple-600 px-2 py-1 rounded ml-2">AI</span>
            </div>
            <div className="text-sm mt-1 text-gray-400">
              {task.reason}
            </div>
            <div className="mt-2 flex gap-2">
              <button
                onClick={() => approve(task)}
                className="bg-green-600 px-3 py-1 rounded"
              >
                ✅ Approve
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
