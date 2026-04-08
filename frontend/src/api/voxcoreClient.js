// VoxCore API Client
// Only entry point for conversation/query logic

export async function sendMessage({ sessionId, message }) {
  const res = await fetch("/api/conversation/message", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      session_id: sessionId,
      message
    })
  });

  return res.json();
}
