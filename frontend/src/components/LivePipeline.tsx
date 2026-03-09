import { useState, useEffect } from "react"

interface PipelineStep {
  name: string
  status: "pending" | "active" | "complete" | "error"
  duration: number
}

export default function LivePipeline() {
  const [steps, setSteps] = useState<PipelineStep[]>([
    { name: "Input Parsing", status: "complete", duration: 45 },
    { name: "Intent Detection", status: "complete", duration: 120 },
    { name: "Schema Mapping", status: "active", duration: 0 },
    { name: "SQL Generation", status: "pending", duration: 0 },
    { name: "Security Check", status: "pending", duration: 0 },
    { name: "Execution", status: "pending", duration: 0 }
  ])

  useEffect(() => {
    const timer = setInterval(() => {
      setSteps(prev => {
        const updated = [...prev]
        const activeIndex = updated.findIndex(s => s.status === "active")
        
        if (activeIndex !== -1 && activeIndex < updated.length - 1) {
          updated[activeIndex].duration += 50
          if (updated[activeIndex].duration > 200) {
            updated[activeIndex].status = "complete"
            updated[activeIndex + 1].status = "active"
          }
        }
        
        return updated
      })
    }, 500)

    return () => clearInterval(timer)
  }, [])

  return (
    <div className="live-pipeline">
      <div className="pipeline-header">
        <h2>🔴 Live Query Pipeline</h2>
        <span className="pipeline-status">Processing...</span>
      </div>

      <div className="pipeline-track">
        {steps.map((step, idx) => (
          <div key={idx} className={`pipeline-step ${step.status}`}>
            <div className="step-indicator">
              {step.status === "complete" && <span>✓</span>}
              {step.status === "active" && <span className="pulse">●</span>}
              {step.status === "pending" && <span>◦</span>}
              {step.status === "error" && <span>✕</span>}
            </div>
            <div className="step-label">{step.name}</div>
            {step.duration > 0 && <div className="step-duration">{step.duration}ms</div>}
            {idx < steps.length - 1 && <div className="step-connector"></div>}
          </div>
        ))}
      </div>
    </div>
  )
}
