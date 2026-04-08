import "@testing-library/jest-dom/vitest";
import React from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import RevenueByRegionWidget from "./RevenueByRegionWidget";

vi.mock("recharts", () => {
  return {
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="responsive-container">{children}</div>
    ),
    BarChart: ({ children, data }: { children: React.ReactNode; data: Array<{ region: string }> }) => (
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
    { region: "US", revenue: 250, share_of_total: 62.5, rank: 1 },
    { region: "EMEA", revenue: 150, share_of_total: 37.5, rank: 2 },
  ],
  summary_card: {
    title: "Revenue by Region",
    metric_label: "Total Revenue",
    metric_value: 400,
    top_region: "US",
    top_region_revenue: 250,
    region_count: 2,
  },
  insight_summary: {
    headline: "US leads regional revenue.",
    narrative: "US contributes the largest share of current governed revenue.",
    highlights: ["Top performer: US", "Lowest performer: EMEA"],
    risk: "Revenue concentration is elevated in the top region.",
  },
  chart_config: {
    data: [
      { region: "US", revenue: 250, share_of_total: 62.5, rank: 1 },
      { region: "EMEA", revenue: 150, share_of_total: 37.5, rank: 2 },
    ],
  },
  governance: {
    risk_score: 14,
    cost_level: "safe",
    timeout_seconds: 15,
    row_limit: 25,
    warnings: [],
  },
};

const detailSuccessResponse = {
  success: true,
  region: "US",
  summary: {
    region: "US",
    revenue: 250,
    record_count: 5,
    average_revenue: 50,
    current_rank: 1,
    delta_to_leader: 0,
  },
  peer_comparison: {
    rows: [
      { region: "US", revenue: 250, rank: 1, is_selected: true },
      { region: "EMEA", revenue: 150, rank: 2, is_selected: false },
    ],
    row_limit: 5,
    leader_region: "US",
  },
  insight_summary: {
    headline: "US is ranked #1 by governed revenue.",
    narrative: "US remains the strongest region in the bounded peer comparison.",
    highlights: ["Average revenue per record: 50.00", "Peer rows returned: 2"],
  },
  chart_config: {
    library: "recharts",
    type: "bar",
    x_key: "region",
    y_key: "revenue",
    highlight_key: "is_selected",
    data: [
      { region: "US", revenue: 250, rank: 1, is_selected: true },
      { region: "EMEA", revenue: 150, rank: 2, is_selected: false },
    ],
  },
  governance: {
    summary_query: {
      risk_score: 10,
      cost_level: "safe",
      row_limit: 1,
      timeout_seconds: 15,
      warnings: [],
    },
    peer_query: {
      risk_score: 12,
      cost_level: "safe",
      row_limit: 5,
      timeout_seconds: 15,
      warnings: [],
    },
  },
  response_meta: {
    execution_time_ms: 12,
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

describe("RevenueByRegionWidget modal behavior", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("shows loading state while governed detail is fetching", async () => {
    const detailDeferred = deferredResponse(detailSuccessResponse);
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-region/US")) {
        return detailDeferred.promise;
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByRegionWidget />);
    await screen.findByText("Revenue by Region");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(screen.getByLabelText("Region detail loading")).toBeInTheDocument();

    detailDeferred.resolve(undefined);
    await screen.findByText("US is ranked #1 by governed revenue.");
  });

  it("shows error state when governed detail fetch fails", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-region/US")) {
        return Promise.resolve({
          ok: false,
          status: 400,
          json: async () => ({ detail: "Governed detail unavailable" }),
        });
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByRegionWidget />);
    await screen.findByText("Revenue by Region");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(await screen.findByText("Governed detail unavailable")).toBeInTheDocument();
  });

  it("shows empty state when governed detail has no peer rows", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-region/US")) {
        return createFetchResponse({
          ...detailSuccessResponse,
          peer_comparison: {
            rows: [],
            row_limit: 5,
            leader_region: "N/A",
          },
          chart_config: {
            ...detailSuccessResponse.chart_config,
            data: [],
          },
        });
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByRegionWidget />);
    await screen.findByText("Revenue by Region");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(
      await screen.findByText("No bounded peer comparison data is available for this region yet."),
    ).toBeInTheDocument();
  });

  it("renders successful governed detail with safe governance metadata only", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-region/US")) {
        return createFetchResponse(detailSuccessResponse);
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByRegionWidget />);
    await screen.findByText("Revenue by Region");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(await screen.findByText("US is ranked #1 by governed revenue.")).toBeInTheDocument();
    expect(screen.getByText("Peer Comparison")).toBeInTheDocument();
    expect(screen.getByText("Governance")).toBeInTheDocument();
    expect(screen.getByText("Risk score: 10")).toBeInTheDocument();
    expect(screen.getByText("Row limit: 1")).toBeInTheDocument();
    expect(screen.queryByText(/SELECT/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/sql/i)).not.toBeInTheDocument();
  });

  it("opens the governed modal for the selected region from chart clicks", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-region/US")) {
        return createFetchResponse(detailSuccessResponse);
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByRegionWidget />);
    await screen.findByText("Revenue by Region");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    await screen.findByText("US is ranked #1 by governed revenue.");
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/analytics/revenue-by-region/US"),
      expect.any(Object),
    );
  });

  it("opens the same governed modal from table row clicks", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-region/EMEA")) {
        return createFetchResponse({
          ...detailSuccessResponse,
          region: "EMEA",
          summary: {
            ...detailSuccessResponse.summary,
            region: "EMEA",
            current_rank: 2,
          },
          insight_summary: {
            ...detailSuccessResponse.insight_summary,
            headline: "EMEA is ranked #2 by governed revenue.",
          },
        });
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByRegionWidget />);
    await screen.findByText("Revenue by Region");

    fireEvent.click(screen.getByTestId("region-row-EMEA"));

    expect(await screen.findByText("EMEA is ranked #2 by governed revenue.")).toBeInTheDocument();
    const modal = screen.getByText("Governed Drill-Down").closest("div");
    expect(modal).toBeTruthy();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/analytics/revenue-by-region/EMEA"),
      expect.any(Object),
    );
  });
});
