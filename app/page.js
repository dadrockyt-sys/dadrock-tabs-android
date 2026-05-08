'use client';

import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { Search, ShoppingBag, Youtube, Share2, Heart, MessageSquarePlus, Mail, Globe, ChevronDown, Play, User, ArrowLeft, Lock, Save, AlertCircle, CheckCircle, Music, LogOut, Settings, Facebook, Twitter, Maximize, Smartphone, Upload, X, Image, Calendar, Clock, Trash2, Plus, Trophy, Zap, RefreshCw, Map, Activity, Shield, ExternalLink, Wifi, Database, FileText } from 'lucide-react';
import { getTranslation, locales, localeNames, localeFlags } from '@/lib/i18n';
import NewsletterSignup from '@/components/NewsletterSignup';
import GamificationPanel from '@/components/Gamification';

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";
const DADROCK_TEXT_URL = "https://customer-assets.emergentagent.com/job_nextjs-deploy-3/artifacts/2vno1305_Picsart_26-02-16_06-05-32-255%281%29.png";
const BANNER_URL = "https://customer-assets.emergentagent.com/job_nextjs-deploy-3/artifacts/q10t8nk7_Picsart_26-02-17_18-51-12-061.png";
const HEADPHONES_URL = "https://customer-assets.emergentagent.com/job_bd94fdc7-4b49-4099-93f6-493e89650cc1/artifacts/735ybmfu_Picsart_26-02-22_08-30-43-163.png";
const MARSHALL_AMP_URL = "https://customer-assets.emergentagent.com/job_bd94fdc7-4b49-4099-93f6-493e89650cc1/artifacts/slh9sg74_Picsart_26-02-22_08-40-16-701.png";
const YOUTUBE_CHANNEL = "https://youtube.com/@dadrockytofficial?si=AM8uj6DTefJcP8oZ";

const popularArtists = [
  { name: "Pantera", emoji: "🐆" },
  { name: "Led Zeppelin", emoji: "🎸" },
  { name: "AC/DC", emoji: "⚡" },
  { name: "Van Halen", emoji: "🔥" },
  { name: "Def Leppard", emoji: "🎵" },
  { name: "Ozzy Osbourne", emoji: "🦇" },
  { name: "Metallica", emoji: "🤘" },
  { name: "Black Sabbath", emoji: "🖤" },
  { name: "Aerosmith", emoji: "💎" },
];

// Extended artist database for internal linking
const allArtists = [
  { name: "Led Zeppelin", emoji: "🎸", genre: "classic rock" },
  { name: "AC/DC", emoji: "⚡", genre: "hard rock" },
  { name: "Van Halen", emoji: "🔥", genre: "hard rock" },
  { name: "Def Leppard", emoji: "🎵", genre: "hair metal" },
  { name: "Ozzy Osbourne", emoji: "🦇", genre: "heavy metal" },
  { name: "Metallica", emoji: "🤘", genre: "thrash metal" },
  { name: "Black Sabbath", emoji: "🖤", genre: "heavy metal" },
  { name: "Aerosmith", emoji: "💎", genre: "hard rock" },
  { name: "Deep Purple", emoji: "🎹", genre: "classic rock" },
  { name: "Iron Maiden", emoji: "⚔️", genre: "heavy metal" },
  { name: "Judas Priest", emoji: "🔱", genre: "heavy metal" },
  { name: "Guns N' Roses", emoji: "🌹", genre: "hard rock" },
  { name: "Bon Jovi", emoji: "❤️", genre: "hair metal" },
  { name: "Motley Crue", emoji: "💀", genre: "hair metal" },
  { name: "Kiss", emoji: "💋", genre: "hard rock" },
  { name: "Scorpions", emoji: "🦂", genre: "hard rock" },
  { name: "Whitesnake", emoji: "🐍", genre: "hair metal" },
  { name: "Dio", emoji: "🤘", genre: "heavy metal" },
  { name: "Rainbow", emoji: "🌈", genre: "classic rock" },
  { name: "ZZ Top", emoji: "🎸", genre: "blues rock" },
  { name: "Thin Lizzy", emoji: "🍀", genre: "classic rock" },
  { name: "Boston", emoji: "🚀", genre: "classic rock" },
  { name: "Journey", emoji: "🌟", genre: "classic rock" },
  { name: "Foreigner", emoji: "🌍", genre: "classic rock" },
  { name: "REO Speedwagon", emoji: "🚗", genre: "classic rock" },
  { name: "Styx", emoji: "⛵", genre: "classic rock" },
  { name: "Kansas", emoji: "🌾", genre: "classic rock" },
  { name: "Rush", emoji: "⭐", genre: "progressive rock" },
  { name: "Yes", emoji: "✅", genre: "progressive rock" },
  { name: "Pink Floyd", emoji: "🌙", genre: "progressive rock" },
  { name: "Cream", emoji: "🍦", genre: "blues rock" },
  { name: "The Who", emoji: "🎯", genre: "classic rock" },
  { name: "Jimi Hendrix", emoji: "🔥", genre: "blues rock" },
  { name: "Eric Clapton", emoji: "🎸", genre: "blues rock" },
  { name: "Stevie Ray Vaughan", emoji: "🎵", genre: "blues rock" },
  { name: "Lynyrd Skynyrd", emoji: "🦅", genre: "southern rock" },
  { name: "Allman Brothers", emoji: "🍑", genre: "southern rock" },
  { name: "Pantera", emoji: "🐆", genre: "thrash metal" },
  { name: "Megadeth", emoji: "☠️", genre: "thrash metal" },
  { name: "Slayer", emoji: "🗡️", genre: "thrash metal" },
  { name: "Anthrax", emoji: "🦠", genre: "thrash metal" },
];

// Function to get related artists based on genre or name similarity
function getRelatedArtists(artistName, count = 6) {
  const currentArtist = allArtists.find(a => 
    a.name.toLowerCase() === artistName?.toLowerCase()
  );
  
  if (!currentArtist) {
    // Return random popular artists if not found
    return allArtists.slice(0, count);
  }
  
  // Get artists from same genre, excluding current
  const sameGenre = allArtists.filter(a => 
    a.genre === currentArtist.genre && a.name !== currentArtist.name
  );
  
  // Get some from other genres for variety
  const otherGenre = allArtists.filter(a => 
    a.genre !== currentArtist.genre && a.name !== currentArtist.name
  );
  
  // Mix: 4 from same genre, 2 from others
  const related = [
    ...sameGenre.slice(0, 4),
    ...otherGenre.sort(() => Math.random() - 0.5).slice(0, 2)
  ];
  
  return related.slice(0, count);
}

