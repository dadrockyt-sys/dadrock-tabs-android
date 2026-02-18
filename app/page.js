'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { Search, ShoppingBag, Youtube, Share2, Heart, MessageSquarePlus, Mail, Globe, ChevronDown, Play, User, ArrowLeft, Lock, Save, AlertCircle, CheckCircle, Music, LogOut, Settings, Facebook, Twitter } from 'lucide-react';
import { getTranslation, locales, localeNames, localeFlags } from '@/lib/i18n';

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";
const DADROCK_TEXT_URL = "https://customer-assets.emergentagent.com/job_nextjs-deploy-3/artifacts/2vno1305_Picsart_26-02-16_06-05-32-255%281%29.png";
const BANNER_URL = "https://customer-assets.emergentagent.com/job_nextjs-deploy-3/artifacts/q10t8nk7_Picsart_26-02-17_18-51-12-061.png";
const YOUTUBE_CHANNEL = "https://youtube.com/@dadrockytofficial?si=AM8uj6DTefJcP8oZ";

const popularArtists = [
  { name: "Led Zeppelin", emoji: "🎸" },
  { name: "AC/DC", emoji: "⚡" },
  { name: "Van Halen", emoji: "🔥" },
  { name: "Def Leppard", emoji: "🎵" },
  { name: "Ozzy Osbourne", emoji: "🦇" },
  { name: "Metallica", emoji: "🤘" },
  { name: "Black Sabbath", emoji: "🖤" },
  { name: "Aerosmith", emoji: "💎" },
];

