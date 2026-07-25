import React from 'react';
import { FileText, Trash2, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';
import { apiClient } from '../../services/apiClient';

export interface DocumentItem {
  id: string;
  filename: string;
  file_size: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  chunk_count: number;
  created_at: string;
}

interface DocumentListProps {
  documents: DocumentItem[];
  onDocumentDeleted: () => void;
}

export const DocumentList: React.FC<DocumentListProps> = ({ documents, onDocumentDeleted }) => {
  const handleDelete = async (docId: string) => {
    if (!window.confirm('Are you sure you want to delete this document from the knowledge base?')) return;
    try {
      await apiClient.delete(`/documents/${docId}`);
      onDocumentDeleted();
    } catch (err) {
      alert('Failed to delete document.');
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const renderStatusBadge = (status: DocumentItem['status']) => {
    switch (status) {
      case 'completed':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.375rem', padding: '0.25rem 0.75rem', borderRadius: '9999px', backgroundColor: 'rgba(34, 197, 94, 0.1)', color: '#4ade80', fontSize: '0.75rem', fontWeight: 600 }}>
            <CheckCircle2 size={14} /> Completed
          </span>
        );
      case 'processing':
      case 'pending':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.375rem', padding: '0.25rem 0.75rem', borderRadius: '9999px', backgroundColor: 'rgba(234, 179, 8, 0.1)', color: '#facc15', fontSize: '0.75rem', fontWeight: 600 }}>
            <Clock size={14} /> Processing
          </span>
        );
      case 'failed':
        return (
          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.375rem', padding: '0.25rem 0.75rem', borderRadius: '9999px', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: '#f87171', fontSize: '0.75rem', fontWeight: 600 }}>
            <AlertTriangle size={14} /> Failed
          </span>
        );
    }
  };

  const safeDocs = Array.isArray(documents) ? documents : [];

  if (safeDocs.length === 0) {
    return (
      <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
        <FileText size={48} color="#475569" style={{ margin: '0 auto 1rem' }} />
        <h4 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.5rem' }}>No Knowledge Base Documents</h4>
        <p style={{ fontSize: '0.875rem' }}>Upload PDFs, DOCX, or images above to build your support RAG vector store.</p>
      </div>
    );
  }

  return (
    <div className="glass-card" style={{ padding: '1.5rem', overflowX: 'auto' }}>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1rem' }}>
        Knowledge Base Collection ({safeDocs.length})
      </h3>

      <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.875rem' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.08)', color: '#64748b' }}>
            <th style={{ padding: '0.75rem 1rem' }}>Document Name</th>
            <th style={{ padding: '0.75rem 1rem' }}>Size</th>
            <th style={{ padding: '0.75rem 1rem' }}>Chunks</th>
            <th style={{ padding: '0.75rem 1rem' }}>Status</th>
            <th style={{ padding: '0.75rem 1rem', textAlign: 'right' }}>Actions</th>
          </tr>
        </thead>
        <tbody>
          {safeDocs.map((doc) => (
            <tr key={doc.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', color: '#e2e8f0' }}>
              <td style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem', fontWeight: 500 }}>
                <FileText size={20} color="#818cf8" />
                <span style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '280px' }}>
                  {doc.filename}
                </span>
              </td>
              <td style={{ padding: '1rem', color: '#94a3b8' }}>{formatFileSize(doc.file_size)}</td>
              <td style={{ padding: '1rem', color: '#94a3b8' }}>{doc.chunk_count || 0}</td>
              <td style={{ padding: '1rem' }}>{renderStatusBadge(doc.status)}</td>
              <td style={{ padding: '1rem', textAlign: 'right' }}>
                <button
                  onClick={() => handleDelete(doc.id)}
                  style={{ background: 'transparent', border: 'none', color: '#f87171', cursor: 'pointer', padding: '0.375rem', borderRadius: '0.375rem' }}
                  title="Delete Document"
                >
                  <Trash2 size={18} />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
