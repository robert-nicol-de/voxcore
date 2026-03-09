import React from 'react';
import ReactFlow, { Node, Edge, Controls, Background, MiniMap } from 'reactflow';
import 'reactflow/dist/style.css';

const nodes: Node[] = [
  {
    id: 'accounts',
    data: { label: 'ACCOUNTS' },
    position: { x: 100, y: 100 },
    style: {
      background: '#0f7fbf',
      color: '#fff',
      border: '2px solid #00d4ff',
      padding: '10px 20px',
      borderRadius: '8px',
      fontWeight: 'bold',
      fontSize: '14px',
    },
  },
  {
    id: 'transactions',
    data: { label: 'TRANSACTIONS' },
    position: { x: 400, y: 100 },
    style: {
      background: '#0f7fbf',
      color: '#fff',
      border: '2px solid #00d4ff',
      padding: '10px 20px',
      borderRadius: '8px',
      fontWeight: 'bold',
      fontSize: '14px',
    },
  },
  {
    id: 'customers',
    data: { label: 'CUSTOMERS' },
    position: { x: 250, y: 250 },
    style: {
      background: '#0f7fbf',
      color: '#fff',
      border: '2px solid #00d4ff',
      padding: '10px 20px',
      borderRadius: '8px',
      fontWeight: 'bold',
      fontSize: '14px',
    },
  },
];

const edges: Edge[] = [
  {
    id: 'a-t',
    source: 'accounts',
    target: 'transactions',
    label: 'account_id',
    labelStyle: { fill: '#7fb3ff', fontSize: '12px' },
    style: { stroke: '#0f7fbf', strokeWidth: 2 },
    animated: true,
  },
  {
    id: 'c-a',
    source: 'customers',
    target: 'accounts',
    label: 'customer_id',
    labelStyle: { fill: '#7fb3ff', fontSize: '12px' },
    style: { stroke: '#0f7fbf', strokeWidth: 2 },
    animated: true,
  },
];

export const SchemaMap: React.FC = () => {
  return (
    <div className="schema-map">
      <h2>🗺️ Database Relationship Map</h2>
      <p className="schema-subtitle">Interactive schema visualization showing table relationships</p>
      <div className="react-flow-container">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <Background color="#1a2332" style={{ backgroundColor: '#050a14' }} />
          <Controls />
          <MiniMap
            style={{
              backgroundColor: '#0b1220',
              border: '1px solid rgba(0, 212, 255, 0.2)',
            }}
            maskColor="rgba(0, 0, 0, 0.5)"
          />
        </ReactFlow>
      </div>
      <div className="schema-info">
        <div className="info-item">
          <span className="info-label">Tables:</span>
          <span className="info-value">3 (Accounts, Transactions, Customers)</span>
        </div>
        <div className="info-item">
          <span className="info-label">Relationships:</span>
          <span className="info-value">2 (account_id, customer_id)</span>
        </div>
        <div className="info-item">
          <span className="info-label">Status:</span>
          <span className="info-value">🟢 Connected</span>
        </div>
      </div>
    </div>
  );
};
