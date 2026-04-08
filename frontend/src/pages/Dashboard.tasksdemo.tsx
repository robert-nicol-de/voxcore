import React, { useState, useEffect } from "react";
import Layout from "../components/layout/Layout";
import Chat from "../components/Chat";
import AISuggestions from "../components/AISuggestions";
import StatusStack from "../components/StatusStack";
import { buildStatusStack } from "../utils/buildStatusStack";

// Simulate loading build phases from YAML (replace with real API call in prod)
import phases from "../mock/phases.json";

export default function Dashboard() {
  const [selectedTask, setSelectedTask] = useState(null);
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    // In real app, fetch phases from backend
    setTasks(buildStatusStack(phases));
  }, []);

  return (
    <Layout>
      <div className="dashboard-container">
        <div className="header">
          <h1>VoxCore Intelligence</h1>
          <p>Ask questions. Get insights. Explore your data.</p>
        </div>

        <Chat />
        <AISuggestions />
        <div className="mt-8">
          <StatusStack tasks={tasks} onSelectTask={setSelectedTask} />
        </div>
        {/* Optional: TaskDrawer for selectedTask */}
      </div>
    </Layout>
  );
}
