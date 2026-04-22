import React from "react";
import { Link, useLocation } from "react-router-dom";
import { Menu, X } from "lucide-react";

type NavItem = {
  name: string;
  path: string;
};

const navItems: NavItem[] = [
  { name: "Home", path: "/" },
  { name: "Product", path: "/product" },
  { name: "Security", path: "/security" },
  { name: "Pricing", path: "/pricing" },
];

function isActivePath(currentPath: string, itemPath: string): boolean {
  if (itemPath === "/") return currentPath === "/";
  return currentPath === itemPath || currentPath.startsWith(`${itemPath}/`);
}

function getAuthPageLabel(pathname: string): string | null {
  if (pathname === "/login") return "Login";
  if (pathname === "/signup") return "Sign Up";
  if (pathname === "/forgot-password") return "Reset Access";
  if (pathname === "/reset-password") return "Reset Password";
  return null;
}

export default function MarketingNavbar() {
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const authPageLabel = getAuthPageLabel(location.pathname);
  const isAuthPage = Boolean(authPageLabel);

  React.useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-[#060B16]/80 backdrop-blur-xl">
      <div className="mx-auto flex h-24 max-w-7xl items-center justify-between px-6 lg:px-10">
        <Link to="/" className="flex shrink-0 items-center gap-3">
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
              Governance and Intelligence Layer
            </div>
          </div>
        </Link>

        <nav className="hidden lg:flex items-center rounded-full border border-white/10 bg-white/[0.03] p-1.5 shadow-[0_0_0_1px_rgba(255,255,255,0.02)]">
          {navItems.map((item) => {
            const active = isActivePath(location.pathname, item.path);

            return (
              <Link
                key={item.name}
                to={item.path}
                className={
                  active
                    ? "rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 shadow-sm"
                    : "rounded-full px-6 py-3 text-sm font-medium text-slate-300 transition hover:text-white"
                }
              >
                {item.name}
              </Link>
            );
          })}

          {isAuthPage && (
            <span className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 shadow-sm">
              {authPageLabel}
            </span>
          )}
        </nav>

        <div className="hidden lg:flex items-center gap-3">
          <Link
            to="/login"
            className="rounded-full border border-white/15 px-5 py-3 text-sm font-medium text-white transition hover:bg-white/5"
          >
            Login
          </Link>

          <Link
            to="/signup"
            className="rounded-full bg-white px-6 py-3 text-sm font-semibold text-slate-950 shadow-[0_0_24px_rgba(255,255,255,0.12)] transition hover:-translate-y-0.5"
          >
            Deploy VoxCore
          </Link>
        </div>

        <button
          type="button"
          aria-label={mobileOpen ? "Close menu" : "Open menu"}
          onClick={() => setMobileOpen((v) => !v)}
          className="inline-flex h-11 w-11 items-center justify-center rounded-xl border border-white/10 bg-white/[0.03] text-white transition hover:bg-white/[0.06] lg:hidden"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {mobileOpen && (
        <div className="border-t border-white/10 bg-[#060B16]/95 lg:hidden">
          <div className="mx-auto max-w-7xl px-6 py-5">
            <div className="space-y-2">
              {navItems.map((item) => {
                const active = isActivePath(location.pathname, item.path);

                return (
                  <Link
                    key={item.name}
                    to={item.path}
                    className={
                      active
                        ? "block rounded-2xl bg-white px-4 py-3 text-sm font-semibold text-slate-950"
                        : "block rounded-2xl px-4 py-3 text-sm font-medium text-slate-300 transition hover:bg-white/[0.05] hover:text-white"
                    }
                  >
                    {item.name}
                  </Link>
                );
              })}

              {isAuthPage && (
                <div className="rounded-2xl border border-cyan-400/20 bg-cyan-400/[0.06] px-4 py-3 text-sm font-medium text-cyan-200">
                  {authPageLabel}
                </div>
              )}
            </div>

            <div className="mt-5 flex flex-col gap-3">
              <Link
                to="/login"
                className="rounded-full border border-white/15 px-5 py-3 text-center text-sm font-medium text-white transition hover:bg-white/5"
              >
                Login
              </Link>

              <Link
                to="/signup"
                className="rounded-full bg-white px-6 py-3 text-center text-sm font-semibold text-slate-950 shadow-[0_0_24px_rgba(255,255,255,0.12)] transition hover:-translate-y-0.5"
              >
                Deploy VoxCore
              </Link>
            </div>
          </div>
        </div>
      )}
    </header>
  );
}
