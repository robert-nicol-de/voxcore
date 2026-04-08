import { useEffect, useState } from "react";

export default function ApprovalsPage() {
  const [requests, setRequests] = useState([]);

  async function fetchRequests() {
    const res = await fetch("/api/approvals/pending");
    const data = await res.json();
    setRequests(data.requests);
  }

  useEffect(() => {
    fetchRequests();
  }, []);

  async function approve(id) {
    await fetch(`/api/approvals/${id}/approve`, { method: "POST" });
    fetchRequests();
  }

  async function reject(id) {
    await fetch(`/api/approvals/${id}/reject`, { method: "POST" });
    fetchRequests();
  }

  return (
    <div className="p-6">
      <h1 className="text-xl font-bold mb-4">Approval Queue</h1>

      {requests.map((r: any) => (
        <div key={r.id} className="border p-4 mb-3 rounded-xl shadow">
          <p><b>Query:</b> {r.query}</p>
          <p><b>User:</b> {r.user_id}</p>
          <p><b>Risk:</b> {r.risk_score}</p>
          <p><b>Reason:</b> {r.reason}</p>

          <div className="mt-2 flex gap-2">
            <button
              onClick={() => approve(r.id)}
              className="bg-green-500 text-white px-3 py-1 rounded"
            >
              Approve
            </button>

            <button
              onClick={() => reject(r.id)}
              className="bg-red-500 text-white px-3 py-1 rounded"
            >
              Reject
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}
