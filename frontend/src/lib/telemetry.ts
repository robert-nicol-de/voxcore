import { apiUrl } from "./api";

type TelemetryPayload = {
  event: string;
  dataset?: string;
  metadata?: Record<string, unknown>;
};

export async function trackFeatureEvent(payload: TelemetryPayload): Promise<void> {
  const token = localStorage.getItem("voxcore_token") || localStorage.getItem("vox_token") || "";
  if (!token) {
    return;
  }

  try {
    await fetch(apiUrl("/api/v1/platform/telemetry"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(payload),
    });
  } catch {
    // Telemetry should never interrupt user workflows.
  }
}
