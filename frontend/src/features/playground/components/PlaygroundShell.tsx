/**
 * PlaygroundShell
 *
 * The page frame container for the entire Playground experience.
 * Provides consistent spacing, max-width constraints, and layout structure.
 *
 * Design principles:
 * - Spacious and calm (generous vertical breathing room)
 * - Expensive-feeling (premium padding and spacing)
 * - Flexible (adapts to different content arrangements)
 */

import React from "react";

interface PlaygroundShellProps {
  children: React.ReactNode;
  className?: string;
}

export function PlaygroundShell({ children, className = "" }: PlaygroundShellProps) {
  return (
    <div className={`min-h-screen bg-[#020817] px-6 py-12 lg:px-8 xl:py-16 ${className}`}>
      {/* Constrained width container for breathing room at wider viewports */}
      <div className="mx-auto max-w-4xl">
        {children}
      </div>
    </div>
  );
}
