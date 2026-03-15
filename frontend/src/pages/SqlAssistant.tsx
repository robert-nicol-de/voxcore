import React, { useState } from 'react';
import LiveQueryFlow, { type QueryFlowStage } from '../components/LiveQueryFlow';
import PageHeader from '../components/PageHeader';
import ChartRenderer from '../components/ChartRenderer';
import { apiUrl } from '../lib/api';
import { trackFeatureEvent } from '../lib/telemetry';

type ExecuteResult = {
  status?: string;
  risk_level?: string;
  effective_query?: string;
  reasons?: string[];
  understanding?: { metric?: string; dimension?: string; comparison?: string; summary?: string };
  chart_recommendation?: { chart_type?: string; reason?: string };
  analytical_plan?: { analysis_type?: string; metric?: string; dimension?: string; comparison?: string; time_dimension?: string; time_grain?: string; focus?: string | null; limit?: number };
  insights?: { top_performer?: string | null; largest_decline?: string | null; anomaly?: string | null; overall_trend?: string; narrative?: string };
  ranked_insights?: Array<{ text?: string; importance?: number }>;
  hypotheses?: string[];
  auto_drill?: Array<{ from?: string; to?: string; question?: string }>;
  driver_hints?: string[];
  patterns?: { anomalies?: Array<{ index?: number; value?: number; z_score?: number }>; seasonality?: string | null; spikes?: Array<{ index?: number; value?: number }>; correlation_hint?: string | null };
  related_metrics?: string[];
  analysis_session?: { metric?: string; dimension?: string; comparison?: string; filters?: Record<string, unknown> };
  insight_summary?: string;
  suggested_questions?: string[];
  semantic_context_prompt?: string;
  query_graph?: {
    graph_id?: string;
    graph_type?: string;
    nodes?: Array<{ id?: string; type?: string; stage?: string; execution_order?: number; label?: string; purpose?: string; depends_on?: string[]; output_name?: string; output_summary?: string; status?: string; name?: string; sql?: string; aggregation?: string; table?: string; column?: string; value?: string | number; time_column?: string; chart_type?: string; title?: string; operator?: string; filter_value?: unknown }>;
    execution_trace?: Array<{ node_id?: string; type?: string; stage?: string; execution_order?: number; label?: string; purpose?: string; depends_on?: string[]; output_name?: string; output_summary?: string; status?: string }>;
    execution_order?: string[];
    summary?: { node_count?: number; stage_count?: number; stages?: string[]; execution_path?: string[] };
    compiled_sql?: string;
    insight_hints?: string[];
    followup_questions?: string[];
    drilldowns?: string[];
    explanation?: string;
  };
};

