import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import './Chat.css';
import ConnectionHeader from './ConnectionHeader';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  text: string;
  timestamp: Date;
  sql?: string;
  results?: any[];
  chart?: any;
}

const Chat = forwardRef((_, ref) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      type: 'assistant',
      text: '👋 Welcome! I\'m your SQL Assistant. Ask me anything about your data in plain English, and I\'ll generate the SQL for you.',
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 120) + 'px';
    }
  }, [input]);

  const handleQuestionSelect = (question: string) => {
    setInput(question);
    if (inputRef.current) {
      inputRef.current.focus();
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.style.height = 'auto';
          inputRef.current.style.height = Math.min(inputRef.current.scrollHeight, 120) + 'px';
        }
      }, 0);
    }
  };

  useImperativeHandle(ref, () => ({
    handleQuestionSelect
  }));

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const questionText = input;
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      text: questionText,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/v1/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: questionText,
          warehouse: 'sqlserver',
          execute: true,
          dry_run: false,
          session_id: 'test'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        const assistantMessage: Message = {
          id: Date.now().toString(),
          type: 'assistant',
          text: data.explanation || '✓ Query executed successfully',
          timestamp: new Date(),
          sql: data.sql,
          results: data.data,
          chart: data.chart,
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || `API error: ${response.status}`);
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        text: '⚠️ Backend connection error. Make sure the API server is running on http://localhost:8000',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const exportToCSV = (results: any[]) => {
    if (!results || results.length === 0) return;
    
    const headers = Object.keys(results[0]);
    const csvContent = [
      headers.join(','),
      ...results.map(row => 
        headers.map(header => {
          const value = row[header];
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return value;
        }).join(',')
      )
    ].join('\n');
    
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/csv;charset=utf-8,' + encodeURIComponent(csvContent));
    element.setAttribute('download', 'results_' + new Date().getTime() + '.csv');
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  const generateReport = (sql: string, results: any[]) => {
    const reportHtml = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>SQL Query Report</title>
        <style>
          * { box-sizing: border-box; }
          body { font-family: 'Segoe UI', sans-serif; margin: 40px; background: #f5f5f5; }
          .report-container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
          h1 { color: #3b82f6; margin-bottom: 10px; }
          .timestamp { color: #666; font-size: 14px; margin-bottom: 30px; }
          .sql-section { background: #f9fafb; padding: 15px; border-radius: 6px; margin: 20px 0; border-left: 4px solid #3b82f6; }
          .sql-label { font-weight: 600; color: #333; margin-bottom: 10px; }
          pre { background: #1e293b; color: #e2e8f0; padding: 15px; border-radius: 4px; overflow-x: auto; }
          code { font-family: 'Courier New', monospace; font-size: 14px; }
          .results-section { margin: 30px 0; }
          table { width: 100%; border-collapse: collapse; margin-top: 15px; }
          th { background: #3b82f6; color: white; padding: 12px; text-align: left; font-weight: 600; }
          td { padding: 10px 12px; border-bottom: 1px solid #e5e7eb; }
          tr:hover { background: #f9fafb; }
          .no-results { color: #999; font-style: italic; padding: 20px; text-align: center; }
          .print-button { background: #3b82f6; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin: 20px 0; font-size: 14px; }
          .print-button:hover { background: #2563eb; }
          h2 { color: #1e293b; margin-top: 30px; margin-bottom: 10px; }
          @media print {
            body { margin: 0; }
            .print-button { display: none; }
          }
        </style>
      </head>
      <body>
        <div class="report-container">
          <h1>📊 SQL Query Report</h1>
          <div class="timestamp">Generated: ${new Date().toLocaleString()}</div>
          
          <div class="sql-section">
            <div class="sql-label">📝 SQL Query</div>
            <pre><code>${sql.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</code></pre>
          </div>
          
          ${results && results.length > 0 ? `
            <div class="results-section">
              <h2>📈 Results (${results.length} rows)</h2>
              <table>
                <thead>
                  <tr>
                    ${Object.keys(results[0]).map(key => `<th>${key}</th>`).join('')}
                  </tr>
                </thead>
                <tbody>
                  ${results.map((row: any) => `
                    <tr>
                      ${Object.values(row).map(val => `<td>${typeof val === 'number' ? val.toLocaleString() : String(val)}</td>`).join('')}
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          ` : '<div class="no-results">No results to display</div>'}
          
          <button class="print-button" onclick="window.print()">🖨️ Print Report</button>
        </div>
      </body>
      </html>
    `;
    
    const reportWindow = window.open('', '_blank');
    reportWindow?.document.write(reportHtml);
    reportWindow?.document.close();
  };

  return (
    <div className="chat">
      <ConnectionHeader />
      <div className="messages">
        {messages.map(msg => (
          <div key={msg.id} className={`message ${msg.type}`}>
            <div className="message-avatar">
              {msg.type === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <p className="message-text">{msg.text}</p>
              
              {msg.sql && (
                <div className="sql-block">
                  <div className="sql-header">📝 Generated SQL</div>
                  <pre><code>{msg.sql || ''}</code></pre>
                  <div className="sql-tabs">
                    <button className="sql-tab" onClick={() => {
                      if (msg.sql) {
                        navigator.clipboard.writeText(msg.sql);
                        alert('✓ SQL copied to clipboard!');
                      }
                    }}>📋 Copy</button>
                    <button className="sql-tab" onClick={() => generateReport(msg.sql || '', msg.results || [])}>📊 Report</button>
                    <button className="sql-tab" onClick={() => {
                      const subject = 'SQL Query Report';
                      const body = encodeURIComponent('Here is the SQL query:\n\n' + (msg.sql || '') + '\n\nResults:\n' + JSON.stringify(msg.results, null, 2));
                      window.location.href = `mailto:?subject=${subject}&body=${body}`;
                    }}>📧 Email</button>
                    <button className="sql-tab" onClick={() => exportToCSV(msg.results || [])}>📥 Export CSV</button>
                  </div>
                </div>
              )}

              {msg.results && (
                <div className="results-block">
                  <div className="results-header">📊 Results ({msg.results.length} rows)</div>
                  <div className="results-table">
                    <table>
                      <thead>
                        <tr>
                          {Object.keys(msg.results[0] || {}).map(key => (
                            <th key={key}>{key}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {msg.results.slice(0, 5).map((row, idx) => (
                          <tr key={idx}>
                            {Object.values(row).map((val: any, i) => (
                              <td key={i}>{String(val)}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                    {msg.results.length > 5 && (
                      <p className="more-rows">... and {msg.results.length - 5} more rows</p>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message assistant">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div className="typing-indicator">
                <span></span><span></span><span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <div className="input-wrapper">
          <textarea
            ref={inputRef}
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything... (e.g., 'Show top 10 customers by revenue')"
            rows={1}
          />
          <button 
            onClick={handleSendMessage}
            disabled={!input.trim() || loading}
            className="send-btn"
          >
            {loading ? '⏳' : '➤'}
          </button>
        </div>
        <p className="input-hint">💡 Tip: Press Enter to send, Shift+Enter for new line</p>
      </div>
    </div>
  );
});

Chat.displayName = 'Chat';
export default Chat;
