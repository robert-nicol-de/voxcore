import React from "react";

export const Page = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="min-h-screen bg-[#0B0F19] text-white overflow-hidden">
      {children}
    </div>
  );
};
