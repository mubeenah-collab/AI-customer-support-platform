import React, { useEffect, useState } from 'react';
import { Activity, Cpu, HardDrive, Server, Database, CheckCircle2 } from 'lucide-react';
import { apiClient } from '../services/apiClient';

interface ComponentHealth {
  name: string;
  status: string;
  details?: string;
}

interface Metrics {
  cpu_usage_percent: number;
  memory_usage_percent: number;
  disk_usage_percent: number;
  active_db_pool_status: string;
}

export const DashboardPage: React.FC = () => {
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [readiness, setReadiness] = useState<{ status: string; components: ComponentHealth[] } | null>(null);

  const fetchHealthData = async () => {
    try {
      const [metricsRes, readyRes] = await Promise.all([
        apiClient.get('/health/metrics'),
        apiClient.get('/health/ready'),
      ]);
      setMetrics(metricsRes.data);
      setReadiness(readyRes.data);
    } catch (err) {
      console.error('Failed to fetch monitoring metrics:', err);
    }
  };

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(fetchHealthData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
          System Health & <span className="gradient-text">Monitoring</span>
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '0.25rem' }}>
          Real-time resource utilization, database pool metrics, and ChromaDB vector store readiness.
        </p>
      </div>

      {/* Resource Utilization Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1.25rem', marginBottom: '2rem' }}>
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.875rem', fontWeight: 500 }}>CPU Usage</span>
            <Cpu size={20} color="#818cf8" />
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc' }}>
            {metrics ? metrics.cpu_usage_percent.toFixed(1) + '%' : '--'}
          </h2>
          <div style={{ width: '100%', height: '6px', backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: '3px', marginTop: '0.75rem', overflow: 'hidden' }}>
            <div style={{ width: `${metrics?.cpu_usage_percent || 0}%`, height: '100%', background: 'linear-gradient(90deg, #6366f1, #8b5cf6)', borderRadius: '3px' }} />
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.875rem', fontWeight: 500 }}>RAM Memory</span>
            <Server size={20} color="#818cf8" />
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc' }}>
            {metrics ? metrics.memory_usage_percent.toFixed(1) + '%' : '--'}
          </h2>
          <div style={{ width: '100%', height: '6px', backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: '3px', marginTop: '0.75rem', overflow: 'hidden' }}>
            <div style={{ width: `${metrics?.memory_usage_percent || 0}%`, height: '100%', background: 'linear-gradient(90deg, #6366f1, #d946ef)', borderRadius: '3px' }} />
          </div>
        </div>

        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
            <span style={{ color: '#94a3b8', fontSize: '0.875rem', fontWeight: 500 }}>Disk Storage</span>
            <HardDrive size={20} color="#818cf8" />
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: '#f8fafc' }}>
            {metrics ? metrics.disk_usage_percent.toFixed(1) + '%' : '--'}
          </h2>
          <div style={{ width: '100%', height: '6px', backgroundColor: 'rgba(255,255,255,0.08)', borderRadius: '3px', marginTop: '0.75rem', overflow: 'hidden' }}>
            <div style={{ width: `${metrics?.disk_usage_percent || 0}%`, height: '100%', background: 'linear-gradient(90deg, #3b82f6, #6366f1)', borderRadius: '3px' }} />
          </div>
        </div>
      </div>

      {/* Readiness Probes Grid */}
      <div className="glass-card" style={{ padding: '1.5rem' }}>
        <h3 style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity size={20} color="#6366f1" /> Component Health Probes
        </h3>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {readiness?.components.map((comp, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '1rem 1.25rem',
                borderRadius: '0.75rem',
                backgroundColor: 'rgba(15, 23, 42, 0.6)',
                border: '1px solid rgba(255, 255, 255, 0.05)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <Database size={20} color="#818cf8" />
                <div>
                  <p style={{ fontWeight: 600, color: '#f8fafc', textTransform: 'capitalize' }}>
                    {comp.name.replace('_', ' ')}
                  </p>
                  {comp.details && <p style={{ fontSize: '0.75rem', color: '#64748b' }}>{comp.details}</p>}
                </div>
              </div>

              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '0.375rem', padding: '0.25rem 0.75rem', borderRadius: '9999px', backgroundColor: comp.status === 'healthy' ? 'rgba(34, 197, 94, 0.15)' : 'rgba(239, 68, 68, 0.15)', color: comp.status === 'healthy' ? '#4ade80' : '#f87171', fontSize: '0.75rem', fontWeight: 700 }}>
                <CheckCircle2 size={14} /> {comp.status.toUpperCase()}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
