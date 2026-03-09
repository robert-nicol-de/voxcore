import { useState } from "react"

export default function QuerySandbox() {
  const [question, setQuestion] = useState("")
  const [sql, setSql] = useState("")
  const [result, setResult] = useState("")

  function generateSQL() {
    const generatedSQL = `
SELECT region,
       SUM(revenue) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC`

    setSql(generatedSQL)
  }

  function runQuery() {
    setResult("Query executed successfully. 120 rows returned.")
  }

  return (
    <div className="query-sandbox">
      <h2>🧪 AI Query Sandbox</h2>

      <div className="sandbox-section">
        <label>Ask AI a Question</label>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Example: Show revenue by region"
        />
        <button onClick={generateSQL}>
          Generate SQL
        </button>
      </div>

      <div className="sandbox-section">
        <label>Generated SQL</label>
        <textarea
          value={sql}
          onChange={(e) => setSql(e.target.value)}
        />
        <button onClick={runQuery}>
          Run Query
        </button>
      </div>

      <div className="sandbox-section">
        <label>Results</label>
        <div className="sandbox-results">
          {result || "Results will appear here after running a query"}
        </div>
      </div>
    </div>
  )
}
