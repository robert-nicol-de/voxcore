export function getSessionId() {
  let sessionId = localStorage.getItem("vox_session_id");
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem("vox_session_id", sessionId);
  }
  return sessionId;
}
