import React from "react";
import GlobalHeader from "./GlobalHeader";
import SidebarNav from "./SidebarNav";
import ActivityPanel from "./ActivityPanel";
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
