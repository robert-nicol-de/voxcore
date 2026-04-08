import { useEffect, useState } from "react";
import { InsightsResponse } from "../types/insight";

export const useInsights = () => {
  const [data, setData] = useState<InsightsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchInsights = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/insights/latest");
      if (!res.ok) throw new Error("Failed to fetch insights");
      const json = await res.json();
      setData(json);
    } catch (e: any) {
      setError(e.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  return { data, loading, error, refresh: fetchInsights };
};
