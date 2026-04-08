import AppLayout from "../../layouts/AppLayout";

export default function Dashboard() {
  return (
    <AppLayout>
      <h1 className="text-2xl font-bold mb-4">Dashboard</h1>
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white/5 p-4 rounded">Queries Today</div>
        <div className="bg-white/5 p-4 rounded">Risk Alerts</div>
        <div className="bg-white/5 p-4 rounded">Databases Connected</div>
      </div>
    </AppLayout>
  );
}