// Language Selector Component with SEO-friendly URLs
function LanguageSelector({ currentLang }) {
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();

  const handleLanguageChange = (lang) => {
    setIsOpen(false);
    if (lang === 'en') {
      router.push('/');
    } else {
      router.push(`/${lang}`);
    }
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-sm font-medium text-zinc-300 hover:text-white bg-zinc-800/80 hover:bg-zinc-700 rounded-md transition-all border border-zinc-700/50"
      >
        <Globe className="w-4 h-4" />
        <span>{localeFlags[currentLang]}</span>
        <span className="text-xs uppercase">{currentLang}</span>
        <ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-44 bg-zinc-900 border border-zinc-700 rounded-lg shadow-xl overflow-hidden z-50">
          <div className="py-1">
            {locales.map((lang) => (
              <button
                key={lang}
                onClick={() => handleLanguageChange(lang)}
                className={`w-full flex items-center gap-3 px-3 py-2 text-sm transition-colors ${
                  lang === currentLang
                    ? "bg-amber-500/20 text-amber-500"
                    : "text-zinc-300 hover:bg-zinc-800 hover:text-white"
                }`}
              >
                <span className="text-lg">{localeFlags[lang]}</span>
                <span className="flex-1 text-left">{localeNames[lang]}</span>
                {lang === currentLang && <span className="text-amber-500">✓</span>}
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
      className="video-card group flex items-center gap-3 p-2 bg-zinc-900/50 hover:bg-zinc-800 rounded-lg border border-zinc-800 cursor-pointer transition-all"
      onClick={() => onClick(video)}
    >
      <div className="relative w-24 h-16 sm:w-28 sm:h-[72px] flex-shrink-0 overflow-hidden rounded-md">
        <img
          src={video.thumbnail || `https://img.youtube.com/vi/default/mqdefault.jpg`}
          alt={video.song}
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        />
        <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
          <div className="w-8 h-8 rounded-full bg-amber-500 flex items-center justify-center">
            <Play className="w-4 h-4 text-black ml-0.5" fill="currentColor" />
          </div>
        </div>
      </div>

      <div className="flex-1 min-w-0 py-1">
        <h3 className="font-bold text-sm sm:text-base text-white truncate group-hover:text-amber-500 transition-colors uppercase tracking-wide">
          {video.song}
        </h3>
        <div className="flex items-center gap-1.5 mt-1 text-zinc-400">
          <User className="w-3 h-3 flex-shrink-0" />
          <span className="text-xs sm:text-sm truncate">{video.artist}</span>
        </div>
      </div>
    </div>
  );
}

// Main App Component
export default function App({ initialLang = 'en' }) {
  const router = useRouter();
  const pathname = usePathname();
  const [currentPage, setCurrentPage] = useState('home');
  const [currentLang, setCurrentLang] = useState(initialLang);
  const [searchQuery, setSearchQuery] = useState('');
  const [logoClickCount, setLogoClickCount] = useState(0);
  
  // Search page state
  const [searchResults, setSearchResults] = useState([]);
  const [searchType, setSearchType] = useState('all');
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [activeSearch, setActiveSearch] = useState('');
  
  // Watch page state
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [showAd, setShowAd] = useState(true);
  const [adCountdown, setAdCountdown] = useState(5);
  const [adLink, setAdLink] = useState('https://my-store-b8bb42.creator-spring.com/');
  
  // Admin page state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [featuredVideoUrl, setFeaturedVideoUrl] = useState('');
  const [featuredVideoTitle, setFeaturedVideoTitle] = useState('');
  const [featuredVideoArtist, setFeaturedVideoArtist] = useState('');
  const [adminAdLink, setAdminAdLink] = useState('');
  const [saveStatus, setSaveStatus] = useState({ type: '', message: '' });
  const [isSaving, setIsSaving] = useState(false);
  const [stats, setStats] = useState({ total_videos: 0, total_artists: 0 });

  const t = getTranslation(currentLang);

  // Featured video state
  const [featuredVideo, setFeaturedVideo] = useState(null);

  // Load featured video and ad settings on mount
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
          if (data.ad_link) {
            setAdLink(data.ad_link);
          }
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
    setShowAd(true);
    setAdCountdown(5);
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
        setAdminAdLink(data.ad_link || 'https://my-store-b8bb42.creator-spring.com/');
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
          ad_link: adminAdLink,
        }),
      });

      if (res.ok) {
        setSaveStatus({ type: 'success', message: 'Settings saved successfully!' });
        // Update ad link
        setAdLink(adminAdLink);
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

  const embedPreviewUrl = getYouTubeEmbedUrl(featuredVideoUrl);

  // Home Page
  if (currentPage === 'home') {
    return (
      <div className="min-h-screen bg-black">
        {/* Header */}
        <header className="flex items-center justify-between px-4 py-3 bg-black border-b border-zinc-900">
          <div className="flex-1" />
          <img 
            src={BANNER_URL} 
            alt="DadRock Guitar Tabs" 
            className="h-8 sm:h-10 md:h-12"
          />
          <div className="flex-1 flex justify-end items-center gap-2">
            <LanguageSelector currentLang={currentLang} />
            <a
              href="https://my-store-b8bb42.creator-spring.com"
              target="_blank"
              rel="noopener noreferrer"
              className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-amber-500 hover:text-amber-400 transition-colors"
            >
              <ShoppingBag className="w-4 h-4" />
              <span>Support Merch</span>
            </a>
          </div>
        </header>

        {/* Main Content */}
        <main className="flex flex-col items-center px-4 py-8 sm:py-12">
          {/* Logo */}
          <div className="mb-6">
            <img
              src={LOGO_URL}
              alt="DadRock Tabs Logo"
              onClick={handleLogoClick}
              className="w-80 sm:w-96 md:w-[28rem] cursor-pointer select-none hover:scale-105 transition-transform duration-300"
            />
          </div>

          {/* Definition */}
          <div className="text-center mb-6 max-w-xl">
            <div className="flex items-center justify-center gap-2 flex-wrap">
              <img 
                src={DADROCK_TEXT_URL} 
                alt="DadRock" 
                className="h-8 sm:h-10"
              />
              <span className="text-amber-500 text-xl sm:text-2xl">{t.definition.pronunciation}</span>
            </div>
            <p className="text-zinc-500 italic text-sm mt-1">{t.definition.partOfSpeech}</p>
            <p className="text-zinc-300 mt-2 leading-relaxed">
              {t.definition.meaning}
            </p>
          </div>

          {/* Tagline */}
          <p className="text-zinc-400 text-center text-sm sm:text-base mb-6 max-w-lg">
            {t.tagline}
          </p>

          {/* Search Form */}
          <form onSubmit={handleSearch} className="w-full max-w-2xl mb-6">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                <input
                  type="text"
                  placeholder={t.searchPlaceholder}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full h-12 sm:h-14 bg-zinc-900 border border-zinc-700 focus:border-amber-500 rounded-full pl-12 pr-4 text-white placeholder:text-zinc-500 outline-none transition-colors"
                />
              </div>
              <button
                type="submit"
                className="h-12 sm:h-14 px-6 sm:px-8 rounded-full bg-amber-500 text-black font-bold uppercase tracking-wider hover:bg-amber-400 transition-colors"
              >
                {t.searchButton}
              </button>
            </div>
          </form>

          {/* Subscribe Button */}
          <a
            href={YOUTUBE_CHANNEL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-full bg-red-600 hover:bg-red-500 text-white font-bold uppercase tracking-wide transition-colors mb-8"
          >
            <Youtube className="w-5 h-5" />
            {t.subscribe}
          </a>

          {/* Popular Searches */}
          <div className="w-full max-w-2xl mb-8">
            <p className="text-center text-zinc-400 mb-4 flex items-center justify-center gap-2">
              <span>🔥</span> {t.popularSearches}
            </p>
            <div className="flex flex-wrap justify-center gap-2">
              {popularArtists.map((artist) => (
                <button
                  key={artist.name}
                  onClick={() => handleArtistClick(artist.name)}
                  className="px-4 py-2 rounded-full bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 hover:border-amber-500/50 text-sm text-zinc-300 hover:text-white transition-all"
                >
                  {artist.emoji} {artist.name}
                </button>
              ))}
            </div>
          </div>

          {/* Featured Video */}
          {featuredVideo?.url && (
            <div className="w-full max-w-2xl mb-8">
              <p className="text-center text-zinc-400 mb-4 flex items-center justify-center gap-2">
                <span>🎬</span> {t.featuredLesson}
              </p>
              <div className="relative aspect-video rounded-xl overflow-hidden border border-zinc-800">
                <iframe
                  src={getYouTubeEmbedUrl(featuredVideo.url)}
                  title={featuredVideo.title || "Featured Video"}
                  className="absolute inset-0 w-full h-full"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
              {featuredVideo.title && (
                <p className="text-center mt-3 text-zinc-400">
                  🎸 "{featuredVideo.title}" {featuredVideo.artist && `by ${featuredVideo.artist}`}
                </p>
              )}
            </div>
          )}

          {/* Share Section */}
          <div className="mb-8">
            <p className="text-center text-zinc-400 mb-4 flex items-center justify-center gap-2">
              <span>📢</span> {t.shareDadRock}
            </p>
            <div className="flex justify-center gap-3">
              <a
                href={`https://www.facebook.com/sharer/sharer.php?u=${typeof window !== 'undefined' ? window.location.origin : 'https://dadrocktabs.com'}`}
                target="_blank"
                rel="noopener noreferrer"
                className="w-11 h-11 rounded-full bg-blue-600 hover:bg-blue-500 flex items-center justify-center transition-colors"
              >
                <Facebook className="w-5 h-5 text-white" />
              </a>
              <a
                href={`https://twitter.com/intent/tweet?url=${typeof window !== 'undefined' ? window.location.origin : 'https://dadrocktabs.com'}&text=Check out DadRock Tabs!`}
                target="_blank"
                rel="noopener noreferrer"
                className="w-11 h-11 rounded-full bg-sky-500 hover:bg-sky-400 flex items-center justify-center transition-colors"
              >
                <Twitter className="w-5 h-5 text-white" />
              </a>
              <button
                onClick={() => navigator.share?.({ url: window.location.href, title: 'DadRock Tabs' })}
                className="w-11 h-11 rounded-full bg-zinc-700 hover:bg-zinc-600 flex items-center justify-center transition-colors"
              >
                <Share2 className="w-5 h-5 text-white" />
              </button>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="w-full max-w-md space-y-3">
            <a
              href="https://buymeacoffee.com/dadrockytq/commissions"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full py-3.5 rounded-full bg-amber-500 hover:bg-amber-400 text-black font-bold uppercase tracking-wide transition-colors"
            >
              <MessageSquarePlus className="w-5 h-5" />
              {t.makeRequest}
            </a>
            <div className="flex gap-3">
              <a
                href="https://www.paypal.com/donate?hosted_button_id=FKZ2C3QW9ZBTE"
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 py-3 rounded-full bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 hover:text-white transition-all"
              >
                <Heart className="w-4 h-4 text-red-500" />
                {t.support}
              </a>
              <a
                href="https://my-store-b8bb42.creator-spring.com"
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 flex items-center justify-center gap-2 py-3 rounded-full bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 hover:text-white transition-all"
              >
                <ShoppingBag className="w-4 h-4 text-amber-500" />
                {t.merchandise}
              </a>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="py-6 text-center">
          <a
            href="mailto:Dadrockyt@gmail.com"
            className="inline-flex items-center gap-2 px-5 py-2 text-sm text-zinc-400 hover:text-white bg-zinc-900 hover:bg-zinc-800 rounded-full transition-all border border-zinc-800"
          >
            <Mail className="w-4 h-4" />
            {t.contact}
          </a>
          <p className="text-xs text-zinc-600 mt-4">
            {t.footer}
          </p>
        </footer>
      </div>
    );
  }

  // Search Page
  if (currentPage === 'search') {
    return (
      <div className="min-h-screen bg-black">
        <header className="sticky top-0 z-50 bg-black/95 backdrop-blur-sm border-b border-zinc-800">
          <div className="max-w-7xl mx-auto px-4 py-3">
            <div className="flex items-center gap-3">
              <button onClick={() => setCurrentPage('home')} className="text-zinc-400 hover:text-white transition-colors">
                <ArrowLeft className="w-6 h-6" />
              </button>

              <button onClick={() => setCurrentPage('home')}>
                <img src={LOGO_URL} alt="DadRock Tabs" className="w-10 h-10" />
              </button>

              <form onSubmit={(e) => { e.preventDefault(); performSearch(searchQuery, searchType); }} className="flex-1 flex items-center gap-2">
                <div className="flex-1 relative">
                  <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-500" />
                  <input
                    type="text"
                    placeholder="Search for songs or artists..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full h-11 bg-zinc-900 border border-zinc-700 focus:border-amber-500 rounded-full pl-11 pr-4 text-white placeholder:text-zinc-500 outline-none"
                  />
                </div>

                <select
                  value={searchType}
                  onChange={(e) => setSearchType(e.target.value)}
                  className="h-11 px-4 rounded-full bg-zinc-900 border border-zinc-700 text-white outline-none cursor-pointer"
                >
                  <option value="all">All</option>
                  <option value="song">Song</option>
                  <option value="artist">Artist</option>
                </select>

                <button
                  type="submit"
                  className="h-11 px-5 rounded-full bg-amber-500 text-black font-bold hover:bg-amber-400 transition-colors"
                >
                  Search
                </button>
              </form>

              <LanguageSelector currentLang={currentLang} />
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-6">
          {activeSearch && (
            <div className="mb-6">
              <h1 className="text-2xl md:text-3xl font-bold uppercase text-white">
                Results for "{activeSearch}"
              </h1>
              <p className="text-zinc-400 mt-1">
                {totalCount} videos found
              </p>
            </div>
          )}

          {loading && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
              {[...Array(12)].map((_, i) => (
                <div key={i} className="flex items-center gap-3 p-2 bg-zinc-900/50 rounded-lg animate-pulse">
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
              {searchResults.map((video) => (
                <VideoCard key={video.id} video={video} onClick={handleVideoClick} />
              ))}
            </div>
          )}

          {!loading && activeSearch && searchResults.length === 0 && (
            <div className="text-center py-20">
              <p className="text-zinc-400 text-lg">No videos found.</p>
              <p className="text-zinc-500 text-sm mt-2">Try a different search term.</p>
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
        <header className="sticky top-0 z-50 bg-black/95 backdrop-blur-sm border-b border-zinc-800">
          <div className="max-w-4xl mx-auto px-4 py-3">
            <div className="flex items-center gap-4">
              <button onClick={() => setCurrentPage('search')} className="text-zinc-400 hover:text-white transition-colors">
                <ArrowLeft className="w-6 h-6" />
              </button>
              <button onClick={() => setCurrentPage('home')}>
                <img src={LOGO_URL} alt="DadRock Tabs" className="w-10 h-10" />
              </button>
              <div className="flex-1" />
              <LanguageSelector currentLang={currentLang} />
            </div>
          </div>
        </header>

        <main className="max-w-4xl mx-auto px-4 py-8">
          <div className="text-center mb-6">
            <h1 className="text-2xl md:text-4xl font-bold uppercase text-amber-500">
              {selectedVideo.song}
            </h1>
            <p className="text-zinc-400 mt-2 text-lg">by {selectedVideo.artist}</p>
          </div>

          <div className="aspect-video rounded-xl overflow-hidden border border-zinc-800 mb-8">
            <iframe
              src={watchEmbedUrl}
              title={selectedVideo.song}
              className="w-full h-full"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
              allowFullScreen
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href={selectedVideo.youtube_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full bg-red-600 hover:bg-red-500 text-white font-bold uppercase tracking-wide transition-colors"
            >
              <Youtube className="w-6 h-6" />
              Watch on YouTube
            </a>
            <button
              onClick={() => setCurrentPage('search')}
              className="inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 font-bold uppercase tracking-wide transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Go Back
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
                <img src={LOGO_URL} alt="DadRock Tabs" className="w-32" />
              </button>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-8">
              <div className="flex items-center justify-center gap-3 mb-6">
                <div className="w-12 h-12 bg-amber-500/20 rounded-full flex items-center justify-center">
                  <Lock className="w-6 h-6 text-amber-500" />
                </div>
                <h1 className="text-2xl font-bold text-white">Admin Login</h1>
              </div>

              <form onSubmit={handleLogin} className="space-y-4">
                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Password</label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                    placeholder="Enter admin password"
                    required
                  />
                </div>

                {authError && (
                  <div className="flex items-center gap-2 text-red-400 text-sm">
                    <AlertCircle className="w-4 h-4" />
                    {authError}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isLoggingIn}
                  className="w-full py-3 bg-amber-500 text-black font-bold rounded-lg hover:bg-amber-400 transition-colors disabled:opacity-50"
                >
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
                  <Settings className="w-5 h-5 text-amber-500" />
                  Admin Panel
                </h1>
                <p className="text-sm text-zinc-400">Manage your site settings</p>
              </div>
            </div>

            <button
              onClick={handleLogout}
              className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-zinc-300 hover:text-white transition-colors"
            >
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
                <div className="w-12 h-12 bg-amber-500/20 rounded-full flex items-center justify-center">
                  <User className="w-6 h-6 text-amber-500" />
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
              <Music className="w-5 h-5 text-amber-500" />
              Featured Video Settings
            </h2>

            <form onSubmit={handleSaveSettings} className="space-y-6">
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-zinc-400 mb-2">YouTube Video URL</label>
                    <input
                      type="text"
                      value={featuredVideoUrl}
                      onChange={(e) => setFeaturedVideoUrl(e.target.value)}
                      className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                      placeholder="https://youtube.com/watch?v=..."
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-zinc-400 mb-2">Song Title</label>
                    <input
                      type="text"
                      value={featuredVideoTitle}
                      onChange={(e) => setFeaturedVideoTitle(e.target.value)}
                      className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                      placeholder="We Will Rock You"
                    />
                  </div>

                  <div>
                    <label className="block text-sm text-zinc-400 mb-2">Artist Name</label>
                    <input
                      type="text"
                      value={featuredVideoArtist}
                      onChange={(e) => setFeaturedVideoArtist(e.target.value)}
                      className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                      placeholder="Queen"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm text-zinc-400 mb-2">Preview</label>
                  {embedPreviewUrl ? (
                    <div className="aspect-video rounded-lg overflow-hidden border border-zinc-700">
                      <iframe
                        src={embedPreviewUrl}
                        title="Featured Video Preview"
                        className="w-full h-full"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                      />
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

              <button
                type="submit"
                disabled={isSaving}
                className="flex items-center justify-center gap-2 px-8 py-3 bg-amber-500 text-black font-bold rounded-lg hover:bg-amber-400 transition-colors disabled:opacity-50"
              >
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