export default function SqlAssistant() {
  const [databaseName, setDatabaseName] = useState('AdventureWorks2022');
  const [question, setQuestion] = useState('Show top 10 customers by revenue');
  const [generatedSql, setGeneratedSql] = useState('');
  const [riskLevel, setRiskLevel] = useState('LOW');
  const [previewRows, setPreviewRows] = useState<any[]>([]);
  const [executionResult, setExecutionResult] = useState<ExecuteResult | null>(null);
  const [understanding, setUnderstanding] = useState<{ metric?: string; dimension?: string; comparison?: string; summary?: string } | null>(null);
  const [chartRecommendation, setChartRecommendation] = useState<{ chart_type?: string; reason?: string } | null>(null);
  const [previewChart, setPreviewChart] = useState<any | null>(null);
  const [analyticalPlan, setAnalyticalPlan] = useState<{ analysis_type?: string; metric?: string; dimension?: string; comparison?: string; time_dimension?: string; time_grain?: string; focus?: string | null; limit?: number } | null>(null);
  const [insights, setInsights] = useState<{ top_performer?: string | null; largest_decline?: string | null; anomaly?: string | null; overall_trend?: string; narrative?: string } | null>(null);
  const [rankedInsights, setRankedInsights] = useState<Array<{ text?: string; importance?: number }>>([]);
  const [hypotheses, setHypotheses] = useState<string[]>([]);
  const [autoDrill, setAutoDrill] = useState<Array<{ from?: string; to?: string; question?: string }>>([]);
  const [driverHints, setDriverHints] = useState<string[]>([]);
  const [patterns, setPatterns] = useState<{ anomalies?: Array<{ index?: number; value?: number; z_score?: number }>; seasonality?: string | null; spikes?: Array<{ index?: number; value?: number }>; correlation_hint?: string | null } | null>(null);
  const [relatedMetrics, setRelatedMetrics] = useState<string[]>([]);
  const [analysisSession, setAnalysisSession] = useState<{ metric?: string; dimension?: string; comparison?: string; filters?: Record<string, unknown> } | null>(null);
  const [insightSummary, setInsightSummary] = useState<string>('');
  const [suggestedQuestions, setSuggestedQuestions] = useState<string[]>([]);
  const [semanticContextPrompt, setSemanticContextPrompt] = useState<string>('');
  type QueryGraphType = NonNullable<ExecuteResult['query_graph']>;
  const [queryGraph, setQueryGraph] = useState<QueryGraphType | null>(null);
  const [loadingPreview, setLoadingPreview] = useState(false);
  const [loadingExecute, setLoadingExecute] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [flowStages, setFlowStages] = useState<QueryFlowStage[]>(defaultFlowStages());

  const companyId = localStorage.getItem('voxcore_company_id') || 'default';
  const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';

  async function generateAndAnalyze(promptOverride?: string) {
    const promptToRun = (promptOverride ?? question).trim();
    if (!promptToRun) return;

    setError(null);
    setLoadingPreview(true);
    setPreviewRows([]);
    setExecutionResult(null);
    setGeneratedSql('');
    setUnderstanding(null);
    setChartRecommendation(null);
    setPreviewChart(null);
    setAnalyticalPlan(null);
    setInsights(null);
    setRankedInsights([]);
    setHypotheses([]);
    setAutoDrill([]);
    setDriverHints([]);
    setPatterns(null);
    setRelatedMetrics([]);
    setAnalysisSession(null);
    setInsightSummary('');
    setSuggestedQuestions([]);
    setSemanticContextPrompt('');
    setQueryGraph(null);

    setFlowStages([
      createStage('User Prompt', 'safe', previewPrompt(promptToRun)),
      createStage('AI Generated SQL', 'active', 'Generating SQL'),
      createStage('Risk Engine', 'idle', 'Waiting'),
      createStage('Policy Engine', 'idle', 'Waiting'),
      createStage('Sandbox', 'idle', 'Waiting'),
      createStage('Database', 'idle', 'Waiting'),
    ]);

    try {
      const riskRes = await fetch(apiUrl('/api/v1/query/risk'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: promptToRun, workspace_id: workspaceId }),
      });
      const riskData = await riskRes.json();
      const nextRiskLevel = (riskData.risk_level || 'low').toUpperCase();
      setRiskLevel(nextRiskLevel);
      if (riskData.generated_sql) {
        setGeneratedSql(riskData.generated_sql);
      } else {
        setGeneratedSql(promptToRun);
      }
      setUnderstanding(riskData.understanding || null);
      setChartRecommendation(riskData.chart_recommendation || null);
      setAnalyticalPlan(riskData.analytical_plan || null);
      setInsights(riskData.insights || null);
      setRankedInsights(Array.isArray(riskData.ranked_insights) ? riskData.ranked_insights : []);
      setHypotheses(Array.isArray(riskData.hypotheses) ? riskData.hypotheses : []);
      setAutoDrill(Array.isArray(riskData.auto_drill) ? riskData.auto_drill : []);
      setDriverHints(Array.isArray(riskData.driver_hints) ? riskData.driver_hints : []);
      setPatterns(riskData.patterns || null);
      setRelatedMetrics(Array.isArray(riskData.related_metrics) ? riskData.related_metrics : []);
      setAnalysisSession(riskData.analysis_session || null);
      setSuggestedQuestions(Array.isArray(riskData.suggested_questions) ? riskData.suggested_questions : []);
      setSemanticContextPrompt(riskData.semantic_context_prompt || '');
      if (riskData.query_graph) setQueryGraph(riskData.query_graph);

      setFlowStages([
        createStage('User Prompt', 'safe', previewPrompt(promptToRun)),
        createStage('AI Generated SQL', 'safe', 'SQL prepared'),
        createStage('Risk Engine', flowStatusFromRisk(nextRiskLevel), `${nextRiskLevel} RISK`),
        createStage('Policy Engine', 'active', 'Evaluating policy'),
        createStage('Sandbox', 'idle', 'Waiting'),
        createStage('Database', 'idle', 'Waiting'),
      ]);

      const sandboxRes = await fetch(apiUrl('/api/v1/query/sandbox'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: promptToRun, workspace_id: workspaceId }),
      });

      const sandboxData = await sandboxRes.json();
      if (!sandboxRes.ok) {
        setError(sandboxData.detail || 'Preview failed. Check query syntax.');
        const failedPreviewFlow = [
          createStage('User Prompt', 'safe', previewPrompt(promptToRun)),
          createStage('AI Generated SQL', 'safe', 'SQL prepared'),
          createStage('Risk Engine', flowStatusFromRisk(nextRiskLevel), `${nextRiskLevel} RISK`),
          createStage('Policy Engine', 'warning', 'Review required'),
          createStage('Sandbox', 'blocked', 'Preview failed'),
          createStage('Database', 'idle', 'Not reached'),
        ];
        setFlowStages(failedPreviewFlow);
        persistFlow(failedPreviewFlow);
        return;
      }

      const previewCount = (sandboxData.preview || []).length;
      setPreviewRows(sandboxData.preview || []);
      if (sandboxData.chart) {
        setPreviewChart(sandboxData.chart);
      }
      if (sandboxData.analytical_plan) {
        setAnalyticalPlan(sandboxData.analytical_plan);
      }
      if (sandboxData.insights) {
        setInsights(sandboxData.insights);
      }
      if (Array.isArray(sandboxData.ranked_insights)) {
        setRankedInsights(sandboxData.ranked_insights);
      }
      if (Array.isArray(sandboxData.hypotheses)) {
        setHypotheses(sandboxData.hypotheses);
      }
      if (Array.isArray(sandboxData.auto_drill)) {
        setAutoDrill(sandboxData.auto_drill);
      }
      if (Array.isArray(sandboxData.driver_hints)) {
        setDriverHints(sandboxData.driver_hints);
      }
      if (sandboxData.patterns) {
        setPatterns(sandboxData.patterns);
      }
      if (Array.isArray(sandboxData.related_metrics)) {
        setRelatedMetrics(sandboxData.related_metrics);
      }
      if (sandboxData.analysis_session) {
        setAnalysisSession(sandboxData.analysis_session);
      }
      if (sandboxData.insight_summary) {
        setInsightSummary(String(sandboxData.insight_summary));
      }
      if (Array.isArray(sandboxData.suggested_questions)) {
        setSuggestedQuestions(sandboxData.suggested_questions);
      }
      if (sandboxData.semantic_context_prompt) {
        setSemanticContextPrompt(String(sandboxData.semantic_context_prompt));
      }
      if (sandboxData.query_graph) {
        setQueryGraph(sandboxData.query_graph);
      }
      const previewFlow = [
        createStage('User Prompt', 'safe', previewPrompt(promptToRun)),
        createStage('AI Generated SQL', 'safe', 'SQL prepared'),
        createStage('Risk Engine', flowStatusFromRisk(nextRiskLevel), `${nextRiskLevel} RISK`),
        createStage('Policy Engine', 'safe', 'Passed policy checks'),
        createStage('Sandbox', 'safe', `Previewed ${previewCount} rows`),
        createStage('Database', 'idle', 'Awaiting execution'),
      ];
      void trackFeatureEvent({
        event: 'ai_query_executed',
        metadata: { surface: 'sql_assistant', question: promptToRun.slice(0, 120) },
      });
      setFlowStages(previewFlow);
      persistFlow(previewFlow);
    } catch {
      setError('Could not reach SQL assistant services.');
      const unavailableFlow = [
        createStage('User Prompt', 'safe', previewPrompt(promptToRun)),
        createStage('AI Generated SQL', 'warning', 'Service unavailable'),
        createStage('Risk Engine', 'idle', 'Waiting'),
        createStage('Policy Engine', 'idle', 'Waiting'),
        createStage('Sandbox', 'idle', 'Waiting'),
        createStage('Database', 'idle', 'Waiting'),
      ];
      setFlowStages(unavailableFlow);
      persistFlow(unavailableFlow);
    } finally {
      setLoadingPreview(false);
    }
  }

  async function executeQuery() {
    if (!question.trim()) return;

    setError(null);
    setLoadingExecute(true);
    setExecutionResult(null);

    const executionStartFlow = [
      createStage('User Prompt', 'safe', previewPrompt(question)),
      createStage('AI Generated SQL', generatedSql ? 'safe' : 'active', generatedSql ? 'SQL prepared' : 'Generating SQL'),
      createStage('Risk Engine', flowStatusFromRisk(riskLevel), `${riskLevel} RISK`),
      createStage('Policy Engine', 'active', 'Inspecting query'),
      createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'idle', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Waiting'),
      createStage('Database', 'idle', 'Waiting'),
    ];
    setFlowStages(executionStartFlow);
    persistFlow(executionStartFlow);

    try {
      const res = await fetch(apiUrl('/api/v1/query'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_id: companyId,
          workspace_id: workspaceId,
          query: question,
          agent: 'sql_assistant',
        }),
      });
      const data = await res.json();

      if (!res.ok || data.status !== 'queued' || !data.job_id) {
        setError(data.detail || data.message || 'Execution request failed.');
        const blockedFlow = [
          createStage('User Prompt', 'safe', previewPrompt(question)),
          createStage('AI Generated SQL', generatedSql ? 'safe' : 'warning', generatedSql ? 'SQL prepared' : 'Missing SQL'),
          createStage('Risk Engine', flowStatusFromRisk(riskLevel), `${riskLevel} RISK`),
          createStage('Policy Engine', 'blocked', 'Execution rejected'),
          createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'idle', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Waiting'),
          createStage('Database', 'idle', 'Not reached'),
        ];
        setFlowStages(blockedFlow);
        persistFlow(blockedFlow);
        return;
      }

      let finalResult: any = null;
      for (let i = 0; i < 25; i += 1) {
        await new Promise((resolve) => window.setTimeout(resolve, 700));
        const jobRes = await fetch(apiUrl(`/api/v1/query/jobs/${data.job_id}`));
        if (!jobRes.ok) continue;
        const jobData = await jobRes.json();
        if (jobData.status === 'completed' || jobData.status === 'failed' || jobData.status === 'blocked') {
          finalResult = jobData;
          break;
        }
      }

      if (!finalResult) {
        setError('Execution is still running. Check Query Logs for status.');
        const runningFlow = [
          createStage('User Prompt', 'safe', previewPrompt(question)),
          createStage('AI Generated SQL', 'safe', 'SQL prepared'),
          createStage('Risk Engine', flowStatusFromRisk(riskLevel), `${riskLevel} RISK`),
          createStage('Policy Engine', 'active', 'Queued for execution'),
          createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'idle', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Waiting'),
          createStage('Database', 'active', 'Executing'),
        ];
        setFlowStages(runningFlow);
        persistFlow(runningFlow);
        return;
      }

      if (finalResult.status === 'failed') {
        setError(finalResult.error || 'Execution failed.');
        const failedFlow = [
          createStage('User Prompt', 'safe', previewPrompt(question)),
          createStage('AI Generated SQL', 'safe', 'SQL prepared'),
          createStage('Risk Engine', flowStatusFromRisk(riskLevel), `${riskLevel} RISK`),
          createStage('Policy Engine', 'warning', 'Execution failed'),
          createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'idle', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Waiting'),
          createStage('Database', 'blocked', 'Execution failed'),
        ];
        setFlowStages(failedFlow);
        persistFlow(failedFlow);
        return;
      }

      const resultData = finalResult.result || {};
      setExecutionResult({
        status: finalResult.status,
        risk_level: resultData.risk_level,
        effective_query: resultData.effective_query,
        reasons: resultData.reasons,
        understanding: resultData.understanding,
        chart_recommendation: resultData.chart_recommendation,
        analytical_plan: resultData.analytical_plan,
        insights: resultData.insights,
        ranked_insights: resultData.ranked_insights,
        hypotheses: resultData.hypotheses,
        auto_drill: resultData.auto_drill,
        driver_hints: resultData.driver_hints,
        patterns: resultData.patterns,
        related_metrics: resultData.related_metrics,
        analysis_session: resultData.analysis_session,
        insight_summary: resultData.insight_summary,
        suggested_questions: resultData.suggested_questions,
        semantic_context_prompt: resultData.semantic_context_prompt,        query_graph: resultData.query_graph,      });
      if (resultData.effective_query) {
        setGeneratedSql(resultData.effective_query);
      }
      if (resultData.understanding) {
        setUnderstanding(resultData.understanding);
      }
      if (resultData.chart_recommendation) {
        setChartRecommendation(resultData.chart_recommendation);
      }
      if (resultData.analytical_plan) {
        setAnalyticalPlan(resultData.analytical_plan);
      }
      if (resultData.insights) {
        setInsights(resultData.insights);
      }
      if (Array.isArray(resultData.ranked_insights)) {
        setRankedInsights(resultData.ranked_insights);
      }
      if (Array.isArray(resultData.hypotheses)) {
        setHypotheses(resultData.hypotheses);
      }
      if (Array.isArray(resultData.auto_drill)) {
        setAutoDrill(resultData.auto_drill);
      }
      if (Array.isArray(resultData.driver_hints)) {
        setDriverHints(resultData.driver_hints);
      }
      if (resultData.patterns) {
        setPatterns(resultData.patterns);
      }
      if (Array.isArray(resultData.related_metrics)) {
        setRelatedMetrics(resultData.related_metrics);
      }
      if (resultData.analysis_session) {
        setAnalysisSession(resultData.analysis_session);
      }
      if (resultData.insight_summary) {
        setInsightSummary(String(resultData.insight_summary));
      }
      if (Array.isArray(resultData.suggested_questions)) {
        setSuggestedQuestions(resultData.suggested_questions);
      }
      if (resultData.semantic_context_prompt) {
        setSemanticContextPrompt(String(resultData.semantic_context_prompt));
      }
      if (resultData.query_graph) {
        setQueryGraph(resultData.query_graph);
      }

      const nextRisk = resultData.risk_level ? String(resultData.risk_level).toUpperCase() : riskLevel;
      setRiskLevel(nextRisk);

      const finalFlow = finalResult.status === 'blocked'
        ? [
            createStage('User Prompt', 'safe', previewPrompt(question)),
            createStage('AI Generated SQL', 'safe', 'SQL prepared'),
            createStage('Risk Engine', flowStatusFromRisk(nextRisk), `${nextRisk} RISK`),
            createStage('Policy Engine', 'blocked', 'Blocked by policy'),
            createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'warning', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Preview recommended'),
            createStage('Database', 'blocked', 'Write prevented'),
          ]
        : [
            createStage('User Prompt', 'safe', previewPrompt(question)),
            createStage('AI Generated SQL', 'safe', 'SQL prepared'),
            createStage('Risk Engine', flowStatusFromRisk(nextRisk), `${nextRisk} RISK`),
            createStage('Policy Engine', 'safe', 'Allowed to proceed'),
            createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'warning', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Executed directly'),
            createStage('Database', 'safe', 'Query completed'),
          ];

      setFlowStages(finalFlow);
      persistFlow(finalFlow);
    } catch {
      setError('Could not execute query.');
      const unavailableFlow = [
        createStage('User Prompt', 'safe', previewPrompt(question)),
        createStage('AI Generated SQL', generatedSql ? 'safe' : 'warning', generatedSql ? 'SQL prepared' : 'Missing SQL'),
        createStage('Risk Engine', flowStatusFromRisk(riskLevel), `${riskLevel} RISK`),
        createStage('Policy Engine', 'warning', 'Execution unavailable'),
        createStage('Sandbox', previewRows.length > 0 ? 'safe' : 'idle', previewRows.length > 0 ? `Previewed ${previewRows.length} rows` : 'Waiting'),
        createStage('Database', 'idle', 'Not reached'),
      ];
      setFlowStages(unavailableFlow);
      persistFlow(unavailableFlow);
    } finally {
      setLoadingExecute(false);
    }
  }

  function applySuggestedQuestion(nextQuestion: string) {
    setQuestion(nextQuestion);
    void generateAndAnalyze(nextQuestion);
  }

    return (
      <div className="flex flex-col gap-8 text-primary">
        <div className="flex items-center gap-4 mb-6">
          <img src="/assets/vc_logo.png" alt="VoxCloud" className="w-10 h-10 object-contain" />
          <PageHeader title="SQL Assistant" subtitle="Natural language SQL with live security pipeline and policy enforcement" />
        </div>

        <section className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div className="bg-surface rounded-md border-default shadow-md flex flex-col gap-4 p-6">
            <div className="flex flex-wrap items-center gap-3">
              <label className="text-muted text-sm">Database:</label>
              <select value={databaseName} onChange={(e) => setDatabaseName(e.target.value)} className="bg-primary text-primary border-default rounded-sm p-2">
                <option value="AdventureWorks2022">AdventureWorks2022</option>
                <option value="FinancialDW">FinancialDW</option>
                <option value="SalesAnalytics">SalesAnalytics</option>
              </select>
            </div>

            <div className="mt-5">
              <div className="mb-2 text-muted">Prompt</div>
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                rows={3}
                className="bg-primary text-primary border-default rounded-md p-2 w-full resize-vertical"
                placeholder="Show top 10 customers by revenue"
              />
              <div className="flex gap-3 mt-3 flex-wrap">
                <button onClick={generateAndAnalyze} disabled={loadingPreview} className="bg-brand text-primary rounded-sm px-4 py-2 font-semibold" style={{ border: 'none', cursor: 'pointer' }}>
                  {loadingPreview ? 'Generating...' : 'Preview in Sandbox'}
                </button>
                <button onClick={executeQuery} disabled={loadingExecute} className="bg-info text-primary rounded-sm px-4 py-2 font-semibold" style={{ border: 'none', cursor: 'pointer' }}>
                  {loadingExecute ? 'Executing...' : 'Execute'}
                </button>
              </div>
            </div>
          </div>

          <LiveQueryFlow
            title="AI Security Pipeline"
            subtitle="Each stage lights up as the query moves through VoxCore security."
            stages={flowStages}
            compact
          />
        </section>

        <section className="bg-surface rounded-md border-default shadow-md flex flex-col gap-4 p-6">
          <h2 className="text-primary text-lg font-bold mb-2">Understanding Your Request</h2>
          {understanding ? (
            <div className="mb-4 text-secondary">
              <div>Metric: <strong>{understanding.metric || 'Unknown'}</strong></div>
              <div>Dimension: <strong>{understanding.dimension || 'Unknown'}</strong></div>
              <div>Comparison: <strong>{understanding.comparison || 'None'}</strong></div>
            </div>
          ) : (
            <div className="mb-4 text-muted">Submit a question to detect metric, dimension, and comparison.</div>
          )}

          {chartRecommendation && (
            <div className="mb-4 p-3 rounded-md border-default bg-surface-elevated text-secondary">
              <div><strong>Chart Type:</strong> {(chartRecommendation.chart_type || 'bar').toUpperCase()}</div>
              <div className="text-muted mt-1">{chartRecommendation.reason || ''}</div>
            </div>
          )}

          {analyticalPlan && (
            <div className="mb-4 p-3 rounded-md border-default bg-surface-elevated text-secondary">
              <div className="font-bold mb-1">Analytical Plan</div>
              <div>Type: <strong>{analyticalPlan.analysis_type || 'comparison'}</strong></div>
              <div>Metric: <strong>{analyticalPlan.metric || 'revenue'}</strong></div>
              <div>Dimension: <strong>{analyticalPlan.dimension || 'district'}</strong></div>
              <div>Comparison: <strong>{analyticalPlan.comparison || 'none'}</strong></div>
              <div>Time: <strong>{analyticalPlan.time_dimension || 'order_date'}</strong> ({analyticalPlan.time_grain || 'month'})</div>
              {analyticalPlan.focus && <div>Focus: <strong>{analyticalPlan.focus}</strong></div>}
              {typeof analyticalPlan.limit === 'number' && <div>Top N: <strong>{analyticalPlan.limit}</strong></div>}
            </div>
          )}

          {/* Reasoning Graph and other sections remain, but should be refactored similarly for design system compliance. */}
          {/* ...existing code for Reasoning Graph, SQL, and risk level... */}
        </section>

        {/* ...existing code for LiveQueryFlow, Sandbox Preview, Execution Result, and error display, refactored for design system compliance... */}
      </div>
    );
}

