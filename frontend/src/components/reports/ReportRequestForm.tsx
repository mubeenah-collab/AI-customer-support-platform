import React, { useEffect, useState } from 'react';
import { FileText, BarChart2, Sparkles, Loader2 } from 'lucide-react';
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

  useEffect(() => {
    const fetchDocs = async () => {
      try {
        const res = await apiClient.get('/documents');
        const docs = res.data.items || res.data || [];
        setDocuments(docs);
        if (docs.length > 0) setSelectedDocId(docs[0].id);
      } catch (err) {
        console.error('Failed to load documents for report request:', err);
      }
    };
    fetchDocs();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (reportType === 'document' && !selectedDocId) {
      setError('Please select a document to summarize.');
      return;
    }

    if (reportType === 'support' && !topic.trim()) {
      setError('Please provide a topic or scope for the support report.');
      return;
    }

    try {
      setIsLoading(true);
      if (reportType === 'document') {
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
      <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1rem' }}>
        Generate AI Report
      </h3>

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
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>
              Select Knowledge Base Document
            </label>
            <select
              className="input-field"
              value={selectedDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              disabled={documents.length === 0}
            >
              {documents.length === 0 ? (
                <option value="">No documents available. Upload documents first.</option>
              ) : (
                documents.map((doc) => (
                  <option key={doc.id} value={doc.id}>
                    {doc.filename}
                  </option>
                ))
              )}
            </select>
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
          <p style={{ color: '#f87171', fontSize: '0.875rem' }}>{error}</p>
        )}

        <button
          type="submit"
          className="btn-primary"
          disabled={isLoading || (reportType === 'document' && !selectedDocId)}
          style={{ width: '100%', justifyContent: 'center', padding: '0.875rem', opacity: isLoading ? 0.6 : 1 }}
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
