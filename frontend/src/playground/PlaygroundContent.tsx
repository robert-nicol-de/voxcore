import { Link } from "react-router-dom";
import { PlaygroundQueryComposer } from "./PlaygroundQueryComposer";
import { PlaygroundResultsPanel } from "./PlaygroundResultsPanel";
import { ExplainMyDataView } from "@/components/voxcore/ExplainMyDataView";
import { GovernancePoliciesView } from "@/components/voxcore/GovernancePoliciesView";
import { InsightLibraryView } from "@/components/voxcore/InsightLibraryView";
import type { PlaygroundViewModel, PlaygroundDataset } from "@/playground/types";
import type { PlaygroundSection } from "./PlaygroundSidebar";

interface PlaygroundContentProps {
  activeSection: PlaygroundSection;
  activeDataset: PlaygroundDataset;
  query: string;
  onQueryChange: (query: string) => void;
  isRunning: boolean;
  onRun: () => void;
  payload: PlaygroundViewModel;
  onSuggestionClick: (suggestion: string) => void;
  onSelectPoint: (point: Record<string, unknown>) => void;
  queryBoxRef: React.RefObject<HTMLTextAreaElement>;
  currentDataset: {
    title: string;
    description: string;
    emdInsights: Array<{
      title: string;
      summary: string;
      stat: string;
    }>;
    libraryInsights: string[];
    policies: string[];
  };
}

/**
 * Renders the active section content based on activeSection state.
 * Delegates specific view rendering to section-specific components.
 */
export function PlaygroundContent({
  activeSection,
  activeDataset,
  query,
  onQueryChange,
  isRunning,
  onRun,
  payload,
  onSuggestionClick,
  onSelectPoint,
  queryBoxRef,
  currentDataset,
}: PlaygroundContentProps) {
  return (
    <main className="min-w-0 flex-1 px-7 py-8">
      {activeSection === "playground" && (
        <div className="space-y-6">
          {/* Environment info and controls */}
          <div className="flex flex-col gap-3 rounded-[1.75rem] border border-white/10 bg-white/[0.03] px-5 py-4 lg:flex-row lg:items-center lg:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-500">
                Environment
              </div>
              <div className="mt-1 text-sm text-slate-300">
                Playground mode only. No live database access, no destructive
                execution, and all results are bounded to demo data.
              </div>
              <div
                className={`mt-2 text-sm ${
                  payload.mode === "Demo Fallback"
                    ? "text-amber-200"
                    : "text-sky-200/80"
                }`}
              >
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

          {/* Query composer and results */}
          <PlaygroundQueryComposer
            ref={queryBoxRef}
            query={query}
            onQueryChange={onQueryChange}
            onRun={onRun}
            isRunning={isRunning}
          />

          <PlaygroundResultsPanel
            result={payload?.result ?? null}
            onSuggestionClick={onSuggestionClick}
            onSelectPoint={onSelectPoint}
          />
        </div>
      )}

      {activeSection === "policies" && (
        <GovernancePoliciesView currentDataset={currentDataset} />
      )}

      {activeSection === "insights" && (
        <InsightLibraryView currentDataset={currentDataset} />
      )}

      {activeSection === "emd" && (
        <ExplainMyDataView
          currentDataset={currentDataset}
          activeDataset={activeDataset}
        />
      )}
    </main>
  );
}
