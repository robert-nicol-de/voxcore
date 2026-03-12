import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiUrl } from '../../lib/api';

type DrilldownRow = {
  order_id: string;
  order_total: number;
  order_date: string;
  query?: string;
  status?: string;
  risk?: string;
};

type DrilldownResponse = {
  category: string;
  rows: DrilldownRow[];
  total_revenue: number;
};

type Props = {
  category: string;
  dimension?: string;
  onClose: () => void;
};

export default function DrilldownModal({ category, dimension = 'status', onClose }: Props) {
  const navigate = useNavigate();
  const [rows, setRows] = useState<DrilldownRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [totalRevenue, setTotalRevenue] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        const token = localStorage.getItem('voxcore_token') || localStorage.getItem('vox_token') || '';
        const params = new URLSearchParams({ value: category, dimension });
        const res = await fetch(apiUrl(`/api/v1/query/drilldown?${params}`), {
          headers: { Authorization: `Bearer ${token}` },
          signal: controller.signal,
        });

        if (!res.ok) {
          const body = (await res.json().catch(() => ({}))) as { detail?: string };
          throw new Error(body.detail || 'Failed to load drilldown details');
        }

        const data = (await res.json()) as DrilldownResponse;
        setRows(data.rows || []);
        setTotalRevenue(Number(data.total_revenue || 0));
      } catch (e) {
        if (!controller.signal.aborted) {
          setError(e instanceof Error ? e.message : 'Failed to load drilldown data');
          setRows([]);
          setTotalRevenue(0);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    void load();
    return () => controller.abort();
  }, [category, dimension]);

  const modalTitle = useMemo(() => `${category} Revenue Breakdown`, [category]);

  const exploreWithAi = () => {
    const seed = `Analyze ${dimension} = ${category}. Why did this metric change?`;
    localStorage.setItem('voxcore_ai_followup_prompt', seed);
    onClose();
    navigate('/app');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{modalTitle}</h3>
          <button className="secondary-btn" onClick={onClose}>✕</button>
        </div>

        {loading && <div style={{ color: '#9ab3cf', marginBottom: 12 }}>Loading details...</div>}
        {error && <div style={{ color: '#ff7a7a', marginBottom: 12 }}>{error}</div>}

        {!loading && !error && (
          <>
            <table className="drilldown-table">
              <thead>
                <tr>
                  <th>Order ID</th>
                  <th>Total</th>
                  <th>Date</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((r) => (
                  <tr key={r.order_id}>
                    <td>{r.order_id}</td>
                    <td>{r.order_total}</td>
                    <td>{r.order_date}</td>
                  </tr>
                ))}
                {rows.length === 0 && (
                  <tr>
                    <td colSpan={3} style={{ color: '#9ab3cf' }}>No matching records.</td>
                  </tr>
                )}
              </tbody>
            </table>

            <div className="drilldown-footer">
              <div>Total revenue: {totalRevenue}</div>
              <button className="primary-btn" onClick={exploreWithAi}>Explore with AI</button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
