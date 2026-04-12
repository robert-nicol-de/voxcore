/**
 * PlaygroundPage
 *
 * The main Playground page component.
 * Orchestrates the complete Playground experience:
 * - Layout composition (Shell + Hero + QueryComposer + Results)
 * - Store integration (Zustand state management)
 * - API communication (query execution with fallback)
 * - Session persistence (localStorage)
 *
 * Responsibilities:
 * - Initialize store on mount (session ID, initial results)
 * - Wire store selectors to components
 * - Handle query submission (executePlaygroundQuery)
 * - Route between different sections (playground/policies/insights/emd)
 * - Manage drilldown modal state
 *
 * Does NOT contain:
 * - Individual component logic (delegated to sub-components)
 * - Data transformation (delegated to mappers)
 * - Value formatting (delegated to formatters)
 * - Business rules (delegated to services)
 */

import { useRef, useEffect } from "react";

// Store
import {
  usePlaygroundStore,
  buildInitialPlaygroundViewModel,
  executePlaygroundQuery,
} from "@/features/playground";

// Components
import {
  PlaygroundShell,
  PlaygroundHero,
  PlaygroundQueryComposer,
  PlaygroundPromptChips,
  PlaygroundResultStack,
  PlaygroundErrorState,
} from "@/features/playground";

// Old components (to be replaced incrementally)
import { ResultDrilldownModal } from "@/components/voxcore/ResultDrilldownModal";
import { ExplainMyDataView } from "@/components/voxcore/ExplainMyDataView";
import { GovernancePoliciesView } from "@/components/voxcore/GovernancePoliciesView";
import { InsightLibraryView } from "@/components/voxcore/InsightLibraryView";

// Data
import { datasetMetadata } from "@/playground/playgroundData";

export default function PlaygroundPage() {
  // =========================================================================
  // Store Subscriptions (granular to avoid unnecessary re-renders)
  // =========================================================================

  const query = usePlaygroundStore((s) => s.query);
  const setQuery = usePlaygroundStore((s) => s.setQuery);

  const isRunning = usePlaygroundStore((s) => s.isRunning);
  const setIsRunning = usePlaygroundStore((s) => s.setIsRunning);

  const activeSection = usePlaygroundStore((s) => s.activeSection);
  const setActiveSection = usePlaygroundStore((s) => s.setActiveSection);

  const activeDataset = usePlaygroundStore((s) => s.activeDataset);
  const setActiveDataset = usePlaygroundStore((s) => s.setActiveDataset);

  const sessionId = usePlaygroundStore((s) => s.sessionId);
  const setSessionId = usePlaygroundStore((s) => s.setSessionId);

  const payload = usePlaygroundStore((s) => s.payload);
  const setPayload = usePlaygroundStore((s) => s.setPayload);

  const error = usePlaygroundStore((s) => s.error);
  const clearError = usePlaygroundStore((s) => s.clearError);

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
  // Initialization
  // =========================================================================

  /**
   * Initialize session ID and load initial results on mount.
   * Checks localStorage for existing session, creates new if needed.
   */
  useEffect(() => {
    // Check for existing session
    const existingSessionId = window.localStorage.getItem("voxcore_session_id");
    if (existingSessionId) {
      setSessionId(existingSessionId);
    } else {
      // Create new session ID
      const newSessionId = `voxcore-playground-${Date.now()}`;
      window.localStorage.setItem("voxcore_session_id", newSessionId);
      setSessionId(newSessionId);
    }

    // Load initial results
    const initialViewModel = buildInitialPlaygroundViewModel();
    setPayload(initialViewModel);
  }, [setSessionId, setPayload]);

  // =========================================================================
  // Event Handlers
  // =========================================================================

  /**
   * Execute query against backend with fallback.
   * Shows loading state, calls API, updates payload.
   */
  const handleRun = async () => {
    setIsRunning(true);

    try {
      const nextQuery = query.trim() || "Show revenue by region";
      const result = await executePlaygroundQuery({
        query: nextQuery,
        sessionId,
        environment: "dev",
        source: "playground",
        user: "ai-agent",
      });
      setPayload(result);
    } catch (error) {
      console.error("Query execution failed:", error);
      // Error handling delegated to API service (returns fallback)
    } finally {
      setIsRunning(false);
    }
  };

  /**
   * Handle suggestion click: update query and focus input.
   */
  const handleSuggestionClick = (suggestion: string) => {
    setQuery(suggestion);
    // Scroll to input and focus
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

  /**
   * Clear query text.
   */
  const handleClear = () => {
    setQuery("");
    queryBoxRef.current?.focus();
  };

  // =========================================================================
  // Render: Results View (active section content)
  // =========================================================================

  const renderActiveSection = () => {
    // Error state (top priority - show error first)
    if (error) {
      return (
        <div className="mt-10 space-y-6 lg:mt-12">
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
          <div className="mt-10 space-y-6 lg:mt-12">
            <PlaygroundResultStack
              payload={payload}
              isLoading={isRunning}
              onSuggestionClick={handleSuggestionClick}
              onSelectPoint={handleSelectPoint}
            />
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
  // Render: Page
  // =========================================================================

  return (
    <PlaygroundShell>
      {/* Hero messaging */}
      <PlaygroundHero />

      {/* Query input */}
      <div className="mb-10 lg:mb-12 space-y-6">
        <PlaygroundQueryComposer
          ref={queryBoxRef}
          query={query}
          onQueryChange={setQuery}
          onRun={handleRun}
          isRunning={isRunning}
          onClear={handleClear}
        />
        <PlaygroundPromptChips onSelectPrompt={handleSuggestionClick} />
      </div>

      {/* Active section content */}
      {renderActiveSection()}

      {/* Drilldown modal */}
      <ResultDrilldownModal
        open={isDrilldownOpen}
        selectedPoint={selectedPoint}
        onClose={() => setIsDrilldownOpen(false)}
      />
    </PlaygroundShell>
  );
}
