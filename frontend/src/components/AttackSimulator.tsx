import { useState } from "react"

export default function AttackSimulator() {
  const [log, setLog] = useState<string[]>([])

  function simulateAttack(type: string) {
    let message = ""

    if (type === "injection") {
      message = "🔴 SQL Injection detected → Query blocked"
    }

    if (type === "pii") {
      message = "🔴 Sensitive table access detected → Blocked by policy"
    }

    if (type === "drop") {
      message = "🔴 Dangerous DROP TABLE command blocked"
    }

    setLog(prev => [message, ...prev])
  }

  return (
    <div className="attack-simulator">
      <h2>⚔️ Database Attack Simulator</h2>

      <div className="attack-buttons">
        <button onClick={() => simulateAttack("injection")}>
          Simulate SQL Injection
        </button>

        <button onClick={() => simulateAttack("pii")}>
          Simulate PII Access
        </button>

        <button onClick={() => simulateAttack("drop")}>
          Simulate DROP TABLE
        </button>
      </div>

      <div className="attack-log">
        <h3>Security Log</h3>
        {log.length === 0 ? (
          <div className="attack-entry empty">Click a button to simulate an attack...</div>
        ) : (
          log.map((entry, i) => (
            <div key={i} className="attack-entry">
              {entry}
            </div>
          ))
        )}
      </div>
    </div>
  )
}
