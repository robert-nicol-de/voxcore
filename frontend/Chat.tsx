"""Frontend React component - Chat interface"""

import React, { useState, useRef, useEffect } from 'react';
import './Chat.css';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  sql?: string;
  data?: any[];
  chart?: any;
}

export const Chat: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedWarehouse, setSelectedWarehouse] = useState('snowflake');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim()) return;

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date(),
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Call API
      const response = await fetch('/api/v1/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input,
          warehouse: selectedWarehouse,
          execute: true,
          dry_run: true,
          format: 'table',
        }),
      });

      const result = await response.json();

      // Add assistant message
      const assistantMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: result.explanation || 'Query executed successfully',
        timestamp: new Date(),
        sql: result.sql,
        data: result.data,
        chart: result.chart,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, there was an error processing your request.',
        timestamp: new Date(),
      };
      
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>VoxQuery</h1>
        <select 
          value={selectedWarehouse}
          onChange={(e) => setSelectedWarehouse(e.target.value)}
          className="warehouse-selector"
        >
          <option value="snowflake">Snowflake</option>
          <option value="redshift">AWS Redshift</option>
          <option value="bigquery">Google BigQuery</option>
          <option value="postgres">PostgreSQL</option>
          <option value="sqlserver">SQL Server</option>
        </select>
      </div>

      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.role}`}>
            <div className="message-content">
              <p>{msg.content}</p>
              
              {msg.sql && (
                <div className="sql-display">
                  <details>
                    <summary>Generated SQL</summary>
                    <pre><code>{msg.sql}</code></pre>
                  </details>
                </div>
              )}

              {msg.data && (
                <div className="results-table">
                  <table>
                    <thead>
                      <tr>
                        {Object.keys(msg.data[0]).map(col => (
                          <th key={col}>{col}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {msg.data.slice(0, 10).map((row, idx) => (
                        <tr key={idx}>
                          {Object.values(row).map((val, idx) => (
                            <td key={idx}>{String(val)}</td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {msg.data.length > 10 && (
                    <p className="row-count">Showing 10 of {msg.data.length} rows</p>
                  )}
                </div>
              )}

              {msg.chart && (
                <div className="chart-container">
                  {/* Render Vega-Lite chart here using vega-embed library */}
                  <p>Chart would render here</p>
                </div>
              )}
            </div>
            <span className="timestamp">{msg.timestamp.toLocaleTimeString()}</span>
          </div>
        ))}
        
        {loading && (
          <div className="message assistant">
            <div className="loading">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      <form onSubmit={handleSendMessage} className="input-form">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask a question... e.g., 'Show top 10 clients by revenue'"
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          Send
        </button>
      </form>
    </div>
  );
};

export default Chat;
