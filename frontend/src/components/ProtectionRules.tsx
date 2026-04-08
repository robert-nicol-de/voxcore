import { useState } from "react";
import Table from "./Table";

export default function ProtectionRules() {
  const [rules] = useState([
    {
      name: "Block Password Access",
      rule: "SELECT on users.password",
      status: "ACTIVE"
    },
    {
      name: "Prevent DELETE Queries",
      rule: "DELETE statements blocked",
      status: "ACTIVE"
    },
    {
      name: "Protect PII Tables",
      rule: "Access to customer_ssn restricted",
      status: "ACTIVE"
    },
    {
      name: "Row Limit Protection",
      rule: "Max results: 1000 rows",
      status: "ACTIVE"
    }
  ]);

  return (
    <div className="protection-rules">
      <h2>🔐 Database Protection Rules</h2>

      <Table data={rules} loading={false} />
    </div>
  );
}
