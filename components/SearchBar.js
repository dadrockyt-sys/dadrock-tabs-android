'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { Search, X, Music, User, Loader2 } from 'lucide-react';
import Link from 'next/link';

export default function SearchBar({ variant = 'full', placeholder = 'Search artists & songs...' }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState({ artists: [], songs: [] });
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);
  const debounceRef = useRef(null);
  const router = useRouter();

  // Debounced search
  const performSearch = useCallback(async (searchQuery) => {
    if (searchQuery.length < 2) {
      setResults({ artists: [], songs: [] });
      setIsOpen(false);
      return;
    }

    setIsLoading(true);
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(searchQuery)}`);
      const data = await res.json();
      setResults(data);
      setIsOpen(data.artists.length > 0 || data.songs.length > 0);
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      performSearch(query);
    }, 300);
    return () => clearTimeout(debounceRef.current);
  }, [query, performSearch]);

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target) &&
          inputRef.current && !inputRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Keyboard navigation
  const allResults = [...results.artists.map(a => ({ type: 'artist', ...a })), ...results.songs.map(s => ({ type: 'song', ...s }))];
  
  const handleKeyDown = (e) => {
    if (!isOpen) return;
    
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, allResults.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, -1));
    } else if (e.key === 'Enter' && selectedIndex >= 0) {
      e.preventDefault();
      const item = allResults[selectedIndex];
      if (item.type === 'artist') {
        router.push(`/artist/${item.slug}`);
      } else {
        router.push(`/songs/${item.slug}`);
      }
      setIsOpen(false);
      setQuery('');
    } else if (e.key === 'Escape') {
      setIsOpen(false);
    }
  };

  const handleNavigate = (path) => {
    router.push(path);
    setIsOpen(false);
    setQuery('');
  };

  const isCompact = variant === 'compact';

  return (
    <div className={`relative ${isCompact ? 'w-full max-w-xs' : 'w-full max-w-2xl mx-auto'}`}>
      {/* Search Input */}
      <div className={`relative group ${isCompact ? '' : ''}`}>
        <Search className={`absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-amber-500 transition-colors ${isCompact ? 'w-4 h-4' : 'w-5 h-5'}`} />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => { setQuery(e.target.value); setSelectedIndex(-1); }}
          onFocus={() => { if (allResults.length > 0) setIsOpen(true); }}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          className={`w-full bg-zinc-900/80 border border-zinc-700 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 rounded-full text-white placeholder-zinc-500 outline-none transition-all ${
            isCompact ? 'pl-10 pr-8 py-2 text-sm' : 'pl-12 pr-12 py-4 text-lg'
          }`}
        />
        {isLoading && (
          <Loader2 className={`absolute right-4 top-1/2 -translate-y-1/2 text-amber-500 animate-spin ${isCompact ? 'w-4 h-4' : 'w-5 h-5'}`} />
        )}
        {!isLoading && query && (
          <button
            onClick={() => { setQuery(''); setResults({ artists: [], songs: [] }); setIsOpen(false); }}
            className={`absolute right-4 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-white transition-colors ${isCompact ? 'w-4 h-4' : 'w-5 h-5'}`}
          >
            <X className="w-full h-full" />
          </button>
        )}
      </div>

      {/* Results Dropdown */}
      {isOpen && (
        <div
          ref={dropdownRef}
          className="absolute top-full mt-2 w-full bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl shadow-black/50 overflow-hidden z-50 max-h-[400px] overflow-y-auto"
        >
          {/* Artists Section */}
          {results.artists.length > 0 && (
            <div className="p-2">
              <p className="px-3 py-1.5 text-xs font-bold text-zinc-500 uppercase tracking-wider">Artists</p>
              {results.artists.map((artist, i) => (
                <button
                  key={artist.slug}
                  onClick={() => handleNavigate(`/artist/${artist.slug}`)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-colors ${
                    selectedIndex === i ? 'bg-amber-500/10 text-amber-500' : 'hover:bg-zinc-800 text-white'
                  }`}
                >
                  <div className="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-amber-500">
                    <User className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="font-medium">{artist.name}</p>
                    <p className="text-xs text-zinc-500">Artist</p>
                  </div>
                </button>
              ))}
            </div>
          )}

          {/* Divider */}
          {results.artists.length > 0 && results.songs.length > 0 && (
            <div className="border-t border-zinc-800 mx-3" />
          )}

          {/* Songs Section */}
          {results.songs.length > 0 && (
            <div className="p-2">
              <p className="px-3 py-1.5 text-xs font-bold text-zinc-500 uppercase tracking-wider">Songs</p>
              {results.songs.map((song, i) => {
                const idx = results.artists.length + i;
                return (
                  <button
                    key={song.slug}
                    onClick={() => handleNavigate(`/songs/${song.slug}`)}
                    className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-colors ${
                      selectedIndex === idx ? 'bg-amber-500/10 text-amber-500' : 'hover:bg-zinc-800 text-white'
                    }`}
                  >
                    <div className="w-10 h-10 rounded-lg overflow-hidden flex-shrink-0 border border-zinc-700">
                      <img
                        src={song.thumbnail}
                        alt={song.title}
                        className="w-full h-full object-cover"
                      />
                    </div>
                    <div className="min-w-0">
                      <p className="font-medium truncate">{song.title}</p>
                      <p className="text-xs text-zinc-500 truncate">{song.artist}</p>
                    </div>
                    <Music className="w-4 h-4 text-zinc-600 flex-shrink-0 ml-auto" />
                  </button>
                );
              })}
            </div>
          )}

          {/* No results */}
          {results.artists.length === 0 && results.songs.length === 0 && query.length >= 2 && !isLoading && (
            <div className="p-6 text-center text-zinc-500">
              <Search className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>No results found for &quot;{query}&quot;</p>
              <p className="text-xs mt-1">Try a different artist or song name</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
