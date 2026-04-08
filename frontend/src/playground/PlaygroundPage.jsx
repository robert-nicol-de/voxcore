import React, { useState, useEffect } from "react";
import { playgroundSuggestions } from "./PlaygroundSuggestions";

export default function PlaygroundPage({ demoMode = true }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [response, setResponse] = useState(null);

  useEffect(() => {
    if (demoMode) {
      sendMessage("Show revenue by region");
    }
  }, [demoMode]);

  const sendMessage = async (text) => {
    const session_id = localStorage.getItem('voxcore_session_id') || 'default';
    const payload = {
      query: text,
      agent: demoMode ? "playground-agent" : "anonymous",
      company_id: "default",
      workspace_id: "default",
      session_id,
    };

    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    const res = await fetch(`${apiUrl}/api/v1/query`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Demo-Mode": demoMode ? "true" : "false"
      },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const errorText = await res.text();
      console.error("Playground query failed", res.status, errorText);
      return;
    }

    const data = await res.json();

    setMessages((msgs) => [...msgs, { user: text, bot: data.generated_sql || data.error || "No response" }]);
    setResponse(data);
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={{ background: "#0a1a2f", color: "#fff", padding: 16, fontSize: 24 }}>
        VoxCore Playground
      </div>
      <div style={{ display: "flex", flex: 1 }}>
        {/* Chat Panel */}
        <div style={{ flex: 1, borderRight: "1px solid #eee", padding: 24, minWidth: 350 }}>
          <div style={{ marginBottom: 16, color: "#888" }}>Try asking:</div>
          <ul style={{ marginBottom: 24 }}>
            {playgroundSuggestions.map((s, i) => (
              <li key={i} style={{ cursor: "pointer", color: "#0074d9" }} onClick={() => sendMessage(s)}>{s}</li>
            ))}
          </ul>
          <div style={{ height: 300, overflowY: "auto", marginBottom: 16 }}>
            {messages.map((m, i) => (
              <div key={i}>
                <b>You:</b> {m.user}<br />
                <b>VoxCore:</b> {m.bot}
                <hr />
              </div>
            ))}
          </div>
          <form onSubmit={e => { e.preventDefault(); sendMessage(input); setInput(""); }}>
            <input value={input} onChange={e => setInput(e.target.value)} style={{ width: "80%", padding: 8 }} placeholder="Type your question..." />
            <button type="submit" style={{ marginLeft: 8 }}>Send</button>
          </form>
        </div>
        {/* Dashboard Panel */}
        <div style={{ flex: 2, padding: 24 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Demo Dashboard</div>
          {response && (
            <>
              {response.chart && <div style={{ marginBottom: 16 }}>[Chart Placeholder]</div>}
              {response?.data ? (
                <Table data={response.data} />
              ) : (
                <SkeletonTable />
              )}
              {response.suggestions && (
                <div style={{ marginTop: 16 }}>
                  <b>Exploration Suggestions:</b>
                  <ul>
                    {response.suggestions.map((s, i) => <li key={i}>{s}</li>)}
                  </ul>
                </div>
              )}
            </>
          )}
          <button style={{ marginTop: 32, background: "#0074d9", color: "#fff", padding: "8px 16px", border: 0, borderRadius: 4 }}
            onClick={() => sendMessage("Explain This Dataset")}>Explain This Dataset</button>
        </div>
      </div>
    </div>
  );
}
