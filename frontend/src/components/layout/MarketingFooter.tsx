import React from "react";
import { Link } from "react-router-dom";

type FooterLinkGroup = {
  title: string;
  links: Array<{
    label: string;
    to: string;
  }>;
};

const footerGroups: FooterLinkGroup[] = [
  {
    title: "Product",
    links: [
      { label: "Platform", to: "/product" },
      { label: "Governance", to: "/security" },
      { label: "Pricing", to: "/pricing" },
    ],
  },
  {
    title: "Company",
    links: [
      { label: "About VoxCore", to: "/" },
      { label: "Architecture", to: "/product" },
      { label: "Contact Sales", to: "/signup" },
    ],
  },
  {
    title: "Legal",
    links: [
      { label: "Security", to: "/security" },
      { label: "Compliance", to: "/security" },
      { label: "Terms", to: "/terms" },
    ],
  },
  {
    title: "Help",
    links: [
      { label: "Login", to: "/login" },
      { label: "Docs", to: "/help" },
      { label: "Support", to: "/help" },
    ],
  },
];

export default function MarketingFooter() {
  return (
    <footer className="border-t border-white/10 bg-[#040914]">
      <div className="mx-auto max-w-7xl px-6 py-16 md:px-10">
        <div className="grid gap-12 lg:grid-cols-[1.2fr_repeat(4,1fr)]">
          <div>
            <Link to="/" className="inline-flex items-center gap-3">
              <img
                src="/assets/voxcore-logo-symbol.svg"
                alt="VoxCore"
                className="h-11 w-11 rounded-xl object-contain"
              />
              <div>
                <div className="text-2xl font-semibold leading-none text-white">
                  VoxCore
                </div>
                <div className="mt-1 text-[11px] uppercase tracking-[0.24em] text-cyan-400">
                  AI Data Governance
                </div>
              </div>
            </Link>

            <p className="mt-8 max-w-sm text-4xl font-semibold leading-tight text-white">
              Govern every AI query before it touches production data.
            </p>

            <p className="mt-6 max-w-md text-base leading-8 text-slate-300">
              Query routing, governance, bounded execution, insight generation,
              and explainability in one production-grade layer.
            </p>
          </div>

          {footerGroups.map((group) => (
            <div key={group.title}>
              <h4 className="text-lg font-semibold text-white">{group.title}</h4>

              <ul className="mt-5 space-y-4">
                {group.links.map((link) => (
                  <li key={link.label}>
                    <Link
                      to={link.to}
                      className="text-slate-300 transition hover:text-white"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-14 flex flex-col gap-4 border-t border-white/10 pt-6 text-sm text-slate-500 md:flex-row md:items-center md:justify-between">
          <p>© {new Date().getFullYear()} VoxCore. All rights reserved.</p>

          <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
            <Link to="/privacy" className="transition hover:text-white">
              Privacy Policy
            </Link>
            <Link to="/terms" className="transition hover:text-white">
              Terms of Service
            </Link>
            <Link to="/help" className="transition hover:text-white">
              Help
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
