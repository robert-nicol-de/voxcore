import React, { useState } from 'react';
import { sendMessage } from '../api/voxcoreClient';
import { getSessionId } from '../api/session';
import ChartRenderer from '../components/ChartRenderer';
import './Chat.css';

type VoxResponse = {
  message: string;
  data?: any[];
  chart?: any;
  suggestions?: string[];
};

const Chat: React.FC = () => {
  const [messages, setMessages] = useState<VoxResponse[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streamingMessage, setStreamingMessage] = useState<string | null>(null);

  const sessionId = getSessionId();

  function streamText(fullText: string, onUpdate: (text: string) => void) {
    let index = 0;

    const interval = setInterval(() => {
      index += 1;
      onUpdate(fullText.slice(0, index));

      if (index >= fullText.length) {
        clearInterval(interval);
      }
    }, 10);
  }

  async function handleSendMessage(e: React.FormEvent) {
    e.preventDefault();
    if (!input.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const res = await sendMessage({
        sessionId,
        message: input
      });

      setStreamingMessage("");

      streamText(res.message, (partial) => {
        setStreamingMessage(partial);
      });

      setInput('');

      setTimeout(() => {
        setMessages(prev => [...prev, res]);
        setStreamingMessage(null);
      }, res.message.length * 10);

    } catch {
      setError("Something went wrong. Try again.");
      setStreamingMessage(null);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-container">

      {/* INPUT */}
      <form onSubmit={handleSendMessage} className="input-form">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask VoxCore..."
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          {loading ? "Thinking..." : "Ask"}
        </button>
      </form>

      {/* ERROR */}
      {error && <div className="error">{error}</div>}

      {/* MESSAGES */}
      <div className="messages">

        {/* STREAMING MESSAGE */}
        {streamingMessage && (
          <div className="message">
            <div className="narrative">
              {streamingMessage}
              <span className="cursor">|</span>
            </div>
          </div>
        )}

        {/* FINAL MESSAGES */}
        {messages.map((msg, i) => (
          <div key={i} className="message">

            <div className="narrative">
              {msg.message}
            </div>

            {msg.data && (
              <div className="data">
                <pre>{JSON.stringify(msg.data, null, 2)}</pre>
              </div>
            )}

            {msg.chart && (
              <ChartRenderer chart={msg.chart} />
            )}

            {msg.suggestions && (
              <div className="suggestions">
                {msg.suggestions.map((s, i) => (
                  <button key={i} onClick={() => setInput(s)}>
                    {s}
                  </button>
                ))}
              </div>
            )}

          </div>
        ))}

        {/* LOADING */}
        {loading && !streamingMessage && (
          <div className="loading">
            <span className="dot"></span>
            <span className="dot"></span>
            <span className="dot"></span>
          </div>
        )}

      </div>

    </div>
  );
};

export default Chat;