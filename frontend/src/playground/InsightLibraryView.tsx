import { Bookmark, TrendingUp, Clock } from 'lucide-react';

interface LibraryInsight {
  title: string;
  savedAt?: string;
  category?: string;
}

interface InsightLibraryViewProps {
  currentDataset?: string;
}

const insightsByDataset: {
  [key: string]: LibraryInsight[];
} = {
  users: [
    {
      title: 'Dormant-user alert triggered on West region cohort',
      category: 'alert',
      savedAt: '2 hours ago',
    },
    {
      title: 'Spend concentration narrative saved for executive review',
      category: 'narrative',
      savedAt: '5 hours ago',
    },
    {
      title: 'Cohort 24A growth note published to insight timeline',
      category: 'note',
      savedAt: '1 day ago',
    },
  ],
  sales: [
    {
      title: 'Q1 regional performance comparison snapshot',
      category: 'analysis',
      savedAt: '3 days ago',
    },
    {
      title: 'Product cross-sell opportunity matrix',
      category: 'recommendation',
      savedAt: '1 week ago',
    },
  ],
  products: [
    {
      title: 'Product lifecycle maturity heatmap',
      category: 'analysis',
      savedAt: '5 days ago',
    },
  ],
};

export function InsightLibraryView({ currentDataset = 'users' }: InsightLibraryViewProps) {
  const insights = insightsByDataset[currentDataset] || insightsByDataset.users;

  return (
    <div className="h-full flex flex-col overflow-hidden">
      <div className="flex-1 overflow-y-auto">
        <div className="space-y-4">
          <div className="flex items-center gap-3 px-4 py-3 rounded-lg bg-white/4 border border-white/8">
            <Bookmark className="w-4 h-4 text-sky-300 flex-shrink-0" />
            <div className="flex-1">
              <p className="text-sm font-semibold text-white">Saved Insights</p>
              <p className="text-xs text-slate-300 mt-1">
                {insights.length} insights for {currentDataset} dataset
              </p>
            </div>
          </div>

          <div className="space-y-3 px-4 py-2">
            {insights.map((insight, idx) => (
              <div
                key={idx}
                className="rounded-lg border border-slate-500/20 bg-slate-900/40 p-4 hover:bg-slate-900/60 transition cursor-pointer group"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-sm font-medium text-slate-100 group-hover:text-sky-200 transition">
                      {insight.title}
                    </p>
                    {insight.category && (
                      <div className="mt-2 flex items-center gap-2">
                        <span className="px-2 py-1 rounded text-xs font-medium bg-sky-400/10 text-sky-200 border border-sky-400/20">
                          {insight.category}
                        </span>
                      </div>
                    )}
                  </div>
                  <TrendingUp className="w-4 h-4 text-slate-400 flex-shrink-0 mt-1" />
                </div>
                {insight.savedAt && (
                  <div className="flex items-center gap-1 mt-3 text-xs text-slate-400">
                    <Clock className="w-3 h-3" />
                    {insight.savedAt}
                  </div>
                )}
              </div>
            ))}
          </div>

          {insights.length === 0 && (
            <div className="text-center py-12 px-4">
              <Bookmark className="w-8 h-8 text-slate-500 mx-auto mb-3" />
              <p className="text-sm text-slate-300">No insights saved yet</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
