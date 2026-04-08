import RevenueByRegionWidget from "../widgets/RevenueByRegionWidget";
import RevenueByProductWidget from "../widgets/RevenueByProductWidget";
import RevenueByCategoryWidget from "../widgets/RevenueByCategoryWidget";
import RevenueByCustomerWidget from "../widgets/RevenueByCustomerWidget";
import RevenueAnomaliesWidget from "../widgets/RevenueAnomaliesWidget";

export default function Dashboard() {
  return (
    <div className="space-y-6">
      <section className="rounded-[1.75rem] border border-white/10 bg-[radial-gradient(circle_at_top_left,_rgba(56,189,248,0.16),_transparent_42%),linear-gradient(180deg,_rgba(15,23,42,0.96),_rgba(2,6,23,0.98))] p-8 text-white shadow-[0_24px_80px_rgba(2,8,23,0.55)]">
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-sky-300/80">
          VoxCore Dashboard
        </p>
        <div className="mt-3 flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <h1 className="text-3xl font-semibold tracking-tight">Revenue intelligence patterns</h1>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-300">
              Governed analytics flows through routing, validation, risk scoring, bounded execution,
              and insight generation before it reaches this dashboard. Ranked revenue analytics and
              anomaly analytics now share the same governed production foundation.
            </p>
          </div>
          <div className="rounded-2xl border border-emerald-400/20 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-100">
            Query Router {"->"} Governance {"->"} Execution {"->"} Insight {"->"} Exploration
          </div>
        </div>
      </section>

      <RevenueByRegionWidget />
      <RevenueByProductWidget />
      <RevenueByCategoryWidget />
      <RevenueByCustomerWidget />
      <RevenueAnomaliesWidget />
    </div>
  );
}
