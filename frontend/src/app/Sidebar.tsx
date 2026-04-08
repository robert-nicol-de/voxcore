import React from "react";
import { Link, useLocation } from "react-router-dom";

const nav = [
  { label: "Dashboard", path: "/app" },
  { label: "EMD", path: "/app/emd" },
  { label: "Monitoring", path: "/app/monitoring" },
  { label: "Predictions", path: "/app/predictions" },
  { label: "Data Sources", path: "/app/data-sources" },
  { label: "Vault", path: "/app/vault" },
  { label: "Reports", path: "/app/reports" },
  { label: "Settings", path: "/app/settings" },
];

export default function Sidebar() {
  const { pathname } = useLocation();
  return (
    <aside className="w-64 bg-[#111827] border-r border-gray-800 flex flex-col py-8 px-4 min-h-screen">
      <div className="text-2xl font-bold text-white mb-8">VoxCore</div>
      <nav className="flex flex-col gap-2">
        {nav.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={`rounded-xl px-4 py-2 text-white font-medium transition border border-transparent hover:border-blue-500/30 ${
              pathname === item.path ? "bg-blue-900/40 border-blue-500/30" : ""
            }`}
          >
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
