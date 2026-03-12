import { useState } from 'react';
import { apiUrl } from '../lib/api';

export interface SnowflakeConnectionSetupProps {
  onConnect: (credentials: Record<string, string>) => void;
  onCancel?: () => void;
}

/**
 * SnowflakeConnectionSetup
 *
 * Form for Snowflake connection configuration.
 *
 * Required fields:
 * - User
 * - Password
 * - Account (Snowflake account ID, e.g., 'xy12345')
 * - Warehouse
 *
 * Optional fields:
 * - Database
 * - Schema
 * - Role
 */
export default function SnowflakeConnectionSetup({ onConnect, onCancel }: SnowflakeConnectionSetupProps) {
  const [user, setUser] = useState('');
  const [password, setPassword] = useState('');
  const [account, setAccount] = useState('');
  const [warehouse, setWarehouse] = useState('');
  const [database, setDatabase] = useState('');
  const [schema, setSchema] = useState('');
  const [role, setRole] = useState('');
  const [testing, setTesting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleTest = async () => {
    if (!user || !password || !account || !warehouse) {
      setError('User, password, account, and warehouse are required');
      return;
    }

    setTesting(true);
    setError(null);

    try {
      const credentials = { user, password, account, warehouse };
      if (database) credentials.database = database;
      if (schema) credentials.schema = schema;
      if (role) credentials.role = role;

      const res = await fetch(apiUrl('/api/v1/datasources/test-connection'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform: 'snowflake', credentials }),
      });

      const data = (await res.json()) as { valid: boolean; error?: string };
      if (data.valid) {
        setSuccess(true);
        setError(null);
      } else {
        setSuccess(false);
        setError(data.error || 'Connection test failed');
      }
    } catch (e) {
      setSuccess(false);
      setError('Network error');
    } finally {
      setTesting(false);
    }
  };

  const handleSubmit = () => {
    if (!user || !password || !account || !warehouse) {
      setError('User, password, account, and warehouse are required');
      return;
    }

    const credentials: Record<string, string> = { user, password, account, warehouse };
    if (database) credentials.database = database;
    if (schema) credentials.schema = schema;
    if (role) credentials.role = role;

    onConnect(credentials);
  };

  const Field = ({
    label,
    value,
    onChange,
    placeholder,
    help,
    required = false,
    type = 'text',
  }: {
    label: string;
    value: string;
    onChange: (v: string) => void;
    placeholder?: string;
    help?: string;
    required?: boolean;
    type?: string;
  }) => (
    <div style={{ marginBottom: 16 }}>
      <label style={{ display: 'block', fontSize: 12, fontWeight: 600, marginBottom: 6, color: '#e2e8f0' }}>
        {label} {required && <span style={{ color: '#ff5050' }}>*</span>}
      </label>
      <input
        type={type}
        value={value}
        onChange={e => onChange(e.target.value)}
        placeholder={placeholder}
        style={{
          width: '100%',
          background: 'rgba(255,255,255,0.07)',
          border: '1px solid var(--platform-border)',
          borderRadius: 8,
          color: '#fff',
          padding: '10px 14px',
          fontSize: 13,
          boxSizing: 'border-box',
          outline: 'none',
        }}
      />
      {help && (
        <div style={{ fontSize: 11, color: 'var(--platform-muted)', marginTop: 4 }}>
          {help}
        </div>
      )}
    </div>
  );

  return (
    <div
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: 20,
        maxWidth: '480px',
        margin: '0 auto',
        padding: '32px',
      }}
    >
      <div>
        <h2 style={{ margin: 0, fontSize: 20, fontWeight: 700, color: '#fff', marginBottom: 4 }}>
          Connect to Snowflake
        </h2>
        <p style={{ margin: 0, color: 'var(--platform-muted)', fontSize: 13 }}>
          Enter your Snowflake credentials to establish a connection.
        </p>
      </div>

      {error && (
        <div
          style={{
            background: 'rgba(255,80,80,0.1)',
            border: '1px solid rgba(255,80,80,0.3)',
            borderRadius: 8,
            padding: '10px 14px',
            color: '#ff5050',
            fontSize: 12,
          }}
        >
          {error}
        </div>
      )}

      {success && (
        <div
          style={{
            background: 'rgba(34,197,94,0.1)',
            border: '1px solid rgba(34,197,94,0.3)',
            borderRadius: 8,
            padding: '10px 14px',
            color: '#22c55e',
            fontSize: 12,
          }}
        >
          ✓ Connection successful
        </div>
      )}

      <div style={{ borderTop: '1px solid var(--platform-border)', paddingTop: 16 }}>
        <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: 'var(--platform-muted)', marginBottom: 12, letterSpacing: '0.08em' }}>
          Required
        </div>

        <Field
          label="User"
          value={user}
          onChange={setUser}
          placeholder="your_username"
          required
          help="Snowflake username"
        />

        <Field
          label="Password"
          value={password}
          onChange={setPassword}
          placeholder="••••••••"
          type="password"
          required
          help="Snowflake password"
        />

        <Field
          label="Account ID"
          value={account}
          onChange={setAccount}
          placeholder="xy12345"
          required
          help='Snowflake account ID (e.g., "ab12345.us-east-1")'
        />

        <Field
          label="Warehouse"
          value={warehouse}
          onChange={setWarehouse}
          placeholder="COMPUTE_WH"
          required
          help="Snowflake warehouse name"
        />
      </div>

      <div style={{ borderTop: '1px solid var(--platform-border)', paddingTop: 16 }}>
        <div style={{ fontSize: 11, fontWeight: 600, textTransform: 'uppercase', color: 'var(--platform-muted)', marginBottom: 12, letterSpacing: '0.08em' }}>
          Optional
        </div>

        <Field
          label="Database"
          value={database}
          onChange={setDatabase}
          placeholder="ANALYTICS"
          help="Default database (optional)"
        />

        <Field
          label="Schema"
          value={schema}
          onChange={setSchema}
          placeholder="PUBLIC"
          help="Default schema (optional)"
        />

        <Field
          label="Role"
          value={role}
          onChange={setRole}
          placeholder="ANALYST"
          help="Snowflake role (optional)"
        />
      </div>

      <div style={{ display: 'flex', gap: 10, marginTop: 8 }}>
        <button
          onClick={handleTest}
          disabled={testing || !user || !password || !account || !warehouse}
          style={{
            flex: 1,
            background: 'rgba(79,140,255,0.18)',
            border: '1px solid rgba(79,140,255,0.3)',
            color: '#4f8cff',
            borderRadius: 8,
            padding: '10px 16px',
            fontSize: 13,
            cursor: 'pointer',
            fontWeight: 600,
            opacity: testing || !user || !password || !account || !warehouse ? 0.5 : 1,
          }}
        >
          {testing ? 'Testing…' : 'Test Connection'}
        </button>

        <button
          onClick={handleSubmit}
          disabled={!user || !password || !account || !warehouse}
          style={{
            flex: 1,
            background: '#4f8cff',
            border: 'none',
            color: '#fff',
            borderRadius: 8,
            padding: '10px 16px',
            fontSize: 13,
            cursor: 'pointer',
            fontWeight: 600,
            opacity: !user || !password || !account || !warehouse ? 0.5 : 1,
          }}
        >
          Connect
        </button>

        {onCancel && (
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
            }}
          >
            Cancel
          </button>
        )}
      </div>
    </div>
  );
}
