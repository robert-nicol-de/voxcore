import React from "react";

export function GoogleSheetsConnector() {
  const connect = () => {
    window.location.href = "/api/connect/google";
  };

  return (
    <button
      onClick={connect}
      className="px-4 py-2 bg-green-600 text-white rounded-lg"
    >
      🔗 Connect Google Sheets
    </button>
  );
}
