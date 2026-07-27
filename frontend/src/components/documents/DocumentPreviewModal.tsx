import React, { useState } from 'react';
import { FileText, X, Download, Trash2, CheckCircle2, Clock, AlertTriangle, Layers, ExternalLink } from 'lucide-react';
import { DocumentItem } from './DocumentList';
import { apiClient } from '../../services/apiClient';

interface DocumentPreviewModalProps {
  document: DocumentItem | null;
  onClose: () => void;
  onDeleted: () => void;
}

export const DocumentPreviewModal: React.FC<DocumentPreviewModalProps> = ({
  document,
  onClose,
  onDeleted,
}) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  if (!document) return null;

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const handleDownload = async (inline: boolean = false) => {
    try {
      setIsDownloading(true);
      const disposition = inline ? 'inline' : 'attachment';
      const res = await apiClient.get(`/documents/${document.id}/download?disposition=${disposition}`, {
        responseType: 'blob',
      });

      const headerType = res.headers['content-type'];
      const contentType = typeof headerType === 'string' ? headerType : 'application/octet-stream';
      const blob = new Blob([res.data], { type: contentType });
      const url = window.URL.createObjectURL(blob);

      if (inline) {
        window.open(url, '_blank');
      } else {
        const link = window.document.createElement('a');
        link.href = url;
        link.setAttribute('download', document.filename);
        window.document.body.appendChild(link);
        link.click();
        link.remove();
      }
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Failed to download document:', err);
      alert('Could not download or preview file. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Are you sure you want to delete "${document.filename}" from the Knowledge Base?`)) {
      return;
    }
    try {
      setIsDeleting(true);
      await apiClient.delete(`/documents/${document.id}`);
      onDeleted();
      onClose();
    } catch (err) {
      console.error('Failed to delete document:', err);
      alert('Failed to delete document.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        backgroundColor: 'rgba(15, 23, 42, 0.75)',
        backdropFilter: 'blur(8px)',
        zIndex: 1000,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '1.5rem',
      }}
      onClick={onClose}
    >
      <div
        className="glass-card"
        style={{
          width: '100%',
          maxWidth: '560px',
          backgroundColor: '#0f172a',
          border: '1px solid rgba(255, 255, 255, 0.12)',
          borderRadius: '1rem',
          padding: '1.75rem',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)',
          color: '#f8fafc',
          position: 'relative',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close Button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '1.25rem',
            right: '1.25rem',
            background: 'transparent',
            border: 'none',
            color: '#94a3b8',
            cursor: 'pointer',
            padding: '0.25rem',
            borderRadius: '0.375rem',
          }}
        >
          <X size={20} />
        </button>

        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem', marginBottom: '1.5rem' }}>
          <div
            style={{
              padding: '0.75rem',
              borderRadius: '0.75rem',
              backgroundColor: 'rgba(99, 102, 241, 0.15)',
              border: '1px solid rgba(99, 102, 241, 0.3)',
              color: '#818cf8',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <FileText size={28} />
          </div>
          <div style={{ flex: 1, overflow: 'hidden' }}>
            <h3
              style={{
                fontSize: '1.25rem',
                fontWeight: 700,
                color: '#f8fafc',
                margin: 0,
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
              title={document.filename}
            >
              {document.filename}
            </h3>
            <p style={{ fontSize: '0.8125rem', color: '#94a3b8', margin: '0.25rem 0 0 0' }}>
              Knowledge Base Document Details
            </p>
          </div>
        </div>

        {/* Info Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '1rem',
            marginBottom: '1.5rem',
            backgroundColor: 'rgba(30, 41, 59, 0.5)',
            padding: '1rem',
            borderRadius: '0.75rem',
            border: '1px solid rgba(255, 255, 255, 0.05)',
          }}
        >
          <div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
              Status
            </span>
            <div style={{ marginTop: '0.25rem' }}>
              {document.status === 'completed' && (
                <span style={{ color: '#4ade80', fontSize: '0.875rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                  <CheckCircle2 size={14} /> Completed
                </span>
              )}
              {(document.status === 'processing' || document.status === 'pending') && (
                <span style={{ color: '#facc15', fontSize: '0.875rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Clock size={14} /> Processing
                </span>
              )}
              {document.status === 'failed' && (
                <span style={{ color: '#f87171', fontSize: '0.875rem', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.25rem' }}>
                  <AlertTriangle size={14} /> Failed
                </span>
              )}
            </div>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
              File Size
            </span>
            <p style={{ fontSize: '0.875rem', color: '#cbd5e1', fontWeight: 500, margin: '0.25rem 0 0 0' }}>
              {formatFileSize(document.file_size)}
            </p>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
              Indexed Chunks
            </span>
            <p style={{ fontSize: '0.875rem', color: '#cbd5e1', fontWeight: 500, margin: '0.25rem 0 0 0', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <Layers size={14} color="#818cf8" /> {document.chunk_count || 0} chunks
            </p>
          </div>

          <div>
            <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', fontWeight: 600 }}>
              Document ID
            </span>
            <p
              style={{
                fontSize: '0.75rem',
                color: '#94a3b8',
                fontWeight: 400,
                margin: '0.25rem 0 0 0',
                fontFamily: 'monospace',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
              }}
            >
              {document.id}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '0.75rem' }}>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            style={{
              padding: '0.625rem 1rem',
              borderRadius: '0.5rem',
              border: '1px solid rgba(239, 68, 68, 0.3)',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              color: '#f87171',
              fontWeight: 600,
              fontSize: '0.875rem',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.375rem',
            }}
          >
            <Trash2 size={16} /> Delete
          </button>

          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button
              onClick={() => handleDownload(true)}
              disabled={isDownloading}
              style={{
                padding: '0.625rem 1rem',
                borderRadius: '0.5rem',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                backgroundColor: 'rgba(255, 255, 255, 0.05)',
                color: '#e2e8f0',
                fontWeight: 600,
                fontSize: '0.875rem',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.375rem',
              }}
            >
              <ExternalLink size={16} /> Open
            </button>

            <button
              onClick={() => handleDownload(false)}
              disabled={isDownloading}
              style={{
                padding: '0.625rem 1.25rem',
                borderRadius: '0.5rem',
                border: 'none',
                background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                color: '#ffffff',
                fontWeight: 600,
                fontSize: '0.875rem',
                cursor: 'pointer',
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.375rem',
                boxShadow: '0 4px 12px rgba(99, 102, 241, 0.3)',
              }}
            >
              <Download size={16} /> Download File
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
