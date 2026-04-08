  // Drilldown: generate follow-up query and auto-create PR
  const userId = "user_123"; // TODO: Replace with real auth
  const runDrilldown = async (insight: any) => {
    // Track user click
    await fetch("/api/user/event", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        type: "insight_click",
        insight: insight.insight,
        insight_type: insight.type,
        confidence: insight.confidence
      }),
    });
    const res = await fetch("/api/pr/drilldown", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(insight),
    });
    const data = await res.json();
    // Auto-create new PR with drilldown query
    await fetch("/api/pr/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: "Drilldown from insight",
        problem: data.query,
        type: "analysis",
        domain: "auto",
        approach: "AI drilldown",
        metadata: {
          user_id: userId
        }
      }),
    });
    alert("Drilldown PR created: " + data.query);
    await fetchPRs();
  };
import { useState, useEffect } from "react";
import AlertsPanel from "./AlertsPanel";
import Card from "@/components/ui/Card";
import CardContent from "@/components/ui/CardContent";
import Button from "@/components/ui/Button";
import { VoxInput } from "@/components/Input";

type PRForm = {
  title: string;
  type: string;
  domain: string;
  problem: string;
  approach: string;
};

export default function VoxCorePRTool() {
  const [form, setForm] = useState<PRForm>({
    title: "",
    type: "",
    domain: "",
    problem: "",
    approach: "",
  });
  const [prs, setPrs] = useState<any[]>([]);

  const updateField = (key: keyof PRForm, value: string) => {
    setForm({ ...form, [key]: value });
  };

  const fetchPRs = async () => {
    const res = await fetch("/api/pr/list");
    const data = await res.json();
    setPrs(data.prs);
  };

  useEffect(() => {
    fetchPRs();
  }, []);

  const handleSubmit = async () => {
    if (!form.title || !form.type || !form.domain || !form.problem || !form.approach) {
      alert("All fields are required.");
      return;
    }
    const res = await fetch("/api/pr/create", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        ...form,
        metadata: {
          user_id: userId
        }
      }),
    });
    if (res.ok) {
      alert("PR Submitted 🚀");
      setForm({ title: "", type: "", domain: "", problem: "", approach: "" });
      fetchPRs();
    } else {
      alert("Submission failed.");
    }
  };

  const executePR = async (pr: any) => {
    const res = await fetch("/api/pr/execute", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(pr),
    });
    const data = await res.json();
    alert("PR Executed ⚡");
    setPrs((prev) =>
      prev.map((item) =>
        item === pr
          ? {
              ...item,
              pipeline: data.pipeline,
              results: data.results,
            }
          : item
      )
    );
  };

  return (
    <div className="p-6 grid gap-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold">VoxCore PR System</h1>

      <Card>
        <CardContent className="p-4 grid gap-4">
          <h2 className="text-xl font-semibold">PR Title</h2>
          <VoxInput
            placeholder="[Cell] – Description"
            value={form.title}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => updateField("title", e.target.value)}
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4 grid gap-4">
          <h2 className="text-xl font-semibold">PR Type</h2>
          <select
            className="input"
            value={form.type}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => updateField("type", e.target.value)}
          >
            <option value="">Select type</option>
            <option value="feature">Feature</option>
            <option value="bug">Bug Fix</option>
            <option value="performance">Performance</option>
            <option value="security">Security</option>
          </select>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4 grid gap-4">
          <h2 className="text-xl font-semibold">Domain</h2>
          <select
            className="input"
            value={form.domain}
            onChange={(e: React.ChangeEvent<HTMLSelectElement>) => updateField("domain", e.target.value)}
          >
            <option value="">Select domain</option>
            <option value="backend">Backend</option>
            <option value="query">Query Intelligence</option>
            <option value="governance">Governance</option>
            <option value="frontend">Frontend</option>
            <option value="security">Security</option>
          </select>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4 grid gap-4">
          <h2 className="text-xl font-semibold">Problem Statement</h2>
          <textarea
            className="input"
            placeholder="Describe the issue"
            value={form.problem}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => updateField("problem", e.target.value)}
          />
        </CardContent>
      </Card>

      <Card>
        <CardContent className="p-4 grid gap-4">
          <h2 className="text-xl font-semibold">Technical Approach</h2>
          <textarea
            className="input"
            placeholder="Explain solution"
            value={form.approach}
            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => updateField("approach", e.target.value)}
          />
        </CardContent>
      </Card>

      <Button onClick={handleSubmit} className="text-lg">
        Submit PR
      </Button>

      <Card>
        <CardContent className="p-4">
          <h2 className="text-xl font-semibold">PR List</h2>
          {prs.map((pr: any, i: number) => (
            <div key={i} className="border p-2 rounded mb-2">
              <p><b>{pr.title}</b></p>
              <p>{pr.domain || "Auto"} • {pr.type}</p>
              <p>Status: {pr.status}</p>
              <h3 className="font-bold">Execution Pipeline</h3>
              {pr.results?.map((step: any, j: number) => (
                <div key={j} className="border p-2 rounded mb-2">
                  <p>
                    <b>{step.domain}</b> ({step.confidence})
                  </p>
                  <p>{step.result.message}</p>
                  {step.result.message && step.result.message.includes("Skipped") && (
                    <span className="text-yellow-500">⚠️ Skipped</span>
                  )}
                </div>
              ))}
              <Button onClick={() => executePR(pr)}>
                Run PR ⚡
              </Button>

              {/* STEP 4 — SHOW SYSTEM THINKING */}
              {pr.context && (
                <>
                  {pr.context.logs?.some((log: string) => log.includes("Semantic memory")) && (
                    <p className="text-purple-500">🧠 Semantic learning applied</p>
                  )}
                  {pr.context.logs?.some((log: string) => log.includes("AI routing applied")) && (
                    <p className="text-blue-500">🧠 AI Routing Applied</p>
                  )}
                  {pr.context.routing_reason && (
                    <p><b>Routing Reason:</b> {pr.context.routing_reason}</p>
                  )}
                  {pr.context.logs?.some((log: string) => log.includes("AI refinement")) && (
                    <p className="text-purple-500">🤖 AI optimization applied (Groq)</p>
                  )}
                  {pr.context.logs?.some((log: string) => log.includes("Memory applied")) && (
                    <p className="text-blue-500">🧠 Learned optimization applied</p>
                  )}
                  <h3 className="font-bold mt-4">System Context</h3>
                  <pre className="bg-gray-100 p-2 rounded text-sm">
                    {JSON.stringify(pr.context, null, 2)}
                  </pre>
                  {/* STEP 5 — VISUAL MEANING */}
                  <div className="mt-2">
                    <p><b>Data:</b> {pr.context.data ? "✔ Loaded" : "❌ None"}</p>
                    <p><b>Validated:</b> {pr.context.validated ? "✔ Yes" : "❌ No"}</p>
                    <h3 className="font-bold mt-4">Top Insights</h3>
                    {Array.isArray(pr.context?.insights) && pr.context?.insights?.length > 0 && (
                      pr.context.insights.map((insight: any, i: number) => (
                        <div
                          key={i}
                          className="border p-3 rounded mb-2 cursor-pointer hover:bg-gray-50"
                          onClick={() => runDrilldown(insight)}
                        >
                          <p className="font-semibold">
                            {i + 1}. {insight.insight}
                          </p>
                          <p className="text-sm">Type: {insight.type}</p>
                          <p className="text-sm">
                            Confidence: {insight.confidence}{" "}
                            <span>
                              {insight.confidence > 0.9 && (
                                <span className="text-red-600 font-bold">🔥 High Priority</span>
                              )}
                              {insight.confidence > 0.8 && insight.confidence <= 0.9 && "🟠 Medium"}
                              {insight.confidence > 0.6 && insight.confidence <= 0.8 && "🟡 Low"}
                              {insight.confidence <= 0.6 && "🔵 Very Low"}
                            </span>
                          </p>
                        </div>
                      ))
                    )}
                    {(!Array.isArray(pr.context?.insights) || pr.context?.insights?.length === 0) && (
                      <p>No insights available.</p>
                    )}
                    {pr.context?.logs?.some((log: string) => log.includes("AI ranked insights generated")) && (
                      <p className="text-purple-500">🤖 AI Insight Generated</p>
                    )}
                    {pr.context?.logs?.some((log: string) => log.includes("personalized")) && (
                      <p className="text-blue-500">🧠 Personalized for you</p>
                    )}
                  </div>
                  {/* DECISION LOG */}
                  <h3 className="font-bold mt-4">Decision Log</h3>
                  <ul>
                    {pr.context.logs?.map((log: string, i: number) => (
                      <li key={i}>
                        {log.includes("failed") && (
                          <span className="text-red-500">❌ {log}</span>
                        )}
                        {log.includes("success") && (
                          <span className="text-green-500">✅ {log}</span>
                        )}
                        {!log.includes("failed") && !log.includes("success") && (
                          <>• {log}</>
                        )}
                      </li>
                    ))}
                  </ul>
                  {/* STEP 4 — FRONTEND: DISPLAY ALERTS */}
                  <AlertsPanel userId={userId} />
                </>
              )}
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}
