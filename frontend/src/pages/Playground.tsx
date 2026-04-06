import { useEffect, useState, useRef } from "react";
import { Link } from "react-router-dom";

import { buildInitialPlaygroundViewModel, executePlaygroundQuery } from "@/playground/api";
import { PlaygroundQueryComposer } from "@/playground/PlaygroundQueryComposer";
import { PlaygroundResultsPanel } from "@/playground/PlaygroundResultsPanel";
import { ResultDrilldownModal } from "@/components/voxcore/ResultDrilldownModal";
import { ExplainMyDataView } from "@/components/voxcore/ExplainMyDataView";
import { GovernancePoliciesView } from "@/components/voxcore/GovernancePoliciesView";
import { InsightLibraryView } from "@/components/voxcore/InsightLibraryView";
import type { PlaygroundViewModel } from "@/playground/types";

type PlaygroundSection = 'playground' | 'policies' | 'insights' | 'emd'
type PlaygroundDataset = 'users' | 'sales' | 'orders'

const sectionItems = [
  { key: 'playground', label: 'Live Playground', badge: 'ACTIVE' },
  { key: 'policies', label: 'Governance Policies', badge: 'PREVIEW' },
  { key: 'insights', label: 'Insight Library', badge: 'PREVIEW' },
  { key: 'emd', label: 'Explain My Data', badge: 'CORE' },
] as const

const datasetItems = [
  { key: 'users', label: 'Users' },
  { key: 'sales', label: 'Sales' },
  { key: 'orders', label: 'Orders' },
] as const

// Demo dataset metadata for all views
const datasetMeta = {
  users: {
    title: 'Users Dataset',
    description: 'Customer accounts, activity, spend, and lifecycle behavior.',
    emdInsights: [
      {
        title: 'High-value users are clustering in two recent acquisition cohorts',
        summary: 'Recent users from campaign cohorts 24A and 24C show the highest early spend concentration.',
        stat: '+18.4% early spend',
      },
      {
        title: 'Dormancy risk is increasing among long-tail accounts',
        summary: 'A growing slice of users has not returned in the last 45 days.',
        stat: '12.7% dormant',
      },
      {
        title: 'Top 10 users contribute a large share of total spend',
        summary: 'Revenue concentration is high and worth monitoring for churn sensitivity.',
        stat: '34% of spend',
      },
    ],
    libraryInsights: [
      'Dormant-user alert triggered on West region cohort',
      'Spend concentration narrative saved for executive review',
      'Cohort 24A growth note published to insight timeline',
    ],
    policies: [
      'Block raw export of email addresses',
      'Mask personal identifiers for analyst role',
      'Require review for full user table scans',
    ],
  },

  sales: {
    title: 'Sales Dataset',
    description: 'Revenue, product, region, customer, and time-based commercial performance.',
    emdInsights: [
      {
        title: 'Revenue is strongest in the North region',
        summary: 'North continues to lead the revenue mix with stable weekly contribution.',
        stat: '24.7k revenue',
      },
      {
        title: 'Escalated order reviews remain elevated',
        summary: 'Manual escalation volume is still above baseline in two product categories.',
        stat: '+9.2% vs baseline',
      },
      {
        title: 'Premium product mix is improving overall margin',
        summary: 'Higher-priced categories are contributing a larger portion of sales this month.',
        stat: '+4.1 margin pts',
      },
    ],
    libraryInsights: [
      'Regional revenue spike detected in North',
      'Review-status imbalance saved to anomaly feed',
      'Margin narrative published for leadership summary',
    ],
    policies: [
      'Block destructive write operations in sales tables',
      'Limit row count for demo execution',
      'Require bounded aggregations for sandbox access',
    ],
  },

  orders: {
    title: 'Orders Dataset',
    description: 'Order lifecycle, fulfillment state, review status, and operational handling.',
    emdInsights: [
      {
        title: 'Approved orders dominate the current review mix',
        summary: 'Most orders pass review immediately, but escalations still cluster around two workflows.',
        stat: '24.7k approved',
      },
      {
        title: 'Escalation volume is concentrated in one review channel',
        summary: 'One review path is creating a disproportionate share of manual handling.',
        stat: '6.1k escalated',
      },
      {
        title: 'Review backlog remains bounded',
        summary: 'The unresolved review queue is stable and below alert threshold.',
        stat: '4.1k review',
      },
    ],
    libraryInsights: [
      'Review backlog narrative saved',
      'Escalation chain added to anomaly timeline',
      'Approval-rate insight published to operations board',
    ],
    policies: [
      'Prevent unrestricted order detail exports',
      'Block destructive actions on order lifecycle tables',
      'Require aggregation for operational summaries',
    ],
  },
} as const;

