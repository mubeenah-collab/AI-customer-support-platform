import React, { useEffect, useState, useCallback } from 'react';
import { FileText, BarChart2, Sparkles, Loader2, RefreshCw, AlertCircle } from 'lucide-react';
import { apiClient } from '../../services/apiClient';

interface DocumentOption {
  id: string;
  filename: string;
}

interface ReportRequestFormProps {
  onReportGenerated: (reportData: any) => void;
  isLoading: boolean;
  setIsLoading: (val: boolean) => void;
}

export const ReportRequestForm: React.FC<ReportRequestFormProps> = ({
  onReportGenerated,
  isLoading,
  setIsLoading,
}) => {
  const [reportType, setReportType] = useState<'document' | 'support'>('document');
  const [documents, setDocuments] = useState<DocumentOption[]>([]);
  const [selectedDocId, setSelectedDocId] = useState('');
  const [topic, setTopic] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isFetchingDocs, setIsFetchingDocs] = useState(true);

  // Fetch documents from backend API
  const fetchDocs = useCallback(async () => {
    try {
      setIsFetchingDocs(true);
      const res = await apiClient.get('/documents');
      const data = res.data;
      const docsList = Array.isArray(data) ? data : (data?.documents || data?.items || []);
      const safeList = Array.isArray(docsList) ? docsList : [];
      setDocuments(safeList);
      if (safeList.length > 0) {
        setSelectedDocId((prev) => (safeList.some((d) => d.id === prev) ? prev : safeList[0].id));
      } else {
        setSelectedDocId('');
      }
    } catch (err) {
      console.error('Failed to load documents for report request:', err);
      setDocuments([]);
      setSelectedDocId('');
    } finally {
      setIsFetchingDocs(false);
    }
  }, []);

  useEffect(() => {
    fetchDocs();
  }, [fetchDocs]);

  // Window focus listener to refresh document list when user returns/uploads
  useEffect(() => {
    const onFocus = () => fetchDocs();
    window.addEventListener('focus', onFocus);
    return () => window.removeEventListener('focus', onFocus);
  }, [fetchDocs]);

  // Validate and sanitize selectedDocId whenever documents array changes
  useEffect(() => {
    if (documents.length > 0) {
      const isValid = documents.some((d) => d.id === selectedDocId);
      if (!isValid) {
        console.log('[ReportRequestForm] Resetting selectedDocId to active document:', documents[0].id);
        setSelectedDocId(documents[0].id);
      }
    } else {
      setSelectedDocId('');
    }
  }, [documents, selectedDocId]);

  const safeDocs = Array.isArray(documents) ? documents : [];
  const isDocSelectionInvalid =
    reportType === 'document' &&
    (safeDocs.length === 0 || !selectedDocId || !safeDocs.some((d) => d.id === selectedDocId));

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    // Hardened pre-submit check: Verify selectedDocId exists in current documents array
    if (reportType === 'document') {
      const docMatch = safeDocs.find((d) => d.id === selectedDocId);
      if (!docMatch || !selectedDocId) {
        setError('No valid document selected');
        return;
      }
    }

    if (reportType === 'support' && !topic.trim()) {
      setError('Please provide a topic or scope for the support report.');
      return;
    }

    try {
      setIsLoading(true);
      if (reportType === 'document') {
        console.log('[ReportRequestForm] Submitting verified document summary payload:', { document_id: selectedDocId });
        const res = await apiClient.post('/reports/document-summary', {
          document_id: selectedDocId,
        });
        onReportGenerated(res.data);
      } else {
        const res = await apiClient.post('/reports/support-report', {
          topic: topic.trim(),
        });
        onReportGenerated(res.data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Report generation failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
          Generate AI Report
        </h3>
        <button
          type="button"
          onClick={() => fetchDocs()}
          disabled={isFetchingDocs}
          title="Refresh Document List"
          style={{
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '0.5rem',
            color: '#94a3b8',
            padding: '0.4rem 0.75rem',
            display: 'flex',
            alignItems: 'center',
            gap: '0.35rem',
            fontSize: '0.75rem',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <RefreshCw size={14} style={{ animation: isFetchingDocs ? 'spin 1s linear infinite' : 'none' }} />
          <span>{isFetchingDocs ? 'Syncing...' : 'Refresh List'}</span>
        </button>
      </div>

      <div style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem' }}>
        <button
          type="button"
          onClick={() => setReportType('document')}
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            padding: '0.75rem',
            borderRadius: '0.75rem',
            border: reportType === 'document' ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.1)',
            backgroundColor: reportType === 'document' ? 'rgba(99,102,241,0.15)' : 'rgba(15,23,42,0.6)',
            color: reportType === 'document' ? '#ffffff' : '#94a3b8',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <FileText size={18} color={reportType === 'document' ? '#818cf8' : '#64748b'} />
          <span>Document Summary</span>
        </button>

        <button
          type="button"
          onClick={() => setReportType('support')}
          style={{
            flex: 1,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '0.5rem',
            padding: '0.75rem',
            borderRadius: '0.75rem',
            border: reportType === 'support' ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.1)',
            backgroundColor: reportType === 'support' ? 'rgba(99,102,241,0.15)' : 'rgba(15,23,42,0.6)',
            color: reportType === 'support' ? '#ffffff' : '#94a3b8',
            fontWeight: 600,
            cursor: 'pointer',
            transition: 'all 0.15s ease',
          }}
        >
          <BarChart2 size={18} color={reportType === 'support' ? '#818cf8' : '#64748b'} />
          <span>Support Analytics Report</span>
        </button>
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {reportType === 'document' ? (
          <div>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <label style={{ fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1' }}>
                Select Knowledge Base Document
              </label>
              {isFetchingDocs && (
                <span style={{ fontSize: '0.75rem', color: '#818cf8', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                  <Loader2 size={12} style={{ animation: 'spin 1s linear infinite' }} /> Loading documents...
                </span>
              )}
            </div>

            <select
              className="input-field"
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              disabled={isFetchingDocs || safeDocs.length === 0}
            >
              {isFetchingDocs ? (
                <option value="">Loading available documents...</option>
              ) : safeDocs.length === 0 ? (
                <option value="">No documents available. Upload documents first.</option>
              ) : (
                safeDocs.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.filename}
                  </option>
                ))
              )}
            </select>

            {isDocSelectionInvalid && !isFetchingDocs && (
              <p style={{ color: '#f87171', fontSize: '0.85rem', marginTop: '0.5rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <AlertCircle size={14} /> No valid document selected
              </p>
            )}
          </div>
        ) : (
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
              Report Topic / Inquiry Focus Area
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="e.g. Common Billing Errors & Payment Resolution Procedures"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
            />
          </div>
        )}

        {error && (
          <p style={{ color: '#f87171', fontSize: '0.875rem', fontWeight: 600 }}>{error}</p>
        )}

        <button
          type="submit"
          className="btn-primary"
          disabled={
            isLoading ||
            isFetchingDocs ||
            (reportType === 'document' && isDocSelectionInvalid) ||
            (reportType === 'support' && !topic.trim())
          }
          style={{
            width: '100%',
            justifyContent: 'center',
            padding: '0.875rem',
            opacity:
              isLoading || isFetchingDocs || (reportType === 'document' && isDocSelectionInvalid)
                ? 0.5
                : 1,
            cursor:
              isLoading || isFetchingDocs || (reportType === 'document' && isDocSelectionInvalid)
                ? 'not-allowed'
                : 'pointer',
          }}
        >
          {isLoading ? (
            <>
              <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
              <span>Generating Report with Gemini LLM...</span>
            </>
          ) : (
            <>
              <Sparkles size={18} />
              <span>Generate Report</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
};
