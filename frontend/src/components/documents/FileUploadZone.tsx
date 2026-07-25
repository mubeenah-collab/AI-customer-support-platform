import React, { useState, useRef } from 'react';
import { UploadCloud, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { apiClient } from '../../services/apiClient';

interface FileUploadZoneProps {
  onUploadSuccess: () => void;
}

export const FileUploadZone: React.FC<FileUploadZoneProps> = ({ onUploadSuccess }) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.pptx', '.txt', '.csv', '.xlsx', '.png', '.jpg', '.jpeg', '.webp'];

  const validateAndUpload = async (file: File) => {
    setError(null);
    setSuccessMessage(null);

    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      setError(`Unsupported file extension '${ext}'. Allowed: PDF, DOCX, PPTX, TXT, CSV, XLSX, PNG, JPG, WEBP.`);
      return;
    }

    if (file.size > 20 * 1024 * 1024) {
      setError('File size exceeds maximum allowed limit of 20MB.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      setIsUploading(true);
      await apiClient.post('/documents/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setSuccessMessage(`Document '${file.name}' uploaded successfully. Background processing started.`);
      onUploadSuccess();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Document upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      validateAndUpload(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      validateAndUpload(e.target.files[0]);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '2rem', marginBottom: '2rem' }}>
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        style={{
          border: isDragging ? '2px dashed #6366f1' : '2px dashed rgba(255,255,255,0.15)',
          backgroundColor: isDragging ? 'rgba(99,102,241,0.08)' : 'rgba(15,23,42,0.4)',
          borderRadius: '1rem',
          padding: '3rem 2rem',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.25s ease',
        }}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          style={{ display: 'none' }}
          accept=".pdf,.docx,.pptx,.txt,.csv,.xlsx,.png,.jpg,.jpeg,.webp"
        />

        <div style={{ width: '64px', height: '64px', background: 'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.2))', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.25rem' }}>
          <UploadCloud size={32} color="#818cf8" />
        </div>

        <h3 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#f8fafc', marginBottom: '0.5rem' }}>
          {isUploading ? 'Uploading Document...' : 'Drag & Drop Support Documents'}
        </h3>
        <p style={{ color: '#94a3b8', fontSize: '0.875rem', marginBottom: '1rem' }}>
          Supports PDF, DOCX, PPTX, CSV, XLSX, TXT, and Images (Max 20MB)
        </p>

        <button type="button" className="btn-primary" style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>
          Browse Files
        </button>
      </div>

      {error && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', color: '#f87171', padding: '0.75rem 1rem', borderRadius: '0.75rem', fontSize: '0.875rem', marginTop: '1rem' }}>
          <AlertCircle size={18} />
          <span>{error}</span>
        </div>
      )}

      {successMessage && (
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', backgroundColor: 'rgba(34, 197, 94, 0.1)', border: '1px solid rgba(34, 197, 94, 0.3)', color: '#4ade80', padding: '0.75rem 1rem', borderRadius: '0.75rem', fontSize: '0.875rem', marginTop: '1rem' }}>
          <CheckCircle size={18} />
          <span>{successMessage}</span>
        </div>
      )}
    </div>
  );
};
