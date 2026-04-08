import React, { useState, useEffect } from "react";

export function SheetPreview({ sheet }) {
  const [preview, setPreview] = useState(null);

  useEffect(() => {
    if (!sheet) return;
    fetch(`/api/google/sheet-preview?sheet_id=${sheet.id}`)
      .then(res => res.json())
      .then(setPreview);
  }, [sheet]);

  if (!preview) return null;

  return (
    <div className="mt-4 border p-4 rounded-xl">
      <h3 className="font-semibold mb-2">Preview</h3>
      <table className="text-sm">
        <thead>
          <tr>
            {preview.columns.map((c) => (
              <th key={c}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {preview.rows.map((r, i) => (
            <tr key={i}>
              {r.map((cell, j) => (
                <td key={j}>{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
