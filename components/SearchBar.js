'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Search, X, Music, User, Loader2 } from 'lucide-react';

const searchCopy = {
  en: { placeholder: 'Search artists & songs...', artists: 'Artists', artist: 'Artist', songs: 'Songs', noResults: 'No results found for', tryDifferent: 'Try a different artist or song name' },
  es: { placeholder: 'Buscar artistas y canciones...', artists: 'Artistas', artist: 'Artista', songs: 'Canciones', noResults: 'No se encontraron resultados para', tryDifferent: 'Prueba con otro artista o canción' },
  pt: { placeholder: 'Pesquisar artistas e músicas...', artists: 'Artistas', artist: 'Artista', songs: 'Músicas', noResults: 'Nenhum resultado encontrado para', tryDifferent: 'Tente outro artista ou nome de música' },
  'pt-br': { placeholder: 'Pesquisar artistas e músicas...', artists: 'Artistas', artist: 'Artista', songs: 'Músicas', noResults: 'Nenhum resultado encontrado para', tryDifferent: 'Tente outro artista ou nome de música' },
  de: { placeholder: 'Künstler und Songs suchen...', artists: 'Künstler', artist: 'Künstler', songs: 'Songs', noResults: 'Keine Ergebnisse gefunden für', tryDifferent: 'Versuche einen anderen Künstler oder Songnamen' },
  fr: { placeholder: 'Rechercher des artistes et chansons...', artists: 'Artistes', artist: 'Artiste', songs: 'Chansons', noResults: 'Aucun résultat trouvé pour', tryDifferent: 'Essayez un autre artiste ou titre de chanson' },
  it: { placeholder: 'Cerca artisti e canzoni...', artists: 'Artisti', artist: 'Artista', songs: 'Canzoni', noResults: 'Nessun risultato trovato per', tryDifferent: 'Prova un altro artista o titolo di canzone' },
  ja: { placeholder: 'アーティストや曲を検索...', artists: 'アーティスト', artist: 'アーティスト', songs: '曲', noResults: '検索結果がありません:', tryDifferent: '別のアーティスト名または曲名をお試しください' },
  ko: { placeholder: '아티스트 및 곡 검색...', artists: '아티스트', artist: '아티스트', songs: '곡', noResults: '검색 결과가 없습니다:', tryDifferent: '다른 아티스트 또는 곡 이름을 검색해 보세요' },
  zh: { placeholder: '搜索艺人和歌曲...', artists: '艺人', artist: '艺人', songs: '歌曲', noResults: '未找到相关结果：', tryDifferent: '请尝试其他艺人或歌曲名称' },
  ru: { placeholder: 'Поиск исполнителей и песен...', artists: 'Исполнители', artist: 'Исполнитель', songs: 'Песни', noResults: 'Результаты не найдены для', tryDifferent: 'Попробуйте другое имя исполнителя или название песни' },
  hi: { placeholder: 'कलाकार और गाने खोजें...', artists: 'कलाकार', artist: 'कलाकार', songs: 'गाने', noResults: 'कोई परिणाम नहीं मिला:', tryDifferent: 'किसी अन्य कलाकार या गाने का नाम आज़माएँ' },
  sv: { placeholder: 'Sök artister och låtar...', artists: 'Artister', artist: 'Artist', songs: 'Låtar', noResults: 'Inga resultat hittades för', tryDifferent: 'Prova en annan artist eller låttitel' },
  fi: { placeholder: 'Hae artisteja ja kappaleita...', artists: 'Artistit', artist: 'Artisti', songs: 'Kappaleet', noResults: 'Ei tuloksia haulle', tryDifferent: 'Kokeile toista artistia tai kappaleen nimeä' },
};

export default function SearchBar({ variant = 'full', placeholder = null, currentLang = 'en' }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState({ artists: [], songs: [] });
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(-1);
  const inputRef = useRef(null);
  const dropdownRef = useRef(null);
  const debounceRef = useRef(null);
  const router = useRouter();
  const pathname = usePathname() || '/';
  const routeSegment = pathname.split('/').filter(Boolean)[0] || 'en';
  const routeLang = searchCopy[routeSegment] ? routeSegment : 'en';
  const effectiveLang = currentLang !== 'en' ? currentLang : routeLang;
  const prefix = effectiveLang === 'en' ? '' : `/${effectiveLang}`;
  const copy = searchCopy[effectiveLang] || searchCopy.en;
  const isLegacyEnglishPlaceholder = placeholder === searchCopy.en.placeholder;
  const effectivePlaceholder = effectiveLang !== 'en' && (!placeholder || isLegacyEnglishPlaceholder)
    ? copy.placeholder
    : (placeholder || copy.placeholder);

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
        router.push(`${prefix}/artist/${item.slug}`);
      } else {
        router.push(`${prefix}/songs/${item.slug}`);
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
      <div className="relative group">
        <Search className={`absolute left-4 top-1/2 -translate-y-1/2 text-zinc-500 group-focus-within:text-amber-500 transition-colors ${isCompact ? 'w-4 h-4' : 'w-5 h-5'}`} />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => { setQuery(e.target.value); setSelectedIndex(-1); }}
          onFocus={() => { if (allResults.length > 0) setIsOpen(true); }}
          onKeyDown={handleKeyDown}
          placeholder={effectivePlaceholder}
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
            aria-label="Clear search"
          >
            <X className="w-full h-full" />
          </button>
        )}
      </div>

      {isOpen && (
        <div
          ref={dropdownRef}
          className="absolute top-full mt-2 w-full bg-zinc-900 border border-zinc-700 rounded-2xl shadow-2xl shadow-black/50 overflow-hidden z-50 max-h-[400px] overflow-y-auto"
        >
          {results.artists.length > 0 && (
            <div className="p-2">
              <p className="px-3 py-1.5 text-xs font-bold text-zinc-500 uppercase tracking-wider">{copy.artists}</p>
              {results.artists.map((artist, i) => (
                <button
                  key={artist.slug}
                  onClick={() => handleNavigate(`${prefix}/artist/${artist.slug}`)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-left transition-colors ${
                    selectedIndex === i ? 'bg-amber-500/10 text-amber-500' : 'hover:bg-zinc-800 text-white'
                  }`}
                >
                  <div className="w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center text-amber-500">
                    <User className="w-4 h-4" />
                  </div>
                  <div>
                    <p className="font-medium">{artist.name}</p>
                    <p className="text-xs text-zinc-500">{copy.artist}</p>
                  </div>
                </button>
              ))}
            </div>
          )}

          {results.artists.length > 0 && results.songs.length > 0 && (
            <div className="border-t border-zinc-800 mx-3" />
          )}

          {results.songs.length > 0 && (
            <div className="p-2">
              <p className="px-3 py-1.5 text-xs font-bold text-zinc-500 uppercase tracking-wider">{copy.songs}</p>
              {results.songs.map((song, i) => {
                const idx = results.artists.length + i;
                return (
                  <div key={song.slug}>
                    <button
                      onClick={() => handleNavigate(`${prefix}/songs/${song.slug}`)}
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
                  </div>
                );
              })}
            </div>
          )}

          {results.artists.length === 0 && results.songs.length === 0 && query.length >= 2 && !isLoading && (
            <div className="p-6 text-center text-zinc-500">
              <Search className="w-8 h-8 mx-auto mb-2 opacity-50" />
              <p>{copy.noResults} &quot;{query}&quot;</p>
              <p className="text-xs mt-1">{copy.tryDifferent}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
