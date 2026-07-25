import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';

import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DocumentsPage } from './pages/DocumentsPage';

// Placeholder view pages for router initialization
const ChatPage = () => <div className="glass-card" style={{ padding: '2rem' }}><h2>Chat Q&A Console</h2><p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Ask grounded customer support questions using Enterprise RAG.</p></div>;
const SearchPage = () => <div className="glass-card" style={{ padding: '2rem' }}><h2>Semantic Search</h2><p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Search vector embeddings across organizational knowledge.</p></div>;
const ReportsPage = () => <div className="glass-card" style={{ padding: '2rem' }}><h2>Support Reports</h2><p style={{ color: '#94a3b8', marginTop: '0.5rem' }}>Generate structured summaries and analytics reports.</p></div>;

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
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
