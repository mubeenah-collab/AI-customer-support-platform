import React, { useEffect, useState } from 'react';
import { ReportRequestForm } from '../components/reports/ReportRequestForm';
import { ReportViewer, ReportContent } from '../components/reports/ReportViewer';
import { ReportList } from '../components/reports/ReportList';
import { apiClient } from '../services/apiClient';

export const ReportsPage: React.FC = () => {
  const [activeReport, setActiveReport] = useState<ReportContent | null>(null);
  const [reports, setReports] = useState<ReportContent[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchReports = async () => {
    try {
      const res = await apiClient.get('/reports');
      const items = res.data.items || res.data || [];
      setReports(items);
    } catch (err) {
      console.error('Failed to fetch report history:', err);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleReportGenerated = (newReport: ReportContent) => {
    setActiveReport(newReport);
    fetchReports();
  };

  return (
    <div style={{ maxWidth: '950px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
          Summaries & Analytics <span className="gradient-text">Reports</span>
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '0.25rem' }}>
          Generate grounded executive document summaries and support resolution reports powered by Gemini 1.5 Pro.
        </p>
      </div>

      <ReportRequestForm
        onReportGenerated={handleReportGenerated}
        isLoading={isLoading}
        setIsLoading={setIsLoading}
      />

      <ReportViewer report={activeReport} />

      <ReportList reports={reports} onSelectReport={setActiveReport} />
    </div>
  );
};
