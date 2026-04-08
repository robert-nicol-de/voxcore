// Moved from src/components/EnterpriseLayout.tsx as part of enterprise SaaS architecture refactor
import React from "react";
import GlobalHeader from "../components/GlobalHeader";
import SidebarNav from "../components/SidebarNav";
import ActivityPanel from "../components/ActivityPanel";
import "./EnterpriseLayout.css";

const EnterpriseLayout: React.FC<{children: React.ReactNode}> = ({ children }) => (
  <div className="enterprise-layout">
    <GlobalHeader />
    <div className="layout-main">
      <SidebarNav />
      <main className="main-workspace">{children}</main>
    </div>
    <ActivityPanel />
  </div>
);
export default EnterpriseLayout;