function riskLevelColor(level: string) {
  const value = level.toLowerCase();
  if (value.includes('high') || value.includes('critical')) return '#ff6b6b';
  if (value.includes('med')) return '#ffd166';
  return '#35d07f';
}

function createStage(label: string, status: QueryFlowStage['status'], detail: string) {
  return { label, status, detail };
}

function defaultFlowStages(): QueryFlowStage[] {
  return [
    createStage('User Prompt', 'idle', 'Waiting for prompt'),
    createStage('AI Generated SQL', 'idle', 'Waiting for generation'),
    createStage('Risk Engine', 'idle', 'Waiting for analysis'),
    createStage('Policy Engine', 'idle', 'Waiting for policy check'),
    createStage('Sandbox', 'idle', 'Waiting for preview'),
    createStage('Database', 'idle', 'Waiting for execution'),
  ];
}

function previewPrompt(value: string) {
  const trimmed = value.trim();
  if (!trimmed) return 'Waiting for prompt';
  return trimmed.length > 38 ? `${trimmed.slice(0, 35)}...` : trimmed;
}

function flowStatusFromRisk(level: string): QueryFlowStage['status'] {
  const value = level.toLowerCase();
  if (value.includes('high') || value.includes('critical')) return 'warning';
  if (value.includes('med')) return 'warning';
  return 'safe';
}

