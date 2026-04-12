import { useEffect, useState, useRef } from "react";

import { buildInitialPlaygroundViewModel, executePlaygroundQuery } from "@/playground/api";
import { PlaygroundSidebar, type PlaygroundSection } from "@/playground/PlaygroundSidebar";
import { PlaygroundContent } from "@/playground/PlaygroundContent";
import { ResultDrilldownModal } from "@/components/voxcore/ResultDrilldownModal";
import { datasetMetadata } from "@/playground/playgroundData";
import type { PlaygroundViewModel, PlaygroundDataset } from "@/playground/types";

/**
 * Playground Page Component
 * 
 * Orchestrator only - composes layout, manages state, and connects to store/API.
 * Delegates rendering to specialized sub-components:
 * - PlaygroundSidebar: Section and dataset navigation
 * - PlaygroundContent: Active section rendering
 * - ResultDrilldownModal: Detail view for selected data points
 * 
 * State responsibility:
 * - query: User's current query text (text input state)
 * - isRunning: Query execution pending state
 * - sessionId: Server session identifier for query grouping
 * - payload: Query results (PlaygroundViewModel from API)
 * - activeSection: Current view (playground/policies/insights/emd)
 * - activeDataset: Current dataset context (users/sales/orders)
 * - selectedPoint: Drilldown selection state
 * - isDrilldownOpen: Modal visibility state
 */
export default function Playground() {
  // Stateful input
  const [query, setQuery] = useState("Show revenue by region");
  const [isRunning, setIsRunning] = useState(false);

  // Session & response
  const [sessionId, setSessionId] = useState("voxcore-playground");
  const [payload, setPayload] = useState<PlaygroundViewModel>(() =>
    buildInitialPlaygroundViewModel()
  );

  // Navigation & selection
  const [activeSection, setActiveSection] = useState<PlaygroundSection>("playground");
  const [activeDataset, setActiveDataset] = useState<PlaygroundDataset>("sales");
  const [selectedPoint, setSelectedPoint] = useState<Record<string, unknown> | null>(null);
  const [isDrilldownOpen, setIsDrilldownOpen] = useState(false);

  // Ref for scroll-to-focus behavior
  const queryBoxRef = useRef<HTMLTextAreaElement | null>(null);

  // Derived state - lookup current dataset metadata
  const currentDataset = datasetMetadata[activeDataset];

  /**
   * Initialize session ID on mount.
   * Uses localStorage to persist session across page reloads.
   */
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

  /**
   * Execute query and fetch results from API.
   * Debounces with small delay for smoother UX.
   */
  const handleRun = async () => {
    setIsRunning(true);
    window.setTimeout(async () => {
      const nextQuery = query.trim() || "Show revenue by region";
      const nextPayload = await executePlaygroundQuery(nextQuery, sessionId);
      setPayload(nextPayload);
      setIsRunning(false);
    }, 450);
  };

  /**
   * Handle suggestion click: update query text and focus input.
   */
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

  /**
   * Handle data point selection: open drilldown modal.
   */
  const handleSelectPoint = (point: Record<string, unknown>) => {
    setSelectedPoint(point);
    setIsDrilldownOpen(true);
  };

  return (
    <div className="flex min-h-screen bg-[#020817] text-white">
      <PlaygroundSidebar
        activeSection={activeSection}
        onSectionChange={setActiveSection}
        activeDataset={activeDataset}
        onDatasetChange={setActiveDataset}
      />

      <PlaygroundContent
        activeSection={activeSection}
        activeDataset={activeDataset}
        query={query}
        onQueryChange={setQuery}
        isRunning={isRunning}
        onRun={handleRun}
        payload={payload}
        onSuggestionClick={handleSuggestionClick}
        onSelectPoint={handleSelectPoint}
        queryBoxRef={queryBoxRef}
        currentDataset={currentDataset}
      />

      <ResultDrilldownModal
        open={isDrilldownOpen}
        selectedPoint={selectedPoint}
        onClose={() => setIsDrilldownOpen(false)}
      />
    </div>
  );
}
