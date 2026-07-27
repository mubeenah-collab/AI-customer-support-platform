import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Layout } from './components/Layout';

import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { ChatPage } from './pages/ChatPage';
import { SearchPage } from './pages/SearchPage';
import { ReportsPage } from './pages/ReportsPage';
import { DashboardPage } from './pages/DashboardPage';
import { UsersPage } from './pages/UsersPage';
import { ProfilePage } from './pages/ProfilePage';
import { CustomerTicketsPage } from './pages/CustomerTicketsPage';
import { AdminTicketsPage } from './pages/AdminTicketsPage';
import { AdminSettingsPage } from './pages/AdminSettingsPage';
import { CustomerHistoryPage } from './pages/CustomerHistoryPage';

const RootRedirect: React.FC = () => {
  const { isAuthenticated, isAdmin, isLoading } = useAuth();
  if (isLoading) return null;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Navigate to={isAdmin ? '/admin/dashboard' : '/customer/chat'} replace />;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />

          {/* Root Redirect */}
          <Route path="/" element={<RootRedirect />} />

          {/* Admin Portal Protected Routes */}
          <Route element={<ProtectedRoute allowedRoles={['admin']} />}>
            <Route element={<Layout />}>
              <Route path="/admin" element={<Navigate to="/admin/dashboard" replace />} />
              <Route path="/admin/dashboard" element={<DashboardPage />} />
              <Route path="/admin/documents" element={<DocumentsPage />} />
              <Route path="/admin/search" element={<SearchPage />} />
              <Route path="/admin/reports" element={<ReportsPage />} />
              <Route path="/admin/tickets" element={<AdminTicketsPage />} />
              <Route path="/admin/users" element={<UsersPage />} />
              <Route path="/admin/settings" element={<AdminSettingsPage />} />
            </Route>
          </Route>

          {/* Customer Portal Protected Routes */}
          <Route element={<ProtectedRoute allowedRoles={['customer']} />}>
            <Route element={<Layout />}>
              <Route path="/customer" element={<Navigate to="/customer/chat" replace />} />
              <Route path="/customer/chat" element={<ChatPage />} />
              <Route path="/customer/history" element={<CustomerHistoryPage />} />
              <Route path="/customer/tickets" element={<CustomerTicketsPage />} />
              <Route path="/customer/profile" element={<ProfilePage />} />
            </Route>
          </Route>

          {/* Legacy / Direct Route Redirects */}
          <Route element={<ProtectedRoute />}>
            <Route element={<Layout />}>
              <Route path="/chat" element={<Navigate to="/customer/chat" replace />} />
              <Route path="/history" element={<Navigate to="/customer/history" replace />} />
              <Route path="/documents" element={<Navigate to="/admin/documents" replace />} />
              <Route path="/search" element={<Navigate to="/admin/search" replace />} />
              <Route path="/reports" element={<Navigate to="/admin/reports" replace />} />
              <Route path="/dashboard" element={<Navigate to="/admin/dashboard" replace />} />
              <Route path="/users" element={<Navigate to="/admin/users" replace />} />
              <Route path="/settings" element={<Navigate to="/admin/settings" replace />} />
              <Route path="/profile" element={<Navigate to="/customer/profile" replace />} />
            </Route>
          </Route>

          {/* Fallback */}
          <Route path="*" element={<RootRedirect />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
};

export default App;
