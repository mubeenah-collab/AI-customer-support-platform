import React, { useEffect, useState } from 'react';
import { History, MessageSquare, Calendar, ArrowRight, Bot } from 'lucide-react';
import { apiClient } from '../services/apiClient';

interface ChatHistoryItem {
  id: string;
  query: string;
  response: string;
  category?: string;
  created_at: string;
}

export const CustomerHistoryPage: React.FC = () => {
  const [history, setHistory] = useState<ChatHistoryItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchHistory = async () => {
    try {
      const res = await apiClient.get('/chat/history');
      const data = res.data;
      const list = Array.isArray(data) ? data : (data?.messages || data?.items || []);
      setHistory(Array.isArray(list) ? list : []);
    } catch (err) {
      console.error('Failed to fetch chat history:', err);
      setHistory([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
          Support <span className="gradient-text">History</span>
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '0.25rem' }}>
          Review your past AI customer support interactions, query resolution history, and assistant responses.
        </p>
      </div>

      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <History size={20} color="#10b981" /> Interaction Log ({history.length})
        </h3>

        {isLoading ? (
          <p style={{ color: '#94a3b8', fontSize: '0.875rem' }}>Loading conversation history...</p>
        ) : history.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '2.5rem 1rem', color: '#94a3b8' }}>
            <MessageSquare size={40} color="#475569" style={{ margin: '0 auto 1rem' }} />
            <p style={{ fontSize: '0.95rem', fontWeight: 600, color: '#cbd5e1' }}>No Past Sessions Found</p>
            <p style={{ fontSize: '0.875rem', marginTop: '0.25rem' }}>Your past support conversations will appear here once submitted.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {history.map((item, idx) => (
              <div
                key={item.id || idx}
                style={{
                  padding: '1.25rem',
                  borderRadius: '0.75rem',
                  backgroundColor: 'rgba(15, 23, 42, 0.6)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                  <span style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Calendar size={14} /> {new Date(item.created_at || Date.now()).toLocaleString()}
                  </span>
                  {item.category && (
                    <span style={{ fontSize: '0.75rem', padding: '0.2rem 0.5rem', borderRadius: '4px', backgroundColor: 'rgba(255,255,255,0.08)', color: '#cbd5e1' }}>
                      {item.category}
                    </span>
                  )}
                </div>

                <div style={{ marginBottom: '0.75rem' }}>
                  <p style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600, marginBottom: '0.25rem' }}>YOU ASKED:</p>
                  <p style={{ fontSize: '0.95rem', fontWeight: 600, color: '#f8fafc' }}>{item.query}</p>
                </div>

                <div>
                  <p style={{ fontSize: '0.75rem', color: '#10b981', fontWeight: 600, marginBottom: '0.25rem', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                    <Bot size={14} /> AI RESPONSE:
                  </p>
                  <p style={{ fontSize: '0.875rem', color: '#cbd5e1', lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>{item.response}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default CustomerHistoryPage;
