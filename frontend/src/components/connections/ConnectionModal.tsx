import React from "react";

export const ConnectionModal = ({ db, onClose, onConnect }) => {
  if (!db) return null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
      <div className="bg-[#0f172a] p-6 rounded-xl w-[400px] border border-[#1e293b]">
        <h2 className="text-white text-lg mb-4">
          Connect to {db}
        </h2>
        <input
          placeholder="Host"
          className="w-full mb-3 p-2 bg-black border border-gray-700 text-white rounded"
        />
        <input
          placeholder="Database"
          className="w-full mb-3 p-2 bg-black border border-gray-700 text-white rounded"
        />
        <input
          placeholder="Username"
          className="w-full mb-3 p-2 bg-black border border-gray-700 text-white rounded"
        />
        <input
          type="password"
          placeholder="Password"
          className="w-full mb-4 p-2 bg-black border border-gray-700 text-white rounded"
        />
        <button className="w-full bg-blue-600 py-2 rounded" onClick={onConnect}>
          Connect
        </button>
        <button
          onClick={onClose}
          className="w-full mt-2 text-gray-400"
        >
          Cancel
        </button>
      </div>
    </div>
  );
};