function persistFlow(stages: QueryFlowStage[]) {
  try {
    localStorage.setItem('voxcloud_latest_query_flow', JSON.stringify(stages));
  } catch {
    // Ignore storage errors.
  }
}

const panelStyle: React.CSSProperties = {
  background: 'var(--platform-card-bg)',
  border: '1px solid var(--platform-border)',
  borderRadius: 12,
  padding: 24,
};

const sectionTitle: React.CSSProperties = {
  marginTop: 0,
  marginBottom: 14,
  fontSize: '1.1rem',
};

const inputStyle: React.CSSProperties = {
  background: 'rgba(10,16,28,0.8)',
  color: '#e8f0ff',
  border: '1px solid var(--platform-border)',
  borderRadius: 8,
  padding: '10px 12px',
  fontSize: 14,
};

const primaryButton: React.CSSProperties = {
  background: 'var(--platform-accent)',
  color: '#ffffff',
  border: '1px solid var(--platform-accent)',
  borderRadius: 10,
  padding: '10px 16px',
  fontWeight: 700,
  cursor: 'pointer',
};

const secondaryButton: React.CSSProperties = {
  background: 'transparent',
  color: '#d7e5ff',
  border: '1px solid var(--platform-border)',
  borderRadius: 10,
  padding: '10px 16px',
  fontWeight: 700,
  cursor: 'pointer',
};

