import Card from "../components/ui/Card";
import Button, { SecondaryButton } from "../components/ui/Button";

function Feature({ title, text }: { title: string; text: string }) {
  return (
    <div className="p-4 rounded-lg bg-[var(--bg-surface)] border border-[rgba(255,255,255,0.05)]">
      <div className="font-semibold mb-1">{title}</div>
      <div className="text-sm text-[var(--text-secondary)]">{text}</div>
    </div>
  );
}

export default function DevAISection() {
  return (
    <section className="py-24 px-6 bg-[var(--bg-main)] text-[var(--text-primary)]">
      <div className="max-w-5xl mx-auto space-y-12 text-center">
        {/* HEADLINE */}
        <h2 className="text-3xl font-semibold">
          Run AI in production — without losing control
        </h2>
        <p className="text-lg text-[var(--text-secondary)]">
          Build, execute, and govern AI agents with full control, recovery, and auditability.
        </p>
        {/* DEMO */}
        <div className="max-w-2xl mx-auto">
          <Card>
            <p className="text-sm text-[var(--text-secondary)] mb-2">
              Example Execution Flow
            </p>
            <div className="space-y-2 text-sm">
              <div>✔ Insight detected: Revenue drop in EU</div>
              <div>→ Suggested action: Analyze product mix</div>
              <div>→ Agent execution: Running query workflow</div>
              <div>→ Approval required: Finance team</div>
              <div>✔ Action logged and completed</div>
            </div>
          </Card>
        </div>
        {/* PILLARS */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-left">
          <Feature title="Controlled Execution" text="AI takes action only when allowed — never unpredictably." />
          <Feature title="Self-Healing Workflows" text="Failures are detected and corrected automatically." />
          <Feature title="Adaptive Intelligence" text="Learns from previous executions and improves over time." />
          <Feature title="Policy Enforcement" text="Every action is governed, approved, and logged." />
          <Feature title="Full Explainability" text="See exactly what AI did — and why." />
        </div>
        {/* POSITIONING BLOCK */}
        <div className="text-lg font-medium text-[var(--text-secondary)] py-6">
          Most AI tools generate answers.<br />
          <span className="text-[var(--accent-primary)] font-semibold">VoxCore Dev AI executes actions — safely.</span>
        </div>
        {/* CTA */}
        <div className="flex justify-center gap-4">
          <Button>Enable Dev AI</Button>
          <SecondaryButton>View Execution Demo</SecondaryButton>
        </div>
      </div>
    </section>
  );
}