// Helper to extract video ID from YouTube URL
function extractVideoIdFromUrl(url) {
  if (!url) return '';
  let videoId = null;
  if (url.includes('youtube.com/watch?v=')) {
    videoId = url.split('v=')[1]?.split('&')[0];
  } else if (url.includes('youtu.be/')) {
    videoId = url.split('youtu.be/')[1]?.split('?')[0];
  } else if (url.includes('youtube.com/embed/')) {
    videoId = url.split('embed/')[1]?.split('?')[0];
  } else if (url.includes('youtube.com/shorts/')) {
    videoId = url.split('shorts/')[1]?.split('?')[0];
  }
  return videoId || '';
}

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
  // Build song page slug from artist + song
  const songSlug = video.slug || `${(video.artist || '').toLowerCase().replace(/[^a-z0-9]+/g, '-')}-${(video.song || '').toLowerCase().replace(/[^a-z0-9]+/g, '-')}`.replace(/(^-|-$)/g, '');

  const handleClick = () => {
    // Navigate to the song page with flame transition
    if (window.__flameNavigate && songSlug) {
      window.__flameNavigate(`/songs/${songSlug}`);
    } else {
      // Fallback to inline play
      onClick(video);
    }
  };

  return (
    <div
      className="video-card group flex items-center gap-3 p-2 bg-zinc-900/50 hover:bg-zinc-800 rounded-lg border border-zinc-800 cursor-pointer transition-all"
      onClick={handleClick}
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
  const [pageReady, setPageReady] = useState(false);
  
  // Sync currentLang with initialLang when it changes (e.g., navigation to /hi, /es, etc.)
  useEffect(() => {
    if (initialLang !== currentLang) {
      setCurrentLang(initialLang);
    }
  }, [initialLang]);
  
  // Search page state
  const [searchResults, setSearchResults] = useState([]);
  const [searchType, setSearchType] = useState('all');
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [activeSearch, setActiveSearch] = useState('');
  
  // Watch page state
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [showAd, setShowAd] = useState(true);
  const [adDuration, setAdDuration] = useState(5); // Default 5 seconds
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
  const [adminAdDuration, setAdminAdDuration] = useState(5);
  const [saveStatus, setSaveStatus] = useState({ type: '', message: '' });
  const [isSaving, setIsSaving] = useState(false);
  const [stats, setStats] = useState({ total_videos: 0, total_artists: 0 });
  const [isSyncing, setIsSyncing] = useState(false);
  const [syncStatus, setSyncStatus] = useState({ type: '', message: '' });
  const [isCleaning, setIsCleaning] = useState(false);
  const [cleanupStatus, setCleanupStatus] = useState({ type: '', message: '' });
  const [cleanupRemovedVideos, setCleanupRemovedVideos] = useState([]);
  const [showRemovedList, setShowRemovedList] = useState(false);
  
  // Quickies sync state
  const [isSyncingQuickies, setIsSyncingQuickies] = useState(false);
  const [quickiesSyncStatus, setQuickiesSyncStatus] = useState({ type: '', message: '' });
  
  // Sitemap scan state
  const [isScanningPages, setIsScanningPages] = useState(false);
  const [scanResult, setScanResult] = useState(null);
  const [scanStatus, setScanStatus] = useState({ type: '', message: '' });
  const [isAddingPages, setIsAddingPages] = useState(false);
  const [addPagesResult, setAddPagesResult] = useState(null);
  
  // Sitemap ping state
  const [isPinging, setIsPinging] = useState(false);
  const [pingStatus, setPingStatus] = useState({ type: '', message: '' });
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  
  // Health check state
  const [isRunningHealthCheck, setIsRunningHealthCheck] = useState(false);
  const [healthReport, setHealthReport] = useState(null);
  const [healthCheckMode, setHealthCheckMode] = useState('full');
  const [isRemovingDeadVideos, setIsRemovingDeadVideos] = useState(false);
  const [isDeletingDeadUrls, setIsDeletingDeadUrls] = useState(false);
  const [deadUrlAction, setDeadUrlAction] = useState('');
  const [deletingDeadUrls, setDeletingDeadUrls] = useState({});
  
  // AI SEO Content state
  const [aiSeoStatus, setAiSeoStatus] = useState(null);
  const [isGeneratingAi, setIsGeneratingAi] = useState(false);
  const [aiGenerateMode, setAiGenerateMode] = useState('batch_artists');
  const [aiBatchSize, setAiBatchSize] = useState(5);
  const [aiResults, setAiResults] = useState(null);
  const [aiProgress, setAiProgress] = useState('');
  const [showAiDetailView, setShowAiDetailView] = useState(false);
  const [aiDetailData, setAiDetailData] = useState(null);
  const [aiDetailLoading, setAiDetailLoading] = useState(false);
  const [aiDetailFilter, setAiDetailFilter] = useState('all'); // 'all', 'with', 'without'
  const [aiDetailSearch, setAiDetailSearch] = useState('');
  const [isGeneratingSingle, setIsGeneratingSingle] = useState(null); // slug of the artist being generated
  
  // Admin upcoming videos state
  const [adminUpcomingVideos, setAdminUpcomingVideos] = useState([]);
  const [newUpcomingTitle, setNewUpcomingTitle] = useState('');
  const [newUpcomingArtist, setNewUpcomingArtist] = useState('');
  const [newUpcomingDate, setNewUpcomingDate] = useState('');
  const [newUpcomingThumbnail, setNewUpcomingThumbnail] = useState('');
  const [newUpcomingDescription, setNewUpcomingDescription] = useState('');
  const [isAddingUpcoming, setIsAddingUpcoming] = useState(false);
  
  // YouTube OAuth state
  const [youtubeConnected, setYoutubeConnected] = useState(false);
  const [youtubeChannelName, setYoutubeChannelName] = useState('');
  const [isSyncingScheduled, setIsSyncingScheduled] = useState(false);
  const [scheduledSyncStatus, setScheduledSyncStatus] = useState({ type: '', message: '' });

  // Top Lessons state
  const [topLessons, setTopLessons] = useState(Array(10).fill(null).map((_, i) => ({ position: i + 1, youtubeUrl: '', title: '', artist: '' })));
  const [isSavingTopLessons, setIsSavingTopLessons] = useState(false);
  const [topLessonsSaveStatus, setTopLessonsSaveStatus] = useState({ type: '', message: '' });

  // Song Pages state
  const [isSyncingSongs, setIsSyncingSongs] = useState(false);
  const [songSyncStatus, setSongSyncStatus] = useState({ type: '', message: '' });
  const [songPageCount, setSongPageCount] = useState(0);
  const [manualSongUrl, setManualSongUrl] = useState('');
  const [isAddingManualSong, setIsAddingManualSong] = useState(false);
  const [manualSongStatus, setManualSongStatus] = useState({ type: '', message: '' });
  const [songPagesList, setSongPagesList] = useState([]);
  const [showSongsList, setShowSongsList] = useState(false);
  const [deletingSongId, setDeletingSongId] = useState(null);

  const t = getTranslation(currentLang);

  // Featured video state
  const [featuredVideo, setFeaturedVideo] = useState(null);
  const [isFirstVisit, setIsFirstVisit] = useState(false);

  // Handle image upload
  const handleImageUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setUploadError('Invalid file type. Allowed: JPEG, PNG, GIF, WebP');
      return;
    }

    // Validate file size (max 2MB for base64 storage)
    if (file.size > 2 * 1024 * 1024) {
      setUploadError('File too large. Maximum size is 2MB');
      return;
    }

    setIsUploading(true);
    setUploadError('');

    try {
      const authToken = sessionStorage.getItem('dadrock_admin_auth');
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('/api/upload', {
        method: 'POST',
        headers: {
          'Authorization': 'Basic ' + btoa('admin:' + authToken),
        },
        body: formData,
      });

      const data = await response.json();

      if (response.ok && data.url) {
        setAdminAdImage(data.url);
        setUploadError('');
      } else {
        setUploadError(data.error || 'Upload failed. Please try again.');
      }
    } catch (err) {
      console.error('Upload error:', err);
      setUploadError('Network error. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  // Update document title and meta description based on language
  useEffect(() => {
    const t = getTranslation(currentLang);
    // Set page title
    document.title = t.meta_title || 'DadRock Tabs - Free Guitar & Bass Tabs';
    
    // Update meta description
    const metaDescription = document.querySelector('meta[name="description"]');
    if (metaDescription) {
      metaDescription.setAttribute('content', t.meta_description || 'Free guitar and bass tabs for classic rock hits.');
    } else {
      const newMeta = document.createElement('meta');
      newMeta.name = 'description';
      newMeta.content = t.meta_description || 'Free guitar and bass tabs for classic rock hits.';
      document.head.appendChild(newMeta);
    }

    // Update og:title
    const ogTitle = document.querySelector('meta[property="og:title"]');
    if (ogTitle) {
      ogTitle.setAttribute('content', t.meta_title || 'DadRock Tabs');
    }

    // Update og:description
    const ogDesc = document.querySelector('meta[property="og:description"]');
    if (ogDesc) {
      ogDesc.setAttribute('content', t.meta_description || 'Free guitar and bass tabs for classic rock hits.');
    }
  }, [currentLang]);

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
          if (data.ad_duration) {
            const duration = parseInt(data.ad_duration) || 5;
            setAdDuration(duration);
            setAdCountdown(duration);
          }
        }
      })
      .catch(() => {})
      .finally(() => {
        // Set page ready after content loads to prevent animation glitches
        setTimeout(() => setPageReady(true), 100);
      });
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
    setAdCountdown(adDuration); // Use the configurable duration
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
        setAdminAdDuration(data.ad_duration || 5);
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
          ad_duration: adminAdDuration,
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
        setAdDuration(adminAdDuration);
        setAdCountdown(adminAdDuration);
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

  // Cleanup dead/removed YouTube videos
  const handleYouTubeCleanup = async () => {
    if (!confirm('This will scan all videos and remove any dead or unavailable YouTube links. Continue?')) return;
    setIsCleaning(true);
    setCleanupStatus({ type: '', message: '' });
    setCleanupRemovedVideos([]);
    setShowRemovedList(false);
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      const response = await fetch('/api/admin/youtube/cleanup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Basic ${authToken}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setCleanupStatus({ 
          type: 'success', 
          message: data.message 
        });
        if (data.removed_videos && data.removed_videos.length > 0) {
          setCleanupRemovedVideos(data.removed_videos);
        }
        loadAdminData(); // Refresh stats
      } else {
        setCleanupStatus({ type: 'error', message: data.error || 'Cleanup failed' });
      }
    } catch (err) {
      setCleanupStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsCleaning(false);
    }
  };

  // Check YouTube OAuth connection status
  const checkYoutubeConnection = async () => {
    try {
      const res = await fetch('/api/auth/youtube?action=status');
      if (res.ok) {
        const data = await res.json();
        setYoutubeConnected(data.connected);
        setYoutubeChannelName(data.channel_name || '');
      }
    } catch (err) {
      console.error('Failed to check YouTube connection:', err);
    }
  };

  // Sync DadRock Tabs Quickies from YouTube playlist
  const handleSyncQuickies = async () => {
    setIsSyncingQuickies(true);
    setQuickiesSyncStatus({ type: '', message: '' });
    try {
      const res = await fetch('/api/quickies?sync=true');
      const data = await res.json();
      if (res.ok) {
        setQuickiesSyncStatus({
          type: 'success',
          message: `Quickies synced! ${data.total} videos loaded from the playlist.`
        });
      } else {
        setQuickiesSyncStatus({ type: 'error', message: data.error || 'Failed to sync quickies' });
      }
    } catch (err) {
      setQuickiesSyncStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsSyncingQuickies(false);
    }
  };

  // Scan for pages not in sitemap
  const handleScanPages = async () => {
    setIsScanningPages(true);
    setScanStatus({ type: '', message: '' });
    setScanResult(null);
    setAddPagesResult(null);
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      const res = await fetch('/api/admin/sitemap', {
        headers: { 'Authorization': `Basic ${authToken}` }
      });
      const data = await res.json();
      if (res.ok) {
        setScanResult(data);
        if (data.missing_from_sitemap.length === 0) {
          setScanStatus({ type: 'success', message: `All ${data.summary.total_pages} pages are in the sitemap. Everything is up to date!` });
        } else {
          setScanStatus({ type: 'error', message: `Found ${data.missing_from_sitemap.length} pages missing from the sitemap.` });
        }
      } else {
        setScanStatus({ type: 'error', message: data.error || 'Scan failed' });
      }
    } catch (err) {
      setScanStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsScanningPages(false);
    }
  };

  // Add missing pages to sitemap (verify + sync + ping)
  const handleAddMissingPages = async () => {
    setIsAddingPages(true);
    setAddPagesResult(null);
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      
      // Step 1: Trigger the add_missing_pages action
      const res = await fetch('/api/admin/sitemap', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Basic ${authToken}` },
        body: JSON.stringify({ action: 'add_missing_pages' }),
      });
      const data = await res.json();
      
      if (res.ok) {
        setAddPagesResult(data);
        
        // Step 2: Auto-ping search engines to notify of sitemap updates
        await fetch('/api/admin/sitemap', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Basic ${authToken}` },
          body: JSON.stringify({ action: 'ping' }),
        });
        
        // Step 3: Re-scan to verify
        setTimeout(() => handleScanPages(), 2000);
      } else {
        setAddPagesResult({ success: false, message: data.error || 'Failed to add pages' });
      }
    } catch (err) {
      setAddPagesResult({ success: false, message: 'Connection error. Please try again.' });
    } finally {
      setIsAddingPages(false);
    }
  };

  // Ping Google & Bing to re-crawl sitemap
  const handlePingSitemap = async () => {
    setIsPinging(true);
    setPingStatus({ type: '', message: '' });
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      const res = await fetch('/api/admin/sitemap', {
        method: 'POST',
        headers: { 'Authorization': `Basic ${authToken}` }
      });
      const data = await res.json();
      if (res.ok) {
        setPingStatus({ type: 'success', message: data.message });
      } else {
        setPingStatus({ type: 'error', message: data.error || 'Ping failed' });
      }
    } catch (err) {
      setPingStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsPinging(false);
    }
  };

  // Website Health Check
  const handleHealthCheck = async () => {
    setIsRunningHealthCheck(true);
    setHealthReport(null);
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      const res = await fetch(`/api/admin/health?mode=${healthCheckMode}`, {
        headers: { 'Authorization': `Basic ${authToken}` }
      });
      const data = await res.json();
      if (res.ok) {
        setHealthReport(data);
      } else {
        setHealthReport({ success: false, error: data.error || 'Health check failed' });
      }
    } catch (err) {
      setHealthReport({ success: false, error: 'Connection error. Please try again.' });
    } finally {
      setIsRunningHealthCheck(false);
    }
  };

  // Remove dead videos found by health check
  const handleRemoveDeadVideos = async (videoIds) => {
    if (!confirm(`Remove ${videoIds.length} dead video(s) from the database? This cannot be undone.`)) return;
    setIsRemovingDeadVideos(true);
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      const res = await fetch('/api/admin/health', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Basic ${authToken}` },
        body: JSON.stringify({ action: 'remove_dead_videos', video_ids: videoIds }),
      });
      const data = await res.json();
      if (res.ok) {
        alert(data.message || 'Dead videos removed successfully!');
        handleHealthCheck();
        loadStats();
      } else {
        alert(data.error || 'Failed to remove videos');
      }
    } catch (err) {
      alert('Connection error. Please try again.');
    } finally {
      setIsRemovingDeadVideos(false);
    }
  };

  // Delete videos for a specific dead artist URL
  const handleDeleteDeadUrlArtist = async (deadUrl) => {
    // Extract artist slug from URL like "/artist/ac-dc"
    const match = deadUrl.match(/\/artist\/(.+)/);
    if (!match) return;
    
    const slug = match[1];
    // Convert slug back to approximate artist name
    const artistName = slug.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
    
    if (!confirm(`Delete all videos for "${artistName}" (slug: ${slug}) from the database?\n\nThis cannot be undone.`)) return;
    
    setDeletingDeadUrls(prev => ({ ...prev, [deadUrl]: true }));
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      
      // First get details about what will be deleted
      const detailRes = await fetch('/api/admin/health', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Basic ${authToken}` },
        body: JSON.stringify({ action: 'get_dead_url_details', dead_urls: [deadUrl] }),
      });
      const detailData = await detailRes.json();
      
      if (detailData.success && detailData.details && detailData.details.length > 0) {
        const detail = detailData.details[0];
        if (detail.matched_artists.length > 0) {
          // Delete videos for each matched artist
          for (const artist of detail.matched_artists) {
            await fetch('/api/admin/health', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Basic ${authToken}` },
              body: JSON.stringify({ action: 'delete_artist_videos', artist_name: artist }),
            });
          }
          alert(`Deleted videos for: ${detail.matched_artists.join(', ')}`);
        } else {
          alert(`No matching artists found in database for slug "${slug}". This URL may already be cleaned up.`);
        }
      }
      
      // Refresh health check
      handleHealthCheck();
      loadStats();
    } catch (err) {
      alert('Connection error. Please try again.');
    } finally {
      setDeletingDeadUrls(prev => ({ ...prev, [deadUrl]: false }));
    }
  };

  // Delete ALL dead URL artists at once
  const handleDeleteAllDeadUrls = async () => {
    const deadUrls = healthReport?.checks?.internal_urls?.details?.dead_urls || [];
    const artistUrls = deadUrls.filter(u => u.url.startsWith('/artist/'));
    
    if (artistUrls.length === 0) {
      alert('No dead artist URLs to delete.');
      return;
    }
    
    if (!confirm(`Delete videos for ${artistUrls.length} dead artist URL(s)?\n\nThis will remove the database entries causing these broken links. This cannot be undone.`)) return;
    
    setIsDeletingDeadUrls(true);
    setDeadUrlAction('Deleting dead URL artists...');
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      
      // Get details for all dead URLs
      const detailRes = await fetch('/api/admin/health', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Basic ${authToken}` },
        body: JSON.stringify({ action: 'get_dead_url_details', dead_urls: artistUrls.map(u => u.url) }),
      });
      const detailData = await detailRes.json();
      
      let totalDeleted = 0;
      if (detailData.success) {
        for (const detail of (detailData.details || [])) {
          for (const artist of detail.matched_artists) {
            setDeadUrlAction(`Deleting "${artist}"...`);
            const delRes = await fetch('/api/admin/health', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json', 'Authorization': `Basic ${authToken}` },
              body: JSON.stringify({ action: 'delete_artist_videos', artist_name: artist }),
            });
            const delData = await delRes.json();
            if (delData.success) totalDeleted += delData.removed_count;
          }
        }
      }
      
      alert(`Done! Deleted ${totalDeleted} videos from ${artistUrls.length} dead artist URLs.`);
      handleHealthCheck();
      loadStats();
    } catch (err) {
      alert('Connection error. Please try again.');
    } finally {
      setIsDeletingDeadUrls(false);
      setDeadUrlAction('');
    }
  };

  // AI SEO Content — Load status
  const loadAiSeoStatus = async () => {
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      const res = await fetch('/api/admin/generate-seo', {
        headers: { 'Authorization': `Basic ${authToken}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAiSeoStatus(data);
      }
    } catch (e) { /* ignore */ }
  };

  // AI SEO Content — Load detailed artist/song list
  const loadAiDetailView = async (type = 'artists') => {
    setAiDetailLoading(true);
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      const res = await fetch(`/api/admin/generate-seo?detail=${type}`, {
        headers: { 'Authorization': `Basic ${authToken}` }
      });
      if (res.ok) {
        const data = await res.json();
        setAiDetailData(data);
      }
    } catch (e) { /* ignore */ }
    setAiDetailLoading(false);
  };

  // AI SEO Content — Generate for single artist
  const handleGenerateSingleArtist = async (artistName, slug) => {
    setIsGeneratingSingle(slug);
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      const res = await fetch('/api/admin/generate-seo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Basic ${authToken}` },
        body: JSON.stringify({ action: 'generate_artist', artist_name: artistName }),
      });
      if (res.ok) {
        // Refresh detail view and status
        await loadAiDetailView('artists');
        await loadAiSeoStatus();
      }
    } catch (err) { /* ignore */ }
    setIsGeneratingSingle(null);
  };

  // AI SEO Content — Generate
  const handleGenerateAiSeo = async () => {
    setIsGeneratingAi(true);
    setAiResults(null);
    setAiProgress(`Starting ${aiGenerateMode === 'batch_artists' ? 'artist' : 'song'} content generation...`);
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      const res = await fetch('/api/admin/generate-seo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Basic ${authToken}` },
        body: JSON.stringify({ action: aiGenerateMode, batch_size: aiBatchSize }),
      });
      const data = await res.json();
      if (res.ok) {
        setAiResults(data);
        setAiProgress('');
        loadAiSeoStatus();
        // Also refresh detail view if it's open
        if (showAiDetailView) {
          loadAiDetailView(aiGenerateMode === 'batch_songs' ? 'songs' : 'artists');
        }
      } else {
        setAiResults({ error: data.error || 'Generation failed' });
        setAiProgress('');
      }
    } catch (err) {
      setAiResults({ error: 'Connection error. Please try again.' });
      setAiProgress('');
    } finally {
      setIsGeneratingAi(false);
    }
  };


  // Sync scheduled videos from YouTube
  const handleSyncScheduledVideos = async () => {
    setIsSyncingScheduled(true);
    setScheduledSyncStatus({ type: '', message: '' });
    try {
      const storedPassword = sessionStorage.getItem('dadrock_admin_auth');
      const authToken = btoa(`admin:${storedPassword}`);
      const response = await fetch('/api/admin/youtube/scheduled', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Basic ${authToken}`
        }
      });
      const data = await response.json();
      if (response.ok) {
        setScheduledSyncStatus({ 
          type: 'success', 
          message: data.message 
        });
        loadUpcomingVideos(); // Refresh list
      } else {
        if (data.need_reconnect) {
          setYoutubeConnected(false);
        }
        setScheduledSyncStatus({ type: 'error', message: data.error || 'Failed to sync scheduled videos' });
      }
    } catch (err) {
      setScheduledSyncStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsSyncingScheduled(false);
    }
  };

  // Load upcoming videos for admin
  const loadUpcomingVideos = async () => {
    try {
      const authToken = sessionStorage.getItem('dadrock_admin_auth');
      const res = await fetch('/api/admin/upcoming', {
        headers: { 'Authorization': 'Basic ' + btoa('admin:' + authToken) },
      });
      if (res.ok) {
        const data = await res.json();
        setAdminUpcomingVideos(data.upcoming || []);
      }
    } catch (err) {
      console.error('Failed to load upcoming videos:', err);
    }
  };

  // Add upcoming video manually
  const handleAddUpcoming = async () => {
    if (!newUpcomingTitle || !newUpcomingDate) return;
    
    setIsAddingUpcoming(true);
    try {
      const authToken = sessionStorage.getItem('dadrock_admin_auth');
      const res = await fetch('/api/admin/upcoming', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Basic ' + btoa('admin:' + authToken),
        },
        body: JSON.stringify({
          title: newUpcomingTitle,
          artist: newUpcomingArtist,
          scheduled_date: new Date(newUpcomingDate).toISOString(),
          thumbnail: newUpcomingThumbnail,
          description: newUpcomingDescription
        }),
      });
      
      if (res.ok) {
        // Clear form and reload list
        setNewUpcomingTitle('');
        setNewUpcomingArtist('');
        setNewUpcomingDate('');
        setNewUpcomingThumbnail('');
        setNewUpcomingDescription('');
        loadUpcomingVideos();
      }
    } catch (err) {
      console.error('Failed to add upcoming video:', err);
    } finally {
      setIsAddingUpcoming(false);
    }
  };

  // Delete upcoming video
  const handleDeleteUpcoming = async (id) => {
    try {
      const authToken = sessionStorage.getItem('dadrock_admin_auth');
      const res = await fetch(`/api/admin/upcoming/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': 'Basic ' + btoa('admin:' + authToken) },
      });
      
      if (res.ok) {
        loadUpcomingVideos();
      }
    } catch (err) {
      console.error('Failed to delete upcoming video:', err);
    }
  };

  // Load top lessons configuration
  const loadTopLessons = async () => {
    try {
      const authToken = sessionStorage.getItem('dadrock_admin_auth');
      const res = await fetch('/api/admin/top-lessons', {
        headers: { 'Authorization': 'Basic ' + btoa('admin:' + authToken) },
      });
      if (res.ok) {
        const data = await res.json();
        setTopLessons(data.lessons || Array(10).fill(null).map((_, i) => ({ position: i + 1, youtubeUrl: '', title: '', artist: '' })));
      }
    } catch (err) {
      console.error('Failed to load top lessons:', err);
    }
  };

  // Save top lessons configuration
  const handleSaveTopLessons = async () => {
    setIsSavingTopLessons(true);
    setTopLessonsSaveStatus({ type: '', message: '' });
    
    try {
      const authToken = sessionStorage.getItem('dadrock_admin_auth');
      const res = await fetch('/api/admin/top-lessons', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Basic ' + btoa('admin:' + authToken),
        },
        body: JSON.stringify({ lessons: topLessons }),
      });
      
      if (res.ok) {
        setTopLessonsSaveStatus({ type: 'success', message: 'Top lessons saved successfully!' });
      } else {
        const data = await res.json();
        setTopLessonsSaveStatus({ type: 'error', message: data.error || 'Failed to save' });
      }
    } catch (err) {
      setTopLessonsSaveStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsSavingTopLessons(false);
    }
  };

  // Sync top 100 song pages
  const handleSyncSongPages = async () => {
    setIsSyncingSongs(true);
    setSongSyncStatus({ type: '', message: '' });
    try {
      const authToken = sessionStorage.getItem('dadrock_admin_auth');
      const res = await fetch('/api/admin/sync-songs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Basic ' + btoa('admin:' + authToken),
        },
      });
      const data = await res.json();
      if (res.ok) {
        setSongSyncStatus({ type: 'success', message: data.message });
        loadSongPageCount();
      } else {
        setSongSyncStatus({ type: 'error', message: data.error || 'Failed to sync songs' });
      }
    } catch (err) {
      setSongSyncStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsSyncingSongs(false);
    }
  };

  // Load song page count
  const loadSongPageCount = async () => {
    try {
      const res = await fetch('/api/songs?limit=1');
      if (res.ok) {
        const data = await res.json();
        setSongPageCount(data.total || 0);
      }
    } catch (err) {}
  };

  // Add manual song page
  const handleAddManualSong = async () => {
    if (!manualSongUrl.trim()) return;
    setIsAddingManualSong(true);
    setManualSongStatus({ type: '', message: '' });
    try {
      const authToken = sessionStorage.getItem('dadrock_admin_auth');
      const res = await fetch('/api/admin/sync-songs', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Basic ' + btoa('admin:' + authToken),
        },
        body: JSON.stringify({ youtubeUrl: manualSongUrl.trim() }),
      });
      const data = await res.json();
      if (res.ok) {
        setManualSongStatus({ type: 'success', message: `Song page created: ${data.title} by ${data.artist} → /songs/${data.slug}` });
        setManualSongUrl('');
        loadSongPageCount();
        if (showSongsList) loadSongPagesList();
      } else {
        setManualSongStatus({ type: 'error', message: data.error || 'Failed to create song page' });
      }
    } catch (err) {
      setManualSongStatus({ type: 'error', message: 'Connection error. Please try again.' });
    } finally {
      setIsAddingManualSong(false);
    }
  };

  // Load song pages list
  const loadSongPagesList = async () => {
    try {
      const res = await fetch('/api/songs?limit=200');
      if (res.ok) {
        const data = await res.json();
        setSongPagesList(data.songs || []);
      }
    } catch (err) {}
  };

  // Delete a song page
  const handleDeleteSong = async (videoId, title) => {
    if (!confirm(`Delete song page for "${title}"? This cannot be undone.`)) return;
    setDeletingSongId(videoId);
    try {
      const authToken = sessionStorage.getItem('dadrock_admin_auth');
      const res = await fetch('/api/admin/sync-songs', {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Basic ' + btoa('admin:' + authToken),
        },
        body: JSON.stringify({ videoId }),
      });
      if (res.ok) {
        setSongPagesList(prev => prev.filter(s => s.videoId !== videoId));
        setSongPageCount(prev => prev - 1);
      }
    } catch (err) {}
    setDeletingSongId(null);
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
      checkYoutubeConnection();
      loadUpcomingVideos();
      loadTopLessons();
      loadSongPageCount();
      loadAiSeoStatus();
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
          {/* Logo with Marshall Amp Stacks - Bass Emanation Effect */}
          <div className={`mb-4 relative flex items-center justify-center overflow-visible transition-opacity duration-500 ${pageReady ? 'opacity-100' : 'opacity-0'}`}>
            {/* 🎵 Floating Music Notes */}
            {pageReady && (
              <div className="absolute inset-0 pointer-events-none" style={{ zIndex: 20 }}>
                <span className="float-note" style={{ left: '8%' }}>🎵</span>
                <span className="float-note" style={{ left: '22%' }}>🎶</span>
                <span className="float-note" style={{ left: '48%' }}>♪</span>
                <span className="float-note" style={{ left: '68%' }}>🎸</span>
                <span className="float-note" style={{ left: '88%' }}>🤘</span>
              </div>
            )}
            
            {/* 🔥 Ember Sparks */}
            {pageReady && (
              <div className="ember-container" style={{ zIndex: 15 }}>
                <div className="ember" /><div className="ember" /><div className="ember" />
                <div className="ember" /><div className="ember" /><div className="ember" />
              </div>
            )}

            {/* Sound Wave Rings - Only animate when page is ready */}
            {pageReady && (
              <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                <div className="absolute w-[60%] h-[60%] rounded-full border-2 border-amber-500/50 sound-wave-1" />
                <div className="absolute w-[80%] h-[80%] rounded-full border-2 border-red-500/40 sound-wave-2" />
                <div className="absolute w-[100%] h-[100%] rounded-full border border-amber-500/30 sound-wave-3" />
              </div>
            )}
            
            {/* Container for layered images */}
            <div className="relative flex items-center justify-center">
              {/* Left Marshall Amp Stack - Mirrored */}
              <img
                src={MARSHALL_AMP_URL}
                alt="Marshall Amp Left"
                className={`absolute pointer-events-none ${pageReady ? 'amp-left' : ''}`}
                style={{ 
                  height: '100%',
                  width: 'auto',
                  left: '-5%',
                  top: '5%',
                  transform: 'scaleX(-1)',
                  zIndex: 5,
                  opacity: 0.95
                }}
              />
              
              {/* Right Marshall Amp Stack */}
              <img
                src={MARSHALL_AMP_URL}
                alt="Marshall Amp Right"
                className={`absolute pointer-events-none ${pageReady ? 'amp-right' : ''}`}
                style={{ 
                  height: '100%',
                  width: 'auto',
                  right: '-5%',
                  top: '5%',
                  zIndex: 5,
                  opacity: 0.95
                }}
              />
              
              {/* Main Guitar Logo - Centered */}
              <img
                src={LOGO_URL}
                alt="DadRock Tabs Logo"
                onClick={handleLogoClick}
                className={`relative w-[16rem] sm:w-[22rem] md:w-[28rem] cursor-pointer select-none hover:scale-105 transition-transform duration-300 ${pageReady ? 'float-animation logo-glow' : ''}`}
                style={{ zIndex: 10 }}
              />
            </div>
          </div>

          {/* Definition */}
          <div className={`text-center mb-8 max-w-2xl transition-opacity duration-500 ${pageReady ? 'opacity-100' : 'opacity-0'}`} style={{ transitionDelay: '0.1s' }}>
            <div className="flex items-center justify-center gap-3 flex-wrap mb-3">
              <img 
                src={DADROCK_TEXT_URL} 
                alt="DadRock" 
                className="h-12 sm:h-14 md:h-16"
                style={{ filter: 'drop-shadow(0 0 10px rgba(251, 191, 36, 0.4))' }}
              />
              <span className="text-amber-500 text-2xl sm:text-3xl md:text-4xl font-bold neon-flicker">{t.definition.pronunciation}</span>
            </div>
            <p className="text-amber-400/80 italic text-2xl sm:text-3xl md:text-4xl mt-2 tracking-widest font-rock-alt">{t.definition.partOfSpeech}</p>
            <p className="rock-definition mt-5 text-xl sm:text-2xl md:text-3xl px-2">
              {t.definition.meaning}
            </p>
          </div>

          {/* Tagline */}
          <p className={`rock-tagline text-center text-xl sm:text-2xl md:text-3xl mb-10 max-w-2xl px-4 leading-relaxed transition-opacity duration-500 ${pageReady ? 'opacity-100' : 'opacity-0'}`} style={{ transitionDelay: '0.2s' }}>
            {t.tagline}
          </p>

          {/* Search Form with Gradient Border */}
          <form onSubmit={handleSearch} className={`w-full max-w-2xl mb-8 transition-opacity duration-500 ${pageReady ? 'opacity-100' : 'opacity-0'}`} style={{ transitionDelay: '0.3s' }}>
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

          {/* 🎲 Random Song Button */}
          <button
            onClick={async () => {
              try {
                const res = await fetch('/api/random-song');
                const data = await res.json();
                if (data.slug) {
                  if (window.__flameNavigate) {
                    window.__flameNavigate(`/songs/${data.slug}`);
                  } else {
                    window.location.href = `/songs/${data.slug}`;
                  }
                }
              } catch (e) { console.error(e); }
            }}
            className={`inline-flex items-center gap-2 px-8 py-4 rounded-full bg-gradient-to-r from-red-600 via-orange-500 to-amber-500 hover:from-red-500 hover:via-orange-400 hover:to-amber-400 text-white font-bold uppercase tracking-wide mb-4 transition-all duration-500 fire-glow bass-drop-hover ${pageReady ? 'opacity-100' : 'opacity-0'}`}
            style={{ transitionDelay: '0.35s' }}
          >
            <span className="text-xl rock-bounce">🎲</span>
            Random Song
          </button>

          {/* Subscribe Button with Pulse Glow */}
          <a
            href={YOUTUBE_CHANNEL}
            target="_blank"
            rel="noopener noreferrer"
            className={`inline-flex items-center gap-2 px-8 py-4 rounded-full subscribe-btn ${pageReady ? 'pulse-glow' : ''} text-white font-bold uppercase tracking-wide mb-4 transition-opacity duration-500 ${pageReady ? 'opacity-100' : 'opacity-0'}`}
            style={{ transitionDelay: '0.4s' }}
          >
            <Youtube className="w-6 h-6" />
            {t.subscribe}
          </a>

          {/* Coming Soon Button - Links to dedicated landing page */}
          <Link
            href="/coming-soon"
            className={`inline-flex items-center gap-2 px-8 py-4 rounded-full bg-purple-600 hover:bg-purple-500 text-white font-bold uppercase tracking-wide mb-10 transition-all duration-500 ${pageReady ? 'opacity-100' : 'opacity-0'}`}
            style={{ transitionDelay: '0.45s' }}
          >
            <Calendar className="w-6 h-6" />
            {t.comingSoon || 'Coming Soon'}
          </Link>

          {/* Top Lessons Button - Links to top viewed videos page */}
          <Link
            href="/top-lessons"
            className={`inline-flex items-center gap-2 px-8 py-4 rounded-full bg-amber-600 hover:bg-amber-500 text-white font-bold uppercase tracking-wide mb-4 transition-all duration-500 ${pageReady ? 'opacity-100' : 'opacity-0'}`}
            style={{ transitionDelay: '0.5s' }}
          >
            <Trophy className="w-6 h-6" />
            {t.topLessons || 'Top Lessons'}
          </Link>

          {/* DadRock Tabs Quickies Button */}
          <Link
            href="/quickies"
            className={`inline-flex items-center gap-2 px-8 py-4 rounded-full bg-yellow-500 hover:bg-yellow-400 text-black font-bold uppercase tracking-wide mb-4 transition-all duration-500 ${pageReady ? 'opacity-100' : 'opacity-0'}`}
            style={{ transitionDelay: '0.55s' }}
          >
            <Zap className="w-6 h-6" />
            DadRock Tabs Quickies
          </Link>

          {/* Guitar Tools Button */}
          <Link
            href="/tools"
            className={`inline-flex items-center gap-2 px-8 py-4 rounded-full bg-teal-600 hover:bg-teal-500 text-white font-bold uppercase tracking-wide mb-4 transition-all duration-500 ${pageReady ? 'opacity-100' : 'opacity-0'}`}
            style={{ transitionDelay: '0.6s' }}
          >
            <Music className="w-6 h-6" />
            Guitar Tools
          </Link>

          {/* What's New Button */}
          <Link
            href="/whats-new"
            className={`inline-flex items-center gap-2 px-8 py-4 rounded-full bg-green-600 hover:bg-green-500 text-white font-bold uppercase tracking-wide mb-10 transition-all duration-500 ${pageReady ? 'opacity-100' : 'opacity-0'}`}
            style={{ transitionDelay: '0.65s' }}
          >
            <RefreshCw className="w-6 h-6" />
            What&apos;s New
          </Link>

          {/* Popular Searches with Glassmorphism */}
          <div className="w-full max-w-2xl mb-10 fade-in-up" style={{ animationDelay: '0.6s' }}>
            <div className="glass-card rounded-2xl p-6 fire-glow spotlight-sweep">
              <p className="text-center text-zinc-300 mb-5 flex items-center justify-center gap-3 text-lg font-medium">
                {/* Equalizer Visualizer */}
                <span className="eq-visualizer">
                  <span className="bar" /><span className="bar" /><span className="bar" /><span className="bar" /><span className="bar" /><span className="bar" /><span className="bar" />
                </span>
                <span className="text-2xl rock-bounce">🔥</span> {t.popularSearches}
                <span className="eq-visualizer">
                  <span className="bar" /><span className="bar" /><span className="bar" /><span className="bar" /><span className="bar" /><span className="bar" /><span className="bar" />
                </span>
              </p>
              <div className="flex flex-wrap justify-center gap-3">
                {popularArtists.map((artist, index) => (
                  <button
                    key={artist.name}
                    onClick={() => handleArtistClick(artist.name)}
                    className="artist-btn px-5 py-2.5 rounded-full bg-zinc-800/80 border border-zinc-700 text-sm text-zinc-200 hover:text-white font-medium bass-drop-hover"
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
            {/* Rock Divider */}
            <div className="rock-divider mb-8 max-w-md mx-auto">
              <span className="skull-divider">💀⚡💀</span>
            </div>
            <p className="text-center text-zinc-300 mb-5 flex items-center justify-center gap-2 text-lg font-medium">
              <span className="text-2xl">📢</span> {t.shareDadRock}
            </p>
            <div className="flex justify-center gap-4">
              <a
                href="https://www.facebook.com/sharer/sharer.php?u=https://dadrocktabs.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-12 h-12 rounded-full bg-blue-600 hover:bg-blue-500 flex items-center justify-center transition-all hover:scale-110 hover:shadow-[0_0_20px_rgba(37,99,235,0.5)]"
              >
                <Facebook className="w-5 h-5 text-white" />
              </a>
              <a
                href="https://twitter.com/intent/tweet?url=https://dadrocktabs.com&text=Check%20out%20DadRock%20Tabs!"
                target="_blank"
                rel="noopener noreferrer"
                className="w-12 h-12 rounded-full bg-sky-500 hover:bg-sky-400 flex items-center justify-center transition-all hover:scale-110 hover:shadow-[0_0_20px_rgba(14,165,233,0.5)]"
              >
                <Twitter className="w-5 h-5 text-white" />
              </a>
              <button
                onClick={() => navigator.share?.({ url: 'https://dadrocktabs.com', title: 'DadRock Tabs' })}
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

          {/* FAQ Section for SEO */}
          {t.faq && t.faq.length > 0 && (
            <div className="w-full max-w-4xl mt-16 px-4">
              <h2 className="text-2xl sm:text-3xl font-bold text-center text-amber-500 mb-8 font-rock">
                {t.faqTitle || 'Frequently Asked Questions'}
              </h2>
              <div className="space-y-4">
                {t.faq.map((item, index) => (
                  <details 
                    key={index} 
                    className="group bg-zinc-900/80 border border-zinc-700 rounded-xl overflow-hidden"
                  >
                    <summary className="flex items-center justify-between p-5 cursor-pointer hover:bg-zinc-800/50 transition-colors">
                      <h3 className="text-lg font-semibold text-white pr-4">{item.question}</h3>
                      <ChevronDown className="w-5 h-5 text-amber-500 transform group-open:rotate-180 transition-transform flex-shrink-0" />
                    </summary>
                    <div className="px-5 pb-5 text-zinc-300 leading-relaxed">
                      {item.answer}
                    </div>
                  </details>
                ))}
              </div>
            </div>
          )}

          {/* FAQ Schema for SEO - Invisible structured data */}
          {t.faq && t.faq.length > 0 && (
            <script
              type="application/ld+json"
              dangerouslySetInnerHTML={{
                __html: JSON.stringify({
                  "@context": "https://schema.org",
                  "@type": "FAQPage",
                  "mainEntity": t.faq.map(item => ({
                    "@type": "Question",
                    "name": item.question,
                    "acceptedAnswer": {
                      "@type": "Answer",
                      "text": item.answer
                    }
                  }))
                })
              }}
            />
          )}
        </main>

        {/* About Section */}
        <section className="w-full max-w-3xl mx-auto mt-16 px-4 text-center fade-in-up" style={{ animationDelay: '0.95s' }}>
          <p className="text-zinc-400 text-base leading-relaxed mb-4">
            DadRockTabs provides guitar and bass tab tutorials for classic rock
            and heavy metal bands like AC/DC, Metallica, Black Sabbath, and Van Halen.
          </p>
          <p className="text-zinc-400 text-base leading-relaxed">
            Each lesson includes synchronized tabs with the original music
            so players can follow along and learn the exact riffs and bass lines.
          </p>
        </section>

        {/* Newsletter & Quick Links */}
        <section className="px-4 sm:px-6 py-12 max-w-4xl mx-auto fade-in-up" style={{ animationDelay: '0.9s' }}>
          {/* Rock Divider with Vinyl */}
          <div className="flex items-center justify-center gap-6 mb-8">
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-amber-500/40 to-transparent" />
            <div className="vinyl-record vinyl-spin flex-shrink-0" />
            <div className="flex-1 h-px bg-gradient-to-r from-transparent via-red-500/40 to-transparent" />
          </div>
          
          {/* Quick Browse Links */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-8">
            <Link href="/difficulty/beginner" className="p-4 bg-zinc-900/80 rounded-xl border border-zinc-800 hover:border-green-500/50 text-center transition-all group">
              <span className="text-2xl block mb-1">🌱</span>
              <span className="text-sm font-medium text-zinc-300 group-hover:text-green-400 transition-colors">Beginner</span>
            </Link>
            <Link href="/difficulty/intermediate" className="p-4 bg-zinc-900/80 rounded-xl border border-zinc-800 hover:border-amber-500/50 text-center transition-all group">
              <span className="text-2xl block mb-1">🔥</span>
              <span className="text-sm font-medium text-zinc-300 group-hover:text-amber-400 transition-colors">Intermediate</span>
            </Link>
            <Link href="/difficulty/advanced" className="p-4 bg-zinc-900/80 rounded-xl border border-zinc-800 hover:border-red-500/50 text-center transition-all group">
              <span className="text-2xl block mb-1">⚡</span>
              <span className="text-sm font-medium text-zinc-300 group-hover:text-red-400 transition-colors">Advanced</span>
            </Link>
            <Link href="/learn" className="p-4 bg-zinc-900/80 rounded-xl border border-zinc-800 hover:border-purple-500/50 text-center transition-all group">
              <span className="text-2xl block mb-1">📖</span>
              <span className="text-sm font-medium text-zinc-300 group-hover:text-purple-400 transition-colors">Guides</span>
            </Link>
          </div>
          {/* Newsletter Signup */}
          <NewsletterSignup />
          
          {/* Gamification Panel */}
          <div className="mt-8">
            <GamificationPanel />
          </div>
        </section>

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

          {/* Related Artists Section for Internal Linking - Show after search results */}
          {!loading && searchResults.length > 0 && (
            <div className="mt-12 border-t border-zinc-800 pt-8">
              <h3 className="text-xl font-bold text-amber-500 mb-6 font-rock">
                🎸 Explore More Classic Rock & Metal Artists
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
                {getRelatedArtists(activeSearch, 12).map((artist, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setSearchQuery(artist.name);
                      performSearch(artist.name, 'artist');
                    }}
                    className="flex items-center justify-center gap-2 py-3 px-3 bg-zinc-900/80 hover:bg-zinc-800 border border-zinc-700 hover:border-amber-500/50 rounded-xl text-zinc-200 hover:text-white transition-all group"
                  >
                    <span className="text-lg group-hover:scale-110 transition-transform">{artist.emoji}</span>
                    <span className="font-medium text-sm truncate">{artist.name}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Show Browse All Artists when no search active */}
          {!loading && !activeSearch && (
            <div className="mt-8">
              <h3 className="text-xl font-bold text-amber-500 mb-6 font-rock">
                🎸 Browse All Artists
              </h3>
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
                {allArtists.slice(0, 24).map((artist, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setSearchQuery(artist.name);
                      performSearch(artist.name, 'artist');
                    }}
                    className="flex items-center justify-center gap-2 py-3 px-3 bg-zinc-900/80 hover:bg-zinc-800 border border-zinc-700 hover:border-amber-500/50 rounded-xl text-zinc-200 hover:text-white transition-all group"
                  >
                    <span className="text-lg group-hover:scale-110 transition-transform">{artist.emoji}</span>
                    <span className="font-medium text-sm truncate">{artist.name}</span>
                  </button>
                ))}
              </div>
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
                  style={{ width: `${((adDuration - adCountdown) / adDuration) * 100}%` }}
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

          {/* Video Player Container */}
          <div className="relative mb-4">
            <div 
              id="video-container"
              className="aspect-video rounded-xl overflow-hidden border border-zinc-800 bg-black"
            >
              <iframe
                id="video-iframe"
                src={watchEmbedUrl}
                title={selectedVideo.song}
                className="w-full h-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                allowFullScreen
                style={{ border: 'none' }}
              />
            </div>
            
            {/* Fullscreen hint overlay */}
            <div className="absolute bottom-3 right-3 bg-black/70 px-3 py-1.5 rounded-full text-xs text-zinc-300 flex items-center gap-1.5 pointer-events-none">
              <Maximize className="w-3 h-3" />
              <span>Tap video → ⛶ for fullscreen</span>
            </div>
          </div>

          {/* VideoObject Schema for SEO */}
          <script
            type="application/ld+json"
            dangerouslySetInnerHTML={{
              __html: JSON.stringify({
                "@context": "https://schema.org",
                "@type": "VideoObject",
                "name": `${selectedVideo.song} - ${selectedVideo.artist} Guitar Tab Tutorial`,
                "description": `Learn to play ${selectedVideo.song} by ${selectedVideo.artist} with this guitar and bass tablature video tutorial. Free lesson from DadRock Tabs.`,
                "thumbnailUrl": selectedVideo.thumbnail || `https://img.youtube.com/vi/${selectedVideo.video_id}/maxresdefault.jpg`,
                "uploadDate": selectedVideo.created_at || new Date().toISOString(),
                "contentUrl": selectedVideo.youtube_url,
                "embedUrl": watchEmbedUrl,
                "publisher": {
                  "@type": "Organization",
                  "name": "DadRock Tabs",
                  "logo": {
                    "@type": "ImageObject",
                    "url": LOGO_URL
                  }
                },
                "interactionStatistic": {
                  "@type": "InteractionCounter",
                  "interactionType": { "@type": "WatchAction" },
                  "userInteractionCount": selectedVideo.view_count || 0
                }
              })
            }}
          />

          {/* Open in YouTube App Button */}
          <div className="flex justify-center gap-3 mb-6">
            <button
              onClick={() => {
                // Open in YouTube app (better fullscreen experience on mobile)
                window.open(selectedVideo.youtube_url, '_blank');
              }}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-zinc-800 hover:bg-zinc-700 text-white font-medium rounded-full transition-all border border-zinc-700"
            >
              <Youtube className="w-4 h-4 text-red-500" />
              <span>Open in YouTube App</span>
              <Smartphone className="w-4 h-4 rotate-90 text-zinc-400" />
            </button>
          </div>

          <div className="flex justify-center">
            <button
              onClick={() => setCurrentPage('search')}
              className="inline-flex items-center justify-center gap-3 px-8 py-4 rounded-full bg-zinc-900 hover:bg-zinc-800 border border-zinc-700 font-bold uppercase tracking-wide transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
              Go Back
            </button>
          </div>

          {/* Related Artists Section for Internal Linking */}
          <div className="mt-12 w-full">
            <h3 className="text-xl font-bold text-amber-500 text-center mb-6 font-rock">
              🎸 Explore More Artists Like {selectedVideo.artist}
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
              {getRelatedArtists(selectedVideo.artist, 6).map((artist, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setSearchQuery(artist.name);
                    performSearch(artist.name, 'artist');
                  }}
                  className="flex items-center justify-center gap-2 py-3 px-4 bg-zinc-900/80 hover:bg-zinc-800 border border-zinc-700 hover:border-amber-500/50 rounded-xl text-zinc-200 hover:text-white transition-all group"
                >
                  <span className="text-xl group-hover:scale-110 transition-transform">{artist.emoji}</span>
                  <span className="font-medium truncate">{artist.name}</span>
                </button>
              ))}
            </div>
            <p className="text-center text-zinc-500 text-sm mt-4">
              Click any artist to discover more guitar & bass tabs
            </p>
          </div>

          {/* SEO Content */}
          <div className="mt-12 w-full max-w-3xl mx-auto text-center">
            <p className="text-zinc-400 text-base leading-relaxed mb-4">
              DadRockTabs provides guitar and bass tab tutorials for classic rock
              and heavy metal bands like AC/DC, Metallica, Black Sabbath, and Van Halen.
            </p>
            <p className="text-zinc-400 text-base leading-relaxed">
              Each lesson includes synchronized tabs with the original music
              so players can follow along and learn the exact riffs and bass lines.
            </p>
          </div>

          {/* Animated Logo with Marshall Amps */}
          <div className="mt-10 mb-6 relative flex items-center justify-center overflow-visible">
            {/* Sound Wave Rings */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="absolute w-[60%] h-[60%] rounded-full border-2 border-amber-500/50 sound-wave-1" />
              <div className="absolute w-[80%] h-[80%] rounded-full border-2 border-red-500/40 sound-wave-2" />
              <div className="absolute w-[100%] h-[100%] rounded-full border border-amber-500/30 sound-wave-3" />
            </div>
            
            {/* Container for layered images */}
            <div className="relative flex items-center justify-center">
              {/* Left Marshall Amp Stack - Mirrored */}
              <img
                src={MARSHALL_AMP_URL}
                alt="Marshall Amp Left"
                className="absolute pointer-events-none amp-left"
                style={{ 
                  height: '100%',
                  width: 'auto',
                  left: '-5%',
                  top: '5%',
                  transform: 'scaleX(-1)',
                  zIndex: 5,
                  opacity: 0.95
                }}
              />
              
              {/* Right Marshall Amp Stack */}
              <img
                src={MARSHALL_AMP_URL}
                alt="Marshall Amp Right"
                className="absolute pointer-events-none amp-right"
                style={{ 
                  height: '100%',
                  width: 'auto',
                  right: '-5%',
                  top: '5%',
                  zIndex: 5,
                  opacity: 0.95
                }}
              />
              
              {/* Main Guitar Logo - Centered */}
              <img
                src={LOGO_URL}
                alt="DadRock Tabs Logo"
                onClick={() => setCurrentPage('home')}
                className="relative w-[12rem] sm:w-[16rem] md:w-[20rem] cursor-pointer select-none hover:scale-105 transition-transform duration-300 float-animation logo-glow"
                style={{ zIndex: 10 }}
              />
            </div>
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

            {/* Dead Link Cleanup */}
            <div className="mt-6 pt-6 border-t border-zinc-700">
              <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
                <Trash2 className="w-4 h-4 text-orange-400" />
                Clean Up Dead Links
              </h3>
              <p className="text-zinc-400 text-sm mb-4">
                Scan all videos in the database and remove any that have been deleted, made private, or are no longer available on YouTube.
              </p>
              
              {cleanupStatus.message && (
                <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
                  cleanupStatus.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                }`}>
                  {cleanupStatus.type === 'success' ? <CheckCircle className="w-5 h-5 flex-shrink-0" /> : <AlertCircle className="w-5 h-5 flex-shrink-0" />}
                  <span className="text-sm">{cleanupStatus.message}</span>
                </div>
              )}

              <button
                onClick={handleYouTubeCleanup}
                disabled={isCleaning}
                className="flex items-center justify-center gap-2 px-6 py-3 bg-orange-600 text-white font-bold rounded-lg hover:bg-orange-500 transition-colors disabled:opacity-50"
              >
                {isCleaning ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Scanning... (this may take a moment)
                  </>
                ) : (
                  <>
                    <Trash2 className="w-5 h-5" />
                    Scan &amp; Remove Dead Links
                  </>
                )}
              </button>

              {/* Show removed videos list */}
              {cleanupRemovedVideos.length > 0 && (
                <div className="mt-4">
                  <button
                    onClick={() => setShowRemovedList(!showRemovedList)}
                    className="flex items-center gap-2 text-orange-400 hover:text-orange-300 transition-colors font-medium text-sm"
                  >
                    {showRemovedList ? '▼' : '▶'} View Removed Videos ({cleanupRemovedVideos.length})
                  </button>

                  {showRemovedList && (
                    <div className="mt-3 max-h-64 overflow-y-auto rounded-lg border border-zinc-700">
                      <table className="w-full text-sm">
                        <thead className="bg-zinc-800 sticky top-0">
                          <tr>
                            <th className="text-left px-3 py-2 text-zinc-400 font-medium">#</th>
                            <th className="text-left px-3 py-2 text-zinc-400 font-medium">Song</th>
                            <th className="text-left px-3 py-2 text-zinc-400 font-medium">Artist</th>
                            <th className="text-left px-3 py-2 text-zinc-400 font-medium">URL</th>
                          </tr>
                        </thead>
                        <tbody>
                          {cleanupRemovedVideos.map((video, idx) => (
                            <tr key={video.id} className="border-t border-zinc-800 hover:bg-zinc-800/50">
                              <td className="px-3 py-2 text-zinc-500">{idx + 1}</td>
                              <td className="px-3 py-2 text-white font-medium truncate max-w-[200px]">{video.song}</td>
                              <td className="px-3 py-2 text-zinc-300 truncate max-w-[150px]">{video.artist}</td>
                              <td className="px-3 py-2">
                                <a href={video.youtube_url} target="_blank" rel="noopener noreferrer" className="text-red-400 hover:text-red-300 text-xs truncate max-w-[200px] block line-through">
                                  {video.youtube_url}
                                </a>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* YouTube OAuth & Scheduled Videos Section */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-purple-500" />
              Upcoming / Scheduled Videos
            </h2>
            <p className="text-zinc-400 mb-4">
              Connect your YouTube account to automatically import scheduled videos, or add them manually.
            </p>
            
            {/* YouTube OAuth Connection Status */}
            <div className="mb-6 p-4 bg-zinc-800/50 rounded-lg">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-zinc-400">YouTube Connection Status</p>
                  <p className={`font-semibold ${youtubeConnected ? 'text-green-400' : 'text-zinc-500'}`}>
                    {youtubeConnected ? `✓ Connected: ${youtubeChannelName}` : '○ Not Connected'}
                  </p>
                </div>
                <a
                  href="/api/auth/youtube?action=connect"
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-colors ${
                    youtubeConnected 
                      ? 'bg-zinc-700 text-zinc-300 hover:bg-zinc-600' 
                      : 'bg-purple-600 text-white hover:bg-purple-500'
                  }`}
                >
                  <Youtube className="w-4 h-4" />
                  {youtubeConnected ? 'Reconnect' : 'Connect YouTube'}
                </a>
              </div>
            </div>

            {/* Sync Scheduled Videos Button */}
            {youtubeConnected && (
              <div className="mb-6">
                {scheduledSyncStatus.message && (
                  <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
                    scheduledSyncStatus.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {scheduledSyncStatus.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                    {scheduledSyncStatus.message}
                  </div>
                )}
                <button
                  onClick={handleSyncScheduledVideos}
                  disabled={isSyncingScheduled}
                  className="flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 text-white font-bold rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-50"
                >
                  <Calendar className="w-5 h-5" />
                  {isSyncingScheduled ? 'Syncing Scheduled...' : 'Sync Scheduled Videos'}
                </button>
              </div>
            )}

            {/* Manual Add Upcoming Video */}
            <div className="border-t border-zinc-700 pt-6">
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                <Plus className="w-5 h-5 text-amber-500" />
                Add Upcoming Video Manually
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <input
                  type="text"
                  value={newUpcomingTitle}
                  onChange={(e) => setNewUpcomingTitle(e.target.value)}
                  className="px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                  placeholder="Song Title"
                />
                <input
                  type="text"
                  value={newUpcomingArtist}
                  onChange={(e) => setNewUpcomingArtist(e.target.value)}
                  className="px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                  placeholder="Artist Name"
                />
                <input
                  type="datetime-local"
                  value={newUpcomingDate}
                  onChange={(e) => setNewUpcomingDate(e.target.value)}
                  className="px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                />
                <input
                  type="text"
                  value={newUpcomingThumbnail}
                  onChange={(e) => setNewUpcomingThumbnail(e.target.value)}
                  className="px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                  placeholder="Thumbnail URL (optional)"
                />
              </div>
              <button
                onClick={handleAddUpcoming}
                disabled={isAddingUpcoming || !newUpcomingTitle || !newUpcomingDate}
                className="flex items-center gap-2 px-6 py-3 bg-amber-500 text-black font-bold rounded-lg hover:bg-amber-400 transition-colors disabled:opacity-50"
              >
                <Plus className="w-5 h-5" />
                {isAddingUpcoming ? 'Adding...' : 'Add Upcoming Video'}
              </button>
            </div>

            {/* List of Upcoming Videos */}
            {adminUpcomingVideos.length > 0 && (
              <div className="border-t border-zinc-700 pt-6 mt-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-amber-500" />
                  Scheduled Videos ({adminUpcomingVideos.length})
                </h3>
                <div className="space-y-3">
                  {adminUpcomingVideos.map((video) => (
                    <div key={video.id} className="flex items-center justify-between p-4 bg-zinc-800/50 rounded-lg">
                      <div className="flex items-center gap-4">
                        {video.thumbnail && (
                          <img src={video.thumbnail} alt={video.title} className="w-16 h-10 object-cover rounded" />
                        )}
                        <div>
                          <p className="font-semibold text-white">{video.title}</p>
                          <p className="text-sm text-zinc-400">{video.artist}</p>
                          <p className="text-xs text-purple-400">
                            <Calendar className="w-3 h-3 inline mr-1" />
                            {new Date(video.scheduled_date).toLocaleString()}
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDeleteUpcoming(video.id)}
                        className="p-2 text-red-400 hover:text-red-300 hover:bg-red-500/20 rounded-lg transition-colors"
                      >
                        <Trash2 className="w-5 h-5" />
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* DadRock Tabs Quickies Sync */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-400" />
              DadRock Tabs Quickies
            </h2>
            <p className="text-zinc-400 mb-4">
              Sync videos from the DadRock Tabs Quickies YouTube playlist. This refreshes the quickies page with the latest videos from the playlist.
            </p>

            {quickiesSyncStatus.message && (
              <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
                quickiesSyncStatus.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              }`}>
                {quickiesSyncStatus.type === 'success' ? <CheckCircle className="w-5 h-5 flex-shrink-0" /> : <AlertCircle className="w-5 h-5 flex-shrink-0" />}
                <span className="text-sm">{quickiesSyncStatus.message}</span>
              </div>
            )}

            <button
              onClick={handleSyncQuickies}
              disabled={isSyncingQuickies}
              className="flex items-center justify-center gap-2 px-6 py-3 bg-yellow-500 text-black font-bold rounded-lg hover:bg-yellow-400 transition-colors disabled:opacity-50"
            >
              {isSyncingQuickies ? (
                <>
                  <div className="w-5 h-5 border-2 border-black border-t-transparent rounded-full animate-spin" />
                  Syncing Quickies...
                </>
              ) : (
                <>
                  <RefreshCw className="w-5 h-5" />
                  Sync Quickies from YouTube
                </>
              )}
            </button>
          </div>

          {/* Sitemap Management */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Map className="w-5 h-5 text-blue-400" />
              Sitemap Management
            </h2>
            <p className="text-zinc-400 mb-6">
              Scan for new pages that aren't in the sitemap, and notify Google & Bing to re-crawl your updated sitemap.
            </p>

            {/* Scan for New Pages */}
            <div className="mb-6">
              <h3 className="text-lg font-semibold text-white mb-2">Scan for New Pages</h3>
              <p className="text-zinc-500 text-sm mb-4">
                Checks all artist pages, song pages, and static pages against the current sitemap to find any missing entries.
              </p>

              {scanStatus.message && (
                <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
                  scanStatus.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-orange-500/20 text-orange-400'
                }`}>
                  {scanStatus.type === 'success' ? <CheckCircle className="w-5 h-5 flex-shrink-0" /> : <AlertCircle className="w-5 h-5 flex-shrink-0" />}
                  <span className="text-sm">{scanStatus.message}</span>
                </div>
              )}

              <button
                onClick={handleScanPages}
                disabled={isScanningPages}
                className="flex items-center justify-center gap-2 px-6 py-3 bg-blue-600 text-white font-bold rounded-lg hover:bg-blue-500 transition-colors disabled:opacity-50"
              >
                {isScanningPages ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Scanning Pages...
                  </>
                ) : (
                  <>
                    <Search className="w-5 h-5" />
                    Scan for New Pages
                  </>
                )}
              </button>

              {/* Scan Results */}
              {scanResult && (
                <div className="mt-4 bg-zinc-800/50 rounded-lg p-4">
                  <h4 className="font-semibold text-white mb-3">Scan Results</h4>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                    <div className="bg-zinc-700/50 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-amber-500">{scanResult.summary?.total_pages || 0}</div>
                      <div className="text-xs text-zinc-400">Total Pages</div>
                    </div>
                    <div className="bg-zinc-700/50 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-blue-400">{scanResult.pages_by_type?.artists || 0}</div>
                      <div className="text-xs text-zinc-400">Artist Pages</div>
                    </div>
                    <div className="bg-zinc-700/50 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-purple-400">{scanResult.pages_by_type?.songs || 0}</div>
                      <div className="text-xs text-zinc-400">Song Pages</div>
                    </div>
                    <div className="bg-zinc-700/50 rounded-lg p-3 text-center">
                      <div className="text-2xl font-bold text-green-400">{scanResult.summary?.in_sitemap || 0}</div>
                      <div className="text-xs text-zinc-400">In Sitemap</div>
                    </div>
                  </div>

                  {scanResult.missing_from_sitemap?.length > 0 && (
                    <div className="mt-3">
                      <div className="flex items-center justify-between mb-2">
                        <p className="text-orange-400 font-medium text-sm">
                          ⚠ {scanResult.missing_from_sitemap.length} pages missing from sitemap:
                        </p>
                        <button
                          onClick={handleAddMissingPages}
                          disabled={isAddingPages}
                          className="flex items-center gap-1 px-4 py-2 bg-green-600 text-white text-sm font-bold rounded-lg hover:bg-green-500 transition-colors disabled:opacity-50"
                        >
                          {isAddingPages ? (
                            <>
                              <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                              Syncing...
                            </>
                          ) : (
                            <>
                              <Plus className="w-4 h-4" />
                              Add Missing Pages to Sitemap
                            </>
                          )}
                        </button>
                      </div>
                      
                      {addPagesResult && (
                        <div className={`flex items-start gap-2 p-3 rounded-lg mb-3 ${
                          addPagesResult.success ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                        }`}>
                          {addPagesResult.success ? <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" /> : <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />}
                          <div>
                            <span className="text-sm font-medium">{addPagesResult.message}</span>
                            {addPagesResult.action_taken && (
                              <p className="text-xs mt-1 opacity-80">{addPagesResult.action_taken}</p>
                            )}
                          </div>
                        </div>
                      )}
                      
                      <div className="max-h-48 overflow-y-auto rounded border border-zinc-700">
                        {scanResult.missing_from_sitemap.map((url, i) => (
                          <div key={i} className="px-3 py-2 text-sm text-zinc-300 border-b border-zinc-800 last:border-0">
                            {url}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Ping Search Engines */}
            <div className="border-t border-zinc-700 pt-6">
              <h3 className="text-lg font-semibold text-white mb-2">Update Sitemap & Notify Search Engines</h3>
              <p className="text-zinc-500 text-sm mb-4">
                Pings Google and Bing to re-crawl your sitemap. The sitemap is always generated dynamically, so this just tells search engines to check for updates.
              </p>

              {pingStatus.message && (
                <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
                  pingStatus.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                }`}>
                  {pingStatus.type === 'success' ? <CheckCircle className="w-5 h-5 flex-shrink-0" /> : <AlertCircle className="w-5 h-5 flex-shrink-0" />}
                  <span className="text-sm">{pingStatus.message}</span>
                </div>
              )}

              <button
                onClick={handlePingSitemap}
                disabled={isPinging}
                className="flex items-center justify-center gap-2 px-6 py-3 bg-green-600 text-white font-bold rounded-lg hover:bg-green-500 transition-colors disabled:opacity-50"
              >
                {isPinging ? (
                  <>
                    <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Pinging Search Engines...
                  </>
                ) : (
                  <>
                    <Globe className="w-5 h-5" />
                    Ping Google & Bing
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Website Health Check */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-emerald-400" />
              Website Health Check
            </h2>
            <p className="text-zinc-400 mb-4">
              Comprehensive scan of your website: check for dead YouTube videos, broken internal URLs, API health, database stats, sitemap, and more.
            </p>

            {/* Mode selector */}
            <div className="flex flex-wrap gap-2 mb-4">
              {[
                { value: 'full', label: 'Full Scan', desc: 'Everything' },
                { value: 'quick', label: 'Quick Check', desc: 'APIs, sitemap, robots' },
                { value: 'videos_only', label: 'Dead Videos Only', desc: 'YouTube links' },
                { value: 'urls_only', label: 'Dead URLs Only', desc: 'Internal pages' },
              ].map(m => (
                <button
                  key={m.value}
                  onClick={() => setHealthCheckMode(m.value)}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    healthCheckMode === m.value
                      ? 'bg-emerald-600 text-white'
                      : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-white'
                  }`}
                >
                  {m.label}
                  <span className="block text-xs opacity-70">{m.desc}</span>
                </button>
              ))}
            </div>

            <button
              onClick={handleHealthCheck}
              disabled={isRunningHealthCheck}
              className="flex items-center justify-center gap-2 px-6 py-3 bg-emerald-600 text-white font-bold rounded-lg hover:bg-emerald-500 transition-colors disabled:opacity-50"
            >
              {isRunningHealthCheck ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Running Health Check...
                </>
              ) : (
                <>
                  <Shield className="w-5 h-5" />
                  Run Health Check
                </>
              )}
            </button>

            {/* Health Report Results */}
            {healthReport && (
              <div className="mt-6">
                {!healthReport.success && healthReport.error ? (
                  <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/20 text-red-400">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <span className="text-sm">{healthReport.error}</span>
                  </div>
                ) : (
                  <>
                    {/* Overall Status Banner */}
                    <div className={`flex items-center gap-3 p-4 rounded-lg mb-4 ${
                      healthReport.overall_status === 'healthy' ? 'bg-emerald-500/20 border border-emerald-500/30' :
                      healthReport.overall_status === 'warning' ? 'bg-yellow-500/20 border border-yellow-500/30' :
                      'bg-red-500/20 border border-red-500/30'
                    }`}>
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-xl ${
                        healthReport.overall_status === 'healthy' ? 'bg-emerald-500/30' :
                        healthReport.overall_status === 'warning' ? 'bg-yellow-500/30' :
                        'bg-red-500/30'
                      }`}>
                        {healthReport.overall_status === 'healthy' ? '✅' : healthReport.overall_status === 'warning' ? '⚠️' : '🚨'}
                      </div>
                      <div>
                        <p className={`font-bold text-lg ${
                          healthReport.overall_status === 'healthy' ? 'text-emerald-400' :
                          healthReport.overall_status === 'warning' ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {healthReport.overall_status === 'healthy' ? 'All Systems Healthy' :
                           healthReport.overall_status === 'warning' ? 'Warnings Found' : 'Critical Issues'}
                        </p>
                        <p className="text-xs text-zinc-400">
                          {healthReport.total_checks} checks completed • {new Date(healthReport.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>

                    {/* Issues Summary */}
                    {healthReport.issues && healthReport.issues.length > 0 && (
                      <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3 mb-4">
                        <p className="text-yellow-400 font-semibold text-sm mb-2">Issues Found:</p>
                        <ul className="text-sm text-yellow-300 space-y-1">
                          {healthReport.issues.map((issue, i) => (
                            <li key={i} className="flex items-center gap-2">
                              <span className="text-yellow-500">•</span> {issue}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Check Results Grid */}
                    <div className="space-y-3">
                      {/* Database */}
                      {healthReport.checks.database && (
                        <div className="bg-zinc-800/50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-3">
                            <Database className="w-4 h-4 text-blue-400" />
                            <h4 className="font-semibold text-white">Database</h4>
                            <span className={`ml-auto px-2 py-0.5 rounded-full text-xs font-medium ${
                              healthReport.checks.database.status === 'ok' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                            }`}>
                              {healthReport.checks.database.status === 'ok' ? '● Connected' : '● Error'}
                            </span>
                          </div>
                          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                            {[
                              { label: 'Videos', value: healthReport.checks.database.details?.videos || 0, color: 'text-red-400' },
                              { label: 'Artists', value: healthReport.checks.database.details?.artists || 0, color: 'text-amber-400' },
                              { label: 'Song Pages', value: healthReport.checks.database.details?.song_pages || 0, color: 'text-purple-400' },
                              { label: 'Upcoming', value: healthReport.checks.database.details?.upcoming_videos || 0, color: 'text-blue-400' },
                            ].map((stat, i) => (
                              <div key={i} className="bg-zinc-700/50 rounded-lg p-2 text-center">
                                <div className={`text-xl font-bold ${stat.color}`}>{stat.value}</div>
                                <div className="text-xs text-zinc-400">{stat.label}</div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* API Endpoints */}
                      {healthReport.checks.api_endpoints && (
                        <div className="bg-zinc-800/50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-3">
                            <Wifi className="w-4 h-4 text-cyan-400" />
                            <h4 className="font-semibold text-white">API Endpoints</h4>
                            <span className={`ml-auto px-2 py-0.5 rounded-full text-xs font-medium ${
                              healthReport.checks.api_endpoints.status === 'ok' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                            }`}>
                              {healthReport.checks.api_endpoints.details?.passed || 0}/{healthReport.checks.api_endpoints.details?.total_checked || 0} Passing
                            </span>
                          </div>
                          <div className="space-y-1">
                            {(healthReport.checks.api_endpoints.details?.results || []).map((r, i) => (
                              <div key={i} className="flex items-center gap-2 text-sm">
                                <span className={r.ok ? 'text-emerald-400' : 'text-red-400'}>{r.ok ? '✓' : '✗'}</span>
                                <span className="text-zinc-300 font-mono text-xs">{r.url}</span>
                                <span className={`text-xs ${r.ok ? 'text-zinc-500' : 'text-red-400'}`}>{r.status}</span>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Sitemap & Robots */}
                      {(healthReport.checks.sitemap || healthReport.checks.robots) && (
                        <div className="bg-zinc-800/50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-3">
                            <FileText className="w-4 h-4 text-indigo-400" />
                            <h4 className="font-semibold text-white">SEO Files</h4>
                          </div>
                          <div className="space-y-2">
                            {healthReport.checks.sitemap && (
                              <div className="flex items-center gap-2 text-sm">
                                <span className={healthReport.checks.sitemap.status === 'ok' ? 'text-emerald-400' : 'text-red-400'}>
                                  {healthReport.checks.sitemap.status === 'ok' ? '✓' : '✗'}
                                </span>
                                <span className="text-zinc-300">sitemap.xml</span>
                                {healthReport.checks.sitemap.details?.page_count > 0 && (
                                  <span className="text-zinc-500 text-xs">({healthReport.checks.sitemap.details.page_count} URLs)</span>
                                )}
                              </div>
                            )}
                            {healthReport.checks.robots && (
                              <div className="flex items-center gap-2 text-sm">
                                <span className={healthReport.checks.robots.status === 'ok' ? 'text-emerald-400' : 'text-yellow-400'}>
                                  {healthReport.checks.robots.status === 'ok' ? '✓' : '⚠'}
                                </span>
                                <span className="text-zinc-300">robots.txt</span>
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Internal URLs */}
                      {healthReport.checks.internal_urls && (
                        <div className="bg-zinc-800/50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-3">
                            <Globe className="w-4 h-4 text-green-400" />
                            <h4 className="font-semibold text-white">Internal Pages</h4>
                            <span className={`ml-auto px-2 py-0.5 rounded-full text-xs font-medium ${
                              healthReport.checks.internal_urls.status === 'ok' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-yellow-500/20 text-yellow-400'
                            }`}>
                              {healthReport.checks.internal_urls.details?.alive || 0}/{healthReport.checks.internal_urls.details?.total_checked || 0} Alive
                            </span>
                          </div>
                          {healthReport.checks.internal_urls.details?.dead > 0 && (
                            <div className="mt-2">
                              <div className="flex items-center justify-between mb-2">
                                <p className="text-yellow-400 text-sm font-medium">
                                  {healthReport.checks.internal_urls.details.dead} Dead/Broken URL(s):
                                </p>
                                {healthReport.checks.internal_urls.details.dead_urls.some(u => u.url.startsWith('/artist/')) && (
                                  <button
                                    onClick={handleDeleteAllDeadUrls}
                                    disabled={isDeletingDeadUrls}
                                    className="flex items-center gap-1 px-3 py-1 bg-red-600 text-white text-xs font-bold rounded-lg hover:bg-red-500 transition-colors disabled:opacity-50"
                                  >
                                    <Trash2 className="w-3 h-3" />
                                    {isDeletingDeadUrls ? (deadUrlAction || 'Deleting...') : 'Delete All Dead Artist Videos'}
                                  </button>
                                )}
                              </div>
                              <div className="max-h-64 overflow-y-auto rounded border border-zinc-700">
                                {(healthReport.checks.internal_urls.details?.dead_urls || []).map((u, i) => (
                                  <div key={i} className="flex items-center gap-2 px-3 py-2 text-sm border-b border-zinc-800 last:border-0 group hover:bg-zinc-700/30">
                                    <span className="text-red-400 font-mono text-xs w-8 flex-shrink-0">{u.status || 'ERR'}</span>
                                    <span className="text-zinc-300 truncate flex-1">{u.url}</span>
                                    {u.error && <span className="text-zinc-500 text-xs">({u.error})</span>}
                                    {u.url.startsWith('/artist/') && (
                                      <button
                                        onClick={() => handleDeleteDeadUrlArtist(u.url)}
                                        disabled={deletingDeadUrls[u.url]}
                                        className="opacity-0 group-hover:opacity-100 flex items-center gap-1 px-2 py-1 bg-red-600/80 text-white text-xs rounded hover:bg-red-500 transition-all disabled:opacity-50 flex-shrink-0"
                                        title={`Delete videos for this artist`}
                                      >
                                        <Trash2 className="w-3 h-3" />
                                        {deletingDeadUrls[u.url] ? '...' : 'Delete'}
                                      </button>
                                    )}
                                  </div>
                                ))}
                              </div>
                              <p className="text-zinc-500 text-xs mt-2">
                                Hover over a dead URL to see the delete button. Deleting removes the database entries causing broken links.
                              </p>
                            </div>
                          )}
                          {healthReport.checks.internal_urls.details?.dead === 0 && (
                            <p className="text-emerald-400 text-sm">All {healthReport.checks.internal_urls.details?.total_checked} internal pages are returning 200 OK.</p>
                          )}
                        </div>
                      )}

                      {/* Dead Videos */}
                      {healthReport.checks.dead_videos && (
                        <div className="bg-zinc-800/50 rounded-lg p-4">
                          <div className="flex items-center gap-2 mb-3">
                            <Youtube className="w-4 h-4 text-red-400" />
                            <h4 className="font-semibold text-white">YouTube Video Links</h4>
                            <span className={`ml-auto px-2 py-0.5 rounded-full text-xs font-medium ${
                              healthReport.checks.dead_videos.status === 'ok' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-yellow-500/20 text-yellow-400'
                            }`}>
                              {healthReport.checks.dead_videos.details?.alive || 0}/{healthReport.checks.dead_videos.details?.total_checked || 0} Alive
                            </span>
                          </div>
                          <p className="text-xs text-zinc-500 mb-2">
                            Method: {healthReport.checks.dead_videos.details?.method || 'N/A'}
                            {healthReport.checks.dead_videos.details?.api_error && (
                              <span className="text-yellow-400 ml-2">(API error: {healthReport.checks.dead_videos.details.api_error})</span>
                            )}
                          </p>
                          {healthReport.checks.dead_videos.details?.dead > 0 && (
                            <div className="mt-2">
                              <div className="flex items-center justify-between mb-2">
                                <p className="text-yellow-400 text-sm font-medium">
                                  {healthReport.checks.dead_videos.details.dead} Dead Video(s) Found:
                                </p>
                                <button
                                  onClick={() => handleRemoveDeadVideos(healthReport.checks.dead_videos.details.dead_videos.map(v => v.id))}
                                  disabled={isRemovingDeadVideos}
                                  className="flex items-center gap-1 px-3 py-1 bg-red-600 text-white text-xs font-bold rounded-lg hover:bg-red-500 transition-colors disabled:opacity-50"
                                >
                                  <Trash2 className="w-3 h-3" />
                                  {isRemovingDeadVideos ? 'Removing...' : 'Remove All Dead Videos'}
                                </button>
                              </div>
                              <div className="max-h-48 overflow-y-auto rounded border border-zinc-700">
                                <table className="w-full text-sm">
                                  <thead className="bg-zinc-800 sticky top-0">
                                    <tr>
                                      <th className="text-left px-3 py-2 text-zinc-400 font-medium">Song</th>
                                      <th className="text-left px-3 py-2 text-zinc-400 font-medium">Artist</th>
                                      <th className="text-left px-3 py-2 text-zinc-400 font-medium">URL</th>
                                    </tr>
                                  </thead>
                                  <tbody>
                                    {(healthReport.checks.dead_videos.details?.dead_videos || []).map((video, idx) => (
                                      <tr key={idx} className="border-t border-zinc-800 hover:bg-zinc-800/50">
                                        <td className="px-3 py-2 text-white font-medium truncate max-w-[150px]">{video.song}</td>
                                        <td className="px-3 py-2 text-zinc-300 truncate max-w-[120px]">{video.artist}</td>
                                        <td className="px-3 py-2">
                                          <a href={video.youtube_url} target="_blank" rel="noopener noreferrer" className="text-red-400 hover:text-red-300 text-xs truncate max-w-[200px] block line-through">
                                            {video.youtube_url}
                                          </a>
                                        </td>
                                      </tr>
                                    ))}
                                  </tbody>
                                </table>
                              </div>
                            </div>
                          )}
                          {healthReport.checks.dead_videos.details?.dead === 0 && (
                            <p className="text-emerald-400 text-sm">All {healthReport.checks.dead_videos.details?.total_checked} YouTube videos are alive and accessible.</p>
                          )}
                        </div>
                      )}
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Top Lessons Management Section */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-500" />
              Top 10 Lessons Configuration
            </h2>
            <p className="text-zinc-400 mb-6">
              Manually set the top 10 most viewed lessons that appear on the Top Lessons page. 
              Paste YouTube URLs for each position.
            </p>
            
            {topLessonsSaveStatus.message && (
              <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
                topLessonsSaveStatus.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              }`}>
                {topLessonsSaveStatus.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                {topLessonsSaveStatus.message}
              </div>
            )}

            <div className="space-y-4">
              {topLessons.map((lesson, index) => (
                <div key={index} className="flex items-center gap-4 p-4 bg-zinc-800/50 rounded-lg">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-lg font-bold ${
                    index < 3 
                      ? index === 0 ? 'bg-amber-500 text-black' : index === 1 ? 'bg-zinc-400 text-black' : 'bg-orange-600 text-white'
                      : 'bg-zinc-700 text-zinc-300'
                  }`}>
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `#${index + 1}`}
                  </div>
                  <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-3">
                    <input
                      type="text"
                      value={lesson.youtubeUrl}
                      onChange={(e) => {
                        const newLessons = [...topLessons];
                        newLessons[index] = { ...newLessons[index], youtubeUrl: e.target.value };
                        setTopLessons(newLessons);
                      }}
                      className="px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500 text-sm"
                      placeholder="YouTube URL"
                    />
                    <input
                      type="text"
                      value={lesson.title}
                      onChange={(e) => {
                        const newLessons = [...topLessons];
                        newLessons[index] = { ...newLessons[index], title: e.target.value };
                        setTopLessons(newLessons);
                      }}
                      className="px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500 text-sm"
                      placeholder="Song Title"
                    />
                    <input
                      type="text"
                      value={lesson.artist}
                      onChange={(e) => {
                        const newLessons = [...topLessons];
                        newLessons[index] = { ...newLessons[index], artist: e.target.value };
                        setTopLessons(newLessons);
                      }}
                      className="px-3 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500 text-sm"
                      placeholder="Artist"
                    />
                  </div>
                  {lesson.youtubeUrl && (
                    <img 
                      src={`https://i.ytimg.com/vi/${extractVideoIdFromUrl(lesson.youtubeUrl)}/default.jpg`}
                      alt="Thumbnail preview"
                      className="w-16 h-12 object-cover rounded hidden md:block"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                  )}
                </div>
              ))}
            </div>

            <button
              onClick={handleSaveTopLessons}
              disabled={isSavingTopLessons}
              className="mt-6 flex items-center gap-2 px-6 py-3 bg-amber-500 text-black font-bold rounded-lg hover:bg-amber-400 transition-colors disabled:opacity-50"
            >
              <Save className="w-5 h-5" />
              {isSavingTopLessons ? 'Saving...' : 'Save Top Lessons'}
            </button>
          </div>

          {/* Song Pages Management Section */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Music className="w-5 h-5 text-amber-500" />
              Song Pages (SEO)
            </h2>
            <p className="text-zinc-400 mb-4">
              Generate individual landing pages for your top 100 most viewed lessons (excluding shorts). 
              Each page includes an embedded video, interstitial ad, and auto-generated SEO content.
            </p>
            <p className="text-zinc-300 mb-4">
              Pages live at: <code className="text-amber-400 bg-zinc-800 px-2 py-1 rounded">dadrocktabs.com/songs/artist-song-name</code>
            </p>
            
            {songPageCount > 0 && (
              <div className="bg-zinc-800/50 rounded-lg p-3 mb-4 flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-zinc-300"><strong className="text-white">{songPageCount}</strong> song pages currently active</span>
              </div>
            )}

            {songSyncStatus.message && (
              <div className={`flex items-center gap-2 p-3 rounded-lg mb-4 ${
                songSyncStatus.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
              }`}>
                {songSyncStatus.type === 'success' ? <CheckCircle className="w-5 h-5" /> : <AlertCircle className="w-5 h-5" />}
                <span className="text-sm">{songSyncStatus.message}</span>
              </div>
            )}

            <button
              onClick={handleSyncSongPages}
              disabled={isSyncingSongs}
              className="flex items-center gap-2 px-6 py-3 bg-purple-600 text-white font-bold rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-50"
            >
              <Music className="w-5 h-5" />
              {isSyncingSongs ? 'Syncing Top 100... (this may take a minute)' : 'Sync Top 100 Song Pages'}
            </button>

            {/* Manual Song Page Entry */}
            <div className="mt-6 pt-6 border-t border-zinc-700">
              <h3 className="text-lg font-semibold text-white mb-3">Add Song Page Manually</h3>
              <p className="text-zinc-400 text-sm mb-3">
                Paste a YouTube video URL to create an individual song page with SEO content.
              </p>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={manualSongUrl}
                  onChange={(e) => setManualSongUrl(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="flex-1 px-4 py-2 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                  onKeyDown={(e) => e.key === 'Enter' && handleAddManualSong()}
                />
                <button
                  onClick={handleAddManualSong}
                  disabled={isAddingManualSong || !manualSongUrl.trim()}
                  className="px-6 py-2 bg-amber-500 text-black font-bold rounded-lg hover:bg-amber-400 transition-colors disabled:opacity-50 whitespace-nowrap"
                >
                  {isAddingManualSong ? 'Adding...' : 'Add Song Page'}
                </button>
              </div>
              {manualSongStatus.message && (
                <div className={`mt-3 flex items-center gap-2 p-3 rounded-lg ${
                  manualSongStatus.type === 'success' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                }`}>
                  {manualSongStatus.type === 'success' ? <CheckCircle className="w-5 h-5 flex-shrink-0" /> : <AlertCircle className="w-5 h-5 flex-shrink-0" />}
                  <span className="text-sm">{manualSongStatus.message}</span>
                </div>
              )}
            </div>

            {/* View / Delete Song Pages */}
            <div className="mt-6 pt-6 border-t border-zinc-700">
              <button
                onClick={() => {
                  setShowSongsList(!showSongsList);
                  if (!showSongsList) loadSongPagesList();
                }}
                className="flex items-center gap-2 text-amber-400 hover:text-amber-300 transition-colors font-medium"
              >
                {showSongsList ? '▼' : '▶'} View All Song Pages ({songPageCount})
              </button>

              {showSongsList && (
                <div className="mt-4 max-h-96 overflow-y-auto rounded-lg border border-zinc-700">
                  {songPagesList.length === 0 ? (
                    <p className="text-zinc-500 text-center py-6">No song pages found</p>
                  ) : (
                    <table className="w-full text-sm">
                      <thead className="bg-zinc-800 sticky top-0">
                        <tr>
                          <th className="text-left px-3 py-2 text-zinc-400 font-medium">#</th>
                          <th className="text-left px-3 py-2 text-zinc-400 font-medium">Song</th>
                          <th className="text-left px-3 py-2 text-zinc-400 font-medium">Artist</th>
                          <th className="text-left px-3 py-2 text-zinc-400 font-medium">Views</th>
                          <th className="text-left px-3 py-2 text-zinc-400 font-medium">URL</th>
                          <th className="text-right px-3 py-2 text-zinc-400 font-medium">Action</th>
                        </tr>
                      </thead>
                      <tbody>
                        {songPagesList.map((song, idx) => (
                          <tr key={song.videoId} className="border-t border-zinc-800 hover:bg-zinc-800/50">
                            <td className="px-3 py-2 text-zinc-500">{idx + 1}</td>
                            <td className="px-3 py-2 text-white font-medium truncate max-w-[150px]">{song.title}</td>
                            <td className="px-3 py-2 text-zinc-300 truncate max-w-[120px]">{song.artist}</td>
                            <td className="px-3 py-2 text-zinc-400">{song.viewCount ? song.viewCount.toLocaleString() : '0'}</td>
                            <td className="px-3 py-2">
                              <a href={`/songs/${song.slug}`} target="_blank" rel="noopener noreferrer" className="text-amber-500 hover:text-amber-400 text-xs truncate max-w-[120px] block">
                                /songs/{song.slug}
                              </a>
                            </td>
                            <td className="px-3 py-2 text-right">
                              <button
                                onClick={() => handleDeleteSong(song.videoId, song.title)}
                                disabled={deletingSongId === song.videoId}
                                className="px-3 py-1 bg-red-600/20 text-red-400 hover:bg-red-600/40 rounded text-xs font-medium transition-colors disabled:opacity-50"
                              >
                                {deletingSongId === song.videoId ? '...' : 'Delete'}
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* AI SEO Content Generator */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6 mb-8">
            <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-purple-400" />
              AI SEO Content Generator
            </h2>
            <p className="text-zinc-400 mb-4">
              Use GPT to generate rich, educational content for artist and song pages — including band bios, playing style analysis, gear info, song backstories, and practice tips.
            </p>

            {/* Status Cards with Progress Bar */}
            {aiSeoStatus && (
              <div className="mb-6">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                  <div className="bg-zinc-800/50 rounded-lg p-3 text-center">
                    <div className="text-2xl font-bold text-purple-400">{aiSeoStatus.artists?.with_ai_content || 0}</div>
                    <div className="text-xs text-zinc-400">Artists with AI Content</div>
                  </div>
                  <div className="bg-zinc-800/50 rounded-lg p-3 text-center">
                    <div className="text-2xl font-bold text-zinc-400">{aiSeoStatus.artists?.without_ai_content || 0}</div>
                    <div className="text-xs text-zinc-400">Artists Need Content</div>
                  </div>
                  <div className="bg-zinc-800/50 rounded-lg p-3 text-center">
                    <div className="text-2xl font-bold text-purple-400">{aiSeoStatus.songs?.with_ai_content || 0}</div>
                    <div className="text-xs text-zinc-400">Songs with AI Content</div>
                  </div>
                  <div className="bg-zinc-800/50 rounded-lg p-3 text-center">
                    <div className="text-2xl font-bold text-zinc-400">{aiSeoStatus.songs?.without_ai_content || 0}</div>
                    <div className="text-xs text-zinc-400">Songs Need Content</div>
                  </div>
                </div>

                {/* Artist Progress Bar */}
                {aiSeoStatus.artists?.total > 0 && (
                  <div className="mb-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-zinc-400">Artist Content Progress</span>
                      <span className="text-xs font-semibold text-purple-400">
                        {Math.round(((aiSeoStatus.artists?.with_ai_content || 0) / aiSeoStatus.artists.total) * 100)}%
                      </span>
                    </div>
                    <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-full transition-all duration-500"
                        style={{ width: `${((aiSeoStatus.artists?.with_ai_content || 0) / aiSeoStatus.artists.total) * 100}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* Song Progress Bar */}
                {aiSeoStatus.songs?.total > 0 && (
                  <div className="mb-3">
                    <div className="flex items-center justify-between mb-1">
                      <span className="text-xs text-zinc-400">Song Content Progress</span>
                      <span className="text-xs font-semibold text-purple-400">
                        {Math.round(((aiSeoStatus.songs?.with_ai_content || 0) / aiSeoStatus.songs.total) * 100)}%
                      </span>
                    </div>
                    <div className="w-full h-2 bg-zinc-800 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-purple-600 to-purple-400 rounded-full transition-all duration-500"
                        style={{ width: `${((aiSeoStatus.songs?.with_ai_content || 0) / aiSeoStatus.songs.total) * 100}%` }}
                      />
                    </div>
                  </div>
                )}

                {/* View Details Button */}
                <button
                  onClick={() => {
                    if (!showAiDetailView) {
                      loadAiDetailView(aiGenerateMode === 'batch_songs' ? 'songs' : 'artists');
                    }
                    setShowAiDetailView(!showAiDetailView);
                  }}
                  className="mt-2 flex items-center gap-2 text-sm text-purple-400 hover:text-purple-300 transition-colors"
                >
                  <ChevronDown className={`w-4 h-4 transition-transform ${showAiDetailView ? 'rotate-180' : ''}`} />
                  {showAiDetailView ? 'Hide Details' : 'View All Artists/Songs Status'}
                </button>
              </div>
            )}

            {/* Detail View Panel */}
            {showAiDetailView && (
              <div className="mb-6 bg-zinc-800/30 rounded-lg border border-zinc-700 overflow-hidden">
                <div className="p-3 border-b border-zinc-700 flex flex-wrap items-center gap-3">
                  <div className="flex gap-1">
                    <button
                      onClick={() => { loadAiDetailView('artists'); }}
                      className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                        !aiDetailData?.songs ? 'bg-purple-600 text-white' : 'bg-zinc-700 text-zinc-400 hover:text-white'
                      }`}
                    >
                      Artists
                    </button>
                    <button
                      onClick={() => { loadAiDetailView('songs'); }}
                      className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                        aiDetailData?.songs ? 'bg-purple-600 text-white' : 'bg-zinc-700 text-zinc-400 hover:text-white'
                      }`}
                    >
                      Songs
                    </button>
                  </div>
                  <div className="flex gap-1">
                    {[
                      { value: 'all', label: 'All' },
                      { value: 'without', label: 'Missing' },
                      { value: 'with', label: 'Done' },
                    ].map(f => (
                      <button
                        key={f.value}
                        onClick={() => setAiDetailFilter(f.value)}
                        className={`px-3 py-1.5 rounded text-xs font-medium transition-colors ${
                          aiDetailFilter === f.value
                            ? 'bg-zinc-600 text-white'
                            : 'bg-zinc-800 text-zinc-500 hover:text-white'
                        }`}
                      >
                        {f.label}
                      </button>
                    ))}
                  </div>
                  <div className="flex-1 min-w-[150px]">
                    <input
                      type="text"
                      placeholder="Search..."
                      value={aiDetailSearch}
                      onChange={e => setAiDetailSearch(e.target.value)}
                      className="w-full bg-zinc-800 text-white text-xs border border-zinc-700 rounded px-3 py-1.5 focus:outline-none focus:border-purple-500"
                    />
                  </div>
                </div>

                {aiDetailLoading ? (
                  <div className="p-8 text-center text-zinc-400">
                    <div className="w-6 h-6 border-2 border-purple-400 border-t-transparent rounded-full animate-spin mx-auto mb-2" />
                    Loading...
                  </div>
                ) : aiDetailData ? (
                  <div className="max-h-80 overflow-y-auto">
                    {aiDetailData.artists && (
                      <div className="divide-y divide-zinc-800/50">
                        {aiDetailData.artists
                          .filter(a => {
                            if (aiDetailFilter === 'with') return a.has_content;
                            if (aiDetailFilter === 'without') return !a.has_content;
                            return true;
                          })
                          .filter(a => !aiDetailSearch || a.name.toLowerCase().includes(aiDetailSearch.toLowerCase()))
                          .map(a => (
                            <div key={a.slug} className="flex items-center gap-3 px-4 py-2 hover:bg-zinc-800/40">
                              <span className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                                a.has_content ? 'bg-emerald-500/20 text-emerald-400' : 'bg-zinc-700/50 text-zinc-500'
                              }`}>
                                {a.has_content ? '✓' : '—'}
                              </span>
                              <span className="flex-1 text-sm text-zinc-200 truncate">{a.name}</span>
                              {a.has_content ? (
                                <span className="text-xs text-zinc-500 flex-shrink-0">
                                  {a.generated_at ? new Date(a.generated_at).toLocaleDateString() : 'Done'}
                                </span>
                              ) : (
                                <button
                                  onClick={() => handleGenerateSingleArtist(a.name, a.slug)}
                                  disabled={isGeneratingSingle === a.slug}
                                  className="flex-shrink-0 px-3 py-1 text-xs bg-purple-600/80 text-white rounded hover:bg-purple-500 transition-colors disabled:opacity-50"
                                >
                                  {isGeneratingSingle === a.slug ? (
                                    <span className="flex items-center gap-1">
                                      <span className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin" />
                                      Generating...
                                    </span>
                                  ) : 'Generate'}
                                </button>
                              )}
                            </div>
                          ))
                        }
                      </div>
                    )}
                    {aiDetailData.songs && (
                      <div className="divide-y divide-zinc-800/50">
                        {aiDetailData.songs
                          .filter(s => {
                            if (aiDetailFilter === 'with') return s.has_content;
                            if (aiDetailFilter === 'without') return !s.has_content;
                            return true;
                          })
                          .filter(s => !aiDetailSearch || (s.title || '').toLowerCase().includes(aiDetailSearch.toLowerCase()) || (s.artist || '').toLowerCase().includes(aiDetailSearch.toLowerCase()))
                          .map(s => (
                            <div key={s.slug} className="flex items-center gap-3 px-4 py-2 hover:bg-zinc-800/40">
                              <span className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center text-xs ${
                                s.has_content ? 'bg-emerald-500/20 text-emerald-400' : 'bg-zinc-700/50 text-zinc-500'
                              }`}>
                                {s.has_content ? '✓' : '—'}
                              </span>
                              <div className="flex-1 min-w-0">
                                <span className="text-sm text-zinc-200 truncate block">{s.title}</span>
                                <span className="text-xs text-zinc-500">{s.artist}</span>
                              </div>
                              {s.has_content && (
                                <span className="text-xs text-zinc-500 flex-shrink-0">
                                  {s.generated_at ? new Date(s.generated_at).toLocaleDateString() : 'Done'}
                                </span>
                              )}
                            </div>
                          ))
                        }
                      </div>
                    )}
                  </div>
                ) : null}

                {aiDetailData && (
                  <div className="p-2 border-t border-zinc-700 text-center text-xs text-zinc-500">
                    {aiDetailData.with_content || 0} done / {aiDetailData.total || 0} total 
                    {aiDetailSearch && ` (filtered)`}
                  </div>
                )}
              </div>
            )}

            {/* Mode selector */}
            <div className="flex flex-wrap items-center gap-3 mb-4">
              <div className="flex gap-2">
                {[
                  { value: 'batch_artists', label: 'Generate Artist Content' },
                  { value: 'batch_songs', label: 'Generate Song Content' },
                ].map(m => (
                  <button
                    key={m.value}
                    onClick={() => setAiGenerateMode(m.value)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      aiGenerateMode === m.value
                        ? 'bg-purple-600 text-white'
                        : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700 hover:text-white'
                    }`}
                  >
                    {m.label}
                  </button>
                ))}
              </div>
              <div className="flex items-center gap-2">
                <label className="text-zinc-400 text-sm">Batch size:</label>
                <select
                  value={aiBatchSize}
                  onChange={e => setAiBatchSize(Number(e.target.value))}
                  className="bg-zinc-800 text-white border border-zinc-700 rounded-lg px-3 py-2 text-sm"
                >
                  {[1, 3, 5, 10, 15, 20].map(n => (
                    <option key={n} value={n}>{n}</option>
                  ))}
                </select>
              </div>
            </div>

            <button
              onClick={handleGenerateAiSeo}
              disabled={isGeneratingAi}
              className="flex items-center justify-center gap-2 px-6 py-3 bg-purple-600 text-white font-bold rounded-lg hover:bg-purple-500 transition-colors disabled:opacity-50"
            >
              {isGeneratingAi ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  {aiProgress || 'Generating...'}
                </>
              ) : (
                <>
                  <Zap className="w-5 h-5" />
                  Generate {aiGenerateMode === 'batch_artists' ? 'Artist' : 'Song'} Content ({aiBatchSize})
                </>
              )}
            </button>

            {/* Generation Results */}
            {aiResults && (
              <div className="mt-4">
                {aiResults.error ? (
                  <div className="flex items-center gap-2 p-3 rounded-lg bg-red-500/20 text-red-400">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <span className="text-sm">{aiResults.error}</span>
                  </div>
                ) : (
                  <div className="bg-zinc-800/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <p className="text-emerald-400 font-semibold text-sm">
                        ✓ Generated {aiResults.processed} items • {aiResults.remaining} remaining
                      </p>
                      {aiResults.remaining > 0 && (
                        <button
                          onClick={handleGenerateAiSeo}
                          disabled={isGeneratingAi}
                          className="text-xs px-3 py-1 bg-purple-600 text-white rounded-lg hover:bg-purple-500 disabled:opacity-50"
                        >
                          Generate Next Batch
                        </button>
                      )}
                    </div>
                    <div className="space-y-1 max-h-48 overflow-y-auto">
                      {(aiResults.results || []).map((r, i) => (
                        <div key={i} className="flex items-center gap-2 text-sm">
                          <span className={r.status === 'success' ? 'text-emerald-400' : 'text-red-400'}>
                            {r.status === 'success' ? '✓' : '✗'}
                          </span>
                          <span className="text-zinc-300">{r.artist || r.song}</span>
                          {r.error && <span className="text-red-400 text-xs">({r.error})</span>}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
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
                <label className="block text-sm text-zinc-400 mb-2">Ad Image</label>
                
                {/* Image Preview */}
                {adminAdImage && (
                  <div className="relative mb-3 p-3 bg-zinc-800 rounded-lg">
                    <button
                      type="button"
                      onClick={() => setAdminAdImage('')}
                      className="absolute top-2 right-2 p-1 bg-red-500/80 hover:bg-red-500 rounded-full text-white"
                    >
                      <X className="w-4 h-4" />
                    </button>
                    <p className="text-xs text-zinc-400 mb-2">Current Image:</p>
                    <img 
                      src={adminAdImage} 
                      alt="Ad preview" 
                      className="max-h-40 mx-auto rounded"
                      onError={(e) => e.target.style.display = 'none'}
                    />
                  </div>
                )}
                
                {/* Upload Area */}
                <div className="relative">
                  <input
                    type="file"
                    accept="image/jpeg,image/jpg,image/png,image/gif,image/webp"
                    onChange={handleImageUpload}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                    disabled={isUploading}
                  />
                  <div className={`flex flex-col items-center justify-center gap-3 p-6 border-2 border-dashed rounded-lg transition-colors ${
                    isUploading ? 'border-amber-500 bg-amber-500/10' : 'border-zinc-700 hover:border-amber-500 hover:bg-zinc-800/50'
                  }`}>
                    {isUploading ? (
                      <>
                        <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
                        <span className="text-sm text-amber-500">Uploading...</span>
                      </>
                    ) : (
                      <>
                        <div className="w-12 h-12 bg-zinc-700 rounded-full flex items-center justify-center">
                          <Upload className="w-6 h-6 text-amber-500" />
                        </div>
                        <div className="text-center">
                          <p className="text-sm text-white font-medium">Click to upload image</p>
                          <p className="text-xs text-zinc-500 mt-1">JPEG, PNG, GIF, WebP (max 2MB)</p>
                        </div>
                      </>
                    )}
                  </div>
                </div>
                
                {/* Upload Error */}
                {uploadError && (
                  <div className="flex items-center gap-2 mt-2 text-red-400 text-sm">
                    <AlertCircle className="w-4 h-4" />
                    {uploadError}
                  </div>
                )}
                
                {/* OR divider for URL input */}
                <div className="flex items-center gap-3 my-4">
                  <div className="flex-1 h-px bg-zinc-700" />
                  <span className="text-xs text-zinc-500">OR enter URL</span>
                  <div className="flex-1 h-px bg-zinc-700" />
                </div>
                
                {/* URL Input (fallback) */}
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

              <div>
                <label className="block text-sm text-zinc-400 mb-2">Ad Duration (seconds)</label>
                <div className="flex items-center gap-4">
                  <input
                    type="number"
                    min="5"
                    max="30"
                    value={adminAdDuration}
                    onChange={(e) => {
                      const val = parseInt(e.target.value) || 5;
                      setAdminAdDuration(Math.min(30, Math.max(5, val)));
                    }}
                    className="w-32 px-4 py-3 bg-zinc-800 border border-zinc-700 rounded-lg text-white placeholder-zinc-500 focus:outline-none focus:border-amber-500"
                  />
                  <div className="flex-1">
                    <input
                      type="range"
                      min="5"
                      max="30"
                      value={adminAdDuration}
                      onChange={(e) => setAdminAdDuration(parseInt(e.target.value))}
                      className="w-full h-2 bg-zinc-700 rounded-lg appearance-none cursor-pointer accent-amber-500"
                    />
                    <div className="flex justify-between text-xs text-zinc-500 mt-1">
                      <span>5s (min)</span>
                      <span>30s (max)</span>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-zinc-500 mt-2">
                  How long the interstitial ad displays before the video plays. Default: 5 seconds.
                </p>
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
