import React from 'react';
import { MessageSquare, Plus, Trash2 } from 'lucide-react';

export interface ConversationItem {
  id: string;
  title: string;
  created_at: string;
}

interface ConversationListProps {
  conversations: ConversationItem[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string) => void;
}

export const ConversationList: React.FC<ConversationListProps> = ({
  conversations,
  activeConversationId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
}) => {
  return (
    <div
      style={{
        width: '260px',
        backgroundColor: 'rgba(15, 23, 42, 0.6)',
        borderRight: '1px solid rgba(255, 255, 255, 0.08)',
        padding: '1rem',
        display: 'flex',
        flexDirection: 'column',
        gap: '0.75rem',
      }}
    >
      <button
        onClick={onNewConversation}
        className="btn-primary"
        style={{ width: '100%', justifyContent: 'center', fontSize: '0.875rem', padding: '0.625rem' }}
      >
        <Plus size={18} />
        <span>New Support Chat</span>
      </button>

      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.375rem', marginTop: '0.5rem' }}>
        {conversations.length === 0 ? (
          <p style={{ color: '#64748b', fontSize: '0.8125rem', textAlign: 'center', marginTop: '2rem' }}>
            No previous chats
          </p>
        ) : (
          conversations.map((conv) => {
            const isActive = conv.id === activeConversationId;
            return (
              <div
                key={conv.id}
                onClick={() => onSelectConversation(conv.id)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.625rem 0.75rem',
                  borderRadius: '0.5rem',
                  cursor: 'pointer',
                  backgroundColor: isActive ? 'rgba(99, 102, 241, 0.15)' : 'transparent',
                  border: isActive ? '1px solid rgba(99, 102, 241, 0.3)' : '1px solid transparent',
                  color: isActive ? '#ffffff' : '#94a3b8',
                  fontSize: '0.875rem',
                  transition: 'all 0.15s ease',
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', overflow: 'hidden' }}>
                  <MessageSquare size={16} color={isActive ? '#818cf8' : '#64748b'} />
                  <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {conv.title || 'Support Query'}
                  </span>
                </div>

                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conv.id);
                  }}
                  style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer', padding: '0.25rem' }}
                  title="Delete Conversation"
                >
                  <Trash2 size={14} />
                </button>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
