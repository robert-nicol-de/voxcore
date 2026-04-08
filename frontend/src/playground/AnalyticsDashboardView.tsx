import { BarChart3, TrendingUp, Users, DollarSign } from 'lucide-react';

interface Metric {
  label: string;
  value: string;
  change?: string;
  changeType?: 'positive' | 'negative';
}

interface AnalyticsDashboardViewProps {
  currentDataset?: string;
}

const metricsByDataset: {
  [key: string]: Metric[];
} = {
  users: [
    {
      label: 'Total Active Users',
      value: '247.5K',
      change: '+12.5%',
      changeType: 'positive',
    },
    {
      label: 'Monthly Churn Rate',
      value: '4.2%',
      change: '-0.8%',
      changeType: 'positive',
    },
    {
      label: 'Avg Lifetime Value',
      value: '$2,847',
      change: '+18.3%',
      changeType: 'positive',
    },
    {
      label: 'Premium Adoption',
      value: '34.7%',
      change: '+2.1%',
      changeType: 'positive',
    },
  ],
  sales: [
    {
      label: 'Total Revenue',
      value: '$47.2M',
      change: '+23.5%',
      changeType: 'positive',
    },
    {
      label: 'Avg Deal Size',
      value: '$156K',
      change: '+8.2%',
      changeType: 'positive',
    },
    {
      label: 'Win Rate',
      value: '31.2%',
      change: '+2.4%',
      changeType: 'positive',
    },
    {
      label: 'Pipeline Value',
      value: '$89.5M',
      change: '+35.7%',
      changeType: 'positive',
    },
  ],
  products: [
    {
      label: 'Total SKUs',
      value: '1,247',
      change: '+43',
      changeType: 'positive',
    },
    {
      label: 'Avg Rating',
      value: '4.6/5',
      change: '+0.2',
      changeType: 'positive',
    },
    {
      label: 'Return Rate',
      value: '2.1%',
      change: '-0.5%',
      changeType: 'positive',
    },
    {
      label: 'Stock Health',
      value: '94%',
      change: '+3%',
      changeType: 'positive',
    },
  ],
};

export function AnalyticsDashboardView({
  currentDataset = 'users',
}: AnalyticsDashboardViewProps) {
  const metrics = metricsByDataset[currentDataset] || metricsByDataset.users;

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-4">
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-white/4 border border-white/8">
            <BarChart3 className="w-4 h-4 text-sky-300 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-white">Analytics Dashboard</p>
              <p className="text-xs text-slate-300 mt-1">
                Key metrics for {currentDataset} dataset
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 px-4 py-2">
            {metrics.map((metric, idx) => (
              <div
                key={idx}
                className="rounded-lg border border-slate-500/20 bg-slate-900/40 p-4 hover:bg-slate-900/60 transition"
              >
                <p className="text-xs text-slate-400 font-medium">{metric.label}</p>
                <div className="flex items-end justify-between mt-2 gap-2">
                  <p className="text-lg font-bold text-white">{metric.value}</p>
                  {metric.change && (
                    <div
                      className={`flex items-center gap-1 text-xs font-semibold ${
                        metric.changeType === 'positive'
                          ? 'text-green-300'
                          : 'text-red-300'
                      }`}
                    >
                      <TrendingUp className="w-3 h-3" />
                      {metric.change}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="px-4 py-2">
            <div className="rounded-lg border border-sky-500/20 bg-sky-500/5 p-4">
              <div className="flex items-start gap-3">
                <BarChart3 className="w-5 h-5 text-sky-300 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-sm font-semibold text-sky-100">Pro Tip</p>
                  <p className="text-xs text-sky-200/80 mt-1">
                    Use the SQL Assistant to drill down into any metric and understand the underlying data patterns.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
