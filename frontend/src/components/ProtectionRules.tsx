import { useState } from "react"

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
  ])

  return (
    <div className="protection-rules">
      <h2>🔐 Database Protection Rules</h2>

      <table className="rules-table">
        <thead>
          <tr>
            <th>Rule Name</th>
            <th>Protection</th>
            <th>Status</th>
          </tr>
        </thead>

        <tbody>
          {rules.map((rule, index) => (
            <tr key={index}>
              <td>{rule.name}</td>
              <td className="rule-text">{rule.rule}</td>
              <td className="rule-status">{rule.status}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
