import React from 'react';
import { FileText, Calendar, ChevronRight } from 'lucide-react';
import { ReportContent } from './ReportViewer';

interface ReportListProps {
  reports: ReportContent[];
  onSelectReport: (report: ReportContent) => void;
}

export const ReportList: React.FC<ReportListProps> = ({ reports, onSelectReport }) => {
  const safeReports = Array.isArray(reports) ? reports : [];
  if (safeReports.length === 0) return null;

  return (
    <div className="glass-card" style={{ padding: '1.5rem' }}>
      <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1rem' }}>
        Generated Report History ({safeReports.length})
      </h3>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
        {safeReports.map((rep, idx) => (
          <div
            key={rep.id || idx}
            onClick={() => onSelectReport(rep)}
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              padding: '0.875rem 1rem',
              borderRadius: '0.75rem',
              backgroundColor: 'rgba(15, 23, 42, 0.6)',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <FileText size={18} color="#818cf8" />
              <div>
                <p style={{ fontWeight: 600, color: '#f8fafc', fontSize: '0.875rem' }}>
                  {rep.title || rep.document_name || 'Generated Report'}
                </p>
                {rep.created_at && (
                  <span style={{ fontSize: '0.75rem', color: '#64748b', display: 'flex', alignItems: 'center', gap: '0.25rem', marginTop: '0.125rem' }}>
                    <Calendar size={12} /> {new Date(rep.created_at).toLocaleDateString()}
                  </span>
                )}
              </div>
            </div>

            <ChevronRight size={18} color="#64748b" />
          </div>
        ))}
      </div>
    </div>
  );
};
