import { useState, useEffect } from 'react';
import { apiUrl } from '../lib/api';

export interface PlatformOption {
  code: string;
  name: string;
  tier: number;
  available: boolean;
  description: string;
  doc_url?: string;
}

export interface DataSourceSelectorProps {
  onSelect: (platform: PlatformOption) => void;
  onCancel?: () => void;
}

/**
 * DataSourceSelector
 *
 * Grid-based platform selector for adding new data sources.
 *
 * Displays:
 * - Tier 1: SQL Server, Snowflake, PostgreSQL
 * - Tier 2: BigQuery, Redshift
 * - Tier 3: MySQL, SQLite
 *
 * Shows "Coming Soon" for unavailable platforms.
 */
export default function DataSourceSelector({ onSelect, onCancel }: DataSourceSelectorProps) {
  const [platforms, setPlatforms] = useState<PlatformOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch(apiUrl('/api/v1/datasources/platforms'));
        if (res.ok) {
          const data = (await res.json()) as PlatformOption[];
          setPlatforms(data);
        } else {
          setError('Failed to load platforms');
        }
      } catch (e) {
        setError('Network error loading platforms');
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  const platformsByTier = platforms.reduce(
    (acc, p) => {
      if (!acc[p.tier]) acc[p.tier] = [];
      acc[p.tier].push(p);
      return acc;
    },
    {} as Record<number, PlatformOption[]>,
  );

  const tierLabels: Record<number, string> = {
    1: '🎯 Tier 1: Essential',
    2: '⭐ Tier 2: Enterprise',
    3: '🔧 Tier 3: Additional',
  };

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 28,
        padding: '32px',
        maxWidth: '1000px',
        margin: '0 auto',
      }}
    >
      <div>
        <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: '#fff' }}>
          Select Your Data Platform
        </h2>
        <p style={{ margin: '8px 0 0 0', color: 'var(--platform-muted)', fontSize: 13 }}>
          VoxCore supports multiple data platforms. Choose your database or data warehouse below.
        </p>
      </div>

      {error && (
        <div
          style={{
            background: 'rgba(255,80,80,0.1)',
            border: '1px solid rgba(255,80,80,0.3)',
            borderRadius: 8,
            padding: '12px 16px',
            color: '#ff5050',
            fontSize: 13,
          }}
        >
          {error}
        </div>
      )}

      {loading ? (
        <div style={{ color: 'var(--platform-muted)', textAlign: 'center', padding: '40px' }}>
          Loading platforms…
        </div>
      ) : (
        <>
          {[1, 2, 3].map(tier => {
            const tierPlatforms = platformsByTier[tier] || [];
            if (tierPlatforms.length === 0) return null;

            return (
              <div key={tier}>
                <h3
                  style={{
                    margin: '0 0 12px 0',
                    fontSize: 13,
                    fontWeight: 600,
                    color: 'var(--platform-muted)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.08em',
                  }}
                >
                  {tierLabels[tier]}
                </h3>

                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
                    gap: 14,
                  }}
                >
                  {tierPlatforms.map(platform => (
                    <button
                      key={platform.code}
                      onClick={() => {
                        if (platform.available) {
                          onSelect(platform);
                        }
                      }}
                      disabled={!platform.available}
                      style={{
                        background: platform.available ? 'var(--platform-card-bg)' : 'rgba(0,0,0,0.2)',
                        border:
                          platform.available
                            ? '1px solid var(--platform-border)'
                            : '1px solid rgba(255,255,255,0.1)',
                        borderRadius: 12,
                        padding: '20px',
                        textAlign: 'left',
                        cursor: platform.available ? 'pointer' : 'not-allowed',
                        transition: 'all 0.2s',
                        opacity: platform.available ? 1 : 0.5,
                      }}
                      onMouseEnter={e => {
                        if (platform.available) {
                          const btn = e.currentTarget as HTMLButtonElement;
                          btn.style.background = 'rgba(79, 140, 255, 0.12)';
                          btn.style.borderColor = '#4f8cff';
                        }
                      }}
                      onMouseLeave={e => {
                        const btn = e.currentTarget as HTMLButtonElement;
                        btn.style.background = 'var(--platform-card-bg)';
                        btn.style.borderColor = 'var(--platform-border)';
                      }}
                    >
                      <div
                        style={{
                          fontSize: 16,
                          fontWeight: 700,
                          color: platform.available ? '#e2e8f0' : 'var(--platform-muted)',
                          marginBottom: 8,
                        }}
                      >
                        {platform.name}
                      </div>
                      <div
                        style={{
                          fontSize: 12,
                          color: 'var(--platform-muted)',
                          lineHeight: 1.4,
                          marginBottom: 12,
                        }}
                      >
                        {platform.description}
                      </div>
                      {!platform.available && (
                        <div
                          style={{
                            fontSize: 11,
                            color: '#ffa500',
                            fontWeight: 600,
                            textTransform: 'uppercase',
                            letterSpacing: '0.05em',
                          }}
                        >
                          Coming Soon
                        </div>
                      )}
                      {platform.available && (
                        <div
                          style={{
                            fontSize: 11,
                            color: '#4f8cff',
                            fontWeight: 600,
                          }}
                        >
                          Click to configure →
                        </div>
                      )}
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </>
      )}

      {onCancel && (
        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 10, marginTop: 12 }}>
          <button
            onClick={onCancel}
            style={{
              background: 'transparent',
              border: '1px solid var(--platform-border)',
              color: 'var(--platform-muted)',
              borderRadius: 8,
              padding: '10px 16px',
              fontSize: 13,
              cursor: 'pointer',
              fontWeight: 500,
            }}
          >
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}
