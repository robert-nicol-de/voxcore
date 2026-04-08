import { BarChart3, Eye } from 'lucide-react';

interface EMDInsight {
  title: string;
  summary: string;
  stat: string;
}

interface ExplainMyDataViewProps {
  currentDataset?: string;
  activeDataset?: string;
}

const emdInsightsByDataset: {
  [key: string]: EMDInsight[];
} = {
  users: [
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
  sales: [
    {
      title: 'Enterprise segment is driving 67% of total revenue growth',
      summary: 'Mid-market customers remain stable but enterprise wins are outpacing expectations.',
      stat: '+42% YoY',
    },
    {
      title: 'Q1 showed unexpected seasonal strength in EMEA',
      summary: 'Typical Q1 dip was offset by strong European customer renewals.',
      stat: '€4.2M new ACV',
    },
  ],
  products: [
    {
      title: 'Core product line maturity is slowing growth contribution',
      summary: 'Legacy product SKUs now represent 34% of portfolio but only grow 2.5% YoY.',
      stat: '34% of units',
    },
    {
      title: 'New platform launch exceeded adoption projections',
      summary: 'Platform saw 2.1M activations in first quarter vs 1.2M projected.',
      stat: '+75% adoption',
    },
  ],
};

export function ExplainMyDataView({
  currentDataset = 'users',
  activeDataset,
}: ExplainMyDataViewProps) {
  const dataset = activeDataset || currentDataset;
  const insights = emdInsightsByDataset[dataset] || emdInsightsByDataset.users;

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-4">
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-white/4 border border-white/8">
            <Eye className="w-4 h-4 text-sky-300 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-white">Explain My Data</p>
              <p className="text-xs text-slate-300 mt-1">
                AI-discovered patterns in {dataset} dataset
              </p>
            </div>
          </div>

          <div className="space-y-3 px-4 py-2">
            {insights.map((insight, idx) => (
              <div
                key={idx}
                className="rounded-lg border border-sky-500/15 bg-gradient-to-br from-sky-500/5 to-blue-500/5 p-4 hover:border-sky-500/30 transition"
              >
                <div className="flex gap-3">
                  <BarChart3 className="w-5 h-5 text-sky-300 flex-shrink-0 mt-0.5" />
                  <div className="flex-1">
                    <h3 className="text-sm font-semibold text-sky-100">{insight.title}</h3>
                    <p className="text-xs text-slate-300 mt-2">{insight.summary}</p>
                    <div className="mt-3 flex items-center gap-2">
                      <span className="px-3 py-1 rounded-full bg-sky-400/15 text-xs font-semibold text-sky-200 border border-sky-400/30">
                        {insight.stat}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
