import React, { useState } from "react";
import AppLayout from "./components/AppLayout";
import AskQuery from "./components/AskQuery";
import "./styles/theme.css";

export default function App() {
  const [currentPage, setCurrentPage] = useState("ask-query");

  const renderPage = () => {
    switch (currentPage) {
      case "ask-query":
        return <AskQuery />;
      case "history":
        return <div style={{ color: "var(--text-secondary)" }}>Query History - Coming Soon</div>;
      case "logs":
        return <div style={{ color: "var(--text-secondary)" }}>Governance Logs - Coming Soon</div>;
      case "policies":
        return <div style={{ color: "var(--text-secondary)" }}>Policies - Coming Soon</div>;
      default:
        return <AskQuery />;
    }
  };

  return (
    <AppLayout>
      {renderPage()}
    </AppLayout>
  );
}
