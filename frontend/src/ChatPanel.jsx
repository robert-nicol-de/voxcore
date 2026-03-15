// ChatPanel.jsx
// Handles chat UI, sends messages to the conversation API, displays chat and suggestions
import React, { useState } from 'react';

export default function ChatPanel({ sessionId, onDashboardUpdate }) {
  const [input, setInput] = useState('');
  const [history, setHistory] = useState([]);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: 'user', text: input };
    setHistory(h => [...h, userMsg]);
    setInput('');
    const res = await fetch('/api/conversation/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: input, session_id: sessionId })
    });
    const data = await res.json();
    setHistory(h => [...h, { sender: 'voxcore', text: data.insight || data.response || '...' }]);
    if (onDashboardUpdate) onDashboardUpdate(data);
  };

  return (
    <div className="chat-panel-inner">
      <div className="chat-history">
        {history.map((msg, i) => (
          <div key={i} className={msg.sender}>{msg.text}</div>
        ))}
      </div>
      <div className="chat-input-row">
        <input value={input} onChange={e => setInput(e.target.value)} onKeyDown={e => e.key === 'Enter' && sendMessage()} placeholder="Ask a question..." />
        <button onClick={sendMessage}>Send</button>
      </div>
    </div>
  );
}
