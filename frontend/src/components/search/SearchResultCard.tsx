import React from 'react';
import { FileText, Database, Tag } from 'lucide-react';

export interface SearchResultItem {
  chunk_id: string;
  document_id: string;
  document_name?: string;
  content: string;
  score: number;
  metadata?: Record<string, any>;
}

interface SearchResultCardProps {
  result: SearchResultItem;
}

export const SearchResultCard: React.FC<SearchResultCardProps> = ({ result }) => {
  const percentage = Math.round(result.score * 100);

  return (
    <div className="glass-card" style={{ padding: '1.25rem', marginBottom: '1rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontWeight: 600, color: '#f8fafc' }}>
          <FileText size={18} color="#818cf8" />
          <span>{result.document_name || result.metadata?.filename || 'Support Document'}</span>
        </div>

        <span
          style={{
            padding: '0.25rem 0.75rem',
            borderRadius: '9999px',
            backgroundColor: percentage > 70 ? 'rgba(34, 197, 94, 0.15)' : 'rgba(99, 102, 241, 0.15)',
            color: percentage > 70 ? '#4ade80' : '#a5b4fc',
            fontSize: '0.8125rem',
            fontWeight: 700,
          }}
        >
          {percentage}% Similarity
        </span>
      </div>

      <p style={{ color: '#cbd5e1', fontSize: '0.9375rem', lineHeight: 1.6, marginBottom: '0.75rem', whiteSpace: 'pre-wrap' }}>
        {result.content}
      </p>

      <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', paddingTop: '0.5rem', borderTop: '1px solid rgba(255,255,255,0.05)', fontSize: '0.75rem', color: '#64748b' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
          <Database size={14} /> Chunk ID: {result.chunk_id.substring(0, 12)}...
        </span>
        {result.metadata?.page && (
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
            <Tag size={14} /> Page {result.metadata.page}
          </span>
        )}
      </div>
    </div>
  );
};
