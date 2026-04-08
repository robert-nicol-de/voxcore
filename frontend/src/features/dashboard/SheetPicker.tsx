import React, { useState, useEffect } from "react";

type Sheet = {
  id: string;
  name: string;
};

export function SheetPicker({ onSelect }) {
  const [sheets, setSheets] = useState<Sheet[]>([]);

  useEffect(() => {
    fetch("/api/google/sheets")
      .then(res => res.json())
      .then(data => setSheets(data.files));
  }, []);

  return (
    <div className="grid grid-cols-3 gap-4">
      {sheets.map(sheet => (
        <div
          key={sheet.id}
          onClick={() => onSelect(sheet)}
          className="p-4 border rounded-xl hover:shadow cursor-pointer"
        >
          📄 {sheet.name}
        </div>
      ))}
    </div>
  );
}
