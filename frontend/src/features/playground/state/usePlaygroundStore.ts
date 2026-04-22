/**
 * Playground Store
 *
 * Centralized state management for the Playground feature using Zustand.
 * Single source of truth for all UI, session, and API state.
 *
 * Responsibilities (DOING):
 * - User input (query text)
 * - API state (idle/loading/success/error with status field)
 * - Response data (result payload)
 * - Error tracking (error messages)
 * - Navigation (active section, active dataset)
 * - Session persistence (sessionId via localStorage)
 * - Interaction state (drilldown modal, selected points)
 * - Actions: setQuery, submitQuery (async), resetSession, clearError
 *
 * Responsibilities (DELEGATING):
 * - Fetch logic → playgroundApi.executePlaygroundQuery()
 * - Response normalization → service layer (ensureCompleteResult)
 * - Error handling branches → service/utils layer
 */

import { create } from "zustand";
import { persist } from "zustand/middleware";
import type {
  PlaygroundStateSlice,
  PlaygroundViewModel,
  PlaygroundDataset,
} from "../types/playground";
import {
  executePlaygroundQuery,
  pollQueuedPlaygroundQuery,
} from "../services/playgroundApi";

const INITIAL_QUERY = "Show revenue by region";
const INITIAL_DATASET: PlaygroundDataset = "sales";
const INITIAL_SECTION = "playground" as const;
let latestPlaygroundSubmissionId = 0;

/**
 * Playground Store
 *
 * Uses Zustand with persist middleware to sync sessionId, activeDataset, activeSection to localStorage.
 * Status field tracks query execution state (idle | loading | success | error).
 * All logic delegated to service layer (executePlaygroundQuery).
 */
export const usePlaygroundStore = create<PlaygroundStateSlice>()(
  persist(
    (set) => ({
      // Input state
      query: INITIAL_QUERY,
      setQuery: (query) => set({ query }),

      // Request state for the submit lifecycle.
      // Note: queued canonical execution is represented in payload.result.executionStatus,
      // not as a separate store-level request status.
      status: "idle",
      setStatus: (status) => set({ status }),

      // Result state
      payload: null,
      setPayload: (payload) => set({ payload }),

      // Error state
      error: null,
      setError: (error) => set({ error }),
      clearError: () => set({ error: null }),

      // UI state
      activeSection: INITIAL_SECTION,
      setActiveSection: (activeSection) => set({ activeSection }),

      activeDataset: INITIAL_DATASET,
      setActiveDataset: (activeDataset) => set({ activeDataset }),

      // Session state
      sessionId: `voxcore-playground-${Date.now()}`,
      setSessionId: (sessionId) => set({ sessionId }),

      // Drilldown state
      selectedPoint: null,
      setSelectedPoint: (selectedPoint) => set({ selectedPoint }),

      isDrilldownOpen: false,
      setIsDrilldownOpen: (isDrilldownOpen) => set({ isDrilldownOpen }),

      // Async action: Submit query and fetch results
      // Delegates all fetch/normalize/error-handling logic to service layer
      submitQuery: async (queryOverride?: string) => {
        const currentState = usePlaygroundStore.getState();
        const queryToRun = queryOverride || currentState.query;
        const submissionId = ++latestPlaygroundSubmissionId;

        // Transition to loading
        set({ status: "loading", error: null });

        try {
          // Delegate to service layer (all fetch/normalize logic lives here)
          const result = await executePlaygroundQuery(
            queryToRun,
            currentState.sessionId,
            currentState.activeDataset
          );

          // Success means the frontend received a governed response.
          // The actual execution lifecycle still lives on payload.result.executionStatus
          // and may be "queued" even when this store status is "success".
          set({
            status: "success",
            payload: result,
            error: null,
            query: queryToRun,
          });

          if (result.result.executionStatus === "queued" && result.result.jobId) {
            void pollQueuedPlaygroundQuery(result, (nextPayload) => {
              if (submissionId !== latestPlaygroundSubmissionId) {
                return;
              }

              const latestState = usePlaygroundStore.getState();
              if (
                latestState.payload?.result.jobId &&
                latestState.payload.result.jobId !== nextPayload.result.jobId
              ) {
                return;
              }

              set({
                payload: nextPayload,
                status: "success",
                error: null,
              });
            }).catch((pollError) => {
              if (submissionId !== latestPlaygroundSubmissionId) {
                return;
              }

              const latestState = usePlaygroundStore.getState();
              const currentPayload = latestState.payload;
              if (!currentPayload || currentPayload.result.jobId !== result.result.jobId) {
                return;
              }

              const errorMessage =
                pollError instanceof Error
                  ? pollError.message
                  : "Polling for query completion failed.";

              set({
                payload: {
                  ...currentPayload,
                  notice: `${currentPayload.notice} Polling paused: ${errorMessage}`,
                },
                status: "success",
                error: null,
              });
            });
          }
        } catch (err) {
          // Error state - service layer provides the error message
          const errorMessage =
            err instanceof Error ? err.message : "Query execution failed";
          set({
            status: "error",
            error: errorMessage,
            payload: null,
          });
        }
      },

      // Reset everything to initial state
      resetSession: () => {
        latestPlaygroundSubmissionId += 1;
        set({
          query: INITIAL_QUERY,
          status: "idle",
          payload: null,
          error: null,
          activeSection: INITIAL_SECTION,
          activeDataset: INITIAL_DATASET,
          selectedPoint: null,
          isDrilldownOpen: false,
          sessionId: `voxcore-playground-${Date.now()}`,
        });
      },

      // Legacy reset (kept for backward compatibility)
      reset: () => {
        latestPlaygroundSubmissionId += 1;
        set({
          query: INITIAL_QUERY,
          status: "idle",
          payload: null,
          error: null,
          activeSection: INITIAL_SECTION,
          activeDataset: INITIAL_DATASET,
          selectedPoint: null,
          isDrilldownOpen: false,
        });
      },

      // Legacy UI state setters (for components that set these directly)
      setIsRunning: (running) => {
        // Map boolean to status enum
        set({ status: running ? "loading" : "idle" });
      },

      // Computed property: isRunning
      // Derived from status field, needed for PlaygroundPage backward compatibility
      get isRunning() {
        return this.status === "loading";
      },
    }),
    {
      name: "playground-store",
      partialize: (state) => ({
        sessionId: state.sessionId,
        activeDataset: state.activeDataset,
        activeSection: state.activeSection,
      }),
    }
  )
);


