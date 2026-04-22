/**
 * RichPlaygroundPage
 *
 * Restores the richer VoxCore Playground UI (sidebar + header + content layout)
 * while maintaining the new canonical backend contract and polling logic.
 *
 * Architecture:
 * - Layout: Legacy Header + Sidebar + AdaptedContent (from legacy UI)
 * - State: New usePlaygroundStore (from features/playground)
 * - API: New backend contract (/api/v1/query with job polling)
 * - Components: Mix of legacy layout components + new result components
 *
 * No changes to:
 * - Backend contract (/api/v1/query, job polling)
 * - State management (Zustand store)
 * - Result types and transformations
 * - Terminal state handling (blocked/completed)
 *
 * What's new:
 * - Sidebar navigation between Query Lab, Data Explorer, Insights, Governance
 * - Header branding with VoxCore title
 * - Environment trust badge
 * - Conversion panel (Book Demo, Explore Product)
 * - Better use of horizontal space
 */

import { useRef, useEffect } from "react";

// Store (new)
import {
  usePlaygroundStore,
  buildInitialPlaygroundViewModel,
} from "@/features/playground";

// Legacy layout components (reused as-is)
import { PlaygroundHeader } from "@/playground/legacy/PlaygroundHeader";
import { PlaygroundSidebar } from "@/playground/legacy/PlaygroundSidebar";
import type { PlaygroundSection } from "@/playground/legacy/PlaygroundSidebar";

// New result components
import {
  PlaygroundQueryComposer,
  PlaygroundPromptChips,
  PlaygroundResultStack,
  PlaygroundErrorState,
} from "@/features/playground";

// Legacy panels (reused)
import { PlaygroundConversionPanel } from "@/playground/legacy/PlaygroundConversionPanel";

// Old components (for section views)
import { ResultDrilldownModal } from "@/components/voxcore/ResultDrilldownModal";
import { ExplainMyDataView } from "@/components/voxcore/ExplainMyDataView";
import { GovernancePoliciesView } from "@/components/voxcore/GovernancePoliciesView";
import { InsightLibraryView } from "@/components/voxcore/InsightLibraryView";

