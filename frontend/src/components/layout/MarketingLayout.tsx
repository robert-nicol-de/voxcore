import React from "react";
import MarketingNavbar from "./MarketingNavbar";
import MarketingFooter from "./MarketingFooter";

type MarketingLayoutProps = {
  children: React.ReactNode;
  className?: string;
  contentClassName?: string;
  hideFooter?: boolean;
};

export default function MarketingLayout({
  children,
  className = "",
  contentClassName = "",
  hideFooter = false,
}: MarketingLayoutProps) {
  return (
    <div
      className={[
        "min-h-screen overflow-x-hidden bg-[#030816] text-white",
        "[background-image:radial-gradient(circle_at_top_left,rgba(59,130,246,0.16),transparent_28%),radial-gradient(circle_at_85%_15%,rgba(168,85,247,0.10),transparent_18%)]",
        className,
      ].join(" ")}
    >
      <MarketingNavbar />

      <main className={contentClassName}>{children}</main>

      {!hideFooter && <MarketingFooter />}
    </div>
  );
}

export function MarketingContainer({
  children,
  className = "",
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return <div className={`mx-auto w-full max-w-7xl px-6 lg:px-10 ${className}`}>{children}</div>;
}
