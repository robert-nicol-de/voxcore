import { apiFetch } from "../lib/apiClient";

export const login = (email: string, password: string) => {
  return apiFetch("/api/v1/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
};

// Refresh JWT token using refresh endpoint
export const refreshToken = async () => {
  const token = localStorage.getItem("voxcore_token");
  if (!token) return null;
  try {
    const res = await fetch("/api/v1/auth/refresh", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
    if (!res.ok) throw new Error("Token refresh failed");
    const data = await res.json();
    if (data.token) {
      localStorage.setItem("voxcore_token", data.token);
      return data.token;
    }
    return null;
  } catch (err) {
    // On refresh failure, log out
    localStorage.removeItem("voxcore_token");
    window.location.href = "/login";
    return null;
  }
};
