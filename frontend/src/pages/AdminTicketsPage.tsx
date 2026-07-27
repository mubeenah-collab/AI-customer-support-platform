import React, { useEffect, useState } from 'react';
import { Ticket, Filter, RefreshCw, CheckCircle2 } from 'lucide-react';
import { apiClient } from '../services/apiClient';

interface TicketItem {
  id: string;
  user_id: string;
  subject: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category?: string;
  created_at: string;
}

export const AdminTicketsPage: React.FC = () => {
  const [tickets, setTickets] = useState<TicketItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const fetchTickets = async () => {
    try {
      setIsLoading(true);
      const url = statusFilter !== 'all' ? `/tickets?status=${statusFilter}` : '/tickets';
      const res = await apiClient.get(url);
      const data = res.data;
      setTickets(Array.isArray(data?.items) ? data.items : Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to fetch admin tickets queue:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, [statusFilter]);

  const handleUpdateStatus = async (ticketId: string, newStatus: string) => {
    try {
      await apiClient.patch(`/tickets/${ticketId}`, { status: newStatus });
      fetchTickets();
    } catch (err) {
      alert('Failed to update ticket status.');
    }
  };

  const getPriorityBadgeStyle = (priority: string) => {
    switch (priority) {
      case 'urgent':
        return { bg: 'rgba(239, 68, 68, 0.15)', color: '#f87171' };
      case 'high':
        return { bg: 'rgba(249, 115, 22, 0.15)', color: '#fb923c' };
      case 'medium':
        return { bg: 'rgba(234, 179, 8, 0.15)', color: '#facc15' };
      default:
        return { bg: 'rgba(148, 163, 184, 0.15)', color: '#cbd5e1' };
    }
  };

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
            Support Ticket <span className="gradient-text">Queue</span>
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '0.25rem' }}>
            Manage customer support escalations, assign priorities, and update ticket lifecycle states.
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'rgba(15, 23, 42, 0.6)', padding: '0.5rem 0.75rem', borderRadius: '0.5rem', border: '1px solid rgba(255,255,255,0.08)' }}>
            <Filter size={16} color="#64748b" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              style={{ background: 'transparent', border: 'none', color: '#f8fafc', fontSize: '0.875rem', cursor: 'pointer', outline: 'none' }}
            >
              <option value="all" style={{ backgroundColor: '#0f172a' }}>All Statuses</option>
              <option value="open" style={{ backgroundColor: '#0f172a' }}>Open</option>
              <option value="in_progress" style={{ backgroundColor: '#0f172a' }}>In Progress</option>
              <option value="resolved" style={{ backgroundColor: '#0f172a' }}>Resolved</option>
              <option value="closed" style={{ backgroundColor: '#0f172a' }}>Closed</option>
            </select>
          </div>

          <button onClick={fetchTickets} style={{ padding: '0.5rem', borderRadius: '0.5rem', border: '1px solid rgba(255,255,255,0.1)', background: 'transparent', color: '#94a3b8', cursor: 'pointer' }} title="Refresh Queue">
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>Loading support ticket queue...</div>
      ) : tickets.length === 0 ? (
        <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
          <Ticket size={48} color="#475569" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.5rem' }}>Ticket Queue Clear</h3>
          <p style={{ fontSize: '0.875rem' }}>No customer tickets match the selected status filter.</p>
        </div>
      ) : (
        <div className="glass-card" style={{ padding: '1.5rem', overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', color: '#64748b' }}>
                <th style={{ padding: '0.75rem 1rem' }}>Subject & User</th>
                <th style={{ padding: '0.75rem 1rem' }}>Priority</th>
                <th style={{ padding: '0.75rem 1rem' }}>Category</th>
                <th style={{ padding: '0.75rem 1rem' }}>Status</th>
                <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Update Lifecycle</th>
              </tr>
            </thead>
            <tbody>
              {tickets.map((t) => {
                const priorityBadge = getPriorityBadgeStyle(t.priority);
                return (
                  <tr key={t.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', color: '#e2e8f0' }}>
                    <td style={{ padding: '1rem' }}>
                      <p style={{ fontWeight: 600, color: '#f8fafc', marginBottom: '0.25rem' }}>{t.subject}</p>
                      <p style={{ fontSize: '0.75rem', color: '#64748b' }}>User ID: {t.user_id}</p>
                    </td>
                    <td style={{ padding: '1rem' }}>
                      <span style={{ padding: '0.25rem 0.625rem', borderRadius: '9999px', backgroundColor: priorityBadge.bg, color: priorityBadge.color, fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase' }}>
                        {t.priority}
                      </span>
                    </td>
                    <td style={{ padding: '1rem', color: '#94a3b8', textTransform: 'capitalize' }}>{t.category || 'General'}</td>
                    <td style={{ padding: '1rem', textTransform: 'capitalize', fontWeight: 600, color: t.status === 'resolved' ? '#4ade80' : '#facc15' }}>
                      {t.status.replace('_', ' ')}
                    </td>
                    <td style={{ padding: '1rem', textAlign: 'right' }}>
                      <select
                        value={t.status}
                        onChange={(e) => handleUpdateStatus(t.id, e.target.value)}
                        style={{ backgroundColor: '#0f172a', color: '#f8fafc', padding: '0.375rem 0.625rem', borderRadius: '0.375rem', border: '1px solid rgba(255,255,255,0.1)', fontSize: '0.75rem', cursor: 'pointer' }}
                      >
                        <option value="open">Open</option>
                        <option value="in_progress">In Progress</option>
                        <option value="resolved">Resolved</option>
                        <option value="closed">Closed</option>
                      </select>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
