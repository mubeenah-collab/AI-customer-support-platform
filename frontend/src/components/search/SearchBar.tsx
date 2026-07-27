import React from 'react';
import { Search, Sliders, Sparkles } from 'lucide-react';

interface SearchBarProps {
  query: string;
  setQuery: (q: string) => void;
  searchMode: 'semantic' | 'hybrid';
  setSearchMode: (mode: 'semantic' | 'hybrid') => void;
  topK: number;
  setTopK: (k: number) => void;
  onSearch: () => void;
  isLoading: boolean;
}

export const SearchBar: React.FC<SearchBarProps> = ({
  query,
  setQuery,
  searchMode,
  setSearchMode,
  topK,
  setTopK,
  onSearch,
  isLoading,
}) => {
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim() && !isLoading) {
      onSearch();
    }
  };

  return (
    <div className="glass-card" style={{ padding: '1.5rem', marginBottom: '2rem' }}>
      <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <div style={{ position: 'relative', flex: 1 }}>
            <Search size={20} color="#64748b" style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)' }} />
            <input
              type="text"
              className="input-field"
              style={{ paddingLeft: '2.75rem', fontSize: '0.95rem' }}
              placeholder="Search knowledge base using semantic embeddings or hybrid query..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={isLoading || !query.trim()}
            style={{
              padding: '0.75rem 1.5rem',
              opacity: isLoading || !query.trim() ? 0.6 : 1,
              whiteSpace: 'nowrap',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontWeight: 600,
            }}
          >
            <Sparkles size={18} />
            <span>{isLoading ? 'Searching...' : 'Search'}</span>
          </button>
        </div>

        {/* Filter Controls Row */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '1rem',
            paddingTop: '1rem',
            borderTop: '1px solid rgba(255, 255, 255, 0.08)',
            fontSize: '0.875rem',
          }}
        >
          {/* Mode Segmented Controls */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', flexWrap: 'wrap' }}>
            <span style={{ color: '#94a3b8', fontWeight: 600, display: 'inline-flex', alignItems: 'center', gap: '0.375rem', whiteSpace: 'nowrap' }}>
              <Sliders size={16} color="#818cf8" /> Search Mode:
            </span>

            <div
              style={{
                display: 'inline-flex',
                backgroundColor: 'rgba(15, 23, 42, 0.8)',
                borderRadius: '0.625rem',
                padding: '0.25rem',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                gap: '0.25rem',
              }}
            >
              <button
                type="button"
                onClick={() => setSearchMode('semantic')}
                style={{
                  padding: '0.375rem 0.875rem',
                  borderRadius: '0.5rem',
                  border: 'none',
                  backgroundColor: searchMode === 'semantic' ? '#6366f1' : 'transparent',
                  color: searchMode === 'semantic' ? '#ffffff' : '#94a3b8',
                  fontSize: '0.8125rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: searchMode === 'semantic' ? '0 2px 8px rgba(99, 102, 241, 0.4)' : 'none',
                }}
              >
                Semantic (Vector)
              </button>
              <button
                type="button"
                onClick={() => setSearchMode('hybrid')}
                style={{
                  padding: '0.375rem 0.875rem',
                  borderRadius: '0.5rem',
                  border: 'none',
                  backgroundColor: searchMode === 'hybrid' ? '#6366f1' : 'transparent',
                  color: searchMode === 'hybrid' ? '#ffffff' : '#94a3b8',
                  fontSize: '0.8125rem',
                  fontWeight: 600,
                  cursor: 'pointer',
                  whiteSpace: 'nowrap',
                  transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)',
                  boxShadow: searchMode === 'hybrid' ? '0 2px 8px rgba(99, 102, 241, 0.4)' : 'none',
                }}
              >
                Hybrid (Vector + BM25)
              </button>
            </div>
          </div>

          {/* Top-K Results Slider */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', whiteSpace: 'nowrap' }}>
            <span style={{ color: '#94a3b8', fontWeight: 600 }}>Max Results (Top K):</span>
            <span
              style={{
                backgroundColor: 'rgba(99, 102, 241, 0.15)',
                color: '#a5b4fc',
                padding: '0.125rem 0.5rem',
                borderRadius: '0.375rem',
                fontWeight: 700,
                fontSize: '0.8125rem',
                border: '1px solid rgba(99, 102, 241, 0.3)',
                minWidth: '1.75rem',
                textAlign: 'center',
              }}
            >
              {topK}
            </span>
            <input
              type="range"
              min={1}
              max={20}
              value={topK}
              onChange={(e) => setTopK(Number(e.target.value))}
              style={{ accentColor: '#6366f1', cursor: 'pointer', width: '110px' }}
            />
          </div>
        </div>
      </form>
    </div>
  );
};

