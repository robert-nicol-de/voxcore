import React from "react";

export default function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-2xl border border-gray-800 bg-[#111] p-5 mb-6 hover:border-blue-500/30 transition">
      <div className="text-lg font-semibold text-white mb-2">{title}</div>
      <div className="text-gray-200 whitespace-pre-line">{children}</div>
    </div>
  );
}
