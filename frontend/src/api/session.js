// Centralized session ID getter for VoxCore
export function getSessionId() {
  // Try to get from localStorage, fallback to random
  let sessionId = localStorage.getItem('voxcore_session_id');
  if (!sessionId) {
    sessionId = 'sess_' + Math.random().toString(36).slice(2, 12);
    localStorage.setItem('voxcore_session_id', sessionId);
  }
  return sessionId;
}
