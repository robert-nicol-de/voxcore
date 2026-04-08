import { useState } from "react";
import { apiClient } from "@/api/ApiClient";

export default function ConversationInput({ sessionId, onMessageSent }: { sessionId: string, onMessageSent?: () => void }) {
  const [message, setMessage] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = async () => {
    if (!message.trim()) return;
    setLoading(true);
    setError(null);
    const res = await apiClient.request("/api/conversation/message", {
      method: "POST",
      body: JSON.stringify({
        message,
        session_id: sessionId,
      }),
    });
    setLoading(false);
    if (res?.error) {
      setError(res.error);
    } else {
      setMessage("");
      onMessageSent?.();
    }
  };

  return (
    <div className="flex flex-col gap-2 mt-4">
      <div className="flex gap-2">
        <input
          value={message}
          onChange={e => setMessage(e.target.value)}
          className="flex-1 p-2 rounded bg-zinc-800 text-white"
          placeholder="Ask a question..."
          onKeyDown={e => { if (e.key === "Enter") sendMessage(); }}
          disabled={loading}
        />
        <button
          onClick={sendMessage}
          className="bg-blue-600 px-4 py-2 rounded"
          disabled={loading || !message.trim()}
        >
          {loading ? "Sending..." : "Send"}
        </button>
      </div>
      {error && <div className="text-red-400 text-xs">{error}</div>}
    </div>
  );
}
