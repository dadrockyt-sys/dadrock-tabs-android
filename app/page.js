'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Search, ShoppingBag, Youtube, Share2, Heart, MessageSquarePlus, Mail, Globe, ChevronDown, Play, User, ArrowLeft, Lock, Save, AlertCircle, CheckCircle, Music, LogOut, Settings } from 'lucide-react';
import { getTranslation, locales, localeNames, localeFlags } from '@/lib/i18n';

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";
const BANNER_URL = "https://customer-assets.emergentagent.com/job_7476b4fe-b760-45e6-bd6e-bcf2b5ed2e77/artifacts/4hju7m2h_Screenshot_20260217_064912_YouTube.jpg";
const YOUTUBE_CHANNEL = "https://www.youtube.com/@DadRockTabs?sub_confirmation=1";

const popularArtists = [
  { name: "Led Zeppelin", emoji: "guitar" },
  { name: "AC/DC", emoji: "zap" },
  { name: "Van Halen", emoji: "flame" },
  { name: "Def Leppard", emoji: "music" },
  { name: "Ozzy Osbourne", emoji: "bat" },
  { name: "Metallica", emoji: "metal" },
  { name: "Black Sabbath", emoji: "skull" },
  { name: "Aerosmith", emoji: "gem" },
];

// Language Selector Component
function LanguageSelector({ currentLang, onLanguageChange }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-sm font-medium text-zinc-300 hover:text-white bg-zinc-900/80 hover:bg-zinc-800 backdrop-blur-sm rounded-md transition-all border border-zinc-700/50"
      >
        <Globe className="w-4 h-4" />
        <span className="hidden sm:inline">{localeFlags[currentLang]}</span>
        <span className="hidden md:inline text-xs uppercase">{currentLang}</span>
        <ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-44 bg-zinc-900 border border-zinc-700 rounded-lg shadow-xl overflow-hidden z-50">
          <div className="py-1">
            {locales.map((lang) => (
              <button
                key={lang}
                onClick={() => { onLanguageChange(lang); setIsOpen(false); }}
                className={`w-full flex items-center gap-3 px-3 py-2 text-sm transition-colors ${
                  lang === currentLang
                    ? "bg-primary/20 text-primary"
                    : "text-zinc-300 hover:bg-zinc-800 hover:text-white"
                }`}
              >
                <span className="text-lg">{localeFlags[lang]}</span>
                <span className="flex-1 text-left">{localeNames[lang]}</span>
                {lang === currentLang && <span className="text-primary">check</span>}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// Video Card Component
function VideoCard({ video, onClick }) {
  return (
    <div
      className="video-card group flex items-center gap-3 p-2 bg-card/50 hover:bg-card rounded-lg border border-white/5 cursor-pointer transition-all"
      onClick={() => onClick(video)}
    >
      <div className="relative w-24 h-16 sm:w-28 sm:h-[72px] flex-shrink-0 overflow-hidden rounded-md">
        <img
          src={video.thumbnail || `https://img.youtube.com/vi/default/mqdefault.jpg`}
          alt={video.song}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center">
            <Play className="w-4 h-4 text-primary-foreground ml-0.5" fill="currentColor" />
          </div>
        </div>
      </div>

      <div className="flex-1 min-w-0 py-1">
        <h3 className="font-heading text-sm sm:text-base font-bold uppercase tracking-tight text-white truncate group-hover:text-primary transition-colors">
          {video.song}
        </h3>
        <div className="flex items-center gap-1.5 mt-1 text-muted-foreground">
          <User className="w-3 h-3 flex-shrink-0" />
          <span className="text-xs sm:text-sm truncate">{video.artist}</span>
        </div>
      </div>
    </div>
  );
}

// Main App Component
export default function App() {
  const router = useRouter();
  const [currentPage, setCurrentPage] = useState('home');
  const [currentLang, setCurrentLang] = useState('en');
  const [searchQuery, setSearchQuery] = useState('');
  const [featuredVideo, setFeaturedVideo] = useState(null);
  const [logoClickCount, setLogoClickCount] = useState(0);
  
  // Search page state
  const [searchResults, setSearchResults] = useState([]);
  const [searchType, setSearchType] = useState('all');
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [activeSearch, setActiveSearch] = useState('');
  
  // Watch page state
  const [selectedVideo, setSelectedVideo] = useState(null);
  
  // Admin page state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [featuredVideoUrl, setFeaturedVideoUrl] = useState('');
  const [featuredVideoTitle, setFeaturedVideoTitle] = useState('');
  const [featuredVideoArtist, setFeaturedVideoArtist] = useState('');
  const [saveStatus, setSaveStatus] = useState({ type: '', message: '' });
  const [isSaving, setIsSaving] = useState(false);
  const [stats, setStats] = useState({ total_videos: 0, total_artists: 0 });

  const t = getTranslation(currentLang);

  // Load featured video on mount
  useEffect(() => {
    fetch('/api/settings')
      .then(res => res.ok ? res.json() : null)
      .then(data => {
        if (data) {
          setFeaturedVideo({
            url: data.featured_video_url,
            title: data.featured_video_title,
            artist: data.featured_video_artist
          });
        }
      })
      .catch(() => {});
  }, []);

  // Check admin auth on mount
  useEffect(() => {
    const authToken = sessionStorage.getItem('dadrock_admin_auth');
    if (authToken) {
      setIsAuthenticated(true);
    }
  }, []);

  const getYouTubeEmbedUrl = (url) => {
    if (!url) return null;
    if (url.includes('/embed/')) return url;
    const videoIdMatch = url.match(/(?:youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
    return videoIdMatch ? `https://www.youtube.com/embed/${videoIdMatch[1]}` : url;
  };

  // Search functionality
  const performSearch = async (query, type = 'all') => {
    if (!query.trim()) return;
    setLoading(true);
    setActiveSearch(query);
    try {
      const response = await fetch(`/api/videos?search=${encodeURIComponent(query)}&search_type=${type}&limit=100`);
      const data = await response.json();
      setSearchResults(data.videos || []);
      setTotalCount(data.total || 0);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      setCurrentPage('search');
      performSearch(searchQuery, searchType);
    }
  };

  const handleArtistClick = (artist) => {
    setSearchQuery(artist);
    setSearchType('artist');
    setCurrentPage('search');
    performSearch(artist, 'artist');
  };

  const handleVideoClick = (video) => {
    setSelectedVideo(video);
    setCurrentPage('watch');
  };

  const handleLogoClick = () => {
    setLogoClickCount(prev => {
      if (prev + 1 >= 5) {
        setCurrentPage('admin');
        return 0;
      }
      return prev + 1;
    });
  };

  // Admin functions
  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoggingIn(true);
    setAuthError('');

    try {
      const res = await fetch('/api/admin/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      });

      if (res.ok) {
        sessionStorage.setItem('dadrock_admin_auth', password);
        setIsAuthenticated(true);
        loadAdminData();
      } else {
        setAuthError('Invalid password');
      }
    } catch (err) {
      setAuthError('Connection error. Please try again.');
    } finally {
      setIsLoggingIn(false);
    }
  };

  const handleLogout = () => {
    sessionStorage.removeItem('dadrock_admin_auth');
    setIsAuthenticated(false);
    setPassword('');
    setCurrentPage('home');
  };

  const loadAdminData = async () => {
    // Load settings
    try {
      const res = await fetch('/api/settings');
      if (res.ok) {
        const data = await res.json();
        setFeaturedVideoUrl(data.featured_video_url || '');
        setFeaturedVideoTitle(data.featured_video_title || '');
        setFeaturedVideoArtist(data.featured_video_artist || '');
      }
    } catch (err) {}

    // Load stats
    try {
      const authToken = sessionStorage.getItem('dadrock_admin_auth');
      const res = await fetch('/api/admin/stats', {
        headers: { 'Authorization': 'Basic ' + btoa('admin:' + authToken) },
      });
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {}
  };

  const handleSaveSettings = async (e) => {
    e.preventDefault();
    setIsSaving(true);
    setSaveStatus({ type: '', message: '' });

    try {
      const authToken = sessionStorage.getItem('dadrock_admin_auth');
      const res = await fetch('/api/admin/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Basic ' + btoa('admin:' + authToken),
        },
        body: JSON.stringify({
          featured_video_url: featuredVideoUrl,
          featured_video_title: featuredVideoTitle,
          featured_video_artist: featuredVideoArtist,
        }),
      });

      if (res.ok) {
        setSaveStatus({ type: 'success', message: 'Settings saved successfully!' });
        // Update featured video display
        setFeaturedVideo({
          url: featuredVideoUrl,
          title: featuredVideoTitle,
          artist: featuredVideoArtist
        });
      } else {
        setSaveStatus({ type: 'error', message: 'Failed to save settings' });
      }
    } catch (err) {
      setSaveStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    if (currentPage === 'admin' && isAuthenticated) {
      loadAdminData();
    }
  }, [currentPage, isAuthenticated]);

  const embedUrl = getYouTubeEmbedUrl(featuredVideo?.url);
  const embedPreviewUrl = getYouTubeEmbedUrl(featuredVideoUrl);

  // Home Page
  if (currentPage === 'home') {
    return (
      <div className="min-h-screen relative bg-black">
        <div className="min-h-screen relative">
          <div className="relative z-10 flex flex-col min-h-screen">
            {/* Header */}
            <header className="relative pt-8 sm:pt-0">
              <div className="w-full h-14 sm:h-16 md:h-20 lg:h-24 overflow-hidden bg-black">
                <img src={BANNER_URL} alt="DadRock Guitar Tabs Banner" className="w-full h-full object-contain" />
              </div>

              <div className="flex sm:hidden justify-end gap-2 px-4 py-2 bg-black">
                <LanguageSelector currentLang={currentLang} onLanguageChange={setCurrentLang} />
                <a href="https://my-store-b8bb42.creator-spring.com" target="_blank" rel="noopener noreferrer"
                   className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-primary hover:text-primary/80 bg-zinc-900/80 backdrop-blur-sm rounded-md transition-colors border border-zinc-700/50">
                  <ShoppingBag className="w-4 h-4" />
                </a>
              </div>

              <div className="hidden sm:flex absolute top-4 right-4 gap-2 z-20">
                <LanguageSelector currentLang={currentLang} onLanguageChange={setCurrentLang} />
                <a href="https://my-store-b8bb42.creator-spring.com" target="_blank" rel="noopener noreferrer"
                   className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-primary hover:text-primary/80 bg-black/50 backdrop-blur-sm rounded-md transition-colors">
                  <ShoppingBag className="w-4 h-4" />
                  <span>{t.supportMerch}</span>
                </a>
              </div>
            </header>

            {/* Main Content */}
            <main className="flex-1 flex flex-col items-center justify-center px-4 pt-4 md:pt-8 lg:pt-12">
              {/* Logo */}
              <div className="w-full flex justify-center mb-6 md:mb-8 fade-in">
                <img src={LOGO_URL} alt="DadRock Tabs Logo" onClick={handleLogoClick}
                     className="w-48 sm:w-56 md:w-72 lg:w-80 xl:w-96 drop-shadow-[0_0_50px_rgba(245,158,11,0.4)] cursor-pointer select-none hover:drop-shadow-[0_0_60px_rgba(245,158,11,0.6)] transition-all duration-300" />
              </div>

              {/* Definition */}
              <div className="w-full max-w-4xl mb-6 md:mb-8 fade-in px-4">
                <div className="flex flex-col items-center text-center">
                  <div>
                    <h2 className="font-heading text-xl sm:text-2xl md:text-3xl lg:text-4xl font-bold text-white tracking-tight">
                      {t.definition.term} <span className="text-primary font-normal text-sm sm:text-base md:text-xl lg:text-2xl">{t.definition.pronunciation}</span>
                    </h2>
                    <p className="text-muted-foreground italic mt-1 text-xs sm:text-sm">{t.definition.partOfSpeech}</p>
                    <p className="text-white/90 text-sm sm:text-base md:text-lg mt-1 md:mt-2 max-w-md leading-relaxed">
                      {t.definition.meaning}
                    </p>
                  </div>
                </div>
                <p className="text-sm md:text-base lg:text-lg text-muted-foreground text-center mt-4 md:mt-6 max-w-2xl mx-auto">
                  {t.tagline}
                </p>
              </div>

              {/* Search Form */}
              <form onSubmit={handleSearch} className="w-full max-w-3xl fade-in stagger-1">
                <div className="flex flex-col md:flex-row gap-4">
                  <div className="flex-1 relative">
                    <Search className="absolute left-6 top-1/2 -translate-y-1/2 w-6 h-6 text-muted-foreground" />
                    <input type="text" placeholder={t.searchPlaceholder} value={searchQuery}
                           onChange={(e) => setSearchQuery(e.target.value)}
                           className="w-full h-16 text-lg md:text-xl bg-black/50 border-2 border-white/20 focus:border-primary rounded-full pl-16 pr-6 text-white placeholder:text-white/40 backdrop-blur-md outline-none search-input" />
                  </div>
                  <button type="submit" className="h-16 px-10 rounded-full bg-primary text-primary-foreground hover:bg-primary/90 font-heading text-lg uppercase tracking-wider font-bold transition-all">
                    {t.searchButton}
                  </button>
                </div>
              </form>

              {/* Subscribe Button */}
              <div className="mt-6 fade-in stagger-2">
                <a href={YOUTUBE_CHANNEL} target="_blank" rel="noopener noreferrer"
                   className="inline-flex items-center gap-3 px-8 py-4 rounded-full bg-red-600 hover:bg-red-700 text-white font-heading text-lg uppercase tracking-wider transition-all">
                  <Youtube className="w-6 h-6" />
                  {t.subscribe}
                </a>
              </div>

              {/* Featured Video */}
              {embedUrl && (
                <div className="w-full max-w-2xl mt-10 fade-in stagger-3">
                  <h3 className="text-center text-muted-foreground mb-4 flex items-center justify-center gap-2">
                    <span>Film</span> {t.featuredLesson}
                  </h3>
                  <div className="relative aspect-video rounded-xl overflow-hidden border border-white/10">
                    <iframe src={embedUrl} title={featuredVideo?.title || "Featured Video"} className="absolute inset-0 w-full h-full"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
                  </div>
                  {featuredVideo?.title && (
                    <p className="text-center mt-3 text-white/80">
                      Guitar "{featuredVideo.title}" by {featuredVideo.artist}
                    </p>
                  )}
                </div>
              )}

              {/* Popular Artists */}
              <div className="w-full max-w-3xl mt-10 fade-in stagger-4">
                <h3 className="text-center text-muted-foreground mb-4 flex items-center justify-center gap-2">
                  <span>Fire</span> {t.popularSearches}
                </h3>
                <div className="flex flex-wrap justify-center gap-3">
                  {popularArtists.map((artist) => (
                    <button key={artist.name} onClick={() => handleArtistClick(artist.name)}
                            className="px-4 py-2 rounded-full bg-card hover:bg-card/80 border border-white/10 hover:border-primary/50 text-sm transition-all">
                      {artist.name}
                    </button>
                  ))}
                </div>
              </div>

              {/* Share Section */}
              <div className="mt-10 text-center fade-in stagger-5">
                <p className="text-muted-foreground mb-4">Share {t.shareDadRock}</p>
                <div className="flex justify-center gap-4">
                  <button onClick={() => navigator.share?.({ url: window.location.href, title: 'DadRock Tabs' })}
                          className="w-12 h-12 rounded-full bg-zinc-700 hover:bg-zinc-600 flex items-center justify-center transition-colors">
                    <Share2 className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="w-full max-w-md mt-10 space-y-4">
                <a href="https://buymeacoffee.com/dadrocktabs" target="_blank" rel="noopener noreferrer"
                   className="flex items-center justify-center gap-3 w-full py-4 rounded-full bg-primary hover:bg-primary/90 text-primary-foreground font-heading text-lg uppercase tracking-wider transition-all">
                  <MessageSquarePlus className="w-5 h-5" />
                  {t.makeRequest}
                </a>
                <div className="flex gap-4">
                  <a href="https://buymeacoffee.com/dadrocktabs" target="_blank" rel="noopener noreferrer"
                     className="flex-1 flex items-center justify-center gap-2 py-3 rounded-full bg-card hover:bg-card/80 border border-white/10 transition-all">
                    <Heart className="w-4 h-4 text-red-500" />
                    {t.support}
                  </a>
                  <a href="https://my-store-b8bb42.creator-spring.com" target="_blank" rel="noopener noreferrer"
                     className="flex-1 flex items-center justify-center gap-2 py-3 rounded-full bg-card hover:bg-card/80 border border-white/10 transition-all">
                    <ShoppingBag className="w-4 h-4 text-primary" />
                    {t.merchandise}
                  </a>
                </div>
              </div>
            </main>

            {/* Footer */}
            <footer className="p-6 text-center space-y-4">
              <a href="mailto:Dadrockyt@gmail.com"
                 className="inline-flex items-center gap-2 px-6 py-2 text-sm font-medium text-zinc-400 hover:text-white bg-zinc-900/50 hover:bg-zinc-800 rounded-full transition-all border border-zinc-700/50">
                <Mail className="w-4 h-4" />
                {t.contact}
              </a>
              <p className="text-sm text-muted-foreground">{t.footer}</p>
            </footer>
          </div>
        </div>
      </div>
    );
  }

  // Search Page
  if (currentPage === 'search') {
    return (
      <div className="min-h-screen bg-black">
        <header className="sticky top-0 z-50 bg-black/90 backdrop-blur-md border-b border-white/5">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center gap-4">
              <button onClick={() => setCurrentPage('home')} className="text-muted-foreground hover:text-white transition-colors">
                <ArrowLeft className="w-6 h-6" />
              </button>

              <button onClick={() => setCurrentPage('home')}>
                <img src={LOGO_URL} alt="DadRock Tabs" className="w-10 h-10 md:w-12 md:h-12" />
              </button>

              <form onSubmit={(e) => { e.preventDefault(); performSearch(searchQuery, searchType); }} className="flex-1 flex items-center gap-2">
                <div className="flex-1 relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground" />
                  <input type="text" placeholder={t.searchPlaceholder} value={searchQuery}
                         onChange={(e) => setSearchQuery(e.target.value)}
                         className="w-full h-12 bg-card border border-white/10 focus:border-primary rounded-full pl-12 pr-4 text-white placeholder:text-white/40 outline-none" />
                </div>

                <select value={searchType} onChange={(e) => setSearchType(e.target.value)}
                        className="h-12 px-4 rounded-full bg-card border border-white/10 text-white outline-none cursor-pointer">
                  <option value="all">All</option>
                  <option value="song">Song</option>
                  <option value="artist">Artist</option>
                </select>

                <button type="submit" className="h-12 px-6 rounded-full bg-primary text-primary-foreground hover:bg-primary/90">
                  {t.searchButton}
                </button>
              </form>

              <LanguageSelector currentLang={currentLang} onLanguageChange={setCurrentLang} />
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-8">
          {activeSearch && (
            <div className="mb-6">
              <h1 className="font-heading text-2xl md:text-3xl font-bold uppercase">
                {t.resultsFor} "{activeSearch}"
              </h1>
              <p className="text-muted-foreground mt-1">
                {totalCount} {t.videosFound}
              </p>
            </div>
          )}

          {loading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {[...Array(12)].map((_, i) => (
                <div key={i} className="flex items-center gap-3 p-2 bg-card/50 rounded-lg animate-pulse">
                  <div className="w-24 h-16 sm:w-28 sm:h-[72px] rounded-md bg-zinc-800 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="h-4 w-3/4 bg-zinc-800 rounded mb-2" />
                    <div className="h-3 w-1/2 bg-zinc-800 rounded" />
                  </div>
                </div>
              ))}
            </div>
          )}

          {!loading && searchResults.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {searchResults.map((video, index) => (
                <div key={video.id} className={`fade-in stagger-${(index % 5) + 1}`}>
                  <VideoCard video={video} onClick={handleVideoClick} />
                </div>
              ))}
            </div>
          )}

          {!loading && activeSearch && searchResults.length === 0 && (
            <div className="text-center py-20">
              <p className="text-muted-foreground text-lg">{t.noResults}</p>
              <p className="text-sm mt-2">{t.tryDifferent}</p>
            </div>
          )}
        </main>
      </div>
    );
  }

  // Watch Page
  if (currentPage === 'watch' && selectedVideo) {
    const watchEmbedUrl = getYouTubeEmbedUrl(selectedVideo.youtube_url);

    return (
      <div className="min-h-screen bg-black">
        <header className="sticky top-0 z-50 bg-black/90 backdrop-blur-md border-b border-white/5">
          <div className="max-w-4xl mx-auto px-4 py-4">
            <div className="flex items-center gap-4">
              <button onClick={() => setCurrentPage('search')} className="text-muted-foreground hover:text-white transition-colors">
                <ArrowLeft className="w-6 h-6" />
              </button>
              <button onClick={() => setCurrentPage('home')}>
                <img src={LOGO_URL} alt="DadRock Tabs" className="w-10 h-10" />
              </button>
              <div className="flex-1" />
              <LanguageSelector currentLang={currentLang} onLanguageChange={setCurrentLang} />
            </div>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center mb-8">
            <h1 className="font-heading text-2xl md:text-4xl font-bold uppercase text-primary">
              {selectedVideo.song}
            </h1>
            <p className="text-muted-foreground mt-2 text-lg">by {selectedVideo.artist}</p>
          </div>

          <div className="aspect-video rounded-xl overflow-hidden border border-white/10 mb-8">
            <iframe src={watchEmbedUrl} title={selectedVideo.song} className="w-full h-full"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href={selectedVideo.youtube_url} target="_blank" rel="noopener noreferrer"
               className="inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full bg-red-600 hover:bg-red-700 text-white font-heading text-lg uppercase tracking-wider transition-all">
              <Youtube className="w-6 h-6" />
              {t.watchOn}
            </a>
            <button onClick={() => setCurrentPage('search')}
                    className="inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full bg-card hover:bg-card/80 border border-white/10 font-heading text-lg uppercase tracking-wider transition-all">
              <ArrowLeft className="w-5 h-5" />
              {t.goBack}
            </button>
          </div>
        </main>
      </div>
    );
  }

  // Admin Page
  if (currentPage === 'admin') {
    if (!isAuthenticated) {
      return (
        <div className="min-h-screen bg-black flex items-center justify-center p-4">
          <div className="w-full max-w-md">
            <div className="flex justify-center mb-8">
              <button onClick={() => setCurrentPage('home')}>
                <img src={LOGO_URL} alt="DadRock Tabs" className="w-32 drop-shadow-[0_0_30px_rgba(245,158,11,0.4)]" />
              </button>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8">
              <div className="flex items-center justify-center gap-3 mb-6">
                <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center">
                  <Lock className="w-6 h-6 text-primary" />
                </div>
                <h1 className="text-2xl font-bold text-white">Admin Login</h1>
              </div>

              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Password</label>
                  <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
                         className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-primary"
                         placeholder="Enter admin password" required />
                </div>

                {authError && (
                  <div className="flex items-center gap-2 text-red-400 text-sm">
                    <AlertCircle className="w-4 h-4" />
                    {authError}
                  </div>
                )}

                <button type="submit" disabled={isLoggingIn}
                        className="w-full py-3 bg-primary text-black font-bold rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50">
                  {isLoggingIn ? 'Logging in...' : 'Login'}
                </button>
              </form>

              <div className="mt-6 text-center">
                <button onClick={() => setCurrentPage('home')} className="text-zinc-400 hover:text-white text-sm inline-flex items-center gap-2">
                  <ArrowLeft className="w-4 h-4" />
                  Back to Home
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-black">
        <header className="bg-zinc-900 border-b border-zinc-800 px-6 py-4">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button onClick={() => setCurrentPage('home')}>
                <img src={LOGO_URL} alt="DadRock Tabs" className="w-12" />
              </button>
              <div>
                <h1 className="text-xl font-bold text-white flex items-center gap-2">
                  <Settings className="w-5 h-5 text-primary" />
                  Admin Panel
                </h1>
                <p className="text-sm text-zinc-400">Manage your site settings</p>
              </div>
            </div>

            <button onClick={handleLogout}
                    className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-zinc-300 hover:text-white transition-colors">
              <LogOut className="w-4 h-4" />
              Logout
            </button>
          </div>
        </header>

        <main className="max-w-6xl mx-auto px-6 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-red-500/20 rounded-full flex items-center justify-center">
                  <Youtube className="w-6 h-6 text-red-500" />
                </div>
                <div>
                  <p className="text-sm text-zinc-400">Total Videos</p>
                  <p className="text-3xl font-bold text-white">{stats.total_videos.toLocaleString()}</p>
                </div>
              </div>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <p className="text-sm text-zinc-400">Total Artists</p>
                  <p className="text-3xl font-bold text-white">{stats.total_artists.toLocaleString()}</p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <Music className="w-5 h-5 text-primary" />
              Featured Video Settings
            </h2>

            <form onSubmit={handleSaveSettings} className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-zinc-400 mb-2">YouTube Video URL</label>
                    <input type="text" value={featuredVideoUrl} onChange={(e) => setFeaturedVideoUrl(e.target.value)}
                           className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-primary"
                           placeholder="https://youtube.com/watch?v=..." />
                  </div>

                  <div>
                    <label className="block text-sm text-zinc-400 mb-2">Song Title</label>
                    <input type="text" value={featuredVideoTitle} onChange={(e) => setFeaturedVideoTitle(e.target.value)}
                           className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-primary"
                           placeholder="We Will Rock You" />
                  </div>

                  <div>
                    <label className="block text-sm text-zinc-400 mb-2">Artist Name</label>
                    <input type="text" value={featuredVideoArtist} onChange={(e) => setFeaturedVideoArtist(e.target.value)}
                           className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-primary"
                           placeholder="Queen" />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Preview</label>
                  {embedPreviewUrl ? (
                    <div className="aspect-video rounded-lg overflow-hidden border border-zinc-700">
                      <iframe src={embedPreviewUrl} title="Featured Video Preview" className="w-full h-full"
                              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowFullScreen />
                    </div>
                  ) : (
                    <div className="aspect-video rounded-lg border border-zinc-700 bg-zinc-800 flex items-center justify-center">
                      <p className="text-zinc-500">Enter a YouTube URL to see preview</p>
                    </div>
                  )}
                </div>
              </div>

              {saveStatus.message && (
                <div className={`flex items-center gap-2 p-3 rounded-lg ${
                  saveStatus.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                }`}>
                  {saveStatus.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                  {saveStatus.message}
                </div>
              )}

              <button type="submit" disabled={isSaving}
                      className="flex items-center justify-center gap-2 px-8 py-3 bg-primary text-black font-bold rounded-lg hover:bg-primary/90 transition-colors disabled:opacity-50">
                <Save className="w-5 h-5" />
                {isSaving ? 'Saving...' : 'Save Settings'}
              </button>
            </form>
          </div>

          <div className="mt-8 text-center">
            <button onClick={() => setCurrentPage('home')} className="text-zinc-400 hover:text-white inline-flex items-center gap-2">
              <ArrowLeft className="w-4 h-4" />
              Back to Home
            </button>
          </div>
        </main>
      </div>
    );
  }

  return null;
}
