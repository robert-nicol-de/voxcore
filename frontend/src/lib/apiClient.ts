const API_URL = import.meta.env.VITE_API_URL;


function getTenantHeaders() {
  const orgId = localStorage.getItem("voxcore_org_id");
  const workspaceId = localStorage.getItem("voxcore_workspace_id");
  const tenantId = localStorage.getItem("voxcore_tenant_id");
  const headers: Record<string, string> = {};
  if (orgId) headers["X-Org-Id"] = orgId;
  if (workspaceId) headers["X-Workspace-Id"] = workspaceId;
  if (tenantId) headers["X-Tenant-Id"] = tenantId;
  return headers;
}

export const apiFetch = async (
  url: string,
  options: RequestInit = {}
) => {
  const token = localStorage.getItem("voxcore_token");

  const res = await fetch(`${API_URL}${url}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
      ...getTenantHeaders(),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  });

  // ✅ Handle common failures globally
  if (res.status === 401) {
    console.warn("Unauthorized — redirecting to login");
    localStorage.removeItem("voxcore_token");
    window.location.href = "/login";
  }

  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || "API request failed");
  }

  return res.json();
};
