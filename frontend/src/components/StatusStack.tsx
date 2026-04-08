import React from "react";

type Task = {
  id: string;
  description: string;
  status: "not-started" | "in-progress" | "done" | "blocked";
  owner?: string;
};

type Props = {
  tasks: Task[];
  onSelectTask?: (task: Task) => void;
};

export default function StatusStack({ tasks, onSelectTask }: Props) {
  return (
    <div className="space-y-2">
      {tasks.map((task) => {
        const statusColor =
          task.status === "done"
            ? "bg-green-500/20 text-green-400"
            : task.status === "blocked"
            ? "bg-red-500/20 text-red-400"
            : task.status === "in-progress"
            ? "bg-yellow-500/20 text-yellow-400"
            : "bg-zinc-800 text-gray-300";

        const isAI = task.owner === "ai";

        return (
          <div
            key={task.id}
            onClick={() => onSelectTask?.(task)}
            className={`p-3 rounded cursor-pointer transition-all
              ${statusColor}
              ${isAI ? "border border-purple-500 bg-purple-900/20" : ""}
            `}
          >
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span>{task.description}</span>

                {isAI && (
                  <span className="text-xs bg-purple-600 px-2 py-0.5 rounded">
                    AI
                  </span>
                )}
              </div>

              <span className="text-xs uppercase opacity-70">
                {task.status}
              </span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
