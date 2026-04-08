import "@testing-library/jest-dom/vitest";
import React from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import RevenueAnomaliesWidget from "./RevenueAnomaliesWidget";

vi.mock("recharts", () => {
  return {
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="responsive-container">{children}</div>
    ),
    BarChart: ({ children, data }: { children: React.ReactNode; data: Array<{ entity?: string; period?: string }> }) => (
      <div data-testid="bar-chart" data-points={data?.length ?? 0}>
        {children}
      </div>
    ),
    CartesianGrid: () => <div data-testid="chart-grid" />,
    XAxis: () => <div data-testid="x-axis" />,
    YAxis: () => <div data-testid="y-axis" />,
    Tooltip: () => <div data-testid="chart-tooltip" />,
    Bar: ({ children }: { children: React.ReactNode }) => <div data-testid="bar-series">{children}</div>,
    Cell: ({
      children,
      onClick,
    }: {
      children?: React.ReactNode;
      onClick?: () => void;
    }) => (
      <button type="button" data-testid="chart-cell" onClick={onClick}>
        {children}
      </button>
    ),
  };
});

const aggregateResponse = {
  success: true,
  data: [
    {
      entity: "Acme Corp",
      current_revenue: 520,
      baseline_revenue: 300,
      delta_amount: 220,
      delta_percent: 73.33,
      anomaly_score: 73.33,
      anomaly_type: "spike",
      severity: "high",
      observation_count: 12,
    },
    {
      entity: "Globex",
      current_revenue: 180,
      baseline_revenue: 260,
      delta_amount: -80,
      delta_percent: -30.77,
      anomaly_score: 30.77,
      anomaly_type: "drop",
      severity: "medium",
      observation_count: 12,
    },
  ],
  summary_card: {
    title: "Revenue Anomalies",
    metric_label: "Detected anomalies",
    metric_value: 2,
    top_entity: "Acme Corp",
    highest_anomaly_score: 73.33,
    high_severity_count: 1,
  },
  insight_summary: {
    headline: "Acme Corp shows the strongest revenue anomaly.",
    narrative: "Acme Corp is showing a spike of 73.33% versus baseline revenue.",
    highlights: ["Top anomaly: Acme Corp (spike)", "High-severity anomalies: 1"],
    risk: "Multiple high-severity revenue anomalies require review.",
  },
  chart_config: {
    library: "recharts",
    type: "bar",
    x_key: "entity",
    y_key: "delta_percent",
    data: [],
  },
  table: {
    columns: [],
    rows: [],
    default_sort: { key: "anomaly_score", direction: "desc" },
  },
  exploration: {
    suggestions: ["Which products contributed to the largest anomaly?"],
  },
  governance: {
    risk_score: 19,
    cost_level: "safe",
    timeout_seconds: 15,
    row_limit: 12,
    warnings: [],
  },
  response_meta: {
    execution_time_ms: 17,
    recommendations: [],
  },
};

const detailSuccessResponse = {
  success: true,
  entity: "Acme Corp",
  summary: {
    entity: "Acme Corp",
    current_revenue: 520,
    baseline_revenue: 300,
    delta_amount: 220,
    delta_percent: 73.33,
    anomaly_score: 73.33,
    anomaly_type: "spike",
    severity: "high",
    observation_count: 12,
  },
  timeline: {
    rows: [
      {
        period: "2026-04-01",
        revenue: 300,
        expected_revenue: 290,
        deviation_percent: 3.45,
        is_anomaly: false,
      },
      {
        period: "2026-04-02",
        revenue: 520,
        expected_revenue: 300,
        deviation_percent: 73.33,
        is_anomaly: true,
      },
    ],
    row_limit: 12,
  },
  insight_summary: {
    headline: "Acme Corp shows a spike versus baseline.",
    narrative: "Current revenue is 520.00 against a baseline of 300.00.",
    highlights: ["Severity: high", "Observation points returned: 2", "Anomalous timeline points: 1"],
  },
  chart_config: {
    library: "recharts",
    type: "bar",
    x_key: "period",
    y_key: "revenue",
    data: [],
  },
  governance: {
    summary_query: {
      risk_score: 11,
      cost_level: "safe",
      row_limit: 1,
      timeout_seconds: 15,
      warnings: [],
    },
    peer_query: {
      risk_score: 13,
      cost_level: "safe",
      row_limit: 12,
      timeout_seconds: 15,
      warnings: [],
    },
  },
  response_meta: {
    execution_time_ms: 19,
    bounded: true,
    aggregate_only: true,
  },
};

