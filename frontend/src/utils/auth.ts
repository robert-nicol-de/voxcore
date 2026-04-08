
// Utility for logout
export function handleLogout() {
  localStorage.removeItem("auth");
  window.location.href = "/";
}

// Get current user from localStorage (for RBAC)
export function getUser() {
  try {
    const raw = localStorage.getItem("user");
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}