export default function Playground() {
  const [query, setQuery] = useState("Show revenue by region");
  const [isRunning, setIsRunning] = useState(false);
  const [sessionId, setSessionId] = useState("voxcore-playground");
  const [payload, setPayload] = useState<PlaygroundViewModel>(() => buildInitialPlaygroundViewModel());
  const [selectedPoint, setSelectedPoint] = useState<Record<string, unknown> | null>(null);
  const [isDrilldownOpen, setIsDrilldownOpen] = useState(false);
  const [activeSection, setActiveSection] = useState<PlaygroundSection>('playground')
  const [activeDataset, setActiveDataset] = useState<PlaygroundDataset>('sales')
  const queryBoxRef = useRef<HTMLTextAreaElement | null>(null);

  const currentDataset = datasetMeta[activeDataset]

  useEffect(() => {
    const existingSessionId = window.localStorage.getItem("voxcore_session_id");
    if (existingSessionId) {
      setSessionId(existingSessionId);
      return;
    }

    const nextSessionId = `voxcore-playground-${Date.now()}`;
    window.localStorage.setItem("voxcore_session_id", nextSessionId);
    setSessionId(nextSessionId);
  }, []);

  const handleRun = async () => {
    setIsRunning(true);
    window.setTimeout(async () => {
      const nextQuery = query.trim() || "Show revenue by region";
      const nextPayload = await executePlaygroundQuery(nextQuery, sessionId);
      setPayload(nextPayload);
      setIsRunning(false);
    }, 450);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    requestAnimationFrame(() => {
      queryBoxRef.current?.scrollIntoView({
        behavior: 'smooth',
        block: 'center',
      });
      queryBoxRef.current?.focus();
    });
  };

  const handleSelectPoint = (point: Record<string, unknown>) => {
    setSelectedPoint(point);
    setIsDrilldownOpen(true);
  };



  return (
    <div className="flex min-h-screen bg-[#020817] text-white">
      {/* Sidebar */}
      <aside className="w-full max-w-[250px] shrink-0 border-r border-white/10 bg-[#020817] px-5 py-7">
        <div className="rounded-[28px] border border-sky-500/20 bg-sky-500/[0.06] p-5">
          <p className="text-[11px] font-semibold uppercase tracking-[0.22em] text-sky-300/80">
            VoxCore Playground
          </p>
          <h2 className="mt-4 text-[18px] font-semibold leading-8 text-white">
            Governed query simulation
          </h2>
          <p className="mt-3 text-sm leading-7 text-slate-300">
            Explore how VoxCore inspects, bounds, and explains analytic requests before anything reaches data execution.
          </p>
        </div>

        <div className="mt-8">
          <p className="text-[11px] font-semibold uppercase tracking-[0.25em] text-sky-300/70">
            Workspace
          </p>

          <div className="mt-4 space-y-3">
            {sectionItems.map((item) => {
              const isActive = activeSection === item.key

              return (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => setActiveSection(item.key)}
                  className={`w-full rounded-[22px] border px-4 py-4 text-left transition ${
                    isActive
                      ? 'border-white/30 bg-white/[0.06]'
                      : 'border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.05]'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-base font-medium text-white">{item.label}</span>
                    <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">
                      {item.badge}
                    </span>
                  </div>
                </button>
              )
            })}
          </div>
        </div>

        <div className="mt-8">
          <p className="text-[11px] font-semibold uppercase tracking-[0.25em] text-sky-300/70">
            Datasets
          </p>

          <div className="mt-4 space-y-3">
            {datasetItems.map((item) => {
              const isActive = activeDataset === item.key

              return (
                <button
                  key={item.key}
                  type="button"
                  onClick={() => setActiveDataset(item.key)}
                  className={`w-full rounded-[22px] border px-4 py-4 text-left transition ${
                    isActive
                      ? 'border-white/30 bg-white/[0.06]'
                      : 'border-white/10 bg-white/[0.03] hover:border-white/20 hover:bg-white/[0.05]'
                  }`}
                >
                  <div className="flex items-center justify-between gap-3">
                    <span className="text-base font-medium text-white">{item.label}</span>
                    <span className="rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-300">
                      DEMO
                    </span>
                  </div>
                </button>
              )
            })}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="min-w-0 flex-1 px-7 py-8">
      {activeSection === 'playground' && (
        <div className="space-y-6">
          {/* KEEP YOUR EXISTING LIVE PLAYGROUND UI HERE */}
          <div className="flex flex-col gap-3 rounded-[1.75rem] border border-white/10 bg-white/[0.03] px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">Environment</div>
              <div className="mt-1 text-sm text-slate-300">
                Playground mode only. No live database access, no destructive execution, and all results are bounded to demo data.
              </div>
              <div className={`mt-2 text-sm ${payload.mode === "Demo Fallback" ? "text-amber-200" : "text-sky-200/80"}`}>
                {payload.notice}
              </div>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              <div className="rounded-full border border-white/10 bg-white/5 px-4 py-2 text-xs font-semibold uppercase tracking-[0.22em] text-slate-300">
                {payload.mode}
              </div>
              <Link
                to="/"
                className="rounded-full border border-white/12 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-white/30 hover:bg-white/6 hover:text-white"
              >
                Back to Home
              </Link>
              <Link
                to="/product"
                className="rounded-full border border-sky-300/20 bg-sky-400/10 px-4 py-2 text-sm font-medium text-sky-100 transition hover:bg-sky-400/15"
              >
                See Product Architecture
              </Link>
            </div>
          </div>

          <PlaygroundQueryComposer
            ref={queryBoxRef}
            query={query}
            onQueryChange={setQuery}
            onRun={handleRun}
            isRunning={isRunning}
          />

          <PlaygroundResultsPanel 
            result={payload?.result ?? null}
            onSuggestionClick={handleSuggestionClick}
            onSelectPoint={handleSelectPoint}
          />
        </div>
      )}

      {activeSection === 'policies' && (
        <GovernancePoliciesView currentDataset={currentDataset} />
      )}

      {activeSection === 'insights' && (
        <InsightLibraryView currentDataset={currentDataset} />
      )}

      {activeSection === 'emd' && (
        <ExplainMyDataView
          currentDataset={currentDataset}
          activeDataset={activeDataset}
        />
      )}
    </main>

    <ResultDrilldownModal
      open={isDrilldownOpen}
      selectedPoint={selectedPoint}
      onClose={() => setIsDrilldownOpen(false)}
    />
    </div>
  );
}
