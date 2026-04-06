

import React, { useState } from "react";
import Layout from "../components/ui/Layout";
import Section from "../components/ui/Section";
import Card from "../components/ui/Card";
import ChartRenderer from "../components/ChartRenderer";
import { sendQuery } from "../api/voxcoreApi";
import { getSessionId } from "../api/session";

// Optionally import DataTable if it exists, else render JSON for data
// import DataTable from '../components/DataTable';

export default function SqlAssistant() {
  const [question, setQuestion] = useState("Show top 10 customers by revenue");
  const [response, setResponse] = useState<{
    message: string;
    data?: any[];
    chart?: any;
    suggestions?: string[];
  } | null>(null);
  const [loading, setLoading] = useState(false);
  const sessionId = getSessionId();

  const handleAsk = async (input: string) => {
    if (!input || input.trim() === "") {
      console.error("Query is empty");
      return;
    }
    // console.log("Sending query:", input);
    setLoading(true);
    try {
      const res = await sendQuery(input, sessionId);
      setResponse({
        message: res.narrative || res.message,
        data: res.data,
        chart: res.chart,
        suggestions: res.suggestions
      });
    } catch (e) {
      console.error("Request failed:", e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout>
      <Section title="VoxCore Intelligence" subtitle="AI-driven analytics" center>
        {/* Query Input */}
        <Card>
          <form
            onSubmit={e => {
              e.preventDefault();
              handleAsk(question);
            }}
            className="flex gap-2 mb-4"
          >
            <input
              className="flex-1 border rounded px-3 py-2"
              value={question}
              onChange={e => setQuestion(e.target.value)}
              placeholder="Ask a question..."
              disabled={loading}
            />
            <button
              type="submit"
              className="bg-blue-600 text-white px-4 py-2 rounded"
              disabled={loading}
            >
              {loading ? "Thinking..." : "Ask"}
            </button>
          </form>
        </Card>

        {/* 1. NARRATIVE (MANDATORY FIRST) */}
        {response?.message && (
          <Card>
            <div className="text-lg font-semibold">
              {response.message}
            </div>
          </Card>
        )}

        {/* 2. DATA */}
        {response?.data && (
          <Card>
            {/* If DataTable exists, use it. Otherwise, fallback to JSON. */}
            {/* <DataTable data={response.data} /> */}
            <pre className="overflow-x-auto text-sm">{JSON.stringify(response.data, null, 2)}</pre>
          </Card>
        )}

        {/* 3. CHART */}
        {response?.chart && (
          <Card>
            <ChartRenderer chart={response.chart} />
          </Card>
        )}

        {/* 4. SUGGESTIONS */}
        {response?.suggestions && response.suggestions.length > 0 && (
          <Card>
            {response.suggestions.map((s: string, i: number) => (
              <button
                key={i}
                className="bg-gray-200 rounded px-3 py-1 mr-2 mt-2"
                onClick={() => handleAsk(s)}
                disabled={loading}
              >
                {s}
              </button>
            ))}
          </Card>
        )}
      </Section>
    </Layout>
  );
}

