/**
 * TwoColumnGrid
 *
 * Responsive 2-column layout helper for result cards.
 * Stacks to 1 column on mobile (sm), 2 columns on tablet+ (md and up).
 *
 * Used in PlaygroundResultView to organize result sections:
 * - Governance + Why This Answer (explain + governance)
 * - Chart + Data Preview (visualize + explore)
 *
 * Responsibilities:
 * - Provide consistent spacing (gap-6 vertical, gap-4 horizontal)
 * - Stack responsively (flex-col md:grid md:grid-cols-2)
 * - Apply spacing to children (mx-0 lg:mx-auto for centering)
 */

interface TwoColumnGridProps {
  /** Left column content */
  left: React.ReactNode;
  /** Right column content */
  right: React.ReactNode;
  /** Optional CSS class for outer grid */
  className?: string;
}

export function TwoColumnGrid({
  left,
  right,
  className = "",
}: TwoColumnGridProps) {
  return (
    <div className={`flex flex-col gap-6 md:grid md:grid-cols-2 md:gap-4 lg:gap-6 ${className}`}>
      <div>{left}</div>
      <div>{right}</div>
    </div>
  );
}
