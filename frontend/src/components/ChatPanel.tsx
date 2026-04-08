import { useState } from "react";

export default function ChatPanel() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  async function sendMessage(text) {
    const res = await fetch("/api/conversation/message", {
      method: "POST",
      body: JSON.stringify({ message: text, session_id: "demo" }),
      headers: { "Content-Type": "application/json" }
    });
    const data = await res.json();
    setMessages(prev => [...prev, { user: text, ...data }]);
  }

  return (
    <div className="flex flex-col h-full">
      {/* MESSAGES */}
      <div className="flex-1 overflow-auto p-4 space-y-4">
        {messages.map((m, i) => (
          <div key={i}>
            <div className="text-xs text-gray-500">{m.user}</div>
            <div className="bg-gray-100 p-3 rounded-lg">
              {m.message}
            </div>
          </div>
        ))}
      </div>
      {/* INPUT */}
      <div className="p-3 border-t flex gap-2">
        <input
          className="flex-1 border p-2 rounded"
          value={input}
          onChange={e => setInput(e.target.value)}
        />
        <button
          onClick={() => sendMessage(input)}
          className="bg-black text-white px-4 rounded"
        >
          Send
        </button>
      </div>
    </div>
  );
}
