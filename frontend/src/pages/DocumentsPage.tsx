import React, { useEffect, useState } from 'react';
import { FileUploadZone } from '../components/documents/FileUploadZone';
import { DocumentList, DocumentItem } from '../components/documents/DocumentList';
import { apiClient } from '../services/apiClient';

export const DocumentsPage: React.FC = () => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchDocuments = async () => {
    try {
      const res = await apiClient.get('/documents');
      const data = res.data;
      const docList = Array.isArray(data) ? data : (data?.documents || data?.items || []);
      setDocuments(Array.isArray(docList) ? docList : []);
    } catch (err) {
      console.error('Failed to fetch documents:', err);
      setDocuments([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
    const interval = setInterval(fetchDocuments, 5000); // Auto-poll background processing status
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
          Knowledge Base <span className="gradient-text">Documents</span>
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '0.25rem' }}>
          Upload technical manuals, policy PDFs, spreadsheets, and product specs for grounded RAG synthesis.
        </p>
      </div>

      <FileUploadZone onUploadSuccess={fetchDocuments} />
      <DocumentList documents={documents} onDocumentDeleted={fetchDocuments} />
    </div>
  );
};
