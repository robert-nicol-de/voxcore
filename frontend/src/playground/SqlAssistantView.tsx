import { MessageCircle, Sparkles } from 'lucide-react';

interface SqlAssistantViewProps {
  query?: string;
  onQueryChange?: (query: string) => void;
}

export function SqlAssistantView({ query = '', onQueryChange }: SqlAssistantViewProps) {
  return (
    <div className="h-full flex flex-col overflow-hidden bg-gradient-to-b from-slate-950 to-slate-900">
      <div className="flex-1 flex flex-col items-center justify-center px-4 py-12">
        <div className="text-center max-w-md space-y-4">
          <div className="flex justify-center mb-6">
            <div className="p-3 rounded-lg bg-sky-500/10 border border-sky-500/30">
              <MessageCircle className="w-8 h-8 text-sky-300" />
            </div>
          </div>

          <h2 className="text-xl font-semibold text-white">SQL Assistant</h2>
          <p className="text-sm text-slate-300">
            Ask questions about your data in natural language. The assistant will generate optimized SQL queries.
          </p>

          <div className="pt-6 space-y-2">
            <div className="p-3 rounded-lg bg-white/4 border border-white/8 cursor-pointer hover:bg-white/6 transition text-left">
              <div className="flex items-start gap-2">
                <Sparkles className="w-4 h-4 text-sky-300 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-sky-100">What are my top products by revenue?</p>
                  <p className="text-xs text-slate-400 mt-1">Generates aggregated sales query</p>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-white/4 border border-white/8 cursor-pointer hover:bg-white/6 transition text-left">
              <div className="flex items-start gap-2">
                <Sparkles className="w-4 h-4 text-sky-300 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-sky-100">How many users churned last quarter?</p>
                  <p className="text-xs text-slate-400 mt-1">Calculates churn metrics</p>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-lg bg-white/4 border border-white/8 cursor-pointer hover:bg-white/6 transition text-left">
              <div className="flex items-start gap-2">
                <Sparkles className="w-4 h-4 text-sky-300 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-semibold text-sky-100">Show me the customer growth trend by region</p>
                  <p className="text-xs text-slate-400 mt-1">Time-series analysis by dimension</p>
                </div>
              </div>
            </div>
          </div>

          <p className="text-xs text-slate-400 pt-6">
            Use the playground query box above to ask your question or write custom SQL directly.
          </p>
        </div>
      </div>
    </div>
  );
}
