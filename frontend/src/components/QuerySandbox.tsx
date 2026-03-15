import { useEffect, useMemo, useState } from 'react';
import ChartRenderer from '../components/ChartRenderer';
import PageHeader from '../components/PageHeader';
import { apiUrl } from '../lib/api';
import { trackFeatureEvent } from '../lib/telemetry';

type RiskPayload = {
  risk_level?: string;
  reasons?: string[];
  generated_sql?: string;
  query_graph?: { compiled_sql?: string };
  understanding?: { metric?: string; dimension?: string; summary?: string };
  analysis_session?: { metric?: string; dimension?: string; comparison?: string };
};

type SandboxPayload = {
  status?: string;
  rows?: number;
  preview?: Array<Record<string, unknown>>;
  chart?: unknown;
};

type InsightCategory = {
  category: string;
  icon: string;
  insights: string[];
};

type StructuredInsight = {
  id: string;
  rank: number;
  category: string;
  title: string;
  insight: string;
  driver: string;
  impact: string;
  suggested_action: string;
  confidence: number;
  source: string;
};

type DailyReport = {
  title: string;
  report_date: string;
  headline: string;
  driver: string;
  confidence: number;
  source: string;
};

type AskWhyDimension = {
  dimension: string;
  finding: string;
};

type AskWhyPayload = {
  status: string;
  insight_id: string;
  title: string;
  root_cause: string;
  dimensions: AskWhyDimension[];
  recommended_investigation: string;
  confidence: number;
  source: string;
};

type EngineOverview = {
  what_happened: string;
  why_it_happened: string;
  should_the_business_care: string;
  monitoring_mode: string;
};

type DriverSignal = {
  label: string;
  type: string;
  share: number;
};

type AnomalySignal = {
  title: string;
  detail: string;
  severity: string;
};

type ExecutiveBriefing = {
  title: string;
  report_date: string;
  summary_lines: string[];
  priority: string;
  confidence: number;
  source: string;
};

type InsightsPayload = {
  status: string;
  dataset: string;
  standard: string;
  engine_overview: EngineOverview;
  total_insights: number;
  categories: InsightCategory[];
  structured_insights: StructuredInsight[];
  business_drivers: DriverSignal[];
  anomalies: AnomalySignal[];
  daily_report: DailyReport;
  executive_briefing: ExecutiveBriefing;
};

type PlaygroundMode = 'ask' | 'sql';

const CATEGORY_META: Record<string, { emoji: string; color: string }> = {
  summary:  { emoji: '📊', color: '#3b82f6' },
  performers: { emoji: '🏆', color: '#8b5cf6' },
  trend:    { emoji: '📈', color: '#10b981' },
  distribution: { emoji: '🧮', color: '#f97316' },
  outlier:  { emoji: '🔎', color: '#f59e0b' },
  correlation: { emoji: '🧠', color: '#06b6d4' },
  narrative: { emoji: '✨', color: '#ec4899' },
};

const EXAMPLE_QUESTIONS = [
  'Show total revenue',
  'Revenue by country',
  'Top selling products',
  'Average order value by region',
  'Orders this month',
];

const GUARDIAN_BLOCK_PATTERN = /\b(drop|delete|truncate|alter|insert|update)\b/i;

