import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Home from "./pages/Home";
import Playground from "./pages/Playground";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import ForgotPassword from "./pages/ForgotPassword";
import ResetPassword from "./pages/ResetPassword";
import Product from "./pages/Product";
import Security from "./pages/Security";
import Pricing from "./pages/Pricing";
import HelpCenter from "./pages/HelpCenter";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Marketing homepage */}
        <Route path="/" element={<Home />} />

        {/* App entry points */}
        <Route path="/app" element={<Playground />} />
        <Route path="/playground" element={<Playground />} />

        {/* Marketing / supporting pages */}
        <Route path="/product" element={<Product />} />
        <Route path="/security" element={<Security />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/help" element={<HelpCenter />} />
        <Route path="/login" element={<Login />} />
        <Route path="/contact" element={<Signup />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/forgot-password" element={<ForgotPassword />} />
        <Route path="/reset-password" element={<ResetPassword />} />

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
