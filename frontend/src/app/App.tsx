

import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import Dashboard from "./pages/Dashboard";
import EMD from "./pages/EMD";
import Monitoring from "./pages/Monitoring";
import Predictions from "./pages/Predictions";
import DataSources from "./pages/DataSources";
import Vault from "./pages/Vault";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";

export default function App() {
  return (
    <div className="flex min-h-screen bg-[#0a0a0a]">
      <Sidebar />
      <main className="flex-1 p-10 overflow-y-auto">
        <Routes>
          <Route path="/app" element={<Navigate to="/app/dashboard" replace />} />
          <Route path="/app/dashboard" element={<Dashboard />} />
          <Route path="/app/emd" element={<EMD />} />
          <Route path="/app/monitoring" element={<Monitoring />} />
          <Route path="/app/predictions" element={<Predictions />} />
          <Route path="/app/data-sources" element={<DataSources />} />
          <Route path="/app/vault" element={<Vault />} />
          <Route path="/app/reports" element={<Reports />} />
          <Route path="/app/settings" element={<Settings />} />
          {/* Add more routes as needed */}
          <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
        </Routes>
      </main>
    </div>
  );
}
