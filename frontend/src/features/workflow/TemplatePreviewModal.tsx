import React from "react";
import ReactFlow from "reactflow";

export function TemplatePreviewModal({ template, onUse, onClose }) {
  if (!template) return null;

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl w-[800px] p-6">
        <h2 className="text-xl font-semibold mb-2">{template.name}</h2>
        <p className="text-sm text-gray-500 mb-4">{template.description}</p>
        <div className="h-[400px] border rounded-xl">
          <ReactFlow
            nodes={template.nodes}
            edges={template.edges}
            fitView
            nodesDraggable={false}
            panOnDrag={false}
            zoomOnScroll={false}
            zoomOnPinch={false}
            zoomOnDoubleClick={false}
            elementsSelectable={false}
          />
        </div>
        <div className="flex justify-end gap-3 mt-4">
          <button onClick={onClose} className="px-4 py-2 rounded-lg border">Cancel</button>
          <button
            onClick={() => onUse(template)}
            className="bg-black text-white px-4 py-2 rounded-lg"
          >
            Use Template
          </button>
        </div>
      </div>
    </div>
  );
}
