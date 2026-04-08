import "@testing-library/jest-dom/vitest";
import React from "react";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import RevenueByCategoryWidget from "./RevenueByCategoryWidget";

vi.mock("recharts", () => {
  return {
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="responsive-container">{children}</div>
    ),
    BarChart: ({ children, data }: { children: React.ReactNode; data: Array<{ category: string }> }) => (
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
    { category: "Enterprise", revenue: 280, share_of_total: 56, rank: 1 },
    { category: "SMB", revenue: 220, share_of_total: 44, rank: 2 },
  ],
  summary_card: {
    title: "Revenue by Category",
    metric_label: "Total Revenue",
    metric_value: 500,
    top_category: "Enterprise",
    top_category_revenue: 280,
    category_count: 2,
  },
  insight_summary: {
    headline: "Enterprise leads category revenue.",
    narrative: "Enterprise contributes the largest share of current governed revenue.",
    highlights: ["Top performer: Enterprise", "Lowest performer: SMB"],
    risk: "Revenue concentration is elevated in the top category.",
  },
  chart_config: {
    data: [
      { category: "Enterprise", revenue: 280, share_of_total: 56, rank: 1 },
      { category: "SMB", revenue: 220, share_of_total: 44, rank: 2 },
    ],
  },
  governance: {
    risk_score: 15,
    cost_level: "safe",
    timeout_seconds: 15,
    row_limit: 25,
    warnings: [],
  },
};

const detailSuccessResponse = {
  success: true,
  category: "Enterprise",
  summary: {
    category: "Enterprise",
    revenue: 280,
    record_count: 7,
    average_revenue: 40,
    current_rank: 1,
    delta_to_leader: 0,
  },
  peer_comparison: {
    rows: [
      { category: "Enterprise", revenue: 280, rank: 1, is_selected: true },
      { category: "SMB", revenue: 220, rank: 2, is_selected: false },
    ],
    row_limit: 5,
    leader_category: "Enterprise",
  },
  insight_summary: {
    headline: "Enterprise is ranked #1 by governed revenue.",
    narrative: "Enterprise remains the strongest category in the bounded peer comparison.",
    highlights: ["Average revenue per record: 40.00", "Peer rows returned: 2"],
  },
  chart_config: {
    library: "recharts",
    type: "bar",
    x_key: "category",
    y_key: "revenue",
    highlight_key: "is_selected",
    data: [
      { category: "Enterprise", revenue: 280, rank: 1, is_selected: true },
      { category: "SMB", revenue: 220, rank: 2, is_selected: false },
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
      risk_score: 13,
      cost_level: "safe",
      row_limit: 5,
      timeout_seconds: 15,
      warnings: [],
    },
  },
  response_meta: {
    execution_time_ms: 16,
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

describe("RevenueByCategoryWidget modal behavior", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("shows loading state while governed detail is fetching", async () => {
    const detailDeferred = deferredResponse(detailSuccessResponse);
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-category/Enterprise")) {
        return detailDeferred.promise;
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByCategoryWidget />);
    await screen.findByText("Revenue by Category");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(screen.getByLabelText("Category detail loading")).toBeInTheDocument();

    detailDeferred.resolve(undefined);
    await screen.findByText("Enterprise is ranked #1 by governed revenue.");
  });

  it("shows error state when governed detail fetch fails", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-category/Enterprise")) {
        return Promise.resolve({
          ok: false,
          status: 400,
          json: async () => ({ detail: "Governed detail unavailable" }),
        });
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByCategoryWidget />);
    await screen.findByText("Revenue by Category");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(await screen.findByText("Governed detail unavailable")).toBeInTheDocument();
  });

  it("shows empty state when governed detail has no peer rows", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-category/Enterprise")) {
        return createFetchResponse({
          ...detailSuccessResponse,
          peer_comparison: {
            rows: [],
            row_limit: 5,
            leader_category: "N/A",
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

    render(<RevenueByCategoryWidget />);
    await screen.findByText("Revenue by Category");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(
      await screen.findByText("No bounded peer comparison data is available for this category yet."),
    ).toBeInTheDocument();
  });

  it("renders successful governed detail with safe governance metadata only", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-category/Enterprise")) {
        return createFetchResponse(detailSuccessResponse);
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByCategoryWidget />);
    await screen.findByText("Revenue by Category");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    expect(await screen.findByText("Enterprise is ranked #1 by governed revenue.")).toBeInTheDocument();
    expect(screen.getByText("Peer Comparison")).toBeInTheDocument();
    expect(screen.getByText("Governance")).toBeInTheDocument();
    expect(screen.getByText("Risk score: 10")).toBeInTheDocument();
    expect(screen.getByText("Row limit: 1")).toBeInTheDocument();
    expect(screen.queryByText(/SELECT/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/sql/i)).not.toBeInTheDocument();
  });

  it("opens the governed modal for the selected category from chart clicks", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-category/Enterprise")) {
        return createFetchResponse(detailSuccessResponse);
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByCategoryWidget />);
    await screen.findByText("Revenue by Category");

    fireEvent.click(screen.getAllByTestId("chart-cell")[0]);

    await screen.findByText("Enterprise is ranked #1 by governed revenue.");
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/analytics/revenue-by-category/Enterprise"),
      expect.any(Object),
    );
  });

  it("opens the same governed modal from table row clicks", async () => {
    const fetchMock = vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.includes("/api/v1/analytics/revenue-by-category/SMB")) {
        return createFetchResponse({
          ...detailSuccessResponse,
          category: "SMB",
          summary: {
            ...detailSuccessResponse.summary,
            category: "SMB",
            current_rank: 2,
          },
          peer_comparison: {
            ...detailSuccessResponse.peer_comparison,
            leader_category: "Enterprise",
            rows: [
              { category: "Enterprise", revenue: 280, rank: 1, is_selected: false },
              { category: "SMB", revenue: 220, rank: 2, is_selected: true },
            ],
          },
          chart_config: {
            ...detailSuccessResponse.chart_config,
            data: [
              { category: "Enterprise", revenue: 280, rank: 1, is_selected: false },
              { category: "SMB", revenue: 220, rank: 2, is_selected: true },
            ],
          },
          insight_summary: {
            ...detailSuccessResponse.insight_summary,
            headline: "SMB is ranked #2 by governed revenue.",
          },
        });
      }
      return createFetchResponse(aggregateResponse);
    });
    vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);

    render(<RevenueByCategoryWidget />);
    await screen.findByText("Revenue by Category");

    fireEvent.click(screen.getByTestId("category-row-SMB"));

    expect(await screen.findByText("SMB is ranked #2 by governed revenue.")).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining("/api/v1/analytics/revenue-by-category/SMB"),
      expect.any(Object),
    );
  });
});
