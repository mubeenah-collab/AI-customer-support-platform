import React from 'react';
import { FileText, ExternalLink } from 'lucide-react';

export interface Citation {
  document_id: string;
  document_name: string;
  content_snippet: string;
  confidence_score: number;
}

interface SourceCitationCardProps {
  citation: Citation;
}

export const SourceCitationCard: React.FC<SourceCitationCardProps> = ({ citation }) => {
  const score = citation.confidence_score;
  const percentage = typeof score === 'number' && !isNaN(score) && isFinite(score)
    ? Math.max(0, Math.min(100, Math.round(score * 100)))
    : 0;

  return (
    <div
      style={{
        backgroundColor: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(99, 102, 241, 0.2)',
        borderRadius: '0.75rem',
        padding: '0.75rem 1rem',
        marginTop: '0.5rem',
        fontSize: '0.8125rem',
      }}
    >
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.375rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#818cf8' }}>
          <FileText size={16} />
          <span>{citation.document_name}</span>
        </div>
        <span
          style={{
            padding: '0.125rem 0.5rem',
            borderRadius: '9999px',
            backgroundColor: 'rgba(99, 102, 241, 0.15)',
            color: '#a5b4fc',
            fontSize: '0.75rem',
            fontWeight: 600,
          }}
        >
          {percentage}% match
        </span>
      </div>
      <p style={{ color: '#94a3b8', fontStyle: 'italic', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
        "{citation.content_snippet}"
      </p>
    </div>
  );
};
