type UserRecord = {
  id: string;
  name: string;
  region: string;
  plan: string;
  orders: number;
  spend: number;
  createdAt: string;
};

type SaleRecord = {
  month: string;
  region: string;
  category: string;
  customer: string;
  revenue: number;
  orders: number;
};

type OrderRecord = {
  id: string;
  customer: string;
  status: string;
  region: string;
  total: number;
  createdAt: string;
};

export const users: UserRecord[] = [
  { id: "USR-1001", name: "Ava Stone", region: "North America", plan: "Enterprise", orders: 18, spend: 18200, createdAt: "2026-03-28" },
  { id: "USR-1002", name: "Noah Patel", region: "EMEA", plan: "Growth", orders: 9, spend: 8400, createdAt: "2026-03-24" },
  { id: "USR-1003", name: "Lena Brooks", region: "LATAM", plan: "Starter", orders: 4, spend: 2950, createdAt: "2026-03-22" },
  { id: "USR-1004", name: "Milo Chen", region: "North America", plan: "Enterprise", orders: 14, spend: 16300, createdAt: "2026-03-19" },
  { id: "USR-1005", name: "Sara Kim", region: "APAC", plan: "Growth", orders: 11, spend: 10150, createdAt: "2026-03-16" },
  { id: "USR-1006", name: "Ethan Cole", region: "EMEA", plan: "Enterprise", orders: 16, spend: 17450, createdAt: "2026-03-11" }
];

export const sales: SaleRecord[] = [
  { month: "Jan", region: "North America", category: "Platform", customer: "Arbor Labs", revenue: 42000, orders: 52 },
  { month: "Jan", region: "EMEA", category: "Security", customer: "Northwind Health", revenue: 29500, orders: 39 },
  { month: "Jan", region: "APAC", category: "Platform", customer: "Pacific Retail", revenue: 18750, orders: 24 },
  { month: "Feb", region: "North America", category: "Security", customer: "Arbor Labs", revenue: 46800, orders: 58 },
  { month: "Feb", region: "EMEA", category: "Platform", customer: "Helios Bank", revenue: 32200, orders: 42 },
  { month: "Feb", region: "LATAM", category: "Analytics", customer: "LatAm Connect", revenue: 14100, orders: 18 },
  { month: "Mar", region: "North America", category: "Analytics", customer: "Delta Grid", revenue: 51200, orders: 61 },
  { month: "Mar", region: "APAC", category: "Security", customer: "Pacific Retail", revenue: 27600, orders: 33 },
  { month: "Mar", region: "EMEA", category: "Platform", customer: "Helios Bank", revenue: 35100, orders: 44 },
  { month: "Apr", region: "North America", category: "Platform", customer: "Delta Grid", revenue: 54800, orders: 66 },
  { month: "Apr", region: "APAC", category: "Analytics", customer: "Orbit Commerce", revenue: 21400, orders: 28 },
  { month: "Apr", region: "LATAM", category: "Security", customer: "LatAm Connect", revenue: 16800, orders: 21 }
];

export const orders: OrderRecord[] = [
  { id: "ORD-4101", customer: "Arbor Labs", status: "Approved", region: "North America", total: 6400, createdAt: "2026-04-02" },
  { id: "ORD-4102", customer: "Northwind Health", status: "Review", region: "EMEA", total: 4100, createdAt: "2026-04-01" },
  { id: "ORD-4103", customer: "Pacific Retail", status: "Approved", region: "APAC", total: 5200, createdAt: "2026-03-31" },
  { id: "ORD-4104", customer: "Delta Grid", status: "Approved", region: "North America", total: 7300, createdAt: "2026-03-30" },
  { id: "ORD-4105", customer: "Orbit Commerce", status: "Escalated", region: "APAC", total: 6100, createdAt: "2026-03-29" },
  { id: "ORD-4106", customer: "Helios Bank", status: "Approved", region: "EMEA", total: 5800, createdAt: "2026-03-28" }
];
