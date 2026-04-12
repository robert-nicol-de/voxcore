/**
 * Playground Feature Public API
 *
 * Single entry point for importing playground types, services, state, utilities, and components.
 * Enables clean imports throughout the codebase.
 *
 * Usage:
 * import { usePlaygroundStore } from '@/features/playground';
 * import type { PlaygroundViewModel } from '@/features/playground';
 * import { PlaygroundShell, PlaygroundHero, PlaygroundQueryComposer } from '@/features/playground';
 */

// Types
export type {
  // Risk & Classification
  PlaygroundRiskLevel,
  PlaygroundDecision,
  PlaygroundPolicyStatus,
  PlaygroundDataset,
  PlaygroundChartKind,
  // Chart & Data
  PlaygroundColumn,
  PlaygroundRow,
  PlaygroundChartConfig,
  // Backend Response (PRIMARY)
  HeroInsight,
  GovernanceBlock,
  WhyThisAnswer,
  EmdInsight,
  EmdPreview,
  ExecutionMeta,
  PlaygroundQueryResponse,
  // Frontend Composition
  PlaygroundResult,
  PlaygroundViewModel,
  PlaygroundSuggestion,
  PlaygroundMode,
  // UI Components
  PlaygroundGovernanceMeta,
  PlaygroundEmdPanel,
  PlaygroundQueryContext,
  // Execution Status
  PlaygroundExecutionStatus,
  PlaygroundQueryStatus,
  PlaygroundResultStatus,
  // Backward Compatibility Aliases
  PlaygroundWhyThisAnswer,
  PlaygroundEmdInsight,
  PlaygroundEmdPreview,
  // State Management
  PlaygroundStateSlice,
  // API
  PlaygroundApiRequest,
  PlaygroundBackendResponse,
  // Dataset Metadata
  DatasetInsight,
  DatasetMeta,
} from "./types";

// Services
export { buildInitialPlaygroundViewModel, executePlaygroundQuery } from "./services";

// State
export {
  usePlaygroundStore,
  usePlaygroundQuery,
  usePlaygroundStatus,
  usePlaygroundError,
  usePlaygroundIsRunning,
  usePlaygroundActiveSection,
  usePlaygroundActiveDataset,
  usePlaygroundSessionId,
  usePlaygroundPayload,
  usePlaygroundDrilldown,
  usePlaygroundDatasetMeta,
  usePlaygroundExecutionState,
  usePlaygroundActions,
} from "./state";

// Utils
export * from "./utils";

// Components
export {
  PlaygroundShell,
  PlaygroundHero,
  PlaygroundQueryComposer,
  PlaygroundPromptChips,
  PlaygroundResultStack,
  PlaygroundEmptyState,
  PlaygroundLoadingState,
  PlaygroundErrorState,
  TwoColumnGrid,
  PlaygroundResultView,
  PlaygroundTrustBar,
  PlaygroundHeroInsightCard,
  PlaygroundGovernanceCard,
  PlaygroundWhyThisAnswerCard,
  PlaygroundChartCard,
  PlaygroundDataPreviewTable,
  PlaygroundEmdPreviewCard,
  PlaygroundSuggestionsRow,
  PlaygroundSuggestionCard,
  PlaygroundExecutionMeta,
} from "./components";
