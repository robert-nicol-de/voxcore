import React, { useState } from "react";
import { SimulationRunnerAI } from "./SimulationRunnerAI";
import ReactFlow, {
  Background,
  Controls,
  addEdge,
  useNodesState,
  useEdgesState,
  MiniMap
} from "reactflow";
import "reactflow/dist/style.css";
import NodePalette from "./NodePalette";
import NodeConfigPanel from "./NodeConfigPanel";
import { TemplateLibrary } from "./TemplateLibrary";
import { TemplatePreviewModal } from "./TemplatePreviewModal";

const initialNodes = [
  {
    id: "1",
    type: "triggerNode",
    position: { x: 0, y: 50 },
    data: { label: "Trigger: Revenue Drop", type: "trigger", config: { trigger_type: "revenue_drop" } },
    style: { background: "#E0F2FE", borderRadius: 12, padding: 10, border: "2px solid #2563eb" }
  }
];

// --- Template Definitions ---
const revenueRecoveryTemplate = {
  nodes: [
    { id: "1", type: "triggerNode", position: { x: 0, y: 50 }, data: { label: "Revenue Drop", type: "trigger", config: { trigger_type: "revenue_drop" } }, style: { background: "#E0F2FE", borderRadius: 12, padding: 10, border: "2px solid #2563eb" } },
    { id: "2", type: "actionNode", position: { x: 200, y: 100 }, data: { label: "Launch Promo", type: "action", config: { action_type: "launch_promo" } }, style: { background: "#222", color: "#fff", borderRadius: 12, padding: 10 } },
    { id: "3", type: "evaluateNode", position: { x: 200, y: 200 }, data: { label: "Evaluate Impact", type: "evaluate", config: { metric: "impact" } }, style: { background: "#dcfce7", borderRadius: 12, padding: 10 } },
    { id: "4", type: "conditionNode", position: { x: 200, y: 320 }, data: { label: "Impact > 10%?", type: "condition", config: { field: "impact", operator: ">", value: 0.1 } }, style: { background: "#FEF3C7", border: "2px solid #F59E0B", borderRadius: 12, padding: 10 } },
    { id: "5", type: "actionNode", position: { x: 400, y: 420 }, data: { label: "Notify Team", type: "action", config: { action_type: "notify_team" } }, style: { background: "#222", color: "#fff", borderRadius: 12, padding: 10 } },
    { id: "6", type: "loopNode", position: { x: 0, y: 420 }, data: { label: "Retry Promo (max 3x)", type: "loop", config: { max_retries: 3 } }, style: { background: "#f3f4f6", border: "2px dashed #6b7280", borderRadius: 12, padding: 10 } }
  ],
  edges: [
    { id: "e1-2", source: "1", target: "2" },
    { id: "e2-3", source: "2", target: "3" },
    { id: "e3-4", source: "3", target: "4" },
    { id: "e4-5", source: "4", target: "5", label: "YES", animated: true },
    { id: "e4-6", source: "4", target: "6", label: "NO", animated: true },
    { id: "e6-2", source: "6", target: "2", label: "Retry", animated: true }
  ]
};

const churnReductionTemplate = {
  nodes: [
    { id: "1", type: "triggerNode", position: { x: 0, y: 50 }, data: { label: "Churn Risk Detected", type: "trigger", config: { trigger_type: "churn_risk" } }, style: { background: "#E0F2FE", borderRadius: 12, padding: 10, border: "2px solid #2563eb" } },
    { id: "2", type: "actionNode", position: { x: 200, y: 100 }, data: { label: "Offer Retention Deal", type: "action", config: { action_type: "offer_retention" } }, style: { background: "#222", color: "#fff", borderRadius: 12, padding: 10 } },
    { id: "3", type: "scoreNode", position: { x: 200, y: 200 }, data: { label: "Score > 80?", type: "condition", config: { field: "churn_score", operator: "<", value: 0.2 } }, style: { background: "#fef9c3", border: "2px solid #f59e0b", borderRadius: 12, padding: 10 } },
    { id: "4", type: "actionNode", position: { x: 400, y: 300 }, data: { label: "Escalate to Team", type: "action", config: { action_type: "escalate" } }, style: { background: "#222", color: "#fff", borderRadius: 12, padding: 10 } }
  ],
  edges: [
    { id: "e1-2", source: "1", target: "2" },
    { id: "e2-3", source: "2", target: "3" },
    { id: "e3-4", source: "3", target: "4", label: "NO", animated: true }
  ]
};

