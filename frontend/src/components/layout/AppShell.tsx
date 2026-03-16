export default function AppShell({ sidebar, header, children }) {
  return (
    <div className="app-shell">
      {header}
      <div className="layout">
        {sidebar}
        <main>{children}</main>
      </div>
    </div>
  );
}
