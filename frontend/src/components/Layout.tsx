import React, { useState } from 'react';
import { Link, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Bot,
  FileText,
  Search,
  BarChart2,
  User,
  LogOut,
  Activity,
  Users,
  Settings,
  Ticket,
  History,
  Bell,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react';

export const Layout: React.FC = () => {
  const { user, logout, isAdmin } = useAuth();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const adminNavItems = [
    { label: 'Dashboard', path: '/admin/dashboard', icon: Activity },
    { label: 'Documents', path: '/admin/documents', icon: FileText },
    { label: 'Search Console', path: '/admin/search', icon: Search },
    { label: 'Reports & Analytics', path: '/admin/reports', icon: BarChart2 },
    { label: 'Support Queue', path: '/admin/tickets', icon: Ticket },
    { label: 'User Management', path: '/admin/users', icon: Users },
    { label: 'System Settings', path: '/admin/settings', icon: Settings },
  ];

  const customerNavItems = [
    { label: 'AI Support Chat', path: '/customer/chat', icon: Bot },
    { label: 'Support Tickets', path: '/customer/tickets', icon: Ticket },
    { label: 'Chat History', path: '/customer/history', icon: History },
    { label: 'My Profile', path: '/customer/profile', icon: Settings },
  ];

  const navItems = isAdmin ? adminNavItems : customerNavItems;

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: '#050816', color: '#f8fafc' }}>
      {/* Collapsible Glass Sidebar */}
      <aside
        style={{
          width: collapsed ? '80px' : '260px',
          backgroundColor: 'rgba(15, 23, 42, 0.75)',
          backdropFilter: 'blur(20px)',
          WebkitBackdropFilter: 'blur(20px)',
          borderRight: '1px solid rgba(255, 255, 255, 0.08)',
          padding: '1.25rem 1rem',
          display: 'flex',
          flexDirection: 'column',
          transition: 'width 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'sticky',
          top: 0,
          height: '100vh',
          zIndex: 40,
        }}
      >
        {/* Logo Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: collapsed ? 'center' : 'space-between',
            marginBottom: '2rem',
            paddingBottom: '1rem',
            borderBottom: '1px solid rgba(255, 255, 255, 0.06)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div
              style={{
                width: '40px',
                height: '40px',
                background: isAdmin
                  ? 'linear-gradient(135deg, #6366f1, #8b5cf6, #d946ef)'
                  : 'linear-gradient(135deg, #10b981, #06b6d4)',
                borderRadius: '12px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: isAdmin
                  ? '0 0 20px rgba(139, 92, 246, 0.4)'
                  : '0 0 20px rgba(16, 185, 129, 0.4)',
                flexShrink: 0,
              }}
            >
              <Bot size={22} color="#ffffff" />
            </div>
            {!collapsed && (
              <div>
                <h2 style={{ fontSize: '1.125rem', fontWeight: 800, color: '#f8fafc', letterSpacing: '-0.02em' }}>
                  AI Support
                </h2>
                <span
                  style={{
                    fontSize: '0.7rem',
                    color: isAdmin ? '#a78bfa' : '#34d399',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                  }}
                >
                  {isAdmin ? 'Admin Portal' : 'Customer Portal'}
                </span>
              </div>
            )}
          </div>

          <button
            onClick={() => setCollapsed(!collapsed)}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              color: '#94a3b8',
              width: '28px',
              height: '28px',
              display: collapsed ? 'none' : 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              transition: 'all 0.2s ease',
            }}
          >
            <ChevronLeft size={16} />
          </button>
        </div>

        {/* Navigation Items */}
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '0.375rem', flex: 1 }}>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname.startsWith(item.path);
            return (
              <Link
                key={item.path}
                to={item.path}
                title={collapsed ? item.label : undefined}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.875rem',
                  padding: collapsed ? '0.75rem' : '0.75rem 1rem',
                  justifyContent: collapsed ? 'center' : 'flex-start',
                  borderRadius: '0.75rem',
                  color: isActive ? '#ffffff' : '#94a3b8',
                  background: isActive
                    ? isAdmin
                      ? 'linear-gradient(90deg, rgba(99, 102, 241, 0.25), rgba(139, 92, 246, 0.12))'
                      : 'linear-gradient(90deg, rgba(16, 185, 129, 0.25), rgba(6, 182, 212, 0.12))'
                    : 'transparent',
                  border: isActive
                    ? isAdmin
                      ? '1px solid rgba(139, 92, 246, 0.4)'
                      : '1px solid rgba(16, 185, 129, 0.4)'
                    : '1px solid transparent',
                  textDecoration: 'none',
                  fontWeight: isActive ? 700 : 500,
                  fontSize: '0.9rem',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: isActive ? '0 0 15px rgba(139, 92, 246, 0.15)' : 'none',
                }}
              >
                <Icon
                  size={20}
                  color={isActive ? (isAdmin ? '#c084fc' : '#34d399') : '#94a3b8'}
                  style={{ flexShrink: 0 }}
                />
                {!collapsed && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Sidebar Toggle for Collapsed View */}
        {collapsed && (
          <button
            onClick={() => setCollapsed(false)}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              borderRadius: '8px',
              color: '#94a3b8',
              width: '100%',
              padding: '0.5rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              marginBottom: '1rem',
            }}
          >
            <ChevronRight size={16} />
          </button>
        )}

        {/* User Profile & Logout Section */}
        {user && (
          <div
            style={{
              marginTop: 'auto',
              paddingTop: '1rem',
              borderTop: '1px solid rgba(255, 255, 255, 0.08)',
            }}
          >
            {!collapsed ? (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.875rem' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: '0.875rem',
                    color: '#ffffff',
                    flexShrink: 0,
                  }}
                >
                  {user.full_name ? user.full_name[0].toUpperCase() : 'U'}
                </div>
                <div style={{ overflow: 'hidden' }}>
                  <p
                    style={{
                      fontSize: '0.875rem',
                      fontWeight: 700,
                      color: '#f8fafc',
                      whiteSpace: 'nowrap',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {user.full_name}
                  </p>
                  <p
                    style={{
                      fontSize: '0.75rem',
                      color: '#64748b',
                      whiteSpace: 'nowrap',
                      textOverflow: 'ellipsis',
                    }}
                  >
                    {user.email}
                  </p>
                </div>
              </div>
            ) : null}

            <button
              onClick={logout}
              title={collapsed ? 'Sign Out' : undefined}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: collapsed ? 'center' : 'center',
                gap: '0.5rem',
                padding: '0.625rem',
                borderRadius: '0.625rem',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.25)',
                color: '#f87171',
                fontSize: '0.875rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease',
              }}
            >
              <LogOut size={16} />
              {!collapsed && <span>Sign Out</span>}
            </button>
          </div>
        )}
      </aside>

      {/* Main Container */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
        {/* Top Navigation Bar */}
        <header
          style={{
            height: '70px',
            backgroundColor: 'rgba(15, 23, 42, 0.65)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
            padding: '0 2rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            position: 'sticky',
            top: 0,
            zIndex: 30,
          }}
        >
          {/* Global Search Bar */}
          <div style={{ position: 'relative', width: '320px' }}>
            <Search
              size={16}
              color="#64748b"
              style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }}
            />
            <input
              type="text"
              placeholder="Search tickets, documents, users..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{
                width: '100%',
                padding: '0.5rem 1rem 0.5rem 2.5rem',
                borderRadius: '9999px',
                backgroundColor: 'rgba(255, 255, 255, 0.04)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: '#f8fafc',
                fontSize: '0.85rem',
                outline: 'none',
              }}
            />
          </div>

          {/* Right Status & Notifications */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '1.25rem' }}>
            {/* AI Engine Status */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.35rem 0.85rem',
                borderRadius: '9999px',
                backgroundColor: 'rgba(139, 92, 246, 0.12)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                fontSize: '0.75rem',
                fontWeight: 700,
                color: '#c084fc',
              }}
            >
              <Sparkles size={14} color="#c084fc" />
              <span>Gemini 1.5 Pro Active</span>
            </div>

            {/* Live System Status Pill */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.35rem 0.85rem',
                borderRadius: '9999px',
                backgroundColor: 'rgba(16, 185, 129, 0.12)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                fontSize: '0.75rem',
                fontWeight: 700,
                color: '#34d399',
              }}
            >
              <span
                style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: '#34d399',
                  boxShadow: '0 0 8px #34d399',
                }}
              />
              <span>System Operational</span>
            </div>

            {/* Notification Bell */}
            <button
              style={{
                position: 'relative',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                borderRadius: '50%',
                width: '38px',
                height: '38px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: '#cbd5e1',
                cursor: 'pointer',
              }}
            >
              <Bell size={18} />
              <span
                style={{
                  position: 'absolute',
                  top: '6px',
                  right: '6px',
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  backgroundColor: '#8b5cf6',
                  boxShadow: '0 0 6px #8b5cf6',
                }}
              />
            </button>

            {/* User Avatar & Info */}
            {user && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div
                  style={{
                    width: '38px',
                    height: '38px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #6366f1, #8b5cf6)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontWeight: 700,
                    fontSize: '0.9rem',
                    color: '#ffffff',
                    boxShadow: '0 0 15px rgba(99, 102, 241, 0.3)',
                  }}
                >
                  {user.full_name ? user.full_name[0].toUpperCase() : 'U'}
                </div>
              </div>
            )}
          </div>
        </header>

        {/* Page Content View */}
        <main style={{ flex: 1, padding: '2rem', overflowY: 'auto' }}>
          <Outlet />
        </main>
      </div>
    </div>
  );
};
