import React from "react";
import { Card } from "../ui/Card";

interface RiskScoreCardProps {
  score: number;
}

export const RiskScoreCard = ({ score }: RiskScoreCardProps) => {
  const color =
    score > 80 ? "text-red-400" : score > 60 ? "text-yellow-400" : "text-green-400";

  return (
    <Card>
      <div className="text-sm text-gray-400">Risk Score</div>
      <div className={`text-4xl font-bold ${color}`}>{score}</div>
    </Card>
  );
};
