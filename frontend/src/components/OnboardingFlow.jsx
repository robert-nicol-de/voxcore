import React, { useState } from "react";

/**
 * OnboardingFlow - 4-Step Wizard for New Users
 * 
 * Steps:
 * 1. DB Connection - Connect to database
 * 2. Schema Scan - Discover tables and columns
 * 3. Initial Insights - Generate first insights
 * 4. First Question - Ask your first question
 * 
 * Usage:
 * <OnboardingFlow sessionId={sessionId} onComplete={handleComplete} />
 */
export function OnboardingFlow({ sessionId, onComplete = () => {} }) {
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    host: "localhost",
    port: "5432",
    username: "",
    password: "",
    database: "",
  });
  const [schema, setSchema] = useState(null);
  const [insights, setInsights] = useState(null);
  const [question, setQuestion] = useState("");

  // Step 1: Database Connection
  const handleDbConnect = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/onboarding/connect-database", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          host: formData.host,
          port: parseInt(formData.port),
          username: formData.username,
          password: formData.password,
          database: formData.database,
        }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Failed to connect to database");
      }

      setStep(2);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Schema Scan
  const handleSchemaScan = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/onboarding/scan-schema", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error("Failed to scan schema");
      }

      const data = await response.json();
      setSchema(data.schema);
      setStep(3);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 3: Generate Initial Insights
  const handleGenerateInsights = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/onboarding/generate-insights", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });

      if (!response.ok) {
        throw new Error("Failed to generate insights");
      }

      const data = await response.json();
      setInsights(data.insights);
      setStep(4);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Step 4: Submit First Question
  const handleSubmitQuestion = async () => {
    if (!question.trim()) {
      setError("Please enter a question");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          question: question,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to execute query");
      }

      const data = await response.json();
      onComplete({ question, jobId: data.job_id });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: "600px",
        margin: "40px auto",
        padding: "40px",
        borderRadius: "12px",
        border: "1px solid #444",
        backgroundColor: "#1a1a1a",
        fontFamily: "system-ui, -apple-system, sans-serif",
      }}
    >
      {/* Header */}
      <div style={{ marginBottom: "32px" }}>
        <h1 style={{ margin: "0 0 8px 0", fontSize: "28px", fontWeight: "700" }}>
          Welcome to VoxQuery
        </h1>
        <p style={{ margin: 0, color: "#888" }}>
          Let's get you started with your first data analysis
        </p>
      </div>

      {/* Progress Bar */}
      <div style={{ marginBottom: "32px" }}>
        <div
          style={{
            display: "flex",
            gap: "8px",
            marginBottom: "16px",
          }}
        >
          {[1, 2, 3, 4].map((s) => (
            <div
              key={s}
              style={{
                flex: 1,
                height: "4px",
                backgroundColor: s <= step ? "#0087ff" : "#333",
                borderRadius: "2px",
                transition: "all 0.3s",
              }}
            />
          ))}
        </div>
        <p style={{ margin: 0, fontSize: "13px", color: "#888" }}>
          Step {step} of 4
        </p>
      </div>

      {/* Step 1: Database Connection */}
      {step === 1 && (
        <div>
          <h2 style={{ margin: "0 0 20px 0", fontSize: "18px" }}>
            🗄️ Connect Your Database
          </h2>

          <div style={{ display: "grid", gap: "16px" }}>
            <div>
              <label style={{ display: "block", marginBottom: "6px", fontSize: "13px" }}>
                Host
              </label>
              <input
                type="text"
                value={formData.host}
                onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  border: "1px solid #444",
                  borderRadius: "6px",
                  backgroundColor: "#0f0f0f",
                  color: "#ddd",
                  fontSize: "13px",
                  boxSizing: "border-box",
                }}
              />
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px" }}>
              <div>
                <label style={{ display: "block", marginBottom: "6px", fontSize: "13px" }}>
                  Port
                </label>
                <input
                  type="text"
                  value={formData.port}
                  onChange={(e) => setFormData({ ...formData, port: e.target.value })}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #444",
                    borderRadius: "6px",
                    backgroundColor: "#0f0f0f",
                    color: "#ddd",
                    fontSize: "13px",
                    boxSizing: "border-box",
                  }}
                />
              </div>
              <div>
                <label style={{ display: "block", marginBottom: "6px", fontSize: "13px" }}>
                  Database
                </label>
                <input
                  type="text"
                  value={formData.database}
                  onChange={(e) => setFormData({ ...formData, database: e.target.value })}
                  placeholder="database_name"
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    border: "1px solid #444",
                    borderRadius: "6px",
                    backgroundColor: "#0f0f0f",
                    color: "#ddd",
                    fontSize: "13px",
                    boxSizing: "border-box",
                  }}
                />
              </div>
            </div>

            <div>
              <label style={{ display: "block", marginBottom: "6px", fontSize: "13px" }}>
                Username
              </label>
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  border: "1px solid #444",
                  borderRadius: "6px",
                  backgroundColor: "#0f0f0f",
                  color: "#ddd",
                  fontSize: "13px",
                  boxSizing: "border-box",
                }}
              />
            </div>

            <div>
              <label style={{ display: "block", marginBottom: "6px", fontSize: "13px" }}>
                Password
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                style={{
                  width: "100%",
                  padding: "8px 12px",
                  border: "1px solid #444",
                  borderRadius: "6px",
                  backgroundColor: "#0f0f0f",
                  color: "#ddd",
                  fontSize: "13px",
                  boxSizing: "border-box",
                }}
              />
            </div>
          </div>

          {error && (
            <div
              style={{
                marginTop: "16px",
                padding: "12px",
                backgroundColor: "#3d0d0d",
                border: "1px solid #ff4444",
                borderRadius: "6px",
                color: "#ff4444",
                fontSize: "13px",
              }}
            >
              {error}
            </div>
          )}

          <button
            onClick={handleDbConnect}
            disabled={loading || !formData.username || !formData.password || !formData.database}
            style={{
              width: "100%",
              marginTop: "20px",
              padding: "12px",
              backgroundColor: loading ? "#444" : "#0087ff",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              cursor: loading ? "default" : "pointer",
              fontWeight: "500",
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? "Connecting..." : "Next: Scan Schema"}
          </button>
        </div>
      )}

      {/* Step 2: Schema Scan */}
      {step === 2 && (
        <div>
          <h2 style={{ margin: "0 0 20px 0", fontSize: "18px" }}>
            🔍 Scanning Database Schema
          </h2>

          <div
            style={{
              padding: "20px",
              backgroundColor: "#0f0f0f",
              borderRadius: "8px",
              border: "1px solid #333",
              textAlign: "center",
            }}
          >
            {loading ? (
              <>
                <div
                  style={{
                    fontSize: "32px",
                    marginBottom: "12px",
                    animation: "spin 0.8s linear infinite",
                  }}
                >
                  ⚙️
                </div>
                <p style={{ margin: 0, color: "#888" }}>Discovering tables and columns...</p>
              </>
            ) : (
              <>
                <p style={{ margin: "0 0 16px 0", color: "#0d8" }}>✅ Schema scan complete!</p>
                <p style={{ margin: 0, color: "#888", fontSize: "13px" }}>
                  Found {schema?.table_count || "0"} tables with{" "}
                  {schema?.column_count || "0"} columns
                </p>
              </>
            )}
          </div>

          <button
            onClick={handleSchemaScan}
            disabled={loading}
            style={{
              width: "100%",
              marginTop: "20px",
              padding: "12px",
              backgroundColor: loading ? "#444" : "#0087ff",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              cursor: loading ? "default" : "pointer",
              fontWeight: "500",
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? "Scanning..." : "Proceed: Generate Insights"}
          </button>
        </div>
      )}

      {/* Step 3: Initial Insights */}
      {step === 3 && (
        <div>
          <h2 style={{ margin: "0 0 20px 0", fontSize: "18px" }}>
            💡 Generating Initial Insights
          </h2>

          <div
            style={{
              padding: "20px",
              backgroundColor: "#0f0f0f",
              borderRadius: "8px",
              border: "1px solid #333",
            }}
          >
            {loading ? (
              <>
                <div
                  style={{
                    fontSize: "32px",
                    marginBottom: "12px",
                    animation: "spin 0.8s linear infinite",
                  }}
                >
                  ✨
                </div>
                <p style={{ margin: 0, color: "#888", textAlign: "center" }}>
                  Analyzing data and generating insights...
                </p>
              </>
            ) : insights ? (
              <div style={{ display: "grid", gap: "12px" }}>
                {insights.map((insight, i) => (
                  <div
                    key={i}
                    style={{
                      padding: "12px",
                      backgroundColor: "#1a1a1a",
                      borderRadius: "6px",
                      border: "1px solid #333",
                      fontSize: "13px",
                      lineHeight: "1.4",
                      color: "#ddd",
                    }}
                  >
                    {insight}
                  </div>
                ))}
              </div>
            ) : null}
          </div>

          <button
            onClick={handleGenerateInsights}
            disabled={loading}
            style={{
              width: "100%",
              marginTop: "20px",
              padding: "12px",
              backgroundColor: loading ? "#444" : "#0087ff",
              color: "#fff",
              border: "none",
              borderRadius: "6px",
              cursor: loading ? "default" : "pointer",
              fontWeight: "500",
              opacity: loading ? 0.6 : 1,
            }}
          >
            {loading ? "Generating..." : "Proceed: Ask a Question"}
          </button>
        </div>
      )}

      {/* Step 4: First Question */}
      {step === 4 && (
        <div>
          <h2 style={{ margin: "0 0 20px 0", fontSize: "18px" }}>
            ❓ Ask Your First Question
          </h2>

          {insights && (
            <div
              style={{
                marginBottom: "16px",
                padding: "12px",
                backgroundColor: "#0d3d2a",
                borderRadius: "6px",
                border: "1px solid #0d8",
                fontSize: "13px",
                color: "#0d8",
              }}
            >
              ✅ Schema loaded and ready. Ask anything about your data.
            </div>
          )}

          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder='E.g., "What is the total revenue by region?" or "Show me sales trends for Q1"'
            style={{
              width: "100%",
              padding: "12px",
              border: "1px solid #444",
              borderRadius: "6px",
              backgroundColor: "#0f0f0f",
              color: "#ddd",
              fontSize: "13px",
              fontFamily: "system-ui, -apple-system, sans-serif",
              minHeight: "120px",
              boxSizing: "border-box",
              resize: "vertical",
            }}
          />

          {error && (
            <div
              style={{
                marginTop: "12px",
                padding: "12px",
                backgroundColor: "#3d0d0d",
                border: "1px solid #ff4444",
                borderRadius: "6px",
                color: "#ff4444",
                fontSize: "13px",
              }}
            >
              {error}
            </div>
          )}

          <button
            onClick={handleSubmitQuestion}
            disabled={loading || !question.trim()}
            style={{
              width: "100%",
              marginTop: "20px",
              padding: "12px",
              backgroundColor: loading || !question.trim() ? "#444" : "#00d084",
              color: "#000",
              border: "none",
              borderRadius: "6px",
              cursor: loading || !question.trim() ? "default" : "pointer",
              fontWeight: "600",
              opacity: loading || !question.trim() ? 0.6 : 1,
            }}
          >
            {loading ? "Analyzing..." : "🚀 Start Analysis"}
          </button>
        </div>
      )}

      {/* CSS for spin animation */}
      <style>
        {`
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
}
