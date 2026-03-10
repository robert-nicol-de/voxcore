import React, { useState, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import './Chat.css';
import ConnectionHeader from './ConnectionHeader';
import ChartRenderer from './ChartRenderer';
import { ClientDetailsModal } from './ClientDetailsModal';
import { apiUrl, API_BASE_URL } from '../lib/api';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  text: string;
  timestamp: Date;
  sql?: string;
  results?: any[];
  chart?: any;
  column_mapping?: { [key: string]: string };
}

interface EnlargedChart {
  type: string;
  title: string;
  data?: any;
}

interface ClientDetails {
  name: string;
  value: number;
  chartType: string;
  chartTitle: string;
}

interface ChatProps {
  onBackToDashboard?: () => void;
  isPreviewMode?: boolean;
}

const Chat = forwardRef<any, ChatProps>(({ onBackToDashboard, isPreviewMode = false }, ref) => {
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
  const [enlargedChart, setEnlargedChart] = useState<EnlargedChart | null>(null);
  const [clientDetails, setClientDetails] = useState<ClientDetails | null>(null);
  const [isConnected, setIsConnected] = useState(false);
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

  // Check connection status on mount and when it changes
  useEffect(() => {
    const checkConnectionStatus = () => {
      const status = localStorage.getItem('dbConnectionStatus');
      setIsConnected(status === 'connected');
    };

    checkConnectionStatus();

    // Listen for connection status changes
    const handleConnectionChange = () => {
      checkConnectionStatus();
    };

    window.addEventListener('connectionStatusChanged', handleConnectionChange);
    return () => window.removeEventListener('connectionStatusChanged', handleConnectionChange);
  }, []);

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

  const handleChartItemClick = (itemData: any) => {
    setClientDetails({
      name: itemData.name,
      value: itemData.value,
      chartType: itemData.chartType,
      chartTitle: itemData.chartTitle,
    });
  };

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    // Check if database is connected
    const dbConnectionStatus = localStorage.getItem('dbConnectionStatus');
    const selectedDatabase = localStorage.getItem('selectedDatabase');
    
    if (dbConnectionStatus !== 'connected' || !selectedDatabase) {
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        text: '⚠️ Please connect to a database first. Click the "Connect" button in the header to establish a connection.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

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
      const response = await fetch(apiUrl('/api/v1/query'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: questionText,
          warehouse: selectedDatabase,
          execute: true,
          dry_run: false,
          session_id: 'test'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        let messageText = `✓ Query executed successfully\n\n`;
        if (data.generated_sql) {
          messageText += `SQL: ${data.generated_sql}\n`;
        }
        if (data.risk_score !== undefined) {
          messageText += `Risk Score: ${data.risk_score}\n`;
        }
        if (data.execution_time_ms !== undefined) {
          messageText += `Execution Time: ${data.execution_time_ms}ms\n`;
        }
        if (data.rows_returned !== undefined) {
          messageText += `Rows Returned: ${data.rows_returned}\n`;
        }
        
        const assistantMessage: Message = {
          id: Date.now().toString(),
          type: 'assistant',
          text: messageText,
          timestamp: new Date(),
          sql: data.generated_sql || data.final_sql,
          results: data.results,
          chart: data.chart,
          column_mapping: data.column_mapping || {},
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || errorData.error || `API error: ${response.status}`);
      }
    } catch (error) {
      console.error('Error:', error);
      let errorText = `⚠️ Backend connection error. Make sure the API server is running on ${API_BASE_URL}`;
      
      if (error instanceof Error) {
        if (error.name === 'AbortError') {
          errorText = '⏱️ Query timeout - server took too long to respond (10 seconds)';
        } else {
          errorText = `⚠️ Error: ${error.message}`;
        }
      }
      
      const errorMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        text: errorText,
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
    
    const headers = Object.keys(results[0] || {});
    if (headers.length === 0) return;
    
    const csvContent = [
      headers.join(','),
      ...results.map(row => 
        headers.map(header => {
          const value = row?.[header];
          if (value === null || value === undefined) return '';
          if (typeof value === 'string' && (value.includes(',') || value.includes('"'))) {
            return `"${value.replace(/"/g, '""')}"`;
          }
          return String(value);
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
                    ${Object.keys(results[0] || {}).map(key => `<th>${key}</th>`).join('')}
                  </tr>
                </thead>
                <tbody>
                  ${results.map((row: any) => `
                    <tr>
                      ${Object.values(row || {}).map(val => {
                        const displayVal = val === null || val === undefined ? '-' : (typeof val === 'number' ? val.toLocaleString() : String(val));
                        return `<td>${displayVal}</td>`;
                      }).join('')}
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
      {isPreviewMode && (
        <div className="preview-banner">
          Preview Mode — Database connections are disabled.
          <a href="/pricing.html">Subscribe to unlock full access</a>
        </div>
      )}
      <ConnectionHeader onDisconnect={onBackToDashboard} isPreviewMode={isPreviewMode} />
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

              {msg.results && msg.results.length > 0 && (
                <div className="results-block">
                  <div className="results-header">📊 Results ({msg.results.length} rows)</div>
                  <div className="results-table">
                    <table>
                      <thead>
                        <tr>
                          {Object.keys(msg.results[0] || {}).map(key => (
                            <th key={key}>{msg.column_mapping?.[key] || key}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {msg.results.map((row, idx) => (
                          <tr key={idx}>
                            {Object.values(row || {}).map((val: any, i) => (
                              <td key={i}>{val !== null && val !== undefined ? String(val) : '-'}</td>
                            ))}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {msg.chart && (
                <div className="charts-grid-container">
                  <div className="charts-grid">
                    {msg.chart && msg.chart.type === 'bar' && (
                      <div className="chart-grid-item">
                        <div className="chart-grid-header" style={{cursor: 'pointer'}} onClick={() => setEnlargedChart({type: 'bar', title: msg.chart.title, data: msg.chart})}>📊 Bar</div>
                        <ChartRenderer chart={msg.chart} onItemClick={handleChartItemClick} />
                      </div>
                    )}
                    
                    {msg.chart && msg.chart.type === 'bar' && msg.chart.series && msg.chart.series[0] && (
                      <div className="chart-grid-item">
                        <div className="chart-grid-header" style={{cursor: 'pointer'}} onClick={() => setEnlargedChart({type: 'pie', title: 'Proportion', data: {type: 'pie', title: 'Proportion', data: msg.chart.series[0].data.map((val: number, idx: number) => ({value: Number(val) || 0, name: msg.chart.xAxis.data[idx] || `Item ${idx + 1}`}))}})}>🥧 Pie</div>
                        <ChartRenderer chart={{
                          type: 'pie',
                          title: 'Proportion',
                          data: msg.chart.series[0].data.map((val: number, idx: number) => ({
                            value: Number(val) || 0,
                            name: msg.chart.xAxis.data[idx] || `Item ${idx + 1}`
                          }))
                        }} onItemClick={handleChartItemClick} />
                      </div>
                    )}
                    
                    {msg.chart && msg.chart.type === 'bar' && msg.chart.xAxis && msg.chart.series && (
                      <div className="chart-grid-item">
                        <div className="chart-grid-header" style={{cursor: 'pointer'}} onClick={() => setEnlargedChart({type: 'line', title: 'Trend - ' + msg.chart.title, data: {type: 'line', title: 'Trend - ' + msg.chart.title, xAxis: msg.chart.xAxis, yAxis: msg.chart.yAxis, series: msg.chart.series}})}>📈 Line</div>
                        <ChartRenderer chart={{
                          type: 'line',
                          title: 'Trend - ' + msg.chart.title,
                          xAxis: msg.chart.xAxis,
                          yAxis: msg.chart.yAxis,
                          series: msg.chart.series
                        }} onItemClick={handleChartItemClick} />
                      </div>
                    )}
                    
                    {msg.chart && msg.chart.type === 'bar' && msg.chart.xAxis && msg.chart.series && (
                      <div className="chart-grid-item">
                        <div className="chart-grid-header" style={{cursor: 'pointer'}} onClick={() => setEnlargedChart({type: 'bar', title: 'Comparison - ' + msg.chart.title, data: msg.chart})}>📊 Comparison</div>
                        <ChartRenderer chart={{
                          type: 'bar',
                          title: 'Comparison - ' + msg.chart.title,
                          xAxis: msg.chart.xAxis,
                          yAxis: msg.chart.yAxis,
                          series: msg.chart.series
                        }} onItemClick={handleChartItemClick} />
                      </div>
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

      {enlargedChart && (
        <div style={{position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.7)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999}} onClick={() => setEnlargedChart(null)}>
          <div style={{background: 'var(--bg-primary)', borderRadius: '8px', padding: '20px', width: '90%', height: '90%', display: 'flex', flexDirection: 'column', boxShadow: '0 10px 40px rgba(0,0,0,0.3)', overflowY: 'auto'}} onClick={(e) => e.stopPropagation()}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px'}}>
              <h2 style={{margin: 0, color: 'var(--text-primary)'}}>{enlargedChart.title}</h2>
              <button onClick={() => setEnlargedChart(null)} style={{background: 'none', border: 'none', fontSize: '24px', cursor: 'pointer', color: 'var(--text-secondary)'}}>×</button>
            </div>
            <div style={{flex: 1, width: '100%'}}>
              <ChartRenderer chart={enlargedChart.data} onItemClick={handleChartItemClick} />
            </div>
          </div>
        </div>
      )}

      <ClientDetailsModal
        isOpen={!!clientDetails}
        clientName={clientDetails?.name || ''}
        clientValue={clientDetails?.value || 0}
        chartType={clientDetails?.chartType || ''}
        chartTitle={clientDetails?.chartTitle || ''}
        onClose={() => setClientDetails(null)}
      />

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
            disabled={!input.trim() || loading || !isConnected}
            className="send-btn"
            title={!isConnected ? 'Connect to a database first' : ''}
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
