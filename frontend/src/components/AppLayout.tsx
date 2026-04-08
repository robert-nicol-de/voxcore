import { Outlet } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import AIStatusBar from "../components/AIStatusBar";

export default function AppLayout() {
  return (
    <div className="flex h-screen bg-[#070B14] text-white overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <AIStatusBar />
        <main className="flex-1 overflow-auto p-6">
          <div className="max-w-7xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
