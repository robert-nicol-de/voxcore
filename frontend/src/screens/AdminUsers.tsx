import React, { useState, useEffect } from "react";
import Table from "../components/Table";
import { RoleBadge } from "../components/RoleBadge";

interface CompanyUser {
  id: number;
  email: string;
  name: string;
  role: string;
  status: "active" | "inactive";
  created_at: string;
}

interface AdminUsersProps {
  token: string;
}

export const AdminUsers: React.FC<AdminUsersProps> = ({ token }) => {
  const [users, setUsers] = useState<CompanyUser[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showNewUserForm, setShowNewUserForm] = useState(false);
  const [newUser, setNewUser] = useState({ email: "", name: "", role: "user" });

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    // TODO: Replace with actual API call
    // fetch('/api/users', { headers: { 'Authorization': `Bearer ${token}` } })
    //   .then(res => res.ok ? res.json() : Promise.reject(res))
    //   .then(data => {
    //     setUsers(data);
    //     setLoading(false);
    //   })
    //   .catch(() => {
    //     setError('Failed to load users');
    //     setLoading(false);
    //   });
    
    // Mock data
    setUsers([
      { id: 1, email: "admin@company.com", name: "Admin User", role: "admin", status: "active", created_at: "2026-01-15T10:00:00Z" },
      { id: 2, email: "analyst@company.com", name: "John Analyst", role: "user", status: "active", created_at: "2026-02-20T14:30:00Z" },
      { id: 3, email: "dev@company.com", name: "Developer", role: "developer", status: "active", created_at: "2026-02-28T09:15:00Z" },
    ]);
    setLoading(false);
  }, [token]);

  const handleAddUser = () => {
    if (!newUser.email || !newUser.name) return;
    const user: CompanyUser = {
      id: Math.max(...users.map(u => u.id), 0) + 1,
      ...newUser,
      status: "active",
      created_at: new Date().toISOString(),
    };
    setUsers([...users, user]);
    setNewUser({ email: "", name: "", role: "user" });
    setShowNewUserForm(false);
  };

  const handleDeactivateUser = (id: number) => {
    setUsers(users.map(u => u.id === id ? { ...u, status: "inactive" } : u));
  };

  if (loading) return <SkeletonTable />;
  if (error) return <div className="view-content"><p className="error">{error}</p></div>;

  return (
    <div className="view-content">
      <div className="panel">
        <h2>User Management</h2>
        <p>Manage users in your company</p>
        
        {!showNewUserForm && (
          <button className="btn btn-primary" onClick={() => setShowNewUserForm(true)}>
            + Invite User
          </button>
        )}
        
        {showNewUserForm && (
          <div className="form-section">
            <input
              type="email"
              placeholder="Email"
              value={newUser.email}
              onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
            />
            <input
              type="text"
              placeholder="Full Name"
              value={newUser.name}
              onChange={(e) => setNewUser({ ...newUser, name: e.target.value })}
            />
            <select value={newUser.role} onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}>
              <option value="user">User</option>
              <option value="developer">Developer</option>
              <option value="admin">Admin</option>
            </select>
            <button className="btn btn-primary" onClick={handleAddUser}>Invite</button>
            <button className="btn btn-secondary" onClick={() => setShowNewUserForm(false)}>Cancel</button>
          </div>
        )}
        
        <hr />
        
        <Table data={users} loading={loading} />
      </div>
    </div>
  );
};
