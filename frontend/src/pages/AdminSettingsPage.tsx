import React, { useState } from 'react';
import { Settings, Sliders, Shield, Database, Cpu, Save, CheckCircle2 } from 'lucide-react';
import { apiClient } from '../services/apiClient';

export const AdminSettingsPage: React.FC = () => {
  const [llmModel, setLlmModel] = useState('gemini-1.5-pro');
  const [visionModel, setVisionModel] = useState('gemini-1.5-flash');
  const [embeddingModel, setEmbeddingModel] = useState('models/text-embedding-004');
  const [confidenceThreshold, setConfidenceThreshold] = useState('0.7');
  const [maxContextTokens, setMaxContextTokens] = useState('4096');
  const [rateLimitRequests, setRateLimitRequests] = useState('120');
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const handleSaveSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setIsSaved(false);

    // Simulate saving system configuration settings
    setTimeout(() => {
      setIsSaving(false);
      setIsSaved(true);
      setTimeout(() => setIsSaved(false), 4000);
    }, 600);
  };

  return (
    <div style={{ maxWidth: '950px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
          System <span className="gradient-text">Settings</span>
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '0.25rem' }}>
          Configure AI model hyperparameters, RAG confidence thresholds, and system security policies.
        </p>
      </div>

      {isSaved && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            backgroundColor: 'rgba(34, 197, 94, 0.15)',
            border: '1px solid rgba(34, 197, 94, 0.3)',
            color: '#4ade80',
            padding: '0.75rem 1rem',
            borderRadius: '0.75rem',
            fontSize: '0.875rem',
            marginBottom: '1.5rem',
          }}
        >
          <CheckCircle2 size={18} />
          <span>System configuration parameters updated successfully.</span>
        </div>
      )}

      <form onSubmit={handleSaveSettings} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
        {/* AI & LLM Engine Configuration */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Cpu size={20} color="#818cf8" /> AI Models & Inference Orchestration
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>Synthesis LLM Model</label>
              <select
                className="input-field"
                value={llmModel}
                onChange={(e) => setLlmModel(e.target.value)}
                style={{ width: '100%' }}
              >
                <option value="gemini-1.5-pro">Google Gemini 1.5 Pro (Recommended)</option>
                <option value="gemini-1.5-flash">Google Gemini 1.5 Flash</option>
                <option value="gemini-1.0-pro">Google Gemini 1.0 Pro</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>Vision VLM Model</label>
              <select
                className="input-field"
                value={visionModel}
                onChange={(e) => setVisionModel(e.target.value)}
                style={{ width: '100%' }}
              >
                <option value="gemini-1.5-flash">Google Gemini 1.5 Flash VLM</option>
                <option value="gemini-1.5-pro">Google Gemini 1.5 Pro Vision</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>Text Embedding Model</label>
              <select
                className="input-field"
                value={embeddingModel}
                onChange={(e) => setEmbeddingModel(e.target.value)}
                style={{ width: '100%' }}
              >
                <option value="models/text-embedding-004">models/text-embedding-004 (768d)</option>
                <option value="models/embedding-001">models/embedding-001</option>
              </select>
            </div>
          </div>
        </div>

        {/* RAG & Vector Threshold Controls */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Sliders size={20} color="#38bdf8" /> RAG & Confidence Thresholds
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem' }}>
            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>Minimum Confidence Threshold (0.0 - 1.0)</label>
              <input
                type="number"
                step="0.05"
                min="0.1"
                max="1.0"
                className="input-field"
                value={confidenceThreshold}
                onChange={(e) => setConfidenceThreshold(e.target.value)}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>Max Context Window (Tokens)</label>
              <input
                type="number"
                step="512"
                min="1024"
                max="16384"
                className="input-field"
                value={maxContextTokens}
                onChange={(e) => setMaxContextTokens(e.target.value)}
              />
            </div>
          </div>
        </div>

        {/* Security & Rate Limiting Controls */}
        <div className="glass-card" style={{ padding: '1.5rem' }}>
          <h3 style={{ fontSize: '1.125rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Shield size={20} color="#4ade80" /> Security & Rate Limiting
          </h3>

          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: '#cbd5e1', marginBottom: '0.5rem' }}>Rate Limit Max Requests / Minute</label>
            <input
              type="number"
              min="10"
              max="1000"
              className="input-field"
              value={rateLimitRequests}
              onChange={(e) => setRateLimitRequests(e.target.value)}
              style={{ maxWidth: '300px' }}
            />
          </div>
        </div>

        <button
          type="submit"
          className="btn-primary"
          disabled={isSaving}
          style={{ width: 'fit-content', padding: '0.75rem 2rem' }}
        >
          <Save size={18} />
          <span>{isSaving ? 'Saving...' : 'Save System Settings'}</span>
        </button>
      </form>
    </div>
  );
};

export default AdminSettingsPage;
