import React from 'react';
import { FileText, CheckCircle2, Calendar } from 'lucide-react';

export interface ReportContent {
  id?: string;
  title?: string;
  document_name?: string;
  summary?: string;
  key_points?: string[];
  content?: string;
  created_at?: string;
}

interface ReportViewerProps {
  report: ReportContent | null;
}

export const ReportViewer: React.FC<ReportViewerProps> = ({ report }) => {
  if (!report) return null;

  return (
    <div className="glass-card" style={{ padding: '2rem', marginBottom: '2rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1.5rem', paddingBottom: '1rem', borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: '42px', height: '42px', borderRadius: '10px', background: 'linear-gradient(135deg, #6366f1, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <FileText size={22} color="#ffffff" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc' }}>
              {report.title || report.document_name || 'Generated Report'}
            </h2>
            {report.created_at && (
              <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.25rem', marginTop: '0.25rem' }}>
                <Calendar size={12} /> {new Date(report.created_at).toLocaleString()}
              </span>
            )}
          </div>
        </div>

        <span style={{ padding: '0.25rem 0.75rem', borderRadius: '9999px', backgroundColor: 'rgba(34, 197, 94, 0.15)', color: '#4ade80', fontSize: '0.75rem', fontWeight: 700 }}>
          Grounded Gemini Output
        </span>
      </div>

      {report.summary && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 style={{ fontSize: '0.875rem', fontWeight: 600, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
            Executive Summary
          </h4>
          <p style={{ color: '#cbd5e1', lineHeight: 1.6, fontSize: '0.9375rem', whiteSpace: 'pre-wrap' }}>
            {report.summary}
          </p>
        </div>
      )}

      {report.key_points && report.key_points.length > 0 && (
        <div style={{ marginBottom: '1.5rem' }}>
          <h4 style={{ fontSize: '0.875rem', fontWeight: 600, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.75rem' }}>
            Key Highlights
          </h4>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {report.key_points.map((point, idx) => (
              <div key={idx} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.5rem', color: '#e2e8f0', fontSize: '0.875rem', lineHeight: 1.5 }}>
                <CheckCircle2 size={16} color="#4ade80" style={{ flexShrink: 0, marginTop: '0.125rem' }} />
                <span>{point}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {report.content && (
        <div>
          <h4 style={{ fontSize: '0.875rem', fontWeight: 600, color: '#818cf8', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
            Detailed Analysis Content
          </h4>
          <div style={{ backgroundColor: 'rgba(15,23,42,0.6)', padding: '1.25rem', borderRadius: '0.75rem', color: '#cbd5e1', lineHeight: 1.6, fontSize: '0.9375rem', whiteSpace: 'pre-wrap' }}>
            {report.content}
          </div>
        </div>
      )}
    </div>
  );
};