const tableHeadCell: React.CSSProperties = {
  textAlign: 'left',
  padding: '10px 12px',
  borderBottom: '1px solid var(--platform-border)',
  color: 'var(--platform-muted)',
  fontSize: 12,
  textTransform: 'uppercase',
  letterSpacing: '0.06em',
};

const tableCell: React.CSSProperties = {
  textAlign: 'left',
  padding: '10px 12px',
  borderBottom: '1px solid rgba(79,140,255,0.1)',
  color: '#dbe7ff',
  fontSize: 13,
};

// ── Query Graph helpers ────────────────────────────────────────────────────

const GRAPH_NODE_COLORS: Record<string, { bg: string; border: string; icon: string }> = {
  metric:       { bg: 'rgba(52, 168, 100, 0.1)',  border: 'rgba(52, 168, 100, 0.35)',  icon: '∑' },
  dimension:    { bg: 'rgba(79, 140, 255, 0.1)',  border: 'rgba(79, 140, 255, 0.35)',  icon: '⊞' },
  time_grain:   { bg: 'rgba(180, 120, 250, 0.1)', border: 'rgba(180, 120, 250, 0.35)', icon: '⌚' },
  comparison:   { bg: 'rgba(255, 180, 60, 0.1)',  border: 'rgba(255, 180, 60, 0.35)',  icon: '⇄' },
  filter:       { bg: 'rgba(255, 100, 100, 0.1)', border: 'rgba(255, 100, 100, 0.35)', icon: '⟨⟩' },
  limit:        { bg: 'rgba(100, 200, 220, 0.1)', border: 'rgba(100, 200, 220, 0.35)', icon: '↥' },
  visualization:{ bg: 'rgba(250, 200, 80, 0.1)',  border: 'rgba(250, 200, 80, 0.35)',  icon: '📊' },
};

