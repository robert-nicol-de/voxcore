import React from "react";

type Template = {
  id: string;
  name: string;
  description: string;
};

export function TemplateLibrary({ onSelect }: { onSelect: (t: Template) => void }) {
  const templates: Template[] = [
    {
      id: "revenue_recovery",
      name: "Revenue Recovery",
      description: "Recover revenue drops with automated promotions"
    },
    {
      id: "churn_reduction",
      name: "Churn Reduction",
      description: "Detect and reduce customer churn"
    },
    {
      id: "sales_spike",
      name: "Sales Spike Response",
      description: "Capitalize on sudden demand increases"
    }
  ];

  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      {templates.map(t => (
        <div
          key={t.id}
          onClick={() => onSelect(t)}
          className="p-4 bg-white border rounded-2xl hover:shadow cursor-pointer"
        >
          <h3 className="font-semibold">{t.name}</h3>
          <p className="text-sm text-gray-500">{t.description}</p>
        </div>
      ))}
    </div>
  );
}
