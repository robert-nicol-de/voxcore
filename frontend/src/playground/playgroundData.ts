/**
 * Playground Dataset Metadata
 *
 * This file contains all mock dataset definitions used by the Playground.
 * Separated to keep Playground.tsx clean and focused on composition.
 */

export interface DatasetInsight {
  title: string;
  summary: string;
  stat: string;
}

export interface DatasetMeta {
  title: string;
  description: string;
  emdInsights: DatasetInsight[];
  libraryInsights: string[];
  policies: string[];
}

export type PlaygroundDataset = 'users' | 'sales' | 'orders';

export const datasetMetadata: Record<PlaygroundDataset, DatasetMeta> = {
  users: {
    title: 'Users Dataset',
    description: 'Customer accounts, activity, spend, and lifecycle behavior.',
    emdInsights: [
      {
        title: 'High-value users are clustering in two recent acquisition cohorts',
        summary: 'Recent users from campaign cohorts 24A and 24C show the highest early spend concentration.',
        stat: '+18.4% early spend',
      },
      {
        title: 'Dormancy risk is increasing among long-tail accounts',
        summary: 'A growing slice of users has not returned in the last 45 days.',
        stat: '12.7% dormant',
      },
      {
        title: 'Top 10 users contribute a large share of total spend',
        summary: 'Revenue concentration is high and worth monitoring for churn sensitivity.',
        stat: '34% of spend',
      },
    ],
    libraryInsights: [
      'Dormant-user alert triggered on West region cohort',
      'Spend concentration narrative saved for executive review',
      'Cohort 24A growth note published to insight timeline',
    ],
    policies: [
      'Block raw export of email addresses',
      'Mask personal identifiers for analyst role',
      'Require review for full user table scans',
    ],
  },

  sales: {
    title: 'Sales Dataset',
    description: 'Revenue, product, region, customer, and time-based commercial performance.',
    emdInsights: [
      {
        title: 'Revenue is strongest in the North region',
        summary: 'North continues to lead the revenue mix with stable weekly contribution.',
        stat: '24.7k revenue',
      },
      {
        title: 'Escalated order reviews remain elevated',
        summary: 'Manual escalation volume is still above baseline in two product categories.',
        stat: '+9.2% vs baseline',
      },
      {
        title: 'Premium product mix is improving overall margin',
        summary: 'Higher-priced categories are contributing a larger portion of sales this month.',
        stat: '+4.1 margin pts',
      },
    ],
    libraryInsights: [
      'Regional revenue spike detected in North',
      'Review-status imbalance saved to anomaly feed',
      'Margin narrative published for leadership summary',
    ],
    policies: [
      'Block destructive write operations in sales tables',
      'Limit row count for demo execution',
      'Require bounded aggregations for sandbox access',
    ],
  },

  orders: {
    title: 'Orders Dataset',
    description: 'Order lifecycle, fulfillment state, review status, and operational handling.',
    emdInsights: [
      {
        title: 'Approved orders dominate the current review mix',
        summary: 'Most orders pass review immediately, but escalations still cluster around two workflows.',
        stat: '24.7k approved',
      },
      {
        title: 'Escalation volume is concentrated in one review channel',
        summary: 'One review path is creating a disproportionate share of manual handling.',
        stat: '6.1k escalated',
      },
      {
        title: 'Review backlog remains bounded',
        summary: 'The unresolved review queue is stable and below alert threshold.',
        stat: '4.1k review',
      },
    ],
    libraryInsights: [
      'Review backlog narrative saved',
      'Escalation chain added to anomaly timeline',
      'Approval-rate insight published to operations board',
    ],
    policies: [
      'Prevent unrestricted order detail exports',
      'Block destructive actions on order lifecycle tables',
      'Require aggregation for operational summaries',
    ],
  },
};
