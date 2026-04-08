import React, { useEffect, useState } from "react";
import RuleBuilder from "./RuleBuilder";
import { RuleList } from "./RuleList";

export default function AutomationPanel() {
  const [rules, setRules] = useState<any[]>([]);
  useEffect(() => {
    fetch("/api/actions/auto-rules")
      .then(res => res.json())
      .then(data => setRules(data.rules || []));
  }, []);
  return (
    <div className="max-w-2xl mx-auto py-8 space-y-8">
      <RuleBuilder />
      <h3 className="text-lg font-semibold mt-8">Active Rules</h3>
      <RuleList rules={rules} />
    </div>
  );
}
