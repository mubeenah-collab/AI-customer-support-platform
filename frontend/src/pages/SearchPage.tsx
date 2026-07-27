import React, { useState } from 'react';
import { SearchBar } from '../components/search/SearchBar';
import { SearchResultCard, SearchResultItem } from '../components/search/SearchResultCard';
import { apiClient } from '../services/apiClient';
import { Search as SearchIcon, Cpu, Code, Layers } from 'lucide-react';

interface InspectionMatch {
  chunk_id: string;
  content_snippet: string;
  document_id: string;
  document_name: string;
  similarity_score: number;
  distance: number;
  relevance_percentage: string;
  metadata: Record<string, any>;
}

interface InspectionData {
  query: string;
  total_chunks_retrieved: number;
  raw_matches: InspectionMatch[];
  formatted_prompt: string;
  context_window_length: number;
  estimated_context_tokens: number;
}

export const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState<'semantic' | 'hybrid'>('semantic');
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [inspectionData, setInspectionData] = useState<InspectionData | null>(null);
  const [isInspectorActive, setIsInspectorActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setHasSearched(true);
    setInspectionData(null);

    try {
      if (isInspectorActive) {
        const res = await apiClient.post('/search/inspect', {
          query,
          top_k: topK,
        });
        setInspectionData(res.data);
      } else {
        const endpoint = searchMode === 'semantic' ? '/search/semantic' : '/search/hybrid';
        const res = await apiClient.post(endpoint, {
          query,
          top_k: topK,
        });
        const data = res.data;
        const list = Array.isArray(data) ? data : (data?.results || data?.items || []);
        setResults(Array.isArray(list) ? list : []);
      }
    } catch (err) {
      console.error('Knowledge search failed:', err);
      setResults([]);
      setInspectionData(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '950px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
            Retrieval & <span className="gradient-text">Inspector Console</span>
          </h1>
          <p style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '0.25rem' }}>
            Deep inspection of vector distances, similarity scoring, formatted RAG prompts, and LLM context windows.
          </p>
        </div>

        <button
          onClick={() => setIsInspectorActive(!isInspectorActive)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.625rem 1rem',
            borderRadius: '0.5rem',
            backgroundColor: isInspectorActive ? 'rgba(99, 102, 241, 0.2)' : 'rgba(15, 23, 42, 0.6)',
            border: isInspectorActive ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.1)',
            color: isInspectorActive ? '#818cf8' : '#94a3b8',
            fontSize: '0.875rem',
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          <Cpu size={18} /> {isInspectorActive ? 'Inspector Mode: ON' : 'Toggle Inspector'}
        </button>
      </div>

      <SearchBar
        query={query}
        setQuery={setQuery}
        searchMode={searchMode}
        setSearchMode={setSearchMode}
        topK={topK}
        setTopK={setTopK}
        onSearch={handleSearch}
        isLoading={isLoading}
      />

      {isInspectorActive && inspectionData ? (
        <div style={{ marginTop: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {/* Summary Metrics Banner */}
          <div className="glass-card" style={{ padding: '1.25rem', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '1rem', textAlign: 'center' }}>
            <div>
              <p style={{ fontSize: '0.75rem', color: '#64748b' }}>Chunks Retrieved</p>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#f8fafc' }}>{inspectionData.total_chunks_retrieved}</h3>
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', color: '#64748b' }}>Context Chars</p>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#818cf8' }}>{inspectionData.context_window_length}</h3>
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', color: '#64748b' }}>Estimated Tokens</p>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#38bdf8' }}>~{inspectionData.estimated_context_tokens}</h3>
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', color: '#64748b' }}>Top Score</p>
              <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#4ade80' }}>
                {inspectionData.raw_matches[0]?.relevance_percentage || 'N/A'}
              </h3>
            </div>
          </div>

          {/* Raw Vector Match Scores Breakdown */}
          <div className="glass-card" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Layers size={18} color="#818cf8" /> Raw Vector Distance Matches
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {inspectionData.raw_matches.map((m, idx) => (
                <div key={m.chunk_id || idx} style={{ padding: '1rem', borderRadius: '0.5rem', backgroundColor: 'rgba(15, 23, 42, 0.6)', border: '1px solid rgba(255,255,255,0.06)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.375rem', fontSize: '0.875rem' }}>
                    <span style={{ fontWeight: 600, color: '#e2e8f0' }}>{m.document_name} <span style={{ color: '#64748b', fontSize: '0.75rem' }}>(Chunk: {m.chunk_id})</span></span>
                    <span style={{ color: '#4ade80', fontWeight: 700 }}>Sim: {m.relevance_percentage} | Dist: {m.distance}</span>
                  </div>
                  <p style={{ fontSize: '0.8125rem', color: '#cbd5e1', whiteSpace: 'pre-wrap' }}>{m.content_snippet}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Formatted RAG Prompt Viewer */}
          <div className="glass-card" style={{ padding: '1.5rem' }}>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: '#f8fafc', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Code size={18} color="#38bdf8" /> Formatted Prompt & Context Window Payload
            </h3>
            <pre style={{ backgroundColor: '#090d16', padding: '1.25rem', borderRadius: '0.5rem', border: '1px solid rgba(255,255,255,0.1)', color: '#a5f3fc', fontSize: '0.8125rem', fontFamily: 'monospace', overflowX: 'auto', whiteSpace: 'pre-wrap', maxHeight: '400px' }}>
              {inspectionData.formatted_prompt}
            </pre>
          </div>
        </div>
      ) : (
        (() => {
          const safeResults = Array.isArray(results) ? results : [];
          return (
            <>
              {hasSearched && (
                <div style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
                  <span>Search Results ({safeResults.length})</span>
                  <span>Mode: <strong style={{ color: '#818cf8', textTransform: 'capitalize' }}>{searchMode}</strong></span>
                </div>
              )}

              {safeResults.map((res, idx) => (
                <SearchResultCard key={res.chunk_id || idx} result={res} />
              ))}

              {hasSearched && safeResults.length === 0 && !isLoading && (
                <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
                  <SearchIcon size={48} color="#475569" style={{ margin: '0 auto 1rem' }} />
                  <h4 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.5rem' }}>No Matches Found</h4>
                  <p style={{ fontSize: '0.875rem' }}>Try broadening your query keywords or switching between Semantic and Hybrid search modes.</p>
                </div>
              )}
            </>
          );
        })()
      )}
    </div>
  );
};