function createFetchResponse(body: unknown, ok = true, status = 200) {
  return Promise.resolve({
    ok,
    status,
    json: async () => body,
  });
}

function deferredResponse(body: unknown) {
  let resolve!: (value: unknown) => void;
  const promise = new Promise((resolver) => {
    resolve = resolver;
  });

  return {
    promise: promise.then(() => ({
      ok: true,
      status: 200,
      json: async () => body,
    })),
    resolve,
  };
}

describe("RevenueAnomaliesWidget modal behavior", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("shows loading state while governed detail is fetching", async () => {
    const detailDeferred = deferredResponse(detailSuccessResponse);
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-anomalies/Acme%20Corp")) {
        return detailDeferred.promise;
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueAnomaliesWidget />);
    await screen.findByText("Revenue Anomalies");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(screen.getByLabelText("Anomaly detail loading")).toBeInTheDocument();

    detailDeferred.resolve(undefined);
    await screen.findByText("Acme Corp shows a spike versus baseline.");
  });

  it("shows error state when governed detail fetch fails", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-anomalies/Acme%20Corp")) {
        return Promise.resolve({
          ok: false,
          status: 400,
          json: async () => ({ detail: "Governed anomaly detail unavailable" }),
        });
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueAnomaliesWidget />);
    await screen.findByText("Revenue Anomalies");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(await screen.findByText("Governed anomaly detail unavailable")).toBeInTheDocument();
  });

  it("shows empty state when governed detail has no timeline rows", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-anomalies/Acme%20Corp")) {
        return createFetchResponse({
          ...detailSuccessResponse,
          timeline: {
            rows: [],
            row_limit: 12,
          },
        });
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueAnomaliesWidget />);
    await screen.findByText("Revenue Anomalies");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(
      await screen.findByText("No bounded anomaly timeline data is available for this entity yet."),
    ).toBeInTheDocument();
  });

  it("renders successful governed detail with safe governance metadata only", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-anomalies/Acme%20Corp")) {
        return createFetchResponse(detailSuccessResponse);
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueAnomaliesWidget />);
    await screen.findByText("Revenue Anomalies");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(await screen.findByText("Acme Corp shows a spike versus baseline.")).toBeInTheDocument();
    expect(screen.getByText("Anomaly Timeline")).toBeInTheDocument();
    expect(screen.getByText("Governance")).toBeInTheDocument();
    expect(screen.getByText("Risk score: 11")).toBeInTheDocument();
    expect(screen.getByText("Row limit: 1")).toBeInTheDocument();
    expect(screen.queryByText(/SELECT/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/sql/i)).not.toBeInTheDocument();
  });

  it("opens the governed modal for the selected entity from chart clicks", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-anomalies/Acme%20Corp")) {
        return createFetchResponse(detailSuccessResponse);
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueAnomaliesWidget />);
    await screen.findByText("Revenue Anomalies");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    await screen.findByText("Acme Corp shows a spike versus baseline.");
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/analytics/revenue-anomalies/Acme%20Corp"),
      expect.any(Object),
    );
  });

  it("opens the same governed modal from table row clicks", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-anomalies/Globex")) {
        return createFetchResponse({
          ...detailSuccessResponse,
          entity: "Globex",
          summary: {
            ...detailSuccessResponse.summary,
            entity: "Globex",
            anomaly_type: "drop",
            severity: "medium",
            delta_percent: -30.77,
          },
          insight_summary: {
            ...detailSuccessResponse.insight_summary,
            headline: "Globex shows a drop versus baseline.",
          },
        });
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueAnomaliesWidget />);
    await screen.findByText("Revenue Anomalies");

    fireEvent.click(screen.getByTestId("anomaly-row-Globex"));

    expect(await screen.findByText("Globex shows a drop versus baseline.")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/analytics/revenue-anomalies/Globex"),
      expect.any(Object),
    );
  });
});
