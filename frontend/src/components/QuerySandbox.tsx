import { useState } from "react"
import PageHeader from '../components/PageHeader'
import { apiUrl } from '../lib/api'

export default function QuerySandbox() {
  const [question, setQuestion] = useState("")
  const [sql, setSql] = useState("")
  const [result, setResult] = useState("")
  const [preview, setPreview] = useState<any[]>([])
  const [loadingPreview, setLoadingPreview] = useState(false)
  const [executingProduction, setExecutingProduction] = useState(false)
  const [riskLevel, setRiskLevel] = useState('LOW')
  const [generatingSql, setGeneratingSql] = useState(false)

  async function generateSQL() {
    setGeneratingSql(true)
    setPreview([])
    setResult('')

    const normalizedQuestion = question.trim().toLowerCase()
    let generatedSQL = `SELECT region,
       SUM(revenue) AS total_revenue
FROM sales
GROUP BY region
ORDER BY total_revenue DESC`

    if (normalizedQuestion.includes('product')) {
      generatedSQL = `SELECT product,
       SUM(revenue) AS total_revenue
FROM sales
GROUP BY product
ORDER BY total_revenue DESC`
    } else if (normalizedQuestion.includes('customer')) {
      generatedSQL = `SELECT customer_name,
       SUM(total) AS total_revenue
FROM orders
GROUP BY customer_name
ORDER BY total_revenue DESC`
    }

    setSql(generatedSQL)

    try {
      const riskResponse = await fetch(apiUrl('/api/v1/query/risk'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: generatedSQL }),
      })

      if (riskResponse.ok) {
        const riskData = await riskResponse.json()
        setRiskLevel((riskData.risk_level || 'low').toUpperCase())
      } else {
        setRiskLevel('LOW')
      }
    } catch {
      setRiskLevel('LOW')
    } finally {
      setGeneratingSql(false)
    }
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
      const companyId = localStorage.getItem('voxcore_company_id') || 'default'
      const workspaceId = localStorage.getItem('voxcore_workspace_id') || 'default'

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
          company_id: companyId,
          workspace_id: workspaceId,
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
    <div className="sandbox-container sandbox-watermark">
      <PageHeader title="Sandbox" subtitle="Preview AI-generated SQL safely before production execution" />

      <div className="card">
        <h3>Ask a question about your data</h3>

        <div className="sandbox-input-row">
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Show revenue by product last month"
            className="sandbox-input"
          />

          <button className="primary-btn" onClick={generateSQL} disabled={generatingSql}>
            {generatingSql ? 'Generating...' : 'Generate SQL'}
          </button>
        </div>
      </div>

      <div className="card">
        <h3>Generated SQL</h3>

        <pre className="sql-preview">{sql || 'SELECT product, SUM(revenue)\nFROM sales\nGROUP BY product'}</pre>

        <div className="sandbox-risk-row">
          <span>Risk Analysis</span>
          <span className={`risk-badge ${riskLevel.toLowerCase()}`}>{riskLevel} RISK</span>
        </div>
      </div>

      <div className="sandbox-actions">
        <button className="secondary-btn" onClick={runQuery} disabled={loadingPreview}>
          {loadingPreview ? 'Previewing...' : 'Preview in Sandbox'}
        </button>

        <button className="primary-btn" onClick={executeOnProduction} disabled={executingProduction}>
          {executingProduction ? 'Executing...' : 'Execute on Production'}
        </button>
      </div>

      <div className="card">
        <h3>Query Results</h3>

        {preview.length === 0 ? (
          <div className="results-placeholder">
            {result || 'Results will appear here after running the query.'}
          </div>
        ) : (
          <div className="sandbox-table-wrap">
            {result && <div className="results-placeholder" style={{ marginBottom: 12 }}>{result}</div>}
            <table className="sandbox-table">
              <thead>
                <tr>
                  {Object.keys(preview[0] || {}).map((key) => (
                    <th key={key}>{key}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {preview.map((row, rowIndex) => (
                  <tr key={rowIndex}>
                    {Object.keys(preview[0] || {}).map((key) => (
                      <td key={`${rowIndex}-${key}`}>{String(row[key] ?? '')}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