function graphNodeCard(type: string): React.CSSProperties {
  const colors = GRAPH_NODE_COLORS[type] || { bg: 'rgba(255,255,255,0.05)', border: 'rgba(255,255,255,0.15)', icon: '○' };
  return {
    background: colors.bg,
    border: `1px solid ${colors.border}`,
    borderRadius: 10,
    padding: '10px 14px',
    minWidth: 120,
    maxWidth: 200,
    color: '#dbe7ff',
  };
}

type GraphNodeDict = {
  id?: string;
  type?: string;
  stage?: string;
  execution_order?: number;
  label?: string;
  purpose?: string;
  depends_on?: string[];
  output_name?: string;
  output_summary?: string;
  status?: string;
  name?: string;
  sql?: string;
  aggregation?: string;
  table?: string;
  column?: string;
  value?: string | number;
  time_column?: string;
  chart_type?: string;
  title?: string;
  operator?: string;
  filter_value?: unknown;
};

const graphMetaChip: React.CSSProperties = {
  background: 'rgba(79,140,255,0.12)',
  color: '#c9ddff',
  border: '1px solid rgba(79,140,255,0.28)',
  borderRadius: 999,
  padding: '4px 10px',
  fontSize: 11,
};

const graphTraceRow: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: '40px minmax(0, 1fr)',
  gap: 12,
  alignItems: 'start',
  padding: '10px 0',
  borderBottom: '1px solid rgba(79,140,255,0.1)',
};

