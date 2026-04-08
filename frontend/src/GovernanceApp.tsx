import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import GovernanceDemo from "./pages/GovernanceDemo";

export default function GovernanceApp() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/governance-demo" element={<GovernanceDemo />} />
      </Routes>
    </BrowserRouter>
  );
}
