import React, { useState } from 'react';

interface ApiKey {
  id: string;
  name: string;
  key: string;
  created_at: string;
  last_used: string | null;
  active: boolean;
}

interface ApiKeysProps {
  token: string;
}

export const ApiKeys: React.FC<ApiKeysProps> = ({ token }) => {
  const [keys, setKeys] = useState<ApiKey[]>([
    {
      id: '1',
      name: 'VoxAgent Integration',
      key: 'sk_live_•••••••••••••••••••••••••',
      created_at: '2026-02-15T10:30:00Z',
      last_used: '2026-03-09T14:00:00Z',
      active: true,
    },
  ]);
  const [showNewKeyForm, setShowNewKeyForm] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');

  const handleCreateKey = () => {
    if (!newKeyName) return;
    const newKey: ApiKey = {
      id: String(keys.length + 1),
      name: newKeyName,
      key: 'sk_live_' + Math.random().toString(36).substring(2, 15),
      created_at: new Date().toISOString(),
      last_used: null,
      active: true,
    };
    setKeys([...keys, newKey]);
    setNewKeyName('');
    setShowNewKeyForm(false);
  };

  const handleRevokeKey = (id: string) => {
    setKeys(keys.map(k => k.id === id ? { ...k, active: false } : k));
  };

  return (
    <div className="view-content">
      <div className="panel">
        <h2>API Keys</h2>
        <p>Manage API keys for integrations and VoxAgent</p>
        
        {!showNewKeyForm && (
          <button className="btn btn-primary" onClick={() => setShowNewKeyForm(true)}>
            + Generate New Key
          </button>
        )}
        
        {showNewKeyForm && (
          <div className="form-section">
            <input
              type="text"
              placeholder="Key name (e.g., VoxAgent Production)"
              value={newKeyName}
              onChange={(e) => setNewKeyName(e.target.value)}
            />
            <button className="btn btn-primary" onClick={handleCreateKey}>Create Key</button>
            <button className="btn btn-secondary" onClick={() => setShowNewKeyForm(false)}>Cancel</button>
          </div>
        )}
        
        <hr />
        
        <h3>Active Keys</h3>
        {keys.filter(k => k.active).length === 0 ? (
          <p>No active keys</p>
        ) : (
          <table className="keys-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Key</th>
                <th>Created</th>
                <th>Last Used</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {keys.filter(k => k.active).map((k) => (
                <tr key={k.id}>
                  <td>{k.name}</td>
                  <td><code>{k.key}</code></td>
                  <td>{new Date(k.created_at).toLocaleDateString()}</td>
                  <td>{k.last_used ? new Date(k.last_used).toLocaleString() : 'Never'}</td>
                  <td><button className="btn btn-danger btn-small" onClick={() => handleRevokeKey(k.id)}>Revoke</button></td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};
