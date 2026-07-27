import React, { useEffect, useState } from 'react';
import { Ticket, Plus, CheckCircle2, Clock, AlertCircle, HelpCircle } from 'lucide-react';
import { apiClient } from '../services/apiClient';

interface SupportTicketItem {
  id: string;
  subject: string;
  description: string;
  status: 'open' | 'in_progress' | 'resolved' | 'closed';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  category?: string;
  created_at: string;
}

export const CustomerTicketsPage: React.FC = () => {
  const [tickets, setTickets] = useState<SupportTicketItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('medium');
  const [category, setCategory] = useState('technical');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTickets = async () => {
    try {
      const res = await apiClient.get('/tickets');
      const data = res.data;
      setTickets(Array.isArray(data?.items) ? data.items : Array.isArray(data) ? data : []);
    } catch (err) {
      console.error('Failed to fetch support tickets:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  const handleCreateTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!subject.trim() || !description.trim()) return;

    try {
      setIsSubmitting(true);
      setError(null);
      await apiClient.post('/tickets', {
        subject,
        description,
        priority,
        category,
      });
      setShowCreateModal(false);
      setSubject('');
      setDescription('');
      fetchTickets();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to submit support ticket.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStatusBadge = (status: SupportTicketItem['status']) => {
    switch (status) {
      case 'resolved':
      case 'closed':
        return (
          <span style={{ padding: '0.25rem 0.75rem', borderRadius: '9999px', backgroundColor: 'rgba(34, 197, 94, 0.15)', color: '#4ade80', fontSize: '0.75rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.375rem' }}>
            <CheckCircle2 size={14} /> {status.toUpperCase()}
          </span>
        );
      case 'in_progress':
        return (
          <span style={{ padding: '0.25rem 0.75rem', borderRadius: '9999px', backgroundColor: 'rgba(99, 102, 241, 0.15)', color: '#818cf8', fontSize: '0.75rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.375rem' }}>
            <Clock size={14} /> IN PROGRESS
          </span>
        );
      default:
        return (
          <span style={{ padding: '0.25rem 0.75rem', borderRadius: '9999px', backgroundColor: 'rgba(234, 179, 8, 0.15)', color: '#facc15', fontSize: '0.75rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.375rem' }}>
            <HelpCircle size={14} /> OPEN
          </span>
        );
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
            My Support <span className="gradient-text">Tickets</span>
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '0.25rem' }}>
            Track human support escalations and submit technical inquiries directly to engineering support.
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="btn-primary"
          style={{ padding: '0.75rem 1.25rem', gap: '0.5rem' }}
        >
          <Plus size={18} /> Submit Ticket
        </button>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: '#94a3b8' }}>Loading support tickets...</div>
      ) : tickets.length === 0 ? (
        <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
          <Ticket size={48} color="#475569" style={{ margin: '0 auto 1rem' }} />
          <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.5rem' }}>No Active Support Tickets</h3>
          <p style={{ fontSize: '0.875rem' }}>If the AI assistant was unable to resolve your query, submit a ticket for human agent escalation.</p>
        </div>
      ) : (
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {tickets.map((ticket) => (
              <div
                key={ticket.id}
                style={{
                  padding: '1.25rem',
                  borderRadius: '0.75rem',
                  backgroundColor: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc' }}>{ticket.subject}</h4>
                  {renderStatusBadge(ticket.status)}
                </div>
                <p style={{ color: '#cbd5e1', fontSize: '0.875rem', marginBottom: '0.75rem', whiteSpace: 'pre-wrap' }}>
                  {ticket.description}
                </p>
                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: '#64748b' }}>
                  <span>Priority: <strong style={{ color: '#94a3b8', textTransform: 'capitalize' }}>{ticket.priority}</strong></span>
                  <span>Category: <strong style={{ color: '#94a3b8', textTransform: 'capitalize' }}>{ticket.category || 'General'}</strong></span>
                  <span>Submitted: {new Date(ticket.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {showCreateModal && (
        <div style={{ position: 'fixed', inset: 0, backgroundColor: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(4px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, padding: '1rem' }}>
          <div className="glass-card" style={{ width: '100%', maxWidth: '500px', padding: '2rem' }}>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f8fafc', marginBottom: '0.5rem' }}>Submit Support Ticket</h2>
            <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '1.5rem' }}>Escalate your technical inquiry directly to software support engineers.</p>

            {error && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#f87171', padding: '0.75rem', borderRadius: '0.5rem', fontSize: '0.875rem', marginBottom: '1rem' }}>
                <AlertCircle size={16} /> {error}
              </div>
            )}

            <form onSubmit={handleCreateTicket} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.375rem' }}>Subject</label>
                <input
                  type="text"
                  className="input-field"
                  placeholder="e.g. Account billing discrepancy"
                  value={subject}
                  onChange={(e) => setSubject(e.target.value)}
                  required
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.375rem' }}>Category</label>
                <select className="input-field" value={category} onChange={(e) => setCategory(e.target.value)} style={{ backgroundColor: '#0f172a', color: '#f8fafc' }}>
                  <option value="technical">Technical Issue</option>
                  <option value="billing">Billing & Invoicing</option>
                  <option value="account">Account Access</option>
                  <option value="general">General Support</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.375rem' }}>Priority Level</label>
                <select className="input-field" value={priority} onChange={(e) => setPriority(e.target.value)} style={{ backgroundColor: '#0f172a', color: '#f8fafc' }}>
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="urgent">Urgent</option>
                </select>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.375rem' }}>Detailed Description</label>
                <textarea
                  rows={4}
                  className="input-field"
                  placeholder="Describe your issue or question in detail..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  required
                />
              </div>

              <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end', marginTop: '1rem' }}>
                <button type="button" onClick={() => setShowCreateModal(false)} style={{ padding: '0.625rem 1rem', borderRadius: '0.5rem', border: '1px solid rgba(255,255,255,0.1)', background: 'transparent', color: '#94a3b8', cursor: 'pointer' }}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary" disabled={isSubmitting} style={{ padding: '0.625rem 1.25rem', opacity: isSubmitting ? 0.7 : 1 }}>
                  {isSubmitting ? 'Submitting...' : 'Submit Ticket'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
