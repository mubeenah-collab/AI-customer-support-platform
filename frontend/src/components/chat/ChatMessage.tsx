import React from 'react';
import { Bot, User as UserIcon } from 'lucide-react';
import { SourceCitationCard, Citation } from './SourceCitationCard';

export interface ChatMessageItem {
  id: string;
  sender: 'user' | 'assistant';
  content: string;
  image_url?: string;
  citations?: Citation[];
  timestamp: string;
}

interface ChatMessageProps {
  message: ChatMessageItem;
}

export const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.sender === 'user';

  return (
    <div
      style={{
        display: 'flex',
        gap: '1rem',
        justifyContent: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '1.5rem',
      }}
    >
      {!isUser && (
        <div
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <Bot size={20} color="#ffffff" />
        </div>
      )}

      <div style={{ maxWidth: '75%' }}>
        <div
          style={{
            backgroundColor: isUser ? '#6366f1' : 'rgba(30, 41, 59, 0.8)',
            color: '#f8fafc',
            padding: '1rem 1.25rem',
            borderRadius: isUser ? '1.25rem 1.25rem 0.25rem 1.25rem' : '1.25rem 1.25rem 1.25rem 0.25rem',
            border: isUser ? 'none' : '1px solid rgba(255,255,255,0.08)',
            boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            lineHeight: 1.6,
            fontSize: '0.9375rem',
          }}
        >
          {message.image_url && (
            <div style={{ marginBottom: '0.75rem' }}>
              <img
                src={message.image_url}
                alt="Attached input preview"
                style={{ maxWidth: '100%', maxHeight: '200px', borderRadius: '0.5rem', objectFit: 'cover' }}
              />
            </div>
          )}

          <div style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div>
        </div>

        {!isUser && message.citations && message.citations.length > 0 && (
          <div style={{ marginTop: '0.75rem' }}>
            <span style={{ fontSize: '0.75rem', fontWeight: 600, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Grounded Sources ({message.citations.length})
            </span>
            {message.citations.map((citation, idx) => (
              <SourceCitationCard key={idx} citation={citation} />
            ))}
          </div>
        )}
      </div>

      {isUser && (
        <div
          style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            backgroundColor: '#334155',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <UserIcon size={18} color="#cbd5e1" />
        </div>
      )}
    </div>
  );
};
