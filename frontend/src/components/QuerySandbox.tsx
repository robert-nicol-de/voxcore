import { useState } from "react"
import { apiUrl } from '../lib/api'

export default function QuerySandbox() {
  const [question, setQuestion] = useState("")
  const [sql, setSql] = useState("")
  const [result, setResult] = useState("")
  const [preview, setPreview] = useState<any[]>([])
  const [loadingPreview, setLoadingPreview] = useState(false)
  const [executingProduction, setExecutingProduction] = useState(false)

  function generateSQL() {
    const generatedSQL = `
SELECT region,
       SUM(revenue) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC`

    setSql(generatedSQL)
  }

  async function runQuery() {
    if (!sql.trim()) {
      setResult('Generate or enter SQL first')
      return
    }

    setLoadingPreview(true)
    try {
      const sandboxResponse = await fetch(apiUrl('/api/v1/query/sandbox'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: sql }),
      })
      const sandboxData = await sandboxResponse.json()

      if (!sandboxResponse.ok) {
        setResult(sandboxData.detail || 'Sandbox failed')
        return
      }

      if (sandboxData.status === 'sandboxed') {
        setPreview(sandboxData.preview || [])
        setResult(`Sandboxed: ${sandboxData.rows} rows, previewing first ${(sandboxData.preview || []).length}`)
      }
    } catch {
      setResult('Sandbox request failed')
    } finally {
      setLoadingPreview(false)
    }
  }

  async function executeOnProduction() {
    if (!sql.trim()) {
      setResult('No SQL to execute')
      return
    }

    setExecutingProduction(true)
    try {
      const inspectResponse = await fetch(apiUrl('/api/v1/query/inspect'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: sql }),
      })
      const inspectData = await inspectResponse.json()
      if (!inspectResponse.ok) {
        setResult(inspectData.detail || 'Inspect failed')
        return
      }
      if (!inspectData.allowed) {
        setResult(`Blocked by inspector: ${inspectData.reason || 'policy block'}`)
        return
      }

      const prodResponse = await fetch(apiUrl('/api/v1/query'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: sql,
          agent: 'sandbox_page',
          company_id: 'default',
        }),
      })
      const prodData = await prodResponse.json()
      if (!prodResponse.ok) {
        setResult(prodData.detail || 'Production execution failed')
        return
      }

      if (prodData.status === 'queued' && prodData.job_id) {
        setResult(`Queued for worker execution (job: ${prodData.job_id})`)

        let finalJob: any = null
        for (let attempt = 0; attempt < 25; attempt++) {
          await new Promise((resolve) => setTimeout(resolve, 800))
          const jobRes = await fetch(apiUrl(`/api/v1/query/jobs/${prodData.job_id}`))
          if (!jobRes.ok) continue
          const jobData = await jobRes.json()
          if (jobData.status === 'completed' || jobData.status === 'blocked' || jobData.status === 'failed') {
            finalJob = jobData
            break
          }
        }

        if (!finalJob) {
          setResult(`Job ${prodData.job_id} still running`)
          return
        }

        if (finalJob.status === 'failed') {
          setResult(finalJob.error || 'Worker execution failed')
          return
        }

        setResult(`Production execution status: ${finalJob.status}`)
        return
      }

      setResult(`Production execution status: ${prodData.status || 'ok'}`)
    } catch {
      setResult('Production execution request failed')
    } finally {
      setExecutingProduction(false)
    }
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
          {loadingPreview ? 'Running Sandbox...' : 'Run Query'}
        </button>
      </div>

      <div className="sandbox-section">
        <label>Sandbox Preview</label>
        <div className="sandbox-results">
          {result || "Results will appear here after running a query"}
        </div>

        {preview.length > 0 && (
          <div style={{ marginTop: 12, background: 'rgba(15,23,42,0.6)', borderRadius: 8, padding: 12 }}>
            {preview.map((row, rowIndex) => (
              <div key={rowIndex} style={{ marginBottom: 8, borderBottom: '1px solid rgba(255,255,255,0.08)', paddingBottom: 8 }}>
                {Object.entries(row).map(([key, value]) => (
                  <div key={key} style={{ fontSize: 13, fontFamily: 'monospace' }}>
                    {key}: {String(value)}
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}

        <button onClick={executeOnProduction} disabled={executingProduction}>
          {executingProduction ? 'Executing...' : 'Execute on Production'}
        </button>
      </div>
    </div>
  )
}
