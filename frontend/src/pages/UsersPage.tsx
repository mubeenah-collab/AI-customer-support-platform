import React, { useEffect, useState } from 'react';
import { Users, Shield, CheckCircle2, XCircle, Calendar } from 'lucide-react';
import { apiClient } from '../services/apiClient';

interface UserRecord {
  id: string;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
  created_at?: string;
}

export const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<UserRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  const fetchUsers = async () => {
    try {
      const res = await apiClient.get('/users');
      setUsers(res.data.items || []);
      setTotal(res.data.total || 0);
    } catch (err) {
      console.error('Failed to fetch user accounts:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
          User <span className="gradient-text">Management</span>
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '0.25rem' }}>
          Platform user directory and access control roles.
        </p>
      </div>

      <div className="glass-card" style={{ padding: '1.5rem', overflowX: 'auto' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1rem' }}>
          Registered Accounts ({total})
        </h3>

        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', color: '#64748b' }}>
              <th style={{ padding: '0.75rem 1rem' }}>User</th>
              <th style={{ padding: '0.75rem 1rem' }}>Role</th>
              <th style={{ padding: '0.75rem 1rem' }}>Status</th>
              <th style={{ padding: '0.75rem 1rem' }}>Registered</th>
            </tr>
          </thead>
          <tbody>
            {users.map((usr) => (
              <tr key={usr.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', color: '#e2e8f0' }}>
                <td style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <div style={{ width: '36px', height: '36px', borderRadius: '50%', backgroundColor: '#1e293b', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Users size={18} color="#818cf8" />
                  </div>
                  <div>
                    <p style={{ fontWeight: 600, color: '#f8fafc' }}>{usr.full_name}</p>
                    <p style={{ fontSize: '0.75rem', color: '#64748b' }}>{usr.email}</p>
                  </div>
                </td>
                <td style={{ padding: '1rem' }}>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', padding: '0.25rem 0.625rem', borderRadius: '9999px', backgroundColor: 'rgba(99,102,241,0.15)', color: '#a5b4fc', fontSize: '0.75rem', fontWeight: 600, textTransform: 'capitalize' }}>
                    <Shield size={12} /> {usr.role}
                  </span>
                </td>
                <td style={{ padding: '1rem' }}>
                  {usr.is_active ? (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', color: '#4ade80', fontSize: '0.75rem', fontWeight: 600 }}>
                      <CheckCircle2 size={14} /> Active
                    </span>
                  ) : (
                    <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.25rem', color: '#f87171', fontSize: '0.75rem', fontWeight: 600 }}>
                      <XCircle size={14} /> Inactive
                    </span>
                  )}
                </td>
                <td style={{ padding: '1rem', color: '#94a3b8' }}>
                  {usr.created_at ? new Date(usr.created_at).toLocaleDateString() : 'N/A'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
