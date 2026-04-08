import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";

const NotFound = () => {
  const navigate = useNavigate();
  useEffect(() => {
    const timer = setTimeout(() => navigate("/", { replace: true }), 1500);
    return () => clearTimeout(timer);
  }, [navigate]);
  return (
    <div className="h-screen flex items-center justify-center text-white text-2xl">
      Page not found — redirecting...
    </div>
  );
};

export default NotFound;
