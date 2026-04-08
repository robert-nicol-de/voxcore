import React from "react";

const SchemaExplorer = () => {
  return (
    <div className="p-6 text-white">
      <h1 className="text-xl font-semibold mb-4">
        Schema Explorer
      </h1>

      <div className="text-gray-400 mb-6">
        No schema loaded yet (layout mode)
      </div>

      {/* Mock UI for layout */}
      <div className="grid grid-cols-3 gap-4">
        {["customers", "orders", "products"].map((table) => (
          <div
            key={table}
            className="bg-[#0f172a] p-4 rounded-xl border border-[#1e293b] hover:border-blue-500 transition"
          >
            <div className="text-sm text-gray-400">Table</div>
            <div className="text-white font-medium">{table}</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default SchemaExplorer;