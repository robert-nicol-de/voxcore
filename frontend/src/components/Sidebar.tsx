        <li>
          <a href="/dashboard/auto" className="block px-4 py-2 hover:bg-blue-100 rounded">
            Auto Dashboard
          </a>
        </li>;
import { NavLink } from "react-router-dom";

export default function Sidebar() {
  return (
    <div className="w-64 bg-[#0B0F1A] border-r border-white/5 p-6">
      <div className="text-lg font-semibold mb-10">VoxCore</div>
      <nav className="space-y-6 text-sm">
        <Group title="Platform">
          <Item to="/app">Dashboard</Item>
          <Item to="/app/playground">Playground</Item>
        </Group>
        <Group title="Governance">
          <Item to="/app/logs">Query Logs</Item>
          <Item to="/app/policies">Policies</Item>
        </Group>
        <Group title="System">
          <Item to="/app/settings">Settings</Item>
          <Item to="/pr-system">🧠 PR Command Center</Item>
        </Group>
      </nav>
    </div>
  );
}

function Group({ title, children }) {
  return (
    <div>
      <div className="text-xs text-gray-500 mb-2 uppercase tracking-wider">
        {title}
      </div>
      <div className="space-y-2">{children}</div>
    </div>
  );
}

function Item({ to, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        `block px-3 py-2 rounded-lg transition ${
          isActive
            ? "bg-blue-600/20 text-blue-400"
            : "text-gray-400 hover:bg-white/5 hover:text-white"
        }`
      }
    >
      {children}
    </NavLink>
  );
}
