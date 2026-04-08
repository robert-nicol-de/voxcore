// frontend/src/api/ApiClient.ts

let retryCount = 0;
const MAX_RETRIES = 3;
const BASE_DELAY = 500; // ms


function getToken() {
  // Always get the latest token
  return localStorage.getItem("voxcore_token") || "";
}

function getTenantHeaders() {
  // Multi-tenant/org/workspace context
  const orgId = localStorage.getItem("voxcore_org_id");
  const workspaceId = localStorage.getItem("voxcore_workspace_id");
  const tenantId = localStorage.getItem("voxcore_tenant_id");
  const headers: Record<string, string> = {};
  if (orgId) headers["X-Org-Id"] = orgId;
  if (workspaceId) headers["X-Workspace-Id"] = workspaceId;
  if (tenantId) headers["X-Tenant-Id"] = tenantId;
  return headers;
}

function handleApiError(err: any) {
  if (err && err.status === 401) {
    // Logout and redirect
    window.location.href = "/login";
    return;
  }
  if (err && err.status === 403) {
    alert("Access Denied");
    return;
  }
  if (err && err.status === 500 && retryCount < MAX_RETRIES) {
    retryCount++;
    const delay = BASE_DELAY * Math.pow(2, retryCount);
    return new Promise((resolve) => setTimeout(resolve, delay)).then(() => {
      // Re-throw to trigger retry in request()
      throw err;
    });
  }
  // Normalize error
  return { error: err?.message || "Unknown error" };
}

export class ApiClient {
  abortControllers: Record<string, AbortController> = {};

  async request(endpoint: string, options: any = {}) {
    retryCount = 0;
    return this._requestWithRetry(endpoint, options);
  }

  async _requestWithRetry(endpoint: string, options: any) {
    const controller = new AbortController();
    if (options.signal) {
      options.signal = options.signal;
    } else {
      options.signal = controller.signal;
    }
    this.abortControllers[endpoint] = controller;

    try {

      const res = await fetch(endpoint, {
        ...options,
        headers: {
          ...(options.headers || {}),
          ...getTenantHeaders(),
          Authorization: `Bearer ${getToken()}`,
          "Content-Type": "application/json",
        },
        signal: options.signal,
      });

      if (!res.ok) {
        let err;
        try {
          err = await res.json();
        } catch {
          err = { status: res.status, message: res.statusText };
        }
        err.status = res.status;
        throw err;
      }
      return res.json();
    } catch (err: any) {
      if (err.name === "AbortError") {
        return { error: "Request cancelled" };
      }
      if (err.status === 500 && retryCount < MAX_RETRIES) {
        retryCount++;
        const delay = BASE_DELAY * Math.pow(2, retryCount);
        await new Promise((resolve) => setTimeout(resolve, delay));
        return this._requestWithRetry(endpoint, options);
      }
      return handleApiError(err);
    }
  }

  cancel(endpoint: string) {
    if (this.abortControllers[endpoint]) {
      this.abortControllers[endpoint].abort();
      delete this.abortControllers[endpoint];
    }
  }
}

export const apiClient = new ApiClient();
