export type Insight = {
  insight: string;
  type: string;
  confidence: number;
};

export type Alert = {
  user_id: string;
  insight: Insight;
  status: string;
};

export type InsightsResponse = {
  insights: Insight[];
  alerts: Alert[];
  personalization?: boolean;
};
