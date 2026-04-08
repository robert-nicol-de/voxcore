
import AskQueryScreen from "@/pages/AskQueryScreen";
import Button, { SecondaryButton } from "@/components/ui/Button";
import { useNavigate } from "react-router-dom";

export default function LandingDemo() {

  const navigate = useNavigate();
  return (
    <div className="bg-[var(--bg-main)] text-[var(--text-primary)]">
        <h1 className="text-2xl font-semibold tracking-tight">AI Governance Platform</h1>

        {/* HERO */}
        <section className="text-center py-20 space-y-6">
          <h1 className="text-4xl font-bold">
            Stop Unsafe AI Queries on Your Data
          </h1>

          <p className="text-lg text-[var(--text-secondary)]">
            VoxCore protects databases from AI access and explains your data instantly.
          </p>

          <Button onClick={() => {
            if (localStorage.getItem("auth") === "true") {
              navigate("/app");
            } else {
              navigate("/login");
            }
          }}>Try Live Demo</Button>
          <SecondaryButton onClick={() => {
            if (localStorage.getItem("auth") === "true") {
              navigate("/app/dashboard");
            } else {
              navigate("/login");
            }
          }} style={{ marginLeft: 12 }}>View Dashboard</SecondaryButton>
        </section>

        {/* LIVE DEMO */}
        <section className="px-6 pb-20">
          <div className="max-w-6xl mx-auto border border-[var(--border-color)] rounded-xl overflow-hidden">
            <AskQueryScreen />
          </div>
        </section>

        {/* VALUE */}
        <section className="text-center pb-20 space-y-4">
          <h2 className="text-2xl font-semibold">Why VoxCore?</h2>

          <div className="flex justify-center gap-8 text-sm text-[var(--text-secondary)]">
            <p>🔒 Query Firewall</p>
            <p>⚡ AI Insights</p>
            <p>📊 Governance Dashboard</p>
          </div>
        </section>

        {/* CTA */}
        <section className="text-center pb-20">
          <Button onClick={() => {
            if (localStorage.getItem("auth") === "true") {
              navigate("/app");
            } else {
              navigate("/login");
            }
          }}>Start Free</Button>
        </section>
      </div>
  );
}