export default function QuerySandbox() {
  const [mode, setMode] = useState<PlaygroundMode>('ask');
  const [question, setQuestion] = useState('Show revenue by country this year');
  const [sqlInput, setSqlInput] = useState('SELECT customer_name, SUM(total) AS total_revenue\nFROM orders\nGROUP BY customer_name\nORDER BY total_revenue DESC');
  const [generatedSql, setGeneratedSql] = useState('');
  const [riskLevel, setRiskLevel] = useState('LOW');
  const [riskReasons, setRiskReasons] = useState<string[]>([]);
  const [understanding, setUnderstanding] = useState<RiskPayload['understanding']>(null);
  const [analysisSession, setAnalysisSession] = useState<RiskPayload['analysis_session']>(null);
  const [previewRows, setPreviewRows] = useState<Array<Record<string, unknown>>>([]);
  const [previewChart, setPreviewChart] = useState<unknown>(null);
  const [statusMessage, setStatusMessage] = useState('Ask a question to start the VoxCore Playground.');
  const [guardianMessage, setGuardianMessage] = useState('');
  const [shareMessage, setShareMessage] = useState('');
  const [insightCategories, setInsightCategories] = useState<InsightCategory[]>([]);
  const [structuredInsights, setStructuredInsights] = useState<StructuredInsight[]>([]);
  const [dailyReport, setDailyReport] = useState<DailyReport | null>(null);
  const [executiveBriefing, setExecutiveBriefing] = useState<ExecutiveBriefing | null>(null);
  const [engineOverview, setEngineOverview] = useState<EngineOverview | null>(null);
  const [driverSignals, setDriverSignals] = useState<DriverSignal[]>([]);
  const [anomalySignals, setAnomalySignals] = useState<AnomalySignal[]>([]);
  const [askWhyByInsightId, setAskWhyByInsightId] = useState<Record<string, AskWhyPayload>>({});
  const [askWhyLoadingId, setAskWhyLoadingId] = useState('');
  const [insightSummary, setInsightSummary] = useState('');
  const [generatingInsights, setGeneratingInsights] = useState(false);
  const [isRunning, setIsRunning] = useState(false);

  const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default';

  const tableColumns = useMemo(() => Object.keys(previewRows[0] || {}), [previewRows]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const sharedQuestion = params.get('pgq');
    const sharedSql = params.get('pgsql');
    const sharedRisk = params.get('pgrisk');

    if (sharedQuestion) {
      setQuestion(sharedQuestion);
      setStatusMessage('Loaded from shared playground link. Click "Run in Playground" to execute.');
    }
    if (sharedSql) {
      setGeneratedSql(sharedSql);
    }
    if (sharedRisk) {
      setRiskLevel(sharedRisk.toUpperCase());
    }
  }, []);

  async function sharePlaygroundLink() {
    const params = new URLSearchParams(window.location.search);
    params.set('pgq', question || '');
    if (generatedSql) params.set('pgsql', generatedSql);
    if (riskLevel) params.set('pgrisk', riskLevel.toLowerCase());

    const shareUrl = `${window.location.origin}${window.location.pathname}?${params.toString()}`;

    try {
      await navigator.clipboard.writeText(shareUrl);
      setShareMessage('Playground link copied to clipboard.');
    } catch {
      setShareMessage(`Copy this share link: ${shareUrl}`);
    }
  }

  async function runPlaygroundQuery(promptOverride?: string) {
    const prompt = (promptOverride ?? question).trim();
    if (!prompt) {
      setStatusMessage('Please enter a question.');
      return;
    }

    setQuestion(prompt);
    setIsRunning(true);
    setGuardianMessage('');
    setShareMessage('');
    setStatusMessage('VoxCore Brain is analyzing your question...');
    setPreviewRows([]);
    setPreviewChart(null);
    setRiskReasons([]);
    setInsightCategories([]);
    setStructuredInsights([]);
    setDailyReport(null);
    setExecutiveBriefing(null);
    setEngineOverview(null);
    setDriverSignals([]);
    setAnomalySignals([]);
    setAskWhyByInsightId({});
    setInsightSummary('');

    if (GUARDIAN_BLOCK_PATTERN.test(prompt)) {
      setRiskLevel('HIGH');
      setGeneratedSql('-- blocked by guardian before SQL generation');
      setGuardianMessage('VoxCore Guardian blocked this query. Unsafe database operation detected. Your data remains protected.');
      setStatusMessage('Query blocked in demo sandbox.');
      setIsRunning(false);
      return;
    }

    try {
      const riskRes = await fetch(apiUrl('/api/v1/query/risk'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: prompt, workspace_id: workspaceId }),
      });

      const riskData = (await riskRes.json()) as RiskPayload;
      if (!riskRes.ok) {
        setStatusMessage('VoxCore Brain could not process this request right now.');
        setIsRunning(false);
        return;
      }

      const sql = String(riskData.generated_sql || riskData.query_graph?.compiled_sql || '').trim();
      setGeneratedSql(sql || '-- no SQL returned by semantic layer');
      setRiskLevel(String(riskData.risk_level || 'low').toUpperCase());
      setRiskReasons(Array.isArray(riskData.reasons) ? riskData.reasons : []);
      setUnderstanding(riskData.understanding || null);
      setAnalysisSession(riskData.analysis_session || null);

      const queryForSandbox = sql || prompt;
      const sandboxRes = await fetch(apiUrl('/api/v1/query/sandbox'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: queryForSandbox, workspace_id: workspaceId }),
      });

      const sandboxData = (await sandboxRes.json()) as SandboxPayload;
      if (!sandboxRes.ok) {
        const detail = String((sandboxData as { detail?: string }).detail || 'Sandbox execution failed.');
        const blocked = detail.toLowerCase().includes('read-only') || detail.toLowerCase().includes('blocked');
        if (blocked) {
          setGuardianMessage('VoxCore Guardian blocked this query. Unsafe database operation detected. Your data remains protected.');
          setStatusMessage('Query blocked by Guardian policy checks.');
        } else {
          setStatusMessage(detail);
        }
        setIsRunning(false);
        return;
      }

      setPreviewRows(Array.isArray(sandboxData.preview) ? sandboxData.preview : []);
      setPreviewChart(sandboxData.chart || null);
      void trackFeatureEvent({
        event: 'ai_query_executed',
        dataset: 'sales',
        metadata: { mode: 'ask', question: prompt.slice(0, 120) },
      });
      setStatusMessage(
        `VoxCore executed safely in demo sandbox and returned ${Number(sandboxData.rows || 0)} rows.`
      );
    } catch {
      setStatusMessage('Playground service is temporarily unavailable.');
    } finally {
      setIsRunning(false);
    }
  }

  async function runSqlMode() {
    const sql = sqlInput.trim();
    if (!sql) {
      setStatusMessage('Please enter SQL.');
      return;
    }

    setIsRunning(true);
    setGuardianMessage('');
    setShareMessage('');
    setGeneratedSql(sql);
    setStatusMessage('Validating SQL with VoxCore Guardian...');
    setPreviewRows([]);
    setPreviewChart(null);
    setRiskReasons([]);
    setInsightCategories([]);
    setStructuredInsights([]);
    setDailyReport(null);
    setExecutiveBriefing(null);
    setEngineOverview(null);
    setDriverSignals([]);
    setAnomalySignals([]);
    setAskWhyByInsightId({});
    setInsightSummary('');

    if (GUARDIAN_BLOCK_PATTERN.test(sql)) {
      setRiskLevel('HIGH');
      setGuardianMessage('VoxCore Guardian blocked this SQL. Unsafe database operation detected. Your data remains protected.');
      setStatusMessage('SQL blocked in demo sandbox.');
      setIsRunning(false);
      return;
    }

    try {
      const riskRes = await fetch(apiUrl('/api/v1/query/risk'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: sql, workspace_id: workspaceId }),
      });

      const riskData = (await riskRes.json()) as RiskPayload;
      if (!riskRes.ok) {
        setStatusMessage('Guardian could not evaluate SQL right now.');
        setIsRunning(false);
        return;
      }

      setRiskLevel(String(riskData.risk_level || 'low').toUpperCase());
      setRiskReasons(Array.isArray(riskData.reasons) ? riskData.reasons : []);
      setUnderstanding(riskData.understanding || null);
      setAnalysisSession(riskData.analysis_session || null);

      const sandboxRes = await fetch(apiUrl('/api/v1/query/sandbox'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: sql, workspace_id: workspaceId }),
      });

      const sandboxData = (await sandboxRes.json()) as SandboxPayload;
      if (!sandboxRes.ok) {
        const detail = String((sandboxData as { detail?: string }).detail || 'Sandbox execution failed.');
        const blocked = detail.toLowerCase().includes('read-only') || detail.toLowerCase().includes('blocked');
        if (blocked) {
          setGuardianMessage('VoxCore Guardian blocked this SQL. Unsafe database operation detected. Your data remains protected.');
          setStatusMessage('SQL blocked by Guardian policy checks.');
        } else {
          setStatusMessage(detail);
        }
        setIsRunning(false);
        return;
      }

      setPreviewRows(Array.isArray(sandboxData.preview) ? sandboxData.preview : []);
      setPreviewChart(sandboxData.chart || null);
      void trackFeatureEvent({
        event: 'ai_query_executed',
        dataset: 'sales',
        metadata: { mode: 'sql' },
      });
      setStatusMessage(`SQL mode executed in demo sandbox and returned ${Number(sandboxData.rows || 0)} rows.`);
    } catch {
      setStatusMessage('Playground service is temporarily unavailable.');
    } finally {
      setIsRunning(false);
    }
  }

  async function generateInsights() {
    setGeneratingInsights(true);
    setGuardianMessage('');
    setShareMessage('');
    setInsightCategories([]);
    setStructuredInsights([]);
    setDailyReport(null);
    setExecutiveBriefing(null);
    setEngineOverview(null);
    setDriverSignals([]);
    setAnomalySignals([]);
    setAskWhyByInsightId({});
    setInsightSummary('VoxCore Brain is scanning the dataset...');
    void trackFeatureEvent({
      event: 'explain_data_clicked',
      dataset: 'sales',
      metadata: { surface: 'playground' },
    });
    try {
      const res = await fetch(apiUrl('/api/v1/playground/insights'));
      if (!res.ok) {
        setInsightSummary('VoxCore could not generate insights right now. Please try again.');
        return;
      }
      const data = (await res.json()) as InsightsPayload;
      if (!Array.isArray(data.categories) || data.categories.length === 0) {
        setInsightSummary('No insights returned from the demo dataset.');
        return;
      }
      setInsightCategories(data.categories);
      setStructuredInsights(Array.isArray(data.structured_insights) ? data.structured_insights : []);
      setDailyReport(data.daily_report || null);
      setExecutiveBriefing(data.executive_briefing || null);
      setEngineOverview(data.engine_overview || null);
      setDriverSignals(Array.isArray(data.business_drivers) ? data.business_drivers : []);
      setAnomalySignals(Array.isArray(data.anomalies) ? data.anomalies : []);
      setInsightSummary(
        `VoxCore AI Analyst reviewed ${data.dataset} using 7 explainability engines · ${data.total_insights} insights were generated after Guardian-approved execution.`
      );
    } catch {
      setInsightSummary('Insight generation is temporarily unavailable.');
      setInsightCategories([]);
      setStructuredInsights([]);
      setDailyReport(null);
      setExecutiveBriefing(null);
      setEngineOverview(null);
      setDriverSignals([]);
      setAnomalySignals([]);
    } finally {
      setGeneratingInsights(false);
    }
  }

  async function askWhy(insightId: string) {
    setAskWhyLoadingId(insightId);
    void trackFeatureEvent({
      event: 'ask_why_triggered',
      dataset: 'sales',
      metadata: { insight_id: insightId },
    });
    try {
      const res = await fetch(apiUrl(`/api/v1/playground/insights/ask-why?insight_id=${encodeURIComponent(insightId)}`));
      if (!res.ok) {
        return;
      }
      const data = (await res.json()) as AskWhyPayload;
      setAskWhyByInsightId((current) => ({ ...current, [insightId]: data }));
    } finally {
      setAskWhyLoadingId('');
    }
  }

  return (
    <div className="sandbox-container sandbox-watermark">
      <PageHeader title="VoxCore Playground" subtitle="Try VoxCore instantly with a demo company: Northwind Retail Group" />

      <div className="card playground-banner">
        <div>
          <div className="playground-banner-title">You are using a Demo Sandbox</div>
          <div className="playground-banner-copy">Your real databases stay protected by VoxCore Guardian.</div>
        </div>
      </div>

      <div className="card">
        <h3>Ask a question about the data</h3>
        <div className="playground-mode-switch" role="tablist" aria-label="Playground mode">
          <button
            className={`playground-mode-btn${mode === 'ask' ? ' active' : ''}`}
            onClick={() => setMode('ask')}
            type="button"
          >
            Ask VoxCore
          </button>
          <button
            className={`playground-mode-btn${mode === 'sql' ? ' active' : ''}`}
            onClick={() => setMode('sql')}
            type="button"
          >
            SQL Mode
          </button>
        </div>
        <div className="sandbox-input-row">
          {mode === 'ask' ? (
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask VoxCore about the demo data..."
              className="sandbox-input"
            />
          ) : (
            <textarea
              value={sqlInput}
              onChange={(e) => setSqlInput(e.target.value)}
              className="sandbox-sql-input"
              rows={5}
              placeholder="SELECT * FROM customers LIMIT 10"
            />
          )}
          <button className="primary-btn" onClick={mode === 'ask' ? () => runPlaygroundQuery() : runSqlMode} disabled={isRunning}>
            {isRunning ? 'Running Playground...' : mode === 'ask' ? 'Run in Playground' : 'Run SQL in Playground'}
          </button>
          <button className="secondary-btn playground-explain-btn" onClick={generateInsights} disabled={generatingInsights || isRunning}>
            {generatingInsights ? 'Analyzing...' : 'Explain My Data'}
          </button>
          <button className="secondary-btn" onClick={sharePlaygroundLink}>
            Share Playground
          </button>
        </div>

        {shareMessage ? <div className="results-placeholder" style={{ marginTop: 10 }}>{shareMessage}</div> : null}

        {mode === 'ask' ? (
          <div className="playground-examples">
            {EXAMPLE_QUESTIONS.map((example) => (
              <button
                key={example}
                className="playground-chip"
                onClick={() => runPlaygroundQuery(example)}
                disabled={isRunning}
              >
                {example}
              </button>
            ))}
          </div>
        ) : (
          <div className="results-placeholder" style={{ marginTop: 10 }}>
            SQL Mode is for advanced users who want direct query exploration with VoxCore Guardian checks.
          </div>
        )}
      </div>

      {guardianMessage ? (
        <div className="card playground-guardian-block">
          <h3>Query Blocked by VoxCore Guardian</h3>
          <p>{guardianMessage}</p>
        </div>
      ) : null}

      <div className="card">
        <h3>VoxCore Brain Generated SQL</h3>
        <pre className="sql-preview">{generatedSql || '-- SQL will appear here after you ask a question'}</pre>
        <div className="sandbox-risk-row">
          <span>Guardian Risk Analysis</span>
          <span className={`risk-badge ${riskLevel.toLowerCase()}`}>{riskLevel} RISK</span>
        </div>
        {riskReasons.length > 0 ? (
          <ul className="playground-reasons">
            {riskReasons.map((reason) => (
              <li key={reason}>{reason}</li>
            ))}
          </ul>
        ) : null}
      </div>

      <div className="card">
        <h3>Semantic Intelligence Layer</h3>
        <div className="playground-semantic-grid">
          <div>
            <span className="playground-semantic-label">Metric</span>
            <span>{understanding?.metric || analysisSession?.metric || 'revenue'}</span>
          </div>
          <div>
            <span className="playground-semantic-label">Dimension</span>
            <span>{understanding?.dimension || analysisSession?.dimension || 'country'}</span>
          </div>
          <div>
            <span className="playground-semantic-label">Summary</span>
            <span>{understanding?.summary || 'VoxCore maps business intent to SQL safely.'}</span>
          </div>
        </div>
      </div>

      <div className="card playground-insights-card">
        <div className="playground-insights-header">
          <h3>VoxCore Insights</h3>
          {insightCategories.length === 0 && !generatingInsights && (
            <button
              className="secondary-btn playground-explain-btn"
              onClick={generateInsights}
              disabled={isRunning}
            >
              Explain My Data
            </button>
          )}
        </div>

        {insightCategories.length === 0 ? (
          <div className="results-placeholder">
            {insightSummary || '\u201cExplain My Data\u201d lets VoxCore Brain profile the business automatically, while Guardian stays in control of execution.'}
          </div>
        ) : (
          <>
            {executiveBriefing ? (
              <div className="executive-briefing-card">
                <div className="executive-briefing-label">{executiveBriefing.title}</div>
                <div className="executive-briefing-grid">
                  <div>
                    <div className="executive-briefing-meta">
                      <span>{executiveBriefing.report_date}</span>
                      <span>{executiveBriefing.priority.toUpperCase()} priority</span>
                      <span>{executiveBriefing.confidence}% confidence</span>
                    </div>
                    <ul className="executive-briefing-list">
                      {executiveBriefing.summary_lines.map((line) => (
                        <li key={line}>{line}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="executive-briefing-source">Source: {executiveBriefing.source}</div>
                </div>
              </div>
            ) : null}
            {dailyReport ? (
              <div className="daily-report-banner">
                <div className="daily-report-title">{dailyReport.title}</div>
                <div className="daily-report-headline">{dailyReport.headline}</div>
                <div className="daily-report-meta">
                  <span>{dailyReport.report_date}</span>
                  <span>{dailyReport.confidence}% confidence</span>
                  <span>{dailyReport.source}</span>
                </div>
              </div>
            ) : null}
            <div className="insights-guardian-flow">
              <span className="igf-step igf-brain">VoxCore Brain</span>
              <span className="igf-arrow">&rarr;</span>
              <span className="igf-step igf-guardian">Guardian Approval</span>
              <span className="igf-arrow">&rarr;</span>
              <span className="igf-step igf-safe">Safe Queries</span>
              <span className="igf-arrow">&rarr;</span>
              <span className="igf-step igf-insights">Insights Generated</span>
            </div>
            <p className="insights-summary-text">{insightSummary}</p>
            {engineOverview ? (
              <div className="engine-overview-grid">
                <div className="engine-overview-card">
                  <span className="engine-overview-label">What Happened?</span>
                  <p>{engineOverview.what_happened}</p>
                </div>
                <div className="engine-overview-card">
                  <span className="engine-overview-label">Why Did It Happen?</span>
                  <p>{engineOverview.why_it_happened}</p>
                </div>
                <div className="engine-overview-card">
                  <span className="engine-overview-label">Should The Business Care?</span>
                  <p>{engineOverview.should_the_business_care}</p>
                </div>
              </div>
            ) : null}
            {(driverSignals.length > 0 || anomalySignals.length > 0) ? (
              <div className="signals-grid">
                {driverSignals.length > 0 ? (
                  <div className="signals-card">
                    <h4>Business Drivers</h4>
                    <ul className="signals-list">
                      {driverSignals.map((driver) => (
                        <li key={`${driver.type}-${driver.label}`}>
                          <span>{driver.type}: {driver.label}</span>
                          <span>{driver.share}% share</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {anomalySignals.length > 0 ? (
                  <div className="signals-card">
                    <h4>Anomalies</h4>
                    <ul className="signals-list anomalies">
                      {anomalySignals.map((anomaly) => (
                        <li key={anomaly.title}>
                          <span>{anomaly.title}</span>
                          <span>{anomaly.detail}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                ) : null}
              </div>
            ) : null}
            <div className="viis-insights-grid">
              {structuredInsights.map((insight) => {
                const askWhyResult = askWhyByInsightId[insight.id];
                return (
                  <div key={insight.id} className="viis-insight-card">
                    <div className="viis-card-topline">
                      <span className="viis-rank-badge">#{insight.rank}</span>
                      <span className="viis-category-tag">{insight.category}</span>
                    </div>
                    <h4 className="viis-insight-title">{insight.title}</h4>
                    <div className="viis-detail-block">
                      <span className="viis-detail-label">Insight</span>
                      <p>{insight.insight}</p>
                    </div>
                    <div className="viis-detail-block">
                      <span className="viis-detail-label">Driver</span>
                      <p>{insight.driver}</p>
                    </div>
                    <div className="viis-detail-block">
                      <span className="viis-detail-label">Impact</span>
                      <p>{insight.impact}</p>
                    </div>
                    <div className="viis-detail-block">
                      <span className="viis-detail-label">Suggested Action</span>
                      <p>{insight.suggested_action}</p>
                    </div>
                    <div className="viis-card-meta">
                      <span>{insight.confidence}% confidence</span>
                      <span>{insight.source}</span>
                    </div>
                    <button
                      className="secondary-btn viis-ask-why-btn"
                      onClick={() => askWhy(insight.id)}
                      disabled={askWhyLoadingId === insight.id}
                    >
                      {askWhyLoadingId === insight.id ? 'Investigating...' : 'Ask VoxCore Why'}
                    </button>
                    {askWhyResult ? (
                      <div className="ask-why-panel">
                        <div className="ask-why-title">Root Cause</div>
                        <p className="ask-why-root">{askWhyResult.root_cause}</p>
                        <div className="ask-why-dimensions">
                          {askWhyResult.dimensions.map((dimension) => (
                            <div key={dimension.dimension} className="ask-why-dimension-card">
                              <span className="ask-why-dimension-label">{dimension.dimension}</span>
                              <span>{dimension.finding}</span>
                            </div>
                          ))}
                        </div>
                        <div className="ask-why-investigation">
                          <span className="viis-detail-label">Recommended Investigation</span>
                          <p>{askWhyResult.recommended_investigation}</p>
                        </div>
                      </div>
                    ) : null}
                  </div>
                );
              })}
            </div>
            <div className="insights-categories">
              {insightCategories.map((cat) => {
                const meta = CATEGORY_META[cat.icon] ?? { emoji: '\ud83d\udca1', color: '#6b7280' };
                return (
                  <div key={cat.category} className="insight-category-block">
                    <div className="insight-category-title" style={{ color: meta.color }}>
                      <span>{meta.emoji}</span>
                      <span>{cat.category}</span>
                    </div>
                    <ul className="playground-insights-list">
                      {cat.insights.map((insight, idx) => (
                        <li key={idx} className="playground-insight-item">
                          <span className="playground-insight-bullet" style={{ color: meta.color }}>&#9679;</span>
                          {insight}
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>


      <div className="card">
        <h3>Results</h3>
        <div className="results-placeholder" style={{ marginBottom: 12 }}>{statusMessage}</div>
        {previewChart ? (
          <div style={{ height: 320, marginBottom: 14 }}>
            <ChartRenderer chart={previewChart} />
          </div>
        ) : null}

        {previewRows.length > 0 ? (
          <div className="sandbox-table-wrap">
            <table className="sandbox-table">
              <thead>
                <tr>
                  {tableColumns.map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewRows.map((row, rowIndex) => (
                  <tr key={`row-${rowIndex}`}>
                    {tableColumns.map((key) => (
                      <td key={`${rowIndex}-${key}`}>{String(row[key] ?? '')}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </div>
    </div>
  );
}
