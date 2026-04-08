import type { ReactNode } from "react";
import { Link, NavLink } from "react-router-dom";

const navItems = [
  { to: "/", label: "Home" },
  { to: "/product", label: "Product" },
  { to: "/security", label: "Security" },
  { to: "/pricing", label: "Pricing" },
];

const footerSections = [
  {
    title: "Product",
    links: [
      { to: "/product", label: "Platform" },
      { to: "/security", label: "Governance" },
      { to: "/pricing", label: "Pricing" },
    ],
  },
  {
    title: "Company",
    links: [
      { to: "/", label: "About VoxCore" },
      { to: "/product", label: "Architecture" },
      { to: "/pricing", label: "Contact Sales" },
    ],
  },
  {
    title: "Legal",
    links: [
      { to: "/security", label: "Security" },
      { to: "/security", label: "Compliance" },
      { to: "/pricing", label: "Terms" },
    ],
  },
  {
    title: "Help",
    links: [
      { to: "/login", label: "Login" },
      { to: "/product", label: "Docs" },
      { to: "/security", label: "Support" },
    ],
  },
];

type MarketingLayoutProps = {
  children: ReactNode;
};

export function MarketingLayout({ children }: MarketingLayoutProps) {
  return (
    <div className="min-h-screen bg-[#050816] text-white">
      <div className="absolute inset-x-0 top-0 -z-0 h-[640px] bg-[radial-gradient(circle_at_top,_rgba(56,189,248,0.18),_transparent_38%),radial-gradient(circle_at_20%_20%,_rgba(99,102,241,0.16),_transparent_34%),radial-gradient(circle_at_80%_10%,_rgba(244,114,182,0.12),_transparent_28%),linear-gradient(180deg,_rgba(11,15,25,0.98),_rgba(5,8,22,1))]" />
      <div className="relative z-10">
        <header className="sticky top-0 z-30 border-b border-white/10 bg-[#050816]/80 backdrop-blur-xl">
          <div className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-5 lg:px-8">
            <Link to="/" className="flex items-center gap-3">
              <div className="flex items-center gap-3">
                <img
                  src="/assets/logo-icon.png"
                  alt="VoxCore"
                  className="h-10 w-10"
                />
                <div className="flex flex-col leading-tight">
                  <span className="text-lg font-semibold text-white">VoxCore</span>
                  <span className="text-xs text-sky-400 tracking-wide">
                    GOVERNANCE AND INTELLIGENCE LAYER
                  </span>
                </div>
              </div>
            </Link>

            <nav className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/5 px-2 py-2 lg:flex">
              {navItems.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) =>
                    [
                      "rounded-full px-4 py-2 text-sm font-medium transition",
                      isActive ? "bg-white text-slate-950" : "text-slate-300 hover:bg-white/8 hover:text-white",
                    ].join(" ")
                  }
                >
                  {item.label}
                </NavLink>
              ))}
            </nav>

            <div className="flex items-center gap-3">
              <Link
                to="/login"
                className="rounded-full border border-white/12 px-4 py-2 text-sm font-medium text-slate-200 transition hover:border-white/30 hover:bg-white/6 hover:text-white"
              >
                Login
              </Link>
              <Link
                to="/pricing"
                className="rounded-full bg-white px-5 py-2.5 text-sm font-semibold text-slate-950 transition hover:scale-[1.01] hover:bg-slate-100"
              >
                Deploy VoxCore
              </Link>
            </div>
          </div>
        </header>

        <main>{children}</main>

        <footer className="border-t border-white/10 bg-[#040712]">
          <div className="mx-auto grid w-full max-w-7xl gap-12 px-6 py-16 lg:grid-cols-[1.3fr_repeat(4,minmax(0,1fr))] lg:px-8">
            <div className="max-w-sm">
              <div className="text-lg font-semibold tracking-tight text-white">VoxCore</div>
              <div className="mt-1 text-[11px] font-semibold uppercase tracking-[0.34em] text-sky-300/70">
                AI Data Governance
              </div>
              <h2 className="mt-4 text-2xl font-semibold tracking-tight">
                Govern every AI query before it touches production data.
              </h2>
              <p className="mt-4 text-sm leading-6 text-slate-400">
                Query routing, governance, bounded execution, insight generation, and explainability in one production-grade layer.
              </p>
            </div>

            {footerSections.map((section) => (
              <div key={section.title}>
                <h3 className="text-sm font-semibold text-white">{section.title}</h3>
                <ul className="mt-4 space-y-3 text-sm text-slate-400">
                  {section.links.map((link) => (
                    <li key={`${section.title}-${link.label}`}>
                      <Link className="transition hover:text-white" to={link.to}>
                        {link.label}
                      </Link>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </footer>
      </div>
    </div>
  );
}

export function MarketingContainer({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return <div className={`mx-auto w-full max-w-7xl px-6 lg:px-8 ${className}`}>{children}</div>;
}
