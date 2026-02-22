'use client';

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { Search, ShoppingBag, Youtube, Share2, Heart, MessageSquarePlus, Mail, Globe, ChevronDown, Play, User, ArrowLeft, Lock, Save, AlertCircle, CheckCircle, Music, LogOut, Settings, Facebook, Twitter } from 'lucide-react';
import { getTranslation, locales, localeNames, localeFlags } from '@/lib/i18n';

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";
const DADROCK_TEXT_URL = "https://customer-assets.emergentagent.com/job_nextjs-deploy-3/artifacts/2vno1305_Picsart_26-02-16_06-05-32-255%281%29.png";
const BANNER_URL = "https://customer-assets.emergentagent.com/job_nextjs-deploy-3/artifacts/q10t8nk7_Picsart_26-02-17_18-51-12-061.png";
const HEADPHONES_URL = "https://customer-assets.emergentagent.com/job_bd94fdc7-4b49-4099-93f6-493e89650cc1/artifacts/735ybmfu_Picsart_26-02-22_08-30-43-163.png";
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
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleLanguageChange = (lang) => {
    setIsOpen(false);
    if (lang === 'en') {
      router.push('/');
    } else {
      router.push(`/${lang}`);
    }
  };

  // Modal content to be portaled to body
  const modalContent = isOpen && mounted ? createPortal(
    <div 
      style={{ 
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        zIndex: 99999,
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'center',
        paddingTop: '60px',
        backgroundColor: '#000000'
      }}
    >
      {/* Dark backdrop - click to close */}
      <div 
        style={{ 
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: '#000000'
        }}
        onClick={() => setIsOpen(false)}
      />
      
      {/* Language menu card */}
      <div 
        style={{ 
          position: 'relative',
          width: '320px',
          maxWidth: '90vw',
          maxHeight: '80vh',
          overflowY: 'auto',
          borderRadius: '16px',
          backgroundColor: '#262626',
          border: '2px solid #525252',
          boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 1)'
        }}
      >
        {/* Header */}
        <div 
          style={{ 
            position: 'sticky',
            top: 0,
            padding: '16px',
            backgroundColor: '#262626',
            borderBottom: '1px solid #525252',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <span style={{ color: '#ffffff', fontWeight: 'bold', fontSize: '18px' }}>Select Language</span>
          <button 
            onClick={() => setIsOpen(false)}
            style={{
              width: '32px',
              height: '32px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: '50%',
              backgroundColor: '#404040',
              color: '#ffffff',
              border: 'none',
              fontSize: '20px',
              cursor: 'pointer'
            }}
          >
            ×
          </button>
        </div>
        
        {/* Language options */}
        <div style={{ backgroundColor: '#262626' }}>
          {locales.map((lang) => (
            <button
              key={lang}
              onClick={() => handleLanguageChange(lang)}
              style={{ 
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                gap: '16px',
                padding: '16px',
                fontSize: '16px',
                backgroundColor: lang === currentLang ? '#4a4a00' : '#262626',
                color: lang === currentLang ? '#fbbf24' : '#e4e4e7',
                borderBottom: '1px solid #404040',
                border: 'none',
                cursor: 'pointer',
                textAlign: 'left'
              }}
            >
              <span style={{ fontSize: '24px' }}>{localeFlags[lang]}</span>
              <span style={{ flex: 1, fontWeight: '500' }}>{localeNames[lang]}</span>
              {lang === currentLang && <span style={{ color: '#fbbf24', fontWeight: 'bold', fontSize: '20px' }}>✓</span>}
            </button>
          ))}
        </div>
      </div>
    </div>,
    document.body
  ) : null;

  return (
    <>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1.5 text-sm font-medium text-zinc-300 hover:text-white bg-zinc-800/80 hover:bg-zinc-700 rounded-md transition-all border border-zinc-700/50"
      >
        <Globe className="w-4 h-4" />
        <span>{localeFlags[currentLang]}</span>
        <span className="text-xs uppercase">{currentLang}</span>
        <ChevronDown className={`w-3 h-3 transition-transform ${isOpen ? "rotate-180" : ""}`} />
      </button>

      {modalContent}
    </>
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
  const [adImage, setAdImage] = useState('');
  const [adHeadline, setAdHeadline] = useState('Check Out Our Merchandise!');
  const [adDescription, setAdDescription] = useState('Support DadRock Tabs by grabbing some awesome gear');
  const [adButtonText, setAdButtonText] = useState('Shop Now');
  
  // Admin page state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [isLoggingIn, setIsLoggingIn] = useState(false);
  const [featuredVideoUrl, setFeaturedVideoUrl] = useState('');
  const [featuredVideoTitle, setFeaturedVideoTitle] = useState('');
  const [featuredVideoArtist, setFeaturedVideoArtist] = useState('');
  const [adminAdLink, setAdminAdLink] = useState('');
  const [adminAdImage, setAdminAdImage] = useState('');
  const [adminAdHeadline, setAdminAdHeadline] = useState('');
  const [adminAdDescription, setAdminAdDescription] = useState('');
  const [adminAdButtonText, setAdminAdButtonText] = useState('');
  const [saveStatus, setSaveStatus] = useState({ type: '', message: '' });
  const [isSaving, setIsSaving] = useState(false);
  const [stats, setStats] = useState({ total_videos: 0, total_artists: 0 });
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState({ type: '', message: '' });

  const t = getTranslation(currentLang);

  // Featured video state
  const [featuredVideo, setFeaturedVideo] = useState(null);
  const [isFirstVisit, setIsFirstVisit] = useState(false);

  // Check if first visit on mount
  useEffect(() => {
    const hasVisited = localStorage.getItem('dadrock_visited');
    if (!hasVisited) {
      setIsFirstVisit(true);
      localStorage.setItem('dadrock_visited', 'true');
    }
  }, []);

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
          if (data.ad_link) setAdLink(data.ad_link);
          if (data.ad_image) setAdImage(data.ad_image);
          if (data.ad_headline) setAdHeadline(data.ad_headline);
          if (data.ad_description) setAdDescription(data.ad_description);
          if (data.ad_button_text) setAdButtonText(data.ad_button_text);
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

  const getYouTubeEmbedUrl = (url, autoplay = false) => {
    if (!url) return null;
    if (url.includes('/embed/')) {
      return autoplay ? `${url}${url.includes('?') ? '&' : '?'}autoplay=1&mute=1` : url;
    }
    const videoIdMatch = url.match(/(?:youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
    if (videoIdMatch) {
      const baseUrl = `https://www.youtube.com/embed/${videoIdMatch[1]}`;
      return autoplay ? `${baseUrl}?autoplay=1&mute=1` : baseUrl;
    }
    return url;
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
        setAdminAdImage(data.ad_image || '');
        setAdminAdHeadline(data.ad_headline || 'Check Out Our Merchandise!');
        setAdminAdDescription(data.ad_description || 'Support DadRock Tabs by grabbing some awesome gear');
        setAdminAdButtonText(data.ad_button_text || 'Shop Now');
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
          ad_image: adminAdImage,
          ad_headline: adminAdHeadline,
          ad_description: adminAdDescription,
          ad_button_text: adminAdButtonText,
        }),
      });

      if (res.ok) {
        setSaveStatus({ type: 'success', message: 'Settings saved successfully!' });
        // Update ad settings in state
        setAdLink(adminAdLink);
        setAdImage(adminAdImage);
        setAdHeadline(adminAdHeadline);
        setAdDescription(adminAdDescription);
        setAdButtonText(adminAdButtonText);
      } else {
        setSaveStatus({ type: 'error', message: 'Failed to save settings' });
      }
    } catch (err) {
      setSaveStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsSaving(false);
    }
  };

  // Sync videos from YouTube
  const handleYouTubeSync = async () => {
    setIsSyncing(true);
    setSyncStatus({ type: '', message: '' });
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      const response = await fetch('/api/admin/youtube/sync', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Basic ${authToken}`
        },
        body: JSON.stringify({})
      });
      const data = await response.json();
      if (response.ok) {
        setSyncStatus({ 
          type: 'success', 
          message: `Synced ${data.videos_added} new videos! (${data.videos_skipped} already existed)` 
        });
        loadAdminData(); // Refresh stats
      } else {
        setSyncStatus({ type: 'error', message: data.error || 'Failed to sync videos' });
      }
    } catch (err) {
      setSyncStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsSyncing(false);
    }
  };

  // Countdown effect for interstitial ad
  useEffect(() => {
    if (currentPage === 'watch' && showAd && adCountdown > 0) {
      const timer = setTimeout(() => {
        setAdCountdown(adCountdown - 1);
      }, 1000);
      return () => clearTimeout(timer);
    } else if (currentPage === 'watch' && adCountdown === 0 && showAd) {
      setShowAd(false);
    }
  }, [currentPage, showAd, adCountdown]);

  useEffect(() => {
    if (currentPage === 'admin' && isAuthenticated) {
      loadAdminData();
    }
  }, [currentPage, isAuthenticated]);

  const embedPreviewUrl = getYouTubeEmbedUrl(featuredVideoUrl);

  // Home Page
  if (currentPage === 'home') {
    return (
      <div className="min-h-screen bg-black overflow-y-auto bg-guitarist">
        {/* Header - with safe area padding for mobile notch/status bar */}
        <header className="sticky top-0 z-50 bg-black/95 backdrop-blur-sm border-b border-zinc-900 pt-safe">
          <div className="flex items-center justify-between px-3 sm:px-4 py-2 sm:py-3">
            <div className="flex-1" />
            <img 
              src={BANNER_URL} 
              alt="DadRock Guitar Tabs" 
              className="h-6 sm:h-10 md:h-12 max-w-[50%] object-contain"
            />
            <div className="flex-1 flex justify-end items-center gap-1 sm:gap-2">
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
          </div>
        </header>

        {/* Main Content */}
        <main className="flex flex-col items-center px-4 py-6 sm:py-10">
          {/* Logo with Stylized Headphones - Bass Emanation Effect */}
          <div className="mb-4 fade-in-up relative flex items-center justify-center overflow-visible" style={{ animationDelay: '0.1s' }}>
            {/* Sound Wave Rings */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="absolute w-[50%] h-[50%] rounded-full border-2 border-amber-500/50 sound-wave-1" />
              <div className="absolute w-[65%] h-[65%] rounded-full border-2 border-red-500/40 sound-wave-2" />
              <div className="absolute w-[80%] h-[80%] rounded-full border border-amber-500/30 sound-wave-3" />
            </div>
            
            {/* Container for layered images */}
            <div className="relative flex items-center justify-center">
              {/* CSS Stylized Headphone Frame */}
              {/* Headband arc - outer glow */}
              <div 
                className="absolute pointer-events-none"
                style={{
                  width: '95%',
                  height: '50%',
                  top: '-8%',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  border: '6px solid transparent',
                  borderBottom: 'none',
                  borderRadius: '50% 50% 0 0',
                  background: 'linear-gradient(180deg, rgba(90,90,90,1) 0%, rgba(60,60,60,1) 100%) padding-box, linear-gradient(180deg, rgba(150,150,150,0.8), rgba(80,80,80,0.6)) border-box',
                  boxShadow: '0 0 30px rgba(251, 191, 36, 0.4), 0 -5px 20px rgba(251, 191, 36, 0.3)',
                  zIndex: 6
                }}
              />
              {/* Headband padding/cushion */}
              <div 
                className="absolute pointer-events-none"
                style={{
                  width: '70%',
                  height: '12%',
                  top: '-2%',
                  left: '50%',
                  transform: 'translateX(-50%)',
                  background: 'linear-gradient(180deg, rgba(50,50,50,1) 0%, rgba(30,30,30,1) 100%)',
                  borderRadius: '50% 50% 50% 50% / 100% 100% 0% 0%',
                  boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.8)',
                  zIndex: 7
                }}
              />
              
              {/* Left ear cup - outer */}
              <div 
                className="absolute headphone-bass pointer-events-none"
                style={{
                  width: '24%',
                  height: '38%',
                  top: '22%',
                  left: '-2%',
                  background: 'linear-gradient(145deg, rgba(70,70,70,1) 0%, rgba(40,40,40,1) 50%, rgba(50,50,50,1) 100%)',
                  borderRadius: '25% 35% 35% 25%',
                  border: '3px solid rgba(90, 90, 90, 0.9)',
                  boxShadow: '0 0 30px rgba(251, 191, 36, 0.5), inset 0 0 25px rgba(0,0,0,0.7), 5px 5px 15px rgba(0,0,0,0.5)',
                  zIndex: 16
                }}
              />
              {/* Left ear cup - inner cushion */}
              <div 
                className="absolute pointer-events-none"
                style={{
                  width: '18%',
                  height: '28%',
                  top: '27%',
                  left: '1%',
                  background: 'radial-gradient(ellipse at center, rgba(25,25,25,1) 0%, rgba(15,15,15,1) 100%)',
                  borderRadius: '50%',
                  boxShadow: 'inset 0 0 20px rgba(0,0,0,0.9)',
                  zIndex: 17
                }}
              />
              
              {/* Right ear cup - outer */}
              <div 
                className="absolute headphone-bass pointer-events-none"
                style={{
                  width: '24%',
                  height: '38%',
                  top: '22%',
                  right: '-2%',
                  background: 'linear-gradient(215deg, rgba(70,70,70,1) 0%, rgba(40,40,40,1) 50%, rgba(50,50,50,1) 100%)',
                  borderRadius: '35% 25% 25% 35%',
                  border: '3px solid rgba(90, 90, 90, 0.9)',
                  boxShadow: '0 0 30px rgba(251, 191, 36, 0.5), inset 0 0 25px rgba(0,0,0,0.7), -5px 5px 15px rgba(0,0,0,0.5)',
                  zIndex: 16
                }}
              />
              {/* Right ear cup - inner cushion */}
              <div 
                className="absolute pointer-events-none"
                style={{
                  width: '18%',
                  height: '28%',
                  top: '27%',
                  right: '1%',
                  background: 'radial-gradient(ellipse at center, rgba(25,25,25,1) 0%, rgba(15,15,15,1) 100%)',
                  borderRadius: '50%',
                  boxShadow: 'inset 0 0 20px rgba(0,0,0,0.9)',
                  zIndex: 17
                }}
              />
              
              {/* Main Guitar Logo - Centered */}
              <img
                src={LOGO_URL}
                alt="DadRock Tabs Logo"
                onClick={handleLogoClick}
                className="relative w-[18rem] sm:w-[24rem] md:w-[30rem] cursor-pointer select-none hover:scale-105 transition-transform duration-300 float-animation logo-glow"
                style={{ zIndex: 10 }}
              />
            </div>
          </div>

          {/* Definition */}
          <div className="text-center mb-8 max-w-2xl fade-in-up" style={{ animationDelay: '0.2s' }}>
            <div className="flex items-center justify-center gap-3 flex-wrap mb-3">
              <img 
                src={DADROCK_TEXT_URL} 
                alt="DadRock" 
                className="h-12 sm:h-14 md:h-16"
                style={{ filter: 'drop-shadow(0 0 10px rgba(251, 191, 36, 0.4))' }}
              />
              <span className="text-amber-500 text-2xl sm:text-3xl md:text-4xl font-bold text-glow">{t.definition.pronunciation}</span>
            </div>
            <p className="text-amber-400/80 italic text-2xl sm:text-3xl md:text-4xl mt-2 tracking-widest font-rock-alt">{t.definition.partOfSpeech}</p>
            <p className="rock-definition mt-5 text-xl sm:text-2xl md:text-3xl px-2">
              {t.definition.meaning}
            </p>
          </div>

          {/* Tagline */}
          <p className="rock-tagline text-center text-xl sm:text-2xl md:text-3xl mb-10 max-w-2xl px-4 fade-in-up leading-relaxed" style={{ animationDelay: '0.3s' }}>
            {t.tagline}
          </p>

          {/* Search Form with Gradient Border */}
          <form onSubmit={handleSearch} className="w-full max-w-2xl mb-8 fade-in-up" style={{ animationDelay: '0.4s' }}>
            <div className="flex gap-3">
              <div className="flex-1 relative gradient-border">
                <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-zinc-400 z-10" />
                <input
                  type="text"
                  placeholder={t.searchPlaceholder}
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full h-12 sm:h-14 bg-zinc-900/90 rounded-full pl-12 pr-4 text-white placeholder:text-zinc-500 outline-none transition-all focus:bg-zinc-800 focus:shadow-[0_0_30px_rgba(251,191,36,0.3)]"
                />
              </div>
              <button
                type="submit"
                className="h-12 sm:h-14 px-6 sm:px-8 rounded-full gradient-btn text-black font-bold uppercase tracking-wider"
              >
                {t.searchButton}
              </button>
            </div>
          </form>

          {/* Subscribe Button with Pulse Glow */}
          <a
            href={YOUTUBE_CHANNEL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-8 py-4 rounded-full subscribe-btn pulse-glow text-white font-bold uppercase tracking-wide mb-10 fade-in-up"
            style={{ animationDelay: '0.5s' }}
          >
            <Youtube className="w-6 h-6" />
            {t.subscribe}
          </a>

          {/* Popular Searches with Glassmorphism */}
          <div className="w-full max-w-2xl mb-10 fade-in-up" style={{ animationDelay: '0.6s' }}>
            <div className="glass-card rounded-2xl p-6">
              <p className="text-center text-zinc-300 mb-5 flex items-center justify-center gap-2 text-lg font-medium">
                <span className="text-2xl">🔥</span> {t.popularSearches}
              </p>
              <div className="flex flex-wrap justify-center gap-3">
                {popularArtists.map((artist, index) => (
                  <button
                    key={artist.name}
                    onClick={() => handleArtistClick(artist.name)}
                    className="artist-btn px-5 py-2.5 rounded-full bg-zinc-800/80 border border-zinc-700 text-sm text-zinc-200 hover:text-white font-medium"
                    style={{ animationDelay: `${0.7 + index * 0.05}s` }}
                  >
                    <span className="mr-1.5">{artist.emoji}</span> {artist.name}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Featured Video */}
          {featuredVideo?.url && (
            <div className="w-full max-w-2xl mb-10 fade-in-up" style={{ animationDelay: '0.7s' }}>
              <p className="text-center text-zinc-300 mb-5 flex items-center justify-center gap-2 text-lg font-medium">
                <span className="text-2xl">🎬</span> {t.featuredLesson}
              </p>
              <div className="relative aspect-video rounded-2xl overflow-hidden glass-card p-1">
                <div className="absolute inset-0 bg-gradient-to-br from-amber-500/20 via-transparent to-red-500/20 rounded-2xl pointer-events-none" />
                <iframe
                  src={getYouTubeEmbedUrl(featuredVideo.url, isFirstVisit)}
                  title={featuredVideo.title || "Featured Video"}
                  className="relative w-full h-full rounded-xl"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
              {featuredVideo.title && (
                <p className="text-center mt-4 text-zinc-300 text-lg">
                  🎸 <span className="font-semibold text-amber-400">"{featuredVideo.title}"</span> {featuredVideo.artist && <span className="text-zinc-400">by {featuredVideo.artist}</span>}
                </p>
              )}
            </div>
          )}

          {/* Share Section */}
          <div className="mb-10 fade-in-up" style={{ animationDelay: '0.8s' }}>
            <p className="text-center text-zinc-300 mb-5 flex items-center justify-center gap-2 text-lg font-medium">
              <span className="text-2xl">📢</span> {t.shareDadRock}
            </p>
            <div className="flex justify-center gap-4">
              <a
                href={`https://www.facebook.com/sharer/sharer.php?u=${typeof window !== 'undefined' ? window.location.origin : 'https://dadrocktabs.com'}`}
                target="_blank"
                rel="noopener noreferrer"
                className="w-12 h-12 rounded-full bg-blue-600 hover:bg-blue-500 flex items-center justify-center transition-all hover:scale-110 hover:shadow-[0_0_20px_rgba(37,99,235,0.5)]"
              >
                <Facebook className="w-5 h-5 text-white" />
              </a>
              <a
                href={`https://twitter.com/intent/tweet?url=${typeof window !== 'undefined' ? window.location.origin : 'https://dadrocktabs.com'}&text=Check out DadRock Tabs!`}
                target="_blank"
                rel="noopener noreferrer"
                className="w-12 h-12 rounded-full bg-sky-500 hover:bg-sky-400 flex items-center justify-center transition-all hover:scale-110 hover:shadow-[0_0_20px_rgba(14,165,233,0.5)]"
              >
                <Twitter className="w-5 h-5 text-white" />
              </a>
              <button
                onClick={() => navigator.share?.({ url: window.location.href, title: 'DadRock Tabs' })}
                className="w-12 h-12 rounded-full bg-zinc-700 hover:bg-zinc-600 flex items-center justify-center transition-all hover:scale-110 hover:shadow-[0_0_20px_rgba(113,113,122,0.5)]"
              >
                <Share2 className="w-5 h-5 text-white" />
              </button>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="w-full max-w-md space-y-4 fade-in-up" style={{ animationDelay: '0.9s' }}>
            <a
              href="https://buymeacoffee.com/dadrockytq/commissions"
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full py-4 rounded-full gradient-btn text-black font-bold uppercase tracking-wide text-lg"
            >
              <MessageSquarePlus className="w-5 h-5" />
              {t.makeRequest}
            </a>
            <div className="flex gap-3">
              <a
                href="https://www.paypal.com/donate?hosted_button_id=FKZ2C3QW9ZBTE"
                target="_blank"
                rel="noopener noreferrer"
                className="artist-btn flex-1 flex items-center justify-center gap-2 py-3.5 rounded-full bg-zinc-800/80 border border-zinc-700 text-zinc-200 hover:text-white font-medium"
              >
                <Heart className="w-5 h-5 text-red-500" />
                {t.support}
              </a>
              <a
                href="https://my-store-b8bb42.creator-spring.com"
                target="_blank"
                rel="noopener noreferrer"
                className="artist-btn flex-1 flex items-center justify-center gap-2 py-3.5 rounded-full bg-zinc-800/80 border border-zinc-700 text-zinc-200 hover:text-white font-medium"
              >
                <ShoppingBag className="w-5 h-5 text-amber-500" />
                {t.merchandise}
              </a>
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="py-10 text-center fade-in-up" style={{ animationDelay: '1s' }}>
          <a
            href="mailto:Dadrockyt@gmail.com"
            className="artist-btn inline-flex items-center gap-2 px-6 py-3 text-sm text-zinc-300 hover:text-white bg-zinc-800/80 rounded-full border border-zinc-700 font-medium"
          >
            <Mail className="w-4 h-4" />
            {t.contact}
          </a>
          <p className="text-sm text-zinc-500 mt-6">
            {t.footer}
          </p>
        </footer>
      </div>
    );
  }

  // Search Page
  if (currentPage === 'search') {
    return (
      <div className="min-h-screen bg-black bg-guitarist">
        <header className="sticky top-0 z-50 bg-black/95 backdrop-blur-sm border-b border-zinc-800 pt-safe">
          <div className="max-w-7xl mx-auto px-4 py-2 sm:py-3">
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

  // Watch Page with Interstitial Ad
  if (currentPage === 'watch' && selectedVideo) {
    const watchEmbedUrl = getYouTubeEmbedUrl(selectedVideo.youtube_url) + '?autoplay=1';

    // Show interstitial ad
    if (showAd) {
      return (
        <div className="min-h-screen bg-black flex flex-col bg-guitarist">
          <header className="bg-black/95 border-b border-zinc-800 px-4 py-2 sm:py-3 pt-safe">
            <div className="max-w-4xl mx-auto flex items-center gap-4">
              <button onClick={() => setCurrentPage('home')}>
                <img src={LOGO_URL} alt="DadRock Tabs" className="w-10 h-10" />
              </button>
              <div className="flex-1" />
              <div className="text-zinc-400 text-sm">
                Video starts in <span className="text-amber-500 font-bold text-lg">{adCountdown}</span> seconds
              </div>
            </div>
          </header>

          <main className="flex-1 flex flex-col items-center justify-center px-4 py-8">
            <div className="text-center mb-8">
              <p className="text-zinc-500 text-sm uppercase tracking-wider mb-2">Sponsored</p>
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">
                {adHeadline}
              </h2>
              <p className="text-zinc-400">
                {adDescription}
              </p>
            </div>

            <a
              href={adLink}
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full max-w-2xl mb-8"
            >
              <div className="bg-gradient-to-br from-amber-500 via-orange-500 to-red-600 p-1 rounded-2xl hover:scale-[1.02] transition-transform">
                <div className="bg-zinc-900 rounded-xl p-8 text-center">
                  {adImage ? (
                    <img 
                      src={adImage} 
                      alt={adHeadline}
                      className="w-full max-h-64 object-contain mx-auto mb-4 rounded-lg"
                    />
                  ) : (
                    <ShoppingBag className="w-16 h-16 mx-auto mb-4 text-amber-500" />
                  )}
                  <h3 className="text-xl md:text-2xl font-bold text-white mb-2">
                    {adHeadline}
                  </h3>
                  <p className="text-zinc-400 mb-4">
                    {adDescription}
                  </p>
                  <span className="inline-flex items-center gap-2 px-6 py-3 bg-amber-500 text-black font-bold rounded-full">
                    <ShoppingBag className="w-5 h-5" />
                    {adButtonText}
                  </span>
                </div>
              </div>
            </a>

            <div className="text-center">
              <p className="text-zinc-500 mb-4">
                Loading: <span className="text-white font-semibold">{selectedVideo.song}</span> by {selectedVideo.artist}
              </p>
              <div className="w-64 h-2 bg-zinc-800 rounded-full overflow-hidden mx-auto">
                <div 
                  className="h-full bg-amber-500 transition-all duration-1000"
                  style={{ width: `${((5 - adCountdown) / 5) * 100}%` }}
                />
              </div>
              <button
                onClick={() => setShowAd(false)}
                className="mt-6 text-zinc-500 hover:text-white text-sm underline"
                disabled={adCountdown > 0}
              >
                {adCountdown > 0 ? `Skip in ${adCountdown}s` : 'Skip Ad'}
              </button>
            </div>
          </main>
        </div>
      );
    }

    // Show video after ad
    return (
      <div className="min-h-screen bg-black bg-guitarist">
        <header className="sticky top-0 z-50 bg-black/95 backdrop-blur-sm border-b border-zinc-800 pt-safe">
          <div className="max-w-4xl mx-auto px-4 py-2 sm:py-3">
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
      <div className="min-h-screen bg-black bg-guitarist">
        <header className="bg-zinc-900 border-b border-zinc-800 px-4 sm:px-6 py-3 sm:py-4 pt-safe">
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

          {/* YouTube Sync Section */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Youtube className="w-5 h-5 text-red-500" />
              Sync Videos from YouTube
            </h2>
            <p className="text-zinc-400 mb-4">
              Click the button below to sync all videos from the DadRock Tabs YouTube channel to your database.
            </p>
            
            {syncStatus.message && (
              <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
                syncStatus.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              }`}>
                {syncStatus.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                {syncStatus.message}
              </div>
            )}
            
            <button
              onClick={handleYouTubeSync}
              disabled={isSyncing}
              className="flex items-center justify-center gap-2 px-6 py-3 bg-red-600 text-white font-bold rounded-lg hover:bg-red-500 transition-colors disabled:opacity-50"
            >
              <Youtube className="w-5 h-5" />
              {isSyncing ? 'Syncing...' : 'Sync from YouTube'}
            </button>
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

          {/* Interstitial Ad Settings */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mt-6">
            <h2 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <ShoppingBag className="w-5 h-5 text-amber-500" />
              Interstitial Ad Settings
            </h2>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-zinc-400 mb-2">Ad Headline</label>
                <input
                  type="text"
                  value={adminAdHeadline}
                  onChange={(e) => setAdminAdHeadline(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                  placeholder="Check Out Our Merchandise!"
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Ad Description</label>
                <input
                  type="text"
                  value={adminAdDescription}
                  onChange={(e) => setAdminAdDescription(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                  placeholder="Support DadRock Tabs by grabbing some awesome gear"
                />
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Ad Image URL (optional)</label>
                <input
                  type="text"
                  value={adminAdImage}
                  onChange={(e) => setAdminAdImage(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                  placeholder="https://example.com/ad-banner.jpg"
                />
                <p className="text-xs text-zinc-500 mt-2">
                  Leave empty to show default icon. Recommended size: 600x300px
                </p>
                {adminAdImage && (
                  <div className="mt-3 p-2 bg-zinc-800 rounded-lg">
                    <p className="text-xs text-zinc-400 mb-2">Preview:</p>
                    <img 
                      src={adminAdImage} 
                      alt="Ad preview" 
                      className="max-h-32 mx-auto rounded"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Ad Link URL</label>
                <input
                  type="text"
                  value={adminAdLink}
                  onChange={(e) => setAdminAdLink(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                  placeholder="https://my-store-b8bb42.creator-spring.com/"
                />
                <p className="text-xs text-zinc-500 mt-2">
                  Where users go when they click the ad
                </p>
              </div>

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Button Text</label>
                <input
                  type="text"
                  value={adminAdButtonText}
                  onChange={(e) => setAdminAdButtonText(e.target.value)}
                  className="w-full px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                  placeholder="Shop Now"
                />
              </div>

              <div className="bg-zinc-800/50 rounded-lg p-4 mt-4">
                <p className="text-sm text-amber-500 font-medium mb-2">💡 Tips for Paid Ads:</p>
                <ul className="text-xs text-zinc-400 space-y-1">
                  <li>• Use eye-catching images (600x300px recommended)</li>
                  <li>• Keep headlines short and compelling</li>
                  <li>• Include clear call-to-action button text</li>
                  <li>• Track conversions by using UTM parameters in your link</li>
                </ul>
              </div>
            </div>
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