// ============================================================================
// Selectors (for granular subscriptions)
// ============================================================================

/**
 * Get current query string.
 * Triggers re-render only when query changes.
 */
export const usePlaygroundQuery = () =>
  usePlaygroundStore((state) => state.query);

/**
 * Get current execution status (idle | loading | success | error).
 * Replace usePlaygroundIsRunning for cleaner status tracking.
 */
export const usePlaygroundStatus = () =>
  usePlaygroundStore((state) => state.status);

/**
 * Get current error message (null if no error).
 */
export const usePlaygroundError = () =>
  usePlaygroundStore((state) => state.error);

/**
 * Get execution state as boolean (true if loading).
 * Kept for backward compatibility with existing components.
 */
export const usePlaygroundIsRunning = () =>
  usePlaygroundStore((state) => state.status === "loading");

/**
 * Get active section (playground | policies | insights | emd).
 */
export const usePlaygroundActiveSection = () =>
  usePlaygroundStore((state) => state.activeSection);

/**
 * Get active dataset (users | sales | orders).
 */
export const usePlaygroundActiveDataset = () =>
  usePlaygroundStore((state) => state.activeDataset);

/**
 * Get session ID.
 */
export const usePlaygroundSessionId = () =>
  usePlaygroundStore((state) => state.sessionId);

/**
 * Get result payload (PlaygroundViewModel or null).
 */
export const usePlaygroundPayload = () =>
  usePlaygroundStore((state) => state.payload);

/**
 * Get both selected point and drilldown modal state.
 * Triggers re-render only when drilldown state changes.
 */
export const usePlaygroundDrilldown = () =>
  usePlaygroundStore((state) => ({
    selectedPoint: state.selectedPoint,
    isDrilldownOpen: state.isDrilldownOpen,
  }));

/**
 * Get dataset metadata lookup (returns active dataset name).
 * For pairing with external datasetMetadata lookup table.
 */
export const usePlaygroundDatasetMeta = () =>
  usePlaygroundStore((state) => state.activeDataset);

/**
 * Get execution state (status + payload + error).
 * Use this when you need all execution-related state together.
 */
export const usePlaygroundExecutionState = () =>
  usePlaygroundStore((state) => ({
    status: state.status,
    payload: state.payload,
    error: state.error,
  }));

/**
 * True when the latest governed response has been accepted but is still queued.
 */
export const usePlaygroundHasQueuedExecution = () =>
  usePlaygroundStore((state) => state.payload?.result.executionStatus === "queued");

/**
 * Get actions only (for components that don't depend on state change).
 * Use this to avoid unnecessary re-renders when only using actions.
 */
export const usePlaygroundActions = () =>
  usePlaygroundStore((state) => ({
    setQuery: state.setQuery,
    submitQuery: state.submitQuery,
    resetSession: state.resetSession,
    clearError: state.clearError,
    setActiveSection: state.setActiveSection,
    setActiveDataset: state.setActiveDataset,
    setSelectedPoint: state.setSelectedPoint,
    setIsDrilldownOpen: state.setIsDrilldownOpen,
  }));
