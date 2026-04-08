
import { useEffect, useState } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import { OnboardingFlow } from "./components/OnboardingFlow";
import { SessionUsageDisplay } from "./components/SessionUsageDisplay";
import Home from "./pages/Home";
import Playground from "./pages/Playground";
import Dashboard from "./pages/Dashboard";
import Policies from "./pages/Policies";
import QueryLogs from "./pages/QueryLogs";
import Settings from "./pages/Settings";

export default function App() {
  const [sessionId, setSessionId] = useState(null);
  const [onboardingComplete, setOnboardingComplete] = useState(false);
  const [loading, setLoading] = useState(true);

  // Initialize session and check onboarding status
  useEffect(() => {
    let sid = localStorage.getItem("voxcore_session_id");
    const onboardingDone = localStorage.getItem("voxcore_onboarding_complete");

    if (!sid) {
      // New session
      sid = Math.random().toString(36).slice(2) + Date.now().toString(36);
      localStorage.setItem("voxcore_session_id", sid);
    }

    setSessionId(sid);
    setOnboardingComplete(onboardingDone === "true");
    setLoading(false);
  }, []);

  const handleOnboardingComplete = async (data) => {
    // Mark onboarding as complete
    localStorage.setItem("voxcore_onboarding_complete", "true");
    setOnboardingComplete(true);

    // Initialize usage tracking in backend
    try {
      await fetch(`/api/onboarding/complete-onboarding`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId }),
      });
    } catch (error) {
      console.error("Failed to complete onboarding", error);
    }
  };

  if (loading) {
    return (
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          height: "100vh",
          backgroundColor: "#0a0a0a",
          color: "#ddd",
          fontFamily: "system-ui, -apple-system, sans-serif",
        }}
      >
        <div style={{ textAlign: "center" }}>
          <div style={{ fontSize: "48px", marginBottom: "16px" }}>🚀</div>
          <p>Initializing VoxQuery...</p>
        </div>
      </div>
    );
  }

  // Show onboarding to new users
  if (!onboardingComplete) {
    return <OnboardingFlow sessionId={sessionId} onComplete={handleOnboardingComplete} />;
  }

  return (
    <Router>
      <div style={{ display: "flex", flexDirection: "column", minHeight: "100vh" }}>
        {/* Header with Session Usage */}
        <div
          style={{
            padding: "12px 24px",
            backgroundColor: "#0a0a0a",
            borderBottom: "1px solid #333",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <h1 style={{ margin: 0, fontSize: "18px", fontWeight: "600" }}>
            🎤 VoxQuery
          </h1>
          {sessionId && <SessionUsageDisplay sessionId={sessionId} />}
        </div>

        {/* Routes */}
        <div style={{ flex: 1 }}>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<Home />} />
            <Route path="/playground" element={<Playground />} />

            {/* Main SaaS app layout with sidebar */}
            <Route path="/app" element={<AppLayout />}>
              <Route index element={<Dashboard />} />
              <Route path="playground" element={<Playground />} />
              <Route path="policies" element={<Policies />} />
              <Route path="logs" element={<QueryLogs />} />
              <Route path="settings" element={<Settings />} />
            </Route>

            {/* Default redirect */}
            <Route path="*" element={<Navigate to="/app" replace />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}
