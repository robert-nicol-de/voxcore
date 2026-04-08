import { useState } from "react";

export function Tabs({ labels, children }: { labels: string[]; children: React.ReactNode[] }) {
  const [active, setActive] = useState(0);
  return (
    <div>
      <div className="flex gap-2 mb-2">
        {labels.map((label, i) => (
          <button
            key={i}
            className={`px-4 py-2 rounded-t ${active === i ? "bg-blue-600 text-white" : "bg-gray-100 text-gray-600"}`}
            onClick={() => setActive(i)}
          >
            {label}
          </button>
        ))}
      </div>
      <div className="border rounded-b p-4 bg-white">
        {children[active]}
      </div>
    </div>
  );
}
