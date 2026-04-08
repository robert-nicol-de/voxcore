import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from "react";
import "./Chat.css";

import ConnectionHeader from "./ConnectionHeader";
import ChartRenderer from "./ChartRenderer";
import { ClientDetailsModal } from "./ClientDetailsModal";
import { apiUrl, API_BASE_URL } from "../lib/api";
import AuditPanel from "./AuditPanel";
import SchemaTrustBadge from "./SchemaTrustBadge";
import LearningSignal from "./LearningSignal";

interface Message {
  id: string;
  type: "user" | "assistant";
  text: string;
  timestamp: Date;
  sql?: string;
  results?: any[];
  chart?: any;
  column_mapping?: { [key: string]: string };
  sandboxPreview?: any[];
}

interface EnlargedChart {
  type: string;
  title: string;
  data?: any;
}

interface ClientDetails {
  name: string;
  value: number;
  chartType: string;
  chartTitle: string;
}

interface ChatProps {
  onBackToDashboard?: () => void;
  isPreviewMode?: boolean;
}

const Chat = forwardRef<any, ChatProps>(({ onBackToDashboard, isPreviewMode = false }, ref) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "0",
      type: "assistant",
      text: "👋 Welcome! I'm your SQL Assistant. Ask me anything about your data in plain English, and I'll generate the SQL for you.",
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [govResponse, setGovResponse] = useState<any | null>(null);
  const [enlargedChart, setEnlargedChart] = useState<EnlargedChart | null>(null);
  const [clientDetails, setClientDetails] = useState<ClientDetails | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = "auto";
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 120) + "px";
    }
  }, [input]);

  // Check connection status on mount and when it changes
  useEffect(() => {
    const checkConnectionStatus = () => {
      const status = localStorage.getItem("dbConnectionStatus");
      setIsConnected(status === "connected");
    };

    checkConnectionStatus();

    // Listen for connection status changes
    const handleConnectionChange = () => {
      checkConnectionStatus();
    };

    window.addEventListener("connectionStatusChanged", handleConnectionChange);
    return () => window.removeEventListener("connectionStatusChanged", handleConnectionChange);
  }, []);

  const handleQuestionSelect = (question: string) => {
    setInput(question);
    if (inputRef.current) {
      inputRef.current.focus();
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.style.height = "auto";
          inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 120) + "px";
        }
      }, 0);
    }
  };

  useImperativeHandle(ref, () => ({
    handleQuestionSelect
  }));

  const handleChartItemClick = (itemData: any) => {
    setClientDetails({
      name: itemData.name,
      value: itemData.value,
      chartType: itemData.chartType,
      chartTitle: itemData.chartTitle,
    });
  };

  // PHASE 4: Get activeConnectionId from SchemaContext
  const { activeConnectionId, schema } = useSchema ? useSchema() : { activeConnectionId: null, schema: null };

  // --- Connection lock (advanced UX guard) ---
  const [sessionConnectionId, setSessionConnectionId] = useState<string | null>(null);
  useEffect(() => {
    if (activeConnectionId && !sessionConnectionId) {
      setSessionConnectionId(activeConnectionId);
    }
    if (sessionConnectionId && activeConnectionId && sessionConnectionId !== activeConnectionId) {
      // Option A: warn and block
      alert("Start a new session to change connection.");
      // Option B: auto-reset chat (uncomment to enable)
      // setMessages([messages[0]]);
      // setSessionConnectionId(activeConnectionId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeConnectionId]);

  // --- Lightweight schema shape validator ---
  const isValidSchema = (schema: any) => {
    return (
      schema &&
      Array.isArray(schema.tables) &&
      Array.isArray(schema.columns)
    );
  };

  const handleSendMessage = async () => {
  if (!input.trim()) return;

  setLoading(true);
  setGovResponse(null);

  const userMessage = {
    id: Date.now().toString(),
    type: "user",
    text: input,
    timestamp: new Date(),
  };

  setMessages((prev) => [...prev, userMessage]);

  try {
    const res = await fetch("http://localhost:8000/api/v1/query", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: input,
        connection_id: activeConnectionId || "mock-1",
        schema: schema || null,
      }),
    });

    const data = await res.json();
    setGovResponse(data);

    const assistantMessage = {
      id: `${Date.now()}-assistant`,
      type: "assistant",
      text: data?.message || "Response received",
      timestamp: new Date(),
      sql: data?.final_sql || data?.generated_sql || "",
      results: data?.results || data?.data || [],
    };

    setMessages((prev) => [...prev, assistantMessage]);
  } catch (err) {
    console.error(err);
    setMessages((prev) => [
      ...prev,
      {
        id: `${Date.now()}-error`,
        type: "assistant",
        text: "Error contacting VoxCore",
        timestamp: new Date(),
      },
    ]);
  } finally {
    setLoading(false);
    setInput("");
  }
};

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const exportToCSV = (results: any[]) => {
    if (!results || results.length === 0) return;
    
    const headers = Object.keys(results[0] || {});
    if (headers.length === 0) return;
    
    const csvContent = [
      headers.join(","),
      ...results.map(row => 
        headers.map(header => {
          const value = row?.[header];
          if (value === null || value === undefined) return "";
          if (typeof value === "string" && (value.includes(",") || value.includes("\""))) {
            return `"${value.replace(/"/g, "\"\"")}"`;
          }
          return String(value);
        }).join(",")
      )
    ].join("\n");
    
    const element = document.createElement("a");
    element.setAttribute("href", "data:text/csv;charset=utf-8," + encodeURIComponent(csvContent));
    element.setAttribute("download", "results_" + new Date().getTime() + ".csv");
    element.style.display = "none";
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const generateReport = (sql: string, results: any[]) => {
    const reportHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>SQL Query Report</title>
        <style>
          * { box-sizing: border-box; }
          body { font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f5f5; }
          .report-container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
          h1 { color: #3b82f6; margin-bottom: 10px; }
          .timestamp { color: #666; font-size: 14px; margin-bottom: 30px; }
          .sql-section { background: #f9fafb; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #3b82f6; }
          .sql-label { font-weight: 600; color: #333; margin-bottom: 10px; }
          pre { background: #1e293b; color: #e2e8f0; padding: 15px; border-radius: 4px; overflow-x: auto; }
          code { font-family: 'Courier New', monospace; font-size: 14px; }
          .results-section { margin: 30px 0; }
          table { width: 100%; border-collapse: collapse; margin-top: 15px; }
          th { background: #3b82f6; color: white; padding: 12px; text-align: left; font-weight: 600; }
          td { padding: 10px 12px; border-bottom: 1px solid #e5e7eb; }
          tr:hover { background: #f9fafb; }
          .no-results { color: #999; font-style: italic; padding: 20px; text-align: center; }
          .print-button { background: #3b82f6; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 20px 0; font-size: 14px; }
          .print-button:hover { background: #2563eb; }
          h2 { color: #1e293b; margin-top: 30px; margin-bottom: 10px; }
          @media print {
            body { margin: 0; }
            .print-button { display: none; }
          }
        </style>
      </head>
      <body>
        <div class="report-container">
          <h1>📊 SQL Query Report</h1>
          <div class="timestamp">Generated: ${new Date().toLocaleString()}</div>
          
          <div class="sql-section">
            <div class="sql-label">📝 SQL Query</div>
            <pre><code>${sql.replace(/</g, "&lt;").replace(/>/g, "&gt;")}</code></pre>
          </div>
          
          ${results && results.length > 0 ? `
            <div class="results-section">
              <h2>📈 Results (${results.length} rows)</h2>
              <table>
                <thead>
                  <tr>
                    ${Object.keys(results[0] || {}).map(key => `<th>${key}</th>`).join("")}
                  </tr>
                </thead>
                <tbody>
                  ${results.map((row: any) => `
                    <tr>
                      ${Object.values(row || {}).map(val => {
                        const displayVal = val === null || val === undefined ? "-" : (typeof val === "number" ? val.toLocaleString() : String(val));
                        return `<td>${displayVal}</td>`;
                      }).join("")}
                    </tr>
                  `).join("")}
                </tbody>
              </table>
            </div>
          ` : "<div class=\"no-results\">No results to display</div>"}
          
          <button class="print-button" onclick="window.print()">🖨️ Print Report</button>
        </div>
      </body>
      </html>
    `;
    
    const reportWindow = window.open("", "_blank");
    reportWindow?.document.write(reportHtml);
    reportWindow?.document.close();
  };

  // UI GUARD: Block all chat UI if no connection or no schema loaded
  if (!activeConnectionId) {
    return (
      <div className="chat-empty-state">
        <div style={{padding: 48, textAlign: "center", color: "#9ab3cf", fontSize: 20}}>
          <strong>Select a connection to start</strong>
          <p style={{marginTop: 12, fontSize: 15}}>Go to <b>Connections</b> and choose a data source to unlock chat and insights.</p>
        </div>
      </div>
    );
  }

  if (!schema) {
    return (
      <div className="chat-empty-state">
        <div style={{padding: 48, textAlign: "center", color: "#9ab3cf", fontSize: 20}}>
          <strong>Load schema to enable intelligent querying</strong>
          <p style={{marginTop: 12, fontSize: 15}}>Please discover or refresh the schema in the Databases page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat">
      {isPreviewMode && (
        <div className="preview-banner">
          Preview Mode — Database connections are disabled.
          <a href="/pricing.html">Subscribe to unlock full access</a>
        </div>
      )}
      <ConnectionHeader onDisconnect={onBackToDashboard} isPreviewMode={isPreviewMode} />

      <div className="mb-6 p-4 bg-[#0b1220] border border-[#1e293b] rounded-xl">
        <div className="flex items-center justify-between mb-3">
          <div className="text-sm text-gray-400">VoxCore Governance Status</div>
          <div className="text-xs text-green-400">● Active</div>
        </div>

        <div className="text-xs text-blue-400 mb-3">Schema-aware query</div>

        {govResponse?.risk_score !== undefined && (
          <div className="mb-3">
            <div className="text-xs text-gray-400 mb-1">Risk Level</div>
            <div className="w-full h-2 bg-[#1e293b] rounded">
              <div
                className={`h-2 rounded ${
                  govResponse.risk_score > 70
                    ? "bg-red-500"
                    : govResponse.risk_score > 40
                    ? "bg-yellow-500"
                    : "bg-green-500"
                }`}
                style={{ width: `${govResponse.risk_score}%` }}
              />
            </div>
          </div>
        )}

        <div className="flex gap-4 text-xs mb-3">
          <div className="text-green-400">✔ Destructive Blocking</div>
          <div className="text-green-400">✔ SQL Validation</div>
          <div className="text-green-400">✔ Risk Scoring</div>
        </div>

        {govResponse?.success === false && (
          <div className="mt-3 text-red-400 text-sm">🚫 Execution blocked by policy</div>
        )}

        {govResponse?.risk_score !== undefined && (
          <div className="mt-3 text-xs text-gray-400">
            Last query evaluated at risk level {govResponse.risk_score}
          </div>
        )}
      </div>

      <div className="messages">
        {messages.map((msg, idx) => {
          // Try to surface intelligence for assistant messages with audit/schema_trust/learning
          let auditPanel = null;
          let trustBadge = null;
          let learningSignal = null;
          let parsed = {};
          try {
            parsed = typeof msg.results === "object" && msg.results && msg.results[0] && typeof msg.results[0] === "object" ? msg.results[0] : {};
          } catch {}
          // Prefer explicit response fields if present
          const audit = msg.audit || parsed.audit;
          const schemaTrust = msg.schema_trust || parsed.schema_trust;
          const learned = msg.learning_applied || parsed.learning_applied;
          if (audit) {
            auditPanel = <AuditPanel audit={audit} />;
          }
          if (schemaTrust) {
            trustBadge = <SchemaTrustBadge grade={schemaTrust.grade} score={schemaTrust.score} warnings={schemaTrust.warnings || []} />;
          }
          if (learned) {
            learningSignal = <LearningSignal subtle={true} />;
          }
          return (
            <div key={msg.id} className={`message ${msg.type}`}>
              <div className="message-avatar">
                {msg.type === "user" ? "👤" : "🤖"}
              </div>
              <div className="message-content">
                <p className="message-text">{msg.text}</p>
                {/* --- INTELLIGENCE SURFACING --- */}
                {trustBadge}
                {auditPanel}
                {learningSignal}
              </div>
            </div>
          );
        })}
        {loading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {govResponse && (
        <div className="gov-response-panel" style={{ margin: "12px 16px", padding: "12px", borderRadius: "8px", background: "#0b1221", border: "1px solid #1e2a42", color: "#e2e8f0" }}>
          <div style={{ marginBottom: 8, fontWeight: 600 }}>Governance Metadata</div>
          {govResponse.final_sql && (
            <div style={{ marginBottom: 6 }}>
              <div className="text-gray-400 text-xs">Final SQL</div>
              <pre style={{ background: "#020617", color: "#8affb4", padding: 8, borderRadius: 4, overflowX: "auto" }}>{govResponse.final_sql}</pre>
            </div>
          )}
          {govResponse.generated_sql && !govResponse.final_sql && (
            <div style={{ marginBottom: 6 }}>
              <div className="text-gray-400 text-xs">Generated SQL</div>
              <pre style={{ background: "#020617", color: "#8affb4", padding: 8, borderRadius: 4, overflowX: "auto" }}>{govResponse.generated_sql}</pre>
            </div>
          )}
          {govResponse.risk_score !== undefined && govResponse.risk_score !== null && (
            <div style={{ fontWeight: 600, marginBottom: 6 }}>
              Risk Score:{" "}
              <span style={{ color: govResponse.risk_score > 70 ? "#f87171" : govResponse.risk_score > 40 ? "#facc15" : "#34d399" }}>
                {govResponse.risk_score}
              </span>
            </div>
          )}
          {govResponse.success === false && (
            <div style={{ color: "#f87171", marginBottom: 6 }}>🚫 Query blocked by VoxCore</div>
          )}
          {govResponse.was_rewritten && (
            <div style={{ color: "#38bdf8", fontSize: 12, marginBottom: 6 }}>🔄 SQL was rewritten for compatibility</div>
          )}
          {govResponse.results && Array.isArray(govResponse.results) && (
            <div style={{ marginBottom: 0 }}>
              <div className="text-gray-400 text-xs">Results</div>
              <pre style={{ background: "#020617", color: "#cbd5e1", padding: 8, borderRadius: 4, overflowX: "auto" }}>{JSON.stringify(govResponse.results, null, 2)}</pre>
            </div>
          )}
        </div>
      )}

      {enlargedChart && (
        <div style={{position: "fixed", top: 0, left: 0, right: 0, bottom: 0, background: "rgba(0,0,0,0.7)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 9999}} onClick={() => setEnlargedChart(null)}>
          <div style={{background: "var(--bg-primary)", borderRadius: "8px", padding: "20px", width: "90%", height: "90%", display: "flex", flexDirection: "column", boxShadow: "0 10px 40px rgba(0,0,0,0.3)", overflowY: "auto"}} onClick={(e) => e.stopPropagation()}>
            <div style={{display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "15px"}}>
              <h2 style={{margin: 0, color: "var(--text-primary)"}}>{enlargedChart.title}</h2>
              <button onClick={() => setEnlargedChart(null)} style={{background: "none", border: "none", fontSize: "24px", cursor: "pointer", color: "var(--text-secondary)"}}>×</button>
            </div>
            <div style={{flex: 1, width: "100%"}}>
              <ChartRenderer chart={enlargedChart.data} onItemClick={handleChartItemClick} />
            </div>
          </div>
        </div>
      )}

      <ClientDetailsModal
        isOpen={!!clientDetails}
        clientName={clientDetails?.name || ""}
        clientValue={clientDetails?.value || 0}
        chartType={clientDetails?.chartType || ""}
        chartTitle={clientDetails?.chartTitle || ""}
        onClose={() => setClientDetails(null)}
      />

      <div className="input-area">
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything... (e.g., 'Show top 10 customers by revenue')"
            rows={1}
            disabled={!activeConnectionId}
          />
          <button 
            onClick={handleSendMessage}
            disabled={!input.trim() || loading || !activeConnectionId}
            className="send-btn"
            title={!activeConnectionId ? "Select a connection first" : ""}
          >
            {loading ? "⏳" : "➤"}
          </button>
        </div>
        <p className="input-hint">💡 Tip: Press Enter to send, Shift+Enter for new line</p>
      </div>
    </div>
  );
});

Chat.displayName = "Chat";
export default Chat;
