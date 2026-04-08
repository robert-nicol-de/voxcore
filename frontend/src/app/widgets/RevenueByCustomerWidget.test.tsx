import "@testing-library/jest-dom/vitest";
import React from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import RevenueByCustomerWidget from "./RevenueByCustomerWidget";

vi.mock("recharts", () => {
  return {
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="responsive-container">{children}</div>
    ),
    BarChart: ({ children, data }: { children: React.ReactNode; data: Array<{ customer: string }> }) => (
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
    { customer: "Acme Corp", revenue: 360, share_of_total: 60, rank: 1 },
    { customer: "Globex", revenue: 240, share_of_total: 40, rank: 2 },
  ],
  summary_card: {
    title: "Revenue by Customer",
    metric_label: "Total Revenue",
    metric_value: 600,
    top_customer: "Acme Corp",
    top_customer_revenue: 360,
    customer_count: 2,
  },
  insight_summary: {
    headline: "Acme Corp leads customer revenue.",
    narrative: "Acme Corp contributes the largest share of current governed revenue.",
    highlights: ["Top performer: Acme Corp", "Lowest performer: Globex"],
    risk: "Revenue concentration is elevated in the top customer.",
  },
  chart_config: {
    library: "recharts",
    type: "bar",
    x_key: "customer",
    y_key: "revenue",
    series: [{ data_key: "revenue", name: "Revenue", fill: "#8b5cf6" }],
    data: [
      { customer: "Acme Corp", revenue: 360, share_of_total: 60, rank: 1 },
      { customer: "Globex", revenue: 240, share_of_total: 40, rank: 2 },
    ],
  },
  table: {
    columns: [],
    rows: [],
    default_sort: { key: "revenue", direction: "desc" },
  },
  exploration: {
    suggestions: ["Which products are driving the top customer?"],
  },
  governance: {
    risk_score: 17,
    cost_level: "safe",
    timeout_seconds: 15,
    row_limit: 25,
    warnings: [],
  },
  response_meta: {
    execution_time_ms: 14,
    recommendations: [],
  },
};

const detailSuccessResponse = {
  success: true,
  customer: "Acme Corp",
  summary: {
    customer: "Acme Corp",
    revenue: 360,
    record_count: 9,
    average_revenue: 40,
    current_rank: 1,
    delta_to_leader: 0,
  },
  peer_comparison: {
    rows: [
      { customer: "Acme Corp", revenue: 360, rank: 1, is_selected: true },
      { customer: "Globex", revenue: 240, rank: 2, is_selected: false },
    ],
    row_limit: 5,
    leader_customer: "Acme Corp",
  },
  insight_summary: {
    headline: "Acme Corp is ranked #1 by governed revenue.",
    narrative: "Acme Corp remains the strongest customer in the bounded peer comparison.",
    highlights: ["Average revenue per record: 40.00", "Peer rows returned: 2"],
  },
  chart_config: {
    library: "recharts",
    type: "bar",
    x_key: "customer",
    y_key: "revenue",
    highlight_key: "is_selected",
    data: [
      { customer: "Acme Corp", revenue: 360, rank: 1, is_selected: true },
      { customer: "Globex", revenue: 240, rank: 2, is_selected: false },
    ],
  },
  governance: {
    summary_query: {
      risk_score: 12,
      cost_level: "safe",
      row_limit: 1,
      timeout_seconds: 15,
      warnings: [],
    },
    peer_query: {
      risk_score: 15,
      cost_level: "safe",
      row_limit: 5,
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

describe("RevenueByCustomerWidget modal behavior", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("shows loading state while governed detail is fetching", async () => {
    const detailDeferred = deferredResponse(detailSuccessResponse);
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-customer/Acme%20Corp")) {
        return detailDeferred.promise;
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByCustomerWidget />);
    await screen.findByText("Revenue by Customer");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(screen.getByLabelText("Customer detail loading")).toBeInTheDocument();

    detailDeferred.resolve(undefined);
    await screen.findByText("Acme Corp is ranked #1 by governed revenue.");
  });

  it("shows error state when governed detail fetch fails", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-customer/Acme%20Corp")) {
        return Promise.resolve({
          ok: false,
          status: 400,
          json: async () => ({ detail: "Governed detail unavailable" }),
        });
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByCustomerWidget />);
    await screen.findByText("Revenue by Customer");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(await screen.findByText("Governed detail unavailable")).toBeInTheDocument();
  });

  it("shows empty state when governed detail has no peer rows", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-customer/Acme%20Corp")) {
        return createFetchResponse({
          ...detailSuccessResponse,
          peer_comparison: {
            rows: [],
            row_limit: 5,
            leader_customer: "N/A",
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

    render(<RevenueByCustomerWidget />);
    await screen.findByText("Revenue by Customer");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(
      await screen.findByText("No bounded peer comparison data is available for this customer yet."),
    ).toBeInTheDocument();
  });

  it("renders successful governed detail with safe governance metadata only", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-customer/Acme%20Corp")) {
        return createFetchResponse(detailSuccessResponse);
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByCustomerWidget />);
    await screen.findByText("Revenue by Customer");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(await screen.findByText("Acme Corp is ranked #1 by governed revenue.")).toBeInTheDocument();
    expect(screen.getByText("Peer Comparison")).toBeInTheDocument();
    expect(screen.getByText("Governance")).toBeInTheDocument();
    expect(screen.getByText("Risk score: 12")).toBeInTheDocument();
    expect(screen.getByText("Row limit: 1")).toBeInTheDocument();
    expect(screen.queryByText(/SELECT/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/sql/i)).not.toBeInTheDocument();
  });

  it("opens the governed modal for the selected customer from chart clicks", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-customer/Acme%20Corp")) {
        return createFetchResponse(detailSuccessResponse);
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByCustomerWidget />);
    await screen.findByText("Revenue by Customer");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    await screen.findByText("Acme Corp is ranked #1 by governed revenue.");
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/analytics/revenue-by-customer/Acme%20Corp"),
      expect.any(Object),
    );
  });

  it("opens the same governed modal from table row clicks", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-customer/Globex")) {
        return createFetchResponse({
          ...detailSuccessResponse,
          customer: "Globex",
          summary: {
            ...detailSuccessResponse.summary,
            customer: "Globex",
            current_rank: 2,
          },
          peer_comparison: {
            ...detailSuccessResponse.peer_comparison,
            leader_customer: "Acme Corp",
            rows: [
              { customer: "Acme Corp", revenue: 360, rank: 1, is_selected: false },
              { customer: "Globex", revenue: 240, rank: 2, is_selected: true },
            ],
          },
          chart_config: {
            ...detailSuccessResponse.chart_config,
            data: [
              { customer: "Acme Corp", revenue: 360, rank: 1, is_selected: false },
              { customer: "Globex", revenue: 240, rank: 2, is_selected: true },
            ],
          },
          insight_summary: {
            ...detailSuccessResponse.insight_summary,
            headline: "Globex is ranked #2 by governed revenue.",
          },
        });
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByCustomerWidget />);
    await screen.findByText("Revenue by Customer");

    fireEvent.click(screen.getByTestId("customer-row-Globex"));

    expect(await screen.findByText("Globex is ranked #2 by governed revenue.")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/analytics/revenue-by-customer/Globex"),
      expect.any(Object),
    );
  });
});
