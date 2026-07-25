import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';

// Placeholder view pages for router initialization
const ChatPage = () => <div className="glass-card" style={{ padding: '2rem' }}><h2>Chat Q&A Console</h2><p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Ask grounded customer support questions using Enterprise RAG.</p></div>;
const DocumentsPage = () => <div className="glass-card" style={{ padding: '2rem' }}><h2>Knowledge Base Documents</h2><p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Upload and process PDFs, DOCX, CSVs, and technical images.</p></div>;
const SearchPage = () => <div className="glass-card" style={{ padding: '2rem' }}><h2>Semantic Search</h2><p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Search vector embeddings across organizational knowledge.</p></div>;
const ReportsPage = () => <div className="glass-card" style={{ padding: '2rem' }}><h2>Support Reports</h2><p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Generate structured summaries and analytics reports.</p></div>;
const LoginPage = () => <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center' }}><div className="glass-card" style={{ padding: '2.5rem', width: '360px', textAlign: 'center' }}><h2>Sign In</h2><p style={{ color: '#94a3b8', marginTop: '0.5rem', fontSize: '0.875rem' }}>AI Customer Support Platform</p></div></div>;

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/" element={<Navigate to="/chat" replace />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/search" element={<SearchPage />} />
              <Route path="/reports" element={<ReportsPage />} />
            </Route>
          </Route>
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
