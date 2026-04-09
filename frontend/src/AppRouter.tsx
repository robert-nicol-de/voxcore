import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Playground from "./pages/Playground";
import Login from "./pages/Login";
import Product from "./pages/Product";
import Security from "./pages/Security";
import Pricing from "./pages/Pricing";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Main site = real app */}
        <Route path="/" element={<Playground />} />
        <Route path="/app" element={<Playground />} />
        <Route path="/playground" element={<Playground />} />

        {/* Marketing / supporting pages */}
        <Route path="/product" element={<Product />} />
        <Route path="/security" element={<Security />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/login" element={<Login />} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
