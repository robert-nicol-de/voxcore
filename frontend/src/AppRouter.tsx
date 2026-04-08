import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import Playground from "./pages/Playground";
import Login from "./pages/Login";
import Product from "./pages/Product";
import Security from "./pages/Security";
import Pricing from "./pages/Pricing";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Landing & Marketing */}
        <Route path="/" element={<Home />} />
        <Route path="/product" element={<Product />} />
        <Route path="/security" element={<Security />} />
        <Route path="/pricing" element={<Pricing />} />

        {/* Auth */}
        <Route path="/login" element={<Login />} />

        {/* Main App */}
        <Route path="/playground" element={<Playground />} />
        <Route path="/app" element={<Playground />} />

        {/* Fallback */}
        <Route path="*" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}