const salesSpikeTemplate = {
  nodes: [
    { id: "1", type: "triggerNode", position: { x: 0, y: 50 }, data: { label: "Sales Spike", type: "trigger", config: { trigger_type: "sales_spike" } }, style: { background: "#E0F2FE", borderRadius: 12, padding: 10, border: "2px solid #2563eb" } },
    { id: "2", type: "actionNode", position: { x: 200, y: 100 }, data: { label: "Increase Inventory", type: "action", config: { action_type: "increase_inventory" } }, style: { background: "#222", color: "#fff", borderRadius: 12, padding: 10 } },
    { id: "3", type: "actionNode", position: { x: 200, y: 200 }, data: { label: "Notify Fulfillment", type: "action", config: { action_type: "notify_fulfillment" } }, style: { background: "#ede9fe", borderRadius: 12, padding: 10 } }
  ],
  edges: [
    { id: "e1-2", source: "1", target: "2" },
    { id: "e2-3", source: "2", target: "3" }
  ]
};

function loadTemplate(id) {
  if (id === "revenue_recovery") return revenueRecoveryTemplate;
  if (id === "churn_reduction") return churnReductionTemplate;
  if (id === "sales_spike") return salesSpikeTemplate;
  return { nodes: [], edges: [] };
}

  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [showTemplates, setShowTemplates] = useState(true);
  const [previewTemplate, setPreviewTemplate] = useState(null);
  const [branchProbs, setBranchProbs] = useState({});

  const onConnect = (params) => {
    // If source node is a condition, prompt for YES/NO label
    const sourceNode = nodes.find((n) => n.id === params.source);
    let label = undefined;
    if (sourceNode && sourceNode.data.type === "condition") {
      label = window.prompt("Label this branch (YES/NO)?", "YES");
    }
    setEdges((eds) => addEdge({ ...params, label }, eds));
  };

  const onNodeClick = (_event, node) => setSelectedNode(node);

  const onNodeDrop = (type) => {
    const id = (nodes.length + 1).toString();
    const y = 100 + nodes.length * 80;
    let color = "#fff";
    let border = "2px solid #e5e7eb";
    let nodeType = type + "Node";
    if (type === "action") color = "#222";
    if (type === "slack") color = "#ede9fe";
    if (type === "wait") color = "#fef9c3";
    if (type === "evaluate") color = "#dcfce7";
    if (type === "email") color = "#f0f9ff";
    if (type === "trigger") color = "#E0F2FE";
    if (type === "condition") {
      color = "#FEF3C7";
      border = "2px solid #F59E0B";
      nodeType = "conditionNode";
    }
    setNodes((nds) => [
      ...nds,
      {
        id,
        type: nodeType,
        position: { x: 200, y },
        data: { label: type.charAt(0).toUpperCase() + type.slice(1), type, config: {} },
        style: { background: color, borderRadius: 12, padding: 10, border }
      }
    ]);
  };

  const onSave = () => {
    const workflow = {
      steps: nodes.map((n) => ({
        id: n.id,
        type: n.data.type,
        config: n.data.config
      }))
    };
    // TODO: POST to /api/workflows
    alert("Workflow JSON:\n" + JSON.stringify(workflow, null, 2));
  };

  // Auto arrange: simple vertical stacking
  const autoArrange = () => {
    const gapY = 100;
    const startX = 200;
    const arranged = nodes.map((n, i) => ({
      ...n,
      position: { x: startX, y: 50 + i * gapY }
    }));
    setNodes(arranged);
  };

  // Mini toolbar
  const Toolbar = () => (
    <div className="flex gap-2 mb-2 items-center">
      <button className="px-2 py-1 bg-gray-200 rounded" onClick={autoArrange}>Auto Arrange</button>
      <button className="px-2 py-1 bg-blue-600 text-white rounded" onClick={onSave}>Save</button>
    </div>
  );

  // Add animation and snap/grid features
  return (
    <div className="flex gap-4">
      <div className="flex-1">
        {showTemplates && (
          <>
            <h2 className="text-xl font-bold mb-2">⚡ Start with a Template</h2>
            <TemplateLibrary
              onSelect={t => {
                const wf = loadTemplate(t.id);
                setPreviewTemplate({ ...t, ...wf });
              }}
            />
            <TemplatePreviewModal
              template={previewTemplate}
              onUse={tpl => {
                setNodes(tpl.nodes);
                setEdges(tpl.edges);
                setShowTemplates(false);
                setPreviewTemplate(null);
              }}
              onClose={() => setPreviewTemplate(null)}
            />
          </>
        )}
        <NodePalette onNodeDrop={onNodeDrop} />
      </div>
      <div className="h-[600px] w-full bg-gray-50 rounded-xl border relative">
        <Toolbar />
        <ReactFlow
          nodes={nodes.map(n => {
            // Overlay prediction if present
            const pred = n.data && n.data.prediction;
            let borderColor = n.style?.border || "2px solid #e5e7eb";
            let boxShadow = undefined;
            if (pred && pred.confidence !== undefined) {
              if (pred.confidence > 0.8) {
                borderColor = "2px solid #22c55e";
                boxShadow = "0 0 12px rgba(34,197,94,0.6)";
              } else if (pred.confidence > 0.5) {
                borderColor = "2px solid #eab308";
                boxShadow = "0 0 12px rgba(234,179,8,0.6)";
              } else {
                borderColor = "2px solid #ef4444";
                boxShadow = "0 0 12px rgba(239,68,68,0.6)";
              }
            }
            return {
              ...n,
              className: "transition-all duration-300 ease-in-out",
              style: { ...n.style, border: borderColor, boxShadow },
              data: {
                ...n.data,
                // Render overlay in label if prediction exists
                label: (
                  <div>
                    {n.data.label}
                    {pred && pred.impact_range && (
                      <div className="flex justify-between items-center mt-1">
                        <span className="text-xs text-green-600">
                          +{(pred.impact_range[0] * 100).toFixed(0)}%
                          <span> → {(pred.impact_range[1] * 100).toFixed(0)}%</span>
                        </span>
                        <span className="text-xs text-gray-500">
                          {(pred.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    )}
                    {pred && pred.probability_true !== undefined && (
                      <div className="text-xs mt-1">
                        <span className="text-green-600">YES: {(pred.probability_true * 100).toFixed(0)}%</span> &nbsp;
                        <span className="text-red-600">NO: {(pred.probability_false * 100).toFixed(0)}%</span>
                      </div>
                    )}
                  </div>
                )
              }
            };
          })}
          edges={edges.map(e => {
            // Relabel YES/NO edges with branch probabilities if available
            if (e.label && branchProbs) {
              const sourceNode = nodes.find(n => n.id === e.source);
              if (sourceNode && sourceNode.data?.type === "condition") {
                const pred = sourceNode.data.prediction;
                if (pred && (e.label === "YES" || e.label === "NO")) {
                  return {
                    ...e,
                    label: e.label === "YES"
                      ? `${(pred.probability_true * 100).toFixed(0)}%`
                      : `${(pred.probability_false * 100).toFixed(0)}%`
                  };
                }
                const probs = branchProbs[sourceNode.id];
                if (probs && (e.label === "YES" || e.label === "NO")) {
                  return {
                    ...e,
                    label: e.label === "YES"
                      ? `${(probs.YES * 100).toFixed(0)}%`
                      : `${(probs.NO * 100).toFixed(0)}%`
                  };
                }
              }
            }
            return { ...e, animated: true };
          })}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          fitView
          snapToGrid={true}
          snapGrid={[20, 20]}
          nodesDraggable={true}
        >
          <Background gap={20} size={1} color="#e5e7eb" />
          <Controls />
          <MiniMap />
        </ReactFlow>
            {/* AI Simulation Runner */}
        <div className="mt-6">
          <SimulationRunnerAI
            workflow={{ nodes, edges }}
            setNodePredictions={predictions => {
              setNodes(nds =>
                nds.map(n => {
                  const pred = predictions.find(p => p.step_id === n.id);
                  if (pred) {
                    return {
                      ...n,
                      data: {
                        ...n.data,
                        prediction: pred
                      }
                    };
                  }
                  return {
                    ...n,
                    data: { ...n.data, prediction: undefined }
                  };
                })
              );
            }}
            setBranchProbs={setBranchProbs}
          />
        </div>
      </div>
      {selectedNode && (
        <NodeConfigPanel node={selectedNode} onClose={() => setSelectedNode(null)} setNodes={setNodes} />
      )}
    </div>
  );
}
