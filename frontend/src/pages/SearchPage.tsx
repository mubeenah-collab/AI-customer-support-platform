import React, { useState } from 'react';
import { SearchBar } from '../components/search/SearchBar';
import { SearchResultCard, SearchResultItem } from '../components/search/SearchResultCard';
import { apiClient } from '../services/apiClient';
import { Search as SearchIcon } from 'lucide-react';

export const SearchPage: React.FC = () => {
  const [query, setQuery] = useState('');
  const [searchMode, setSearchMode] = useState<'semantic' | 'hybrid'>('semantic');
  const [topK, setTopK] = useState(5);
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;

    setIsLoading(true);
    setHasSearched(true);

    try {
      const endpoint = searchMode === 'semantic' ? '/search/semantic' : '/search/hybrid';
      const res = await apiClient.post(endpoint, {
        query,
        top_k: topK,
      });

      setResults(res.data.results || res.data.items || res.data || []);
    } catch (err) {
      console.error('Knowledge search failed:', err);
      setResults([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
          Semantic & Hybrid <span className="gradient-text">Search</span>
        </h1>
        <p style={{ color: '#94a3b8', fontSize: '0.95rem', marginTop: '0.25rem' }}>
          Query vector embeddings across indexed knowledge base documents with precision similarity scoring.
        </p>
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

      {hasSearched && (
        <div style={{ marginBottom: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#94a3b8', fontSize: '0.875rem' }}>
          <span>Search Results ({results.length})</span>
          <span>Mode: <strong style={{ color: '#818cf8', textTransform: 'capitalize' }}>{searchMode}</strong></span>
        </div>
      )}

      {results.map((res, idx) => (
        <SearchResultCard key={res.chunk_id || idx} result={res} />
      ))}

      {hasSearched && results.length === 0 && !isLoading && (
        <div className="glass-card" style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
          <SearchIcon size={48} color="#475569" style={{ margin: '0 auto 1rem' }} />
          <h4 style={{ fontSize: '1.125rem', fontWeight: 600, color: '#cbd5e1', marginBottom: '0.5rem' }}>No Matches Found</h4>
          <p style={{ fontSize: '0.875rem' }}>Try broadening your query keywords or switching between Semantic and Hybrid search modes.</p>
        </div>
      )}
    </div>
  );
};
