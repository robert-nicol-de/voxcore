import React from "react";
import { Card } from "../ui/Card";

interface PolicyBlockCardProps {
  title: string;
  reason: string;
  policy: string;
}

export const PolicyBlockCard = ({ title, reason, policy }: PolicyBlockCardProps) => {
  return (
    <Card>
      <div className="flex items-start gap-4">
        <div className="text-2xl">🛑</div>
        <div className="flex-1">
          <h4 className="font-semibold mb-2">{title}</h4>
          <p className="text-sm text-gray-400 mb-2">{reason}</p>
          <p className="text-xs text-gray-500">Policy: {policy}</p>
        </div>
      </div>
    </Card>
  );
};