// Data
import { datasetMetadata } from "@/playground/playgroundData";
export default function RichPlaygroundPage() {
  // =========================================================================
  // Store Subscriptions (same as PlaygroundPage, but exposed to sidebar/content)
  // =========================================================================

  const query = usePlaygroundStore((s) => s.query);
  const setQuery = usePlaygroundStore((s) => s.setQuery);

  const isRunning = usePlaygroundStore((s) => s.isRunning);
  const submitQuery = usePlaygroundStore((s) => s.submitQuery);

  const activeSection = usePlaygroundStore((s) => s.activeSection);
  const setActiveSection = usePlaygroundStore((s) => s.setActiveSection);

  const activeDataset = usePlaygroundStore((s) => s.activeDataset);
  const setActiveDataset = usePlaygroundStore((s) => s.setActiveDataset);

  const setSessionId = usePlaygroundStore((s) => s.setSessionId);

  const payload = usePlaygroundStore((s) => s.payload);
  const setPayload = usePlaygroundStore((s) => s.setPayload);

  const error = usePlaygroundStore((s) => s.error);

  const selectedPoint = usePlaygroundStore((s) => s.selectedPoint);
  const setSelectedPoint = usePlaygroundStore((s) => s.setSelectedPoint);

  const isDrilldownOpen = usePlaygroundStore((s) => s.isDrilldownOpen);
  const setIsDrilldownOpen = usePlaygroundStore((s) => s.setIsDrilldownOpen);

  // =========================================================================
  // Derived State
  // =========================================================================

  const currentDataset = datasetMetadata[activeDataset];
  const queryBoxRef = useRef<HTMLTextAreaElement | null>(null);

  // =========================================================================
  // Initialization (same as PlaygroundPage)
  // =========================================================================

  useEffect(() => {
    const existingSessionId = window.localStorage.getItem("voxcore_session_id");
    if (existingSessionId) {
      setSessionId(existingSessionId);
    } else {
      const newSessionId = `voxcore-playground-${Date.now()}`;
      window.localStorage.setItem("voxcore_session_id", newSessionId);
      setSessionId(newSessionId);
    }

    const initialViewModel = buildInitialPlaygroundViewModel();
    setPayload(initialViewModel);
  }, [setSessionId, setPayload]);

  // =========================================================================
  // Event Handlers (same as PlaygroundPage)
  // =========================================================================

  const handleRun = async () => {
    const nextQuery = query.trim() || "Show revenue by region";
    await submitQuery(nextQuery);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    requestAnimationFrame(() => {
      queryBoxRef.current?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
      queryBoxRef.current?.focus();
    });
  };

  const handleSelectPoint = (point: Record<string, unknown>) => {
    setSelectedPoint(point);
    setIsDrilldownOpen(true);
  };

  const handleClear = () => {
    setQuery("");
    queryBoxRef.current?.focus();
  };

  // =========================================================================
  // Render: Active Section Content (routes between playground/policies/insights/emd)
  // =========================================================================

  const renderActiveSection = () => {
    // Error state (top priority)
    if (error) {
      return (
        <div className="space-y-6">
          <PlaygroundErrorState
            error={error}
            onSelectPrompt={handleSuggestionClick}
          />
        </div>
      );
    }

    if (!payload) {
      return null;
    }

    switch (activeSection) {
      case "playground":
        return (
          <div className="space-y-8 pb-14 lg:space-y-10 lg:pb-20">
            <div className="grid gap-8 xl:grid-cols-[minmax(0,1fr)_260px] xl:items-start">
              <div className="space-y-6 lg:space-y-7">
                <div className="flex flex-col gap-5 rounded-[2rem] border border-white/8 bg-white/[0.03] px-5 py-5 shadow-[0_18px_60px_rgba(2,8,23,0.24)] backdrop-blur-sm sm:px-6 lg:px-7 lg:py-6">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                    <div className="space-y-3">
                      <div className="text-[11px] font-semibold uppercase tracking-[0.3em] text-sky-300/70">
                        AI Query Lab
                      </div>
                      <div className="space-y-2">
                        <h2 className="text-2xl font-semibold tracking-tight text-white lg:text-[2rem]">
                          Ask a governed business question
                        </h2>
                        <p className="max-w-2xl text-sm leading-6 text-slate-400 lg:text-[15px]">
                          The query composer stays front and center while results settle below it, so blocked and successful terminal states remain easy to compare.
                        </p>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2 lg:max-w-[280px] lg:justify-end">
                      <div className="rounded-full border border-sky-400/20 bg-sky-400/10 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.2em] text-sky-200">
                        Dataset: {currentDataset?.title || activeDataset}
                      </div>
                      <div className="rounded-full border border-emerald-300/20 bg-emerald-400/10 px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.2em] text-emerald-200">
                        {payload?.mode || "Live Backend"}
                      </div>
                    </div>
                  </div>
                </div>

                <div className="sticky top-4 z-20 rounded-[2.25rem] border border-white/6 bg-[#020817]/88 p-1 shadow-[0_20px_65px_rgba(2,8,23,0.42)] backdrop-blur-xl">
                  <PlaygroundQueryComposer
                    ref={queryBoxRef}
                    query={query}
                    onQueryChange={setQuery}
                    onRun={handleRun}
                    isRunning={isRunning}
                    onClear={handleClear}
                  />
                </div>

                <PlaygroundPromptChips onSelectPrompt={handleSuggestionClick} />
              </div>

              <div className="hidden xl:block">
                <div className="sticky top-4 space-y-4 rounded-[2rem] border border-white/8 bg-white/[0.03] p-5 shadow-[0_18px_50px_rgba(2,8,23,0.22)] backdrop-blur-sm">
                  <div className="space-y-2">
                    <div className="text-[11px] font-semibold uppercase tracking-[0.28em] text-slate-500">
                      Workspace
                    </div>
                    <h3 className="text-lg font-semibold text-white">
                      Focused governed preview
                    </h3>
                    <p className="text-sm leading-6 text-slate-400">
                      Submit from the lab, then review the terminal decision and result stack without leaving the working surface.
                    </p>
                  </div>

                  <div className="space-y-3 rounded-[1.25rem] border border-white/8 bg-black/20 p-4">
                    <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">
                      Current context
                    </div>
                    <div className="space-y-2 text-sm text-slate-300">
                      <div className="flex items-center justify-between gap-4">
                        <span className="text-slate-500">Section</span>
                        <span className="font-medium text-white">AI Query Lab</span>
                      </div>
                      <div className="flex items-center justify-between gap-4">
                        <span className="text-slate-500">Dataset</span>
                        <span className="font-medium text-white">{currentDataset?.title || activeDataset}</span>
                      </div>
                      <div className="flex items-center justify-between gap-4">
                        <span className="text-slate-500">Guardrails</span>
                        <span className="font-medium text-white">Live governed</span>
                      </div>
                    </div>
                  </div>

                  <div className="rounded-[1.25rem] border border-white/8 bg-white/[0.02] p-4">
                    <div className="text-[11px] font-semibold uppercase tracking-[0.24em] text-slate-500">
                      Quick read
                    </div>
                    <div className="mt-3 space-y-2 text-sm leading-6 text-slate-400">
                      <p>Blocked states stay explicit and isolated.</p>
                      <p>Successful runs keep the answer and trust metadata visually grouped.</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {payload && (
              <div className="space-y-8 lg:space-y-10">
                <PlaygroundResultStack
                  payload={payload}
                  isLoading={isRunning}
                  onSuggestionClick={handleSuggestionClick}
                  onSelectPoint={handleSelectPoint}
                />

                {/* Environment info and controls (subtitle, not prominent) */}
                <div className="rounded-[1.5rem] border border-white/8 bg-white/[0.03] px-5 py-4 shadow-[0_16px_40px_rgba(2,8,23,0.18)] animate-fade-in">
                  <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400 flex items-center gap-1.5">
                        <span>✓</span> Secure Environment
                      </div>
                      <div className="mt-2 text-sm text-slate-400 flex flex-wrap gap-x-4 gap-y-1">
                        <span>Safe sample data</span>
                        <span>Every query governed</span>
                        <span>Fully audited</span>
                      </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-2">
                      <div className="rounded-full border border-emerald-300/30 bg-emerald-400/10 px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.22em] text-emerald-200">
                        🛡️ {payload.mode}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Conversion panel - show after successful query with results */}
                {!isRunning && !error && payload?.result && (
                  <PlaygroundConversionPanel />
                )}
              </div>
            )}
          </div>
        );

      case "policies":
        return currentDataset ? (
          <GovernancePoliciesView currentDataset={currentDataset} />
        ) : null;

      case "insights":
        return currentDataset ? (
          <InsightLibraryView currentDataset={currentDataset} />
        ) : null;

      case "emd":
        return currentDataset ? (
          <ExplainMyDataView
            currentDataset={currentDataset}
            activeDataset={activeDataset}
          />
        ) : null;

      default:
        return null;
    }
  };

  // =========================================================================
  // Render: Layout (Header + Sidebar + Content)
  // =========================================================================

  return (
    <div className="relative flex h-screen flex-col overflow-hidden bg-[#020817]">
      <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(56,189,248,0.12),transparent_28%),radial-gradient(circle_at_10%_20%,rgba(14,165,233,0.08),transparent_24%)]" />
      {/* Header - fixed at top, full width, z-indexed above sidebar */}
      <div className="shrink-0 z-50">
        <PlaygroundHeader mode={payload?.mode || "Live Backend"} />
      </div>

      {/* Main content area */}
      <div className="relative z-10 flex min-h-0 flex-1 overflow-hidden">
        {/* Sidebar - fixed position (260px width, positioned absolutely from viewport) */}
        <PlaygroundSidebar
          activeSection={activeSection as PlaygroundSection}
          onSectionChange={(section) => setActiveSection(section)}
          activeDataset={activeDataset}
          onDatasetChange={setActiveDataset}
        />

        {/* Content area - add left padding for fixed sidebar, scrollable */}
        <main className="flex-1 overflow-y-auto bg-transparent pl-[92px] sm:pl-[104px] lg:pl-[248px]">
          <div className="mx-auto max-w-[1180px] px-4 py-5 sm:px-6 lg:px-9 lg:py-8">
            {renderActiveSection()}
          </div>
        </main>
      </div>

      {/* Drilldown modal */}
      <ResultDrilldownModal
        open={isDrilldownOpen}
        selectedPoint={selectedPoint}
        onClose={() => setIsDrilldownOpen(false)}
      />
    </div>
  );
}