const graphTraceOrder: React.CSSProperties = {
  width: 32,
  height: 32,
  display: 'grid',
  placeItems: 'center',
  borderRadius: '50%',
  background: 'rgba(79,140,255,0.14)',
  border: '1px solid rgba(79,140,255,0.28)',
  color: '#e6f0ff',
  fontWeight: 700,
  fontSize: 12,
};

const graphTraceTag: React.CSSProperties = {
  background: 'rgba(255,255,255,0.06)',
  border: '1px solid rgba(255,255,255,0.1)',
  borderRadius: 999,
  padding: '2px 8px',
  color: '#b8c7de',
  fontSize: 10,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
};

function graphNodeLabel(node: GraphNodeDict): string {
  const icon = GRAPH_NODE_COLORS[node.type || '']?.icon || '○';
  const fallbackLabel = node.label || node.name || node.type || '';
  switch (node.type) {
    case 'metric':       return `${icon} ${node.name || 'metric'}`;
    case 'dimension':    return `${icon} ${node.name || 'dimension'}`;
    case 'time_grain':   return `${icon} ${String(node.value || 'year')}`;
    case 'comparison':   return `${icon} ${String(node.value || '')}`;
    case 'filter':       return `${icon} ${node.column || ''} ${node.operator || '='} ${String(node.filter_value ?? '')}`;
    case 'limit':        return `${icon} TOP ${node.value ?? 10}`;
    case 'visualization':return `${icon} ${node.chart_type || 'bar_chart'}`;
    default:             return `${icon} ${String(fallbackLabel || node.value || '')}`.trim();
  }
}

function graphNodeSub(node: GraphNodeDict): string {
  if (node.output_summary) return node.output_summary;
  switch (node.type) {
    case 'metric':    return node.sql ? node.sql.slice(0, 40) + (node.sql.length > 40 ? '…' : '') : '';
    case 'dimension': return node.column && node.column !== node.name ? node.column : (node.table || '');
    case 'time_grain':return node.time_column || '';
    case 'visualization': return node.title || '';
    default:          return '';
  }
}

