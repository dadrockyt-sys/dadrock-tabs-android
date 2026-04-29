'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Youtube, Music, Home, Users, ShoppingBag, BookOpen, Guitar, Lightbulb, Star, Search } from 'lucide-react';
import LanguageSelector, { useLanguage } from '@/components/LanguageSelector';
import { getSubPageTranslation } from '@/lib/subPageI18n';
import { getSeoMeta, updateDocumentMeta } from '@/lib/seoTranslations';
import { artistToSlug } from '@/lib/slugify';
import SearchBar from '@/components/SearchBar';

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";

// Related artists mapping for internal linking (SEO boost)
// Covers all major artists in the database for maximum cross-linking
const relatedArtistsMap = {
  // Classic Heavy Metal / Thrash
  'AC/DC': ['Van Halen', 'Def Leppard', 'Aerosmith', 'Kiss', 'Scorpions'],
  'Metallica': ['Megadeth', 'Slayer', 'Anthrax', 'Pantera', 'Black Sabbath'],
  'Black Sabbath': ['Ozzy Osbourne', 'Dio', 'Iron Maiden', 'Judas Priest', 'Deep Purple'],
  'Iron Maiden': ['Judas Priest', 'Black Sabbath', 'Metallica', 'Megadeth', 'Dio'],
  'Judas Priest': ['Iron Maiden', 'Black Sabbath', 'Accept', 'Scorpions', 'Dio'],
  'Megadeth': ['Metallica', 'Slayer', 'Anthrax', 'Pantera', 'Iron Maiden'],
  'Slayer': ['Metallica', 'Megadeth', 'Anthrax', 'Pantera', 'Black Sabbath'],
  'Anthrax': ['Metallica', 'Megadeth', 'Slayer', 'Iron Maiden', 'Pantera'],
  'Pantera': ['Metallica', 'Slayer', 'Megadeth', 'Black Sabbath', 'Tool'],
  'Dio': ['Black Sabbath', 'Rainbow', 'Iron Maiden', 'Judas Priest', 'Ozzy Osbourne'],
  'Ozzy Osbourne': ['Black Sabbath', 'Dio', 'Alice Cooper', 'Motley Crue', 'Quiet Riot'],
  
  // Classic Rock / Hard Rock  
  'Van Halen': ['AC/DC', 'Def Leppard', 'Motley Crue', 'Bon Jovi', 'Aerosmith'],
  'Led Zeppelin': ['Deep Purple', 'Black Sabbath', 'The Who', 'Cream', 'Aerosmith'],
  'Aerosmith': ['AC/DC', 'Van Halen', 'Guns N Roses', 'Kiss', 'Bon Jovi'],
  'Deep Purple': ['Led Zeppelin', 'Rainbow', 'Whitesnake', 'Black Sabbath', 'Uriah Heep'],
  'Kiss': ['AC/DC', 'Twisted Sister', 'Motley Crue', 'Alice Cooper', 'Aerosmith'],
  'ZZ Top': ['Lynyrd Skynyrd', 'AC/DC', 'Stevie Ray Vaughan', 'Ted Nugent', 'Bad Company'],
  'Scorpions': ['Accept', 'Def Leppard', 'UFO', 'Judas Priest', 'Dokken'],
  'Rainbow': ['Deep Purple', 'Dio', 'Whitesnake', 'Black Sabbath', 'Uriah Heep'],
  'Thin Lizzy': ['Iron Maiden', 'Def Leppard', 'UFO', 'Gary Moore', 'Whitesnake'],
  'Rush': ['Yes', 'Dream Theater', 'Tool', 'Boston', 'Styx'],
  'Boston': ['Journey', 'Styx', 'Foreigner', 'Rush', 'Kansas'],
  'Journey': ['Boston', 'Foreigner', 'Styx', 'Bon Jovi', 'REO Speedwagon'],
  'Foreigner': ['Journey', 'Boston', 'Styx', 'Bon Jovi', 'Def Leppard'],
  'Styx': ['Journey', 'Boston', 'Rush', 'Foreigner', 'Kansas'],
  'Cream': ['Led Zeppelin', 'Deep Purple', 'Jimi Hendrix', 'The Who', 'Eric Clapton'],
  'Eric Clapton': ['Cream', 'Jimi Hendrix', 'Stevie Ray Vaughan', 'Joe Bonamassa', 'Gary Moore'],
  'Joe Bonamassa': ['Eric Clapton', 'Stevie Ray Vaughan', 'Gary Moore', 'Joe Satriani', 'Santana'],
  'Stevie Ray Vaughan': ['Eric Clapton', 'Jimi Hendrix', 'Joe Bonamassa', 'ZZ Top', 'Gary Moore'],
  'Santana': ['Eric Clapton', 'Joe Satriani', 'Stevie Ray Vaughan', 'Jimi Hendrix', 'Joe Bonamassa'],
  
  // Hair Metal / Glam
  'Def Leppard': ['AC/DC', 'Van Halen', 'Bon Jovi', 'Whitesnake', 'Scorpions'],
  'Bon Jovi': ['Def Leppard', 'Journey', 'Foreigner', 'Van Halen', 'Whitesnake'],
  'Motley Crue': ['Poison', 'Ratt', 'Def Leppard', 'Van Halen', 'Guns N Roses'],
  'Poison': ['Motley Crue', 'Ratt', 'Warrant', 'Cinderella', 'Winger'],
  'Ratt': ['Motley Crue', 'Poison', 'Dokken', 'Cinderella', 'Warrant'],
  'Whitesnake': ['Deep Purple', 'Def Leppard', 'Van Halen', 'Bon Jovi', 'Foreigner'],
  'Guns N Roses': ['Motley Crue', 'Skid Row', 'Poison', 'Aerosmith', 'Slash'],
  'Dokken': ['Ratt', 'Scorpions', 'Queensryche', 'Winger', 'Great White'],
  'Cinderella': ['Poison', 'Ratt', 'Warrant', 'Slaughter', 'Winger'],
  'Warrant': ['Poison', 'Cinderella', 'Ratt', 'Slaughter', 'Firehouse'],
  'Winger': ['Dokken', 'Mr. Big', 'Extreme', 'Cinderella', 'Warrant'],
  'Skid Row': ['Guns N Roses', 'Motley Crue', 'Bon Jovi', 'Poison', 'Ratt'],
  'Twisted Sister': ['Kiss', 'Motley Crue', 'Alice Cooper', 'Quiet Riot', 'Poison'],
  'Quiet Riot': ['Ozzy Osbourne', 'Twisted Sister', 'Ratt', 'Motley Crue', 'Dokken'],
  'Great White': ['Whitesnake', 'Dokken', 'Ratt', 'Tesla', 'Cinderella'],
  'Tesla': ['Great White', 'Def Leppard', 'Dokken', 'Cinderella', 'Bon Jovi'],
  'Firehouse': ['Warrant', 'Slaughter', 'Poison', 'Cinderella', 'Winger'],
  'Slaughter': ['Warrant', 'Firehouse', 'Poison', 'Cinderella', 'Ratt'],
  'Extreme': ['Mr. Big', 'Winger', 'Van Halen', 'Steve Vai', 'Joe Satriani'],
  'Mr. Big': ['Extreme', 'Winger', 'Racer X', 'Steve Vai', 'Van Halen'],
  'Alice Cooper': ['Kiss', 'Ozzy Osbourne', 'Twisted Sister', 'Motley Crue', 'Black Sabbath'],
  'White Lion': ['Ratt', 'Dokken', 'Winger', 'Cinderella', 'Great White'],
  'LA Guns': ['Guns N Roses', 'Motley Crue', 'Ratt', 'Poison', 'Faster Pussycat'],
  
  // Guitar Heroes / Shred
  'Joe Satriani': ['Steve Vai', 'Eric Johnson', 'Santana', 'Joe Bonamassa', 'Extreme'],
  'Steve Vai': ['Joe Satriani', 'Eric Johnson', 'Mr. Big', 'Racer X', 'Extreme'],
  'Yngwie Malmsteen': ['Joe Satriani', 'Steve Vai', 'Racer X', 'Iron Maiden', 'Deep Purple'],
  'Eric Johnson': ['Joe Satriani', 'Steve Vai', 'Stevie Ray Vaughan', 'Eric Clapton', 'Santana'],
  'Racer X': ['Mr. Big', 'Steve Vai', 'Joe Satriani', 'Yngwie Malmsteen', 'Extreme'],
  
  // Grunge / Alternative
  'Soundgarden': ['Alice In Chains', 'Pearl Jam', 'Stone Temple Pilots', 'Audioslave', 'Tool'],
  'Alice In Chains': ['Soundgarden', 'Pearl Jam', 'Stone Temple Pilots', 'Nirvana', 'Tool'],
  'Stone Temple Pilots': ['Alice In Chains', 'Soundgarden', 'Pearl Jam', 'Bush', 'Foo Fighters'],
  'Foo Fighters': ['Stone Temple Pilots', 'Soundgarden', 'Audioslave', 'Queens Of The Stone Age', 'Alice In Chains'],
  'Audioslave': ['Soundgarden', 'Rage Against The Machine', 'Foo Fighters', 'Tool', 'Alice In Chains'],
  'Rage Against The Machine': ['Audioslave', 'Tool', 'Pantera', 'Soundgarden', 'Foo Fighters'],
  'Tool': ['Rage Against The Machine', 'Soundgarden', 'Alice In Chains', 'Pantera', 'Rush'],
  
  // Southern Rock
  'Lynyrd Skynyrd': ['ZZ Top', 'Allman Brothers', 'Bad Company', 'Molly Hatchet', 'Blackfoot'],
  'Bad Company': ['Led Zeppelin', 'Lynyrd Skynyrd', 'Foreigner', 'ZZ Top', 'Free'],
  'Molly Hatchet': ['Lynyrd Skynyrd', 'Blackfoot', 'ZZ Top', 'Bad Company', '38 Special'],
  
  // British Invasion / Classic
  'The Rolling Stones': ['The Beatles', 'The Who', 'Led Zeppelin', 'The Kinks', 'Cream'],
  'The Beatles': ['The Rolling Stones', 'The Who', 'The Kinks', 'Led Zeppelin', 'George Harrison'],
  'The Who': ['Led Zeppelin', 'The Rolling Stones', 'Cream', 'Deep Purple', 'The Kinks'],
};

// Default related artists for any artist not in the map
const defaultRelatedArtists = ['AC/DC', 'Metallica', 'Van Halen', 'Led Zeppelin', 'Black Sabbath'];

// Get related artists for a given artist
function getRelatedArtists(artistName) {
  const normalized = artistName.replace(/ -$/, '').trim();
  
  for (const [key, related] of Object.entries(relatedArtistsMap)) {
    if (key.toLowerCase() === normalized.toLowerCase()) {
      return related;
    }
  }
  
  return defaultRelatedArtists.filter(a => a.toLowerCase() !== normalized.toLowerCase());
}

export default function ArtistPageClient({ artistName, videos, slug, adSettings, initialAiContent, faqItems = [] }) {
  const [lang] = useLanguage();
  const t = getSubPageTranslation(lang);
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [openFaq, setOpenFaq] = useState(null);

  // Update SEO meta tags when language changes
  useEffect(() => {
    const seo = getSeoMeta(lang, 'artist', { artist: artistName });
    updateDocumentMeta(seo.title, seo.description);
  }, [lang, artistName]);
  const [showAd, setShowAd] = useState(false);
  const [adCountdown, setAdCountdown] = useState(adSettings?.ad_duration || 5);
  const [pendingVideo, setPendingVideo] = useState(null);
  const adDuration = adSettings?.ad_duration || 5;
  const [aiContent, setAiContent] = useState(initialAiContent || null);

  // Fetch AI-generated SEO content (client-side fallback if not provided via SSR)
  useEffect(() => {
    if (initialAiContent) return; // Already have it from SSR
    async function fetchAiContent() {
      try {
        const res = await fetch(`/api/seo-content?type=artist&name=${encodeURIComponent(artistName)}`);
        const data = await res.json();
        if (data.found && data.content) {
          setAiContent(data.content);
        }
      } catch (e) {
        // Silently fail — will show default content
      }
    }
    if (artistName) fetchAiContent();
  }, [artistName, initialAiContent]);

  // Handle video click - show ad first
  const handleVideoClick = (video) => {
    setPendingVideo(video);
    setAdCountdown(adDuration);
    setShowAd(true);
  };

  // Countdown effect for interstitial ad
  useEffect(() => {
    if (showAd && adCountdown > 0) {
      const timer = setTimeout(() => setAdCountdown(adCountdown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (adCountdown === 0 && showAd) {
      setShowAd(false);
      setSelectedVideo(pendingVideo);
      setPendingVideo(null);
    }
  }, [showAd, adCountdown]);

  // Get YouTube embed URL
  const getEmbedUrl = (video) => {
    if (video.video_id) {
      return `https://www.youtube.com/embed/${video.video_id}?autoplay=1`;
    }
    return video.youtube_url?.replace('watch?v=', 'embed/') || '';
  };

  // Interstitial Ad Screen
  if (showAd && pendingVideo) {
    return (
      <div className="min-h-screen bg-black flex flex-col">
        <header className="bg-black/95 border-b border-zinc-800 px-4 py-2 sm:py-3">
          <div className="max-w-4xl mx-auto flex items-center gap-4">
            <Link href="/">
              <img src={LOGO_URL} alt="DadRock Tabs" className="w-10 h-10" />
            </Link>
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
              {adSettings?.ad_headline || 'Check Out Our Merchandise!'}
            </h2>
            <p className="text-zinc-400">
              {adSettings?.ad_description || 'Support DadRock Tabs by grabbing some awesome gear'}
            </p>
          </div>

          <a
            href={adSettings?.ad_link || 'https://my-store-b8bb42.creator-spring.com/'}
            target="_blank"
            rel="noopener noreferrer"
            className="block w-full max-w-2xl mb-8"
          >
            <div className="bg-gradient-to-br from-amber-500 via-orange-500 to-red-600 p-1 rounded-2xl hover:scale-[1.02] transition-transform">
              <div className="bg-zinc-900 rounded-xl p-8 text-center">
                {adSettings?.ad_image ? (
                  <img src={adSettings.ad_image} alt={adSettings.ad_headline} className="w-full max-h-64 object-contain mx-auto mb-4 rounded-lg" />
                ) : (
                  <ShoppingBag className="w-16 h-16 mx-auto mb-4 text-amber-500" />
                )}
                <h3 className="text-xl md:text-2xl font-bold text-white mb-2">{adSettings?.ad_headline}</h3>
                <p className="text-zinc-400 mb-4">{adSettings?.ad_description}</p>
                <span className="inline-flex items-center gap-2 px-6 py-3 bg-amber-500 text-black font-bold rounded-full">
                  <ShoppingBag className="w-5 h-5" />
                  {adSettings?.ad_button_text || 'Shop Now'}
                </span>
              </div>
            </div>
          </a>

          <div className="text-center">
            <p className="text-zinc-500 mb-4">
              Loading: <span className="text-white font-semibold">{pendingVideo.song || pendingVideo.title}</span> by {artistName}
            </p>
            <div className="w-64 h-2 bg-zinc-800 rounded-full overflow-hidden mx-auto">
              <div
                className="h-full bg-amber-500 transition-all duration-1000"
                style={{ width: `${((adDuration - adCountdown) / adDuration) * 100}%` }}
              />
            </div>
            <button
              onClick={() => {
                setShowAd(false);
                setSelectedVideo(pendingVideo);
                setPendingVideo(null);
              }}
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

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-zinc-950/90 backdrop-blur-md border-b border-zinc-800">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between gap-4">
            <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity flex-shrink-0">
              <img src={LOGO_URL} alt="DadRock Tabs" className="h-9 w-auto" />
              <span className="text-lg font-bold text-amber-500 hidden sm:block font-rock">DadRock Tabs</span>
            </Link>
            {/* Search Bar — compact in header */}
            <div className="hidden md:block flex-1 max-w-sm mx-4">
              <SearchBar variant="compact" placeholder={t.searchPlaceholder || 'Search artists & songs...'} />
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              <LanguageSelector />
              <Link 
                href="/"
                className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-full text-sm transition-colors"
              >
                <Home className="w-4 h-4" />
                <span className="hidden sm:inline">{t.home}</span>
              </Link>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Breadcrumb */}
        <nav className="mb-6 text-sm text-zinc-400">
          <Link href="/" className="hover:text-amber-500 transition-colors">{t.home}</Link>
          <span className="mx-2">/</span>
          <span className="text-white">{artistName}</span>
        </nav>

        {/* Hero Section — Dramatic Artist Header */}
        <div className="relative mb-10 p-8 sm:p-12 rounded-3xl overflow-hidden hero-gradient-bg fire-glow spotlight-sweep">
          {/* Background accent elements */}
          <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-red-500/5 rounded-full blur-3xl" />
          
          {/* Ember sparks rising from bottom */}
          <div className="ember-container">
            <div className="ember" /><div className="ember" /><div className="ember" />
            <div className="ember" /><div className="ember" /><div className="ember" />
          </div>
          
          <div className="relative z-10">
            <div className="flex flex-col sm:flex-row sm:items-end gap-4 sm:gap-8">
              <div className="flex-1">
                <p className="text-sm font-medium text-amber-500/80 uppercase tracking-widest mb-2 font-rock-alt flex items-center gap-2">
                  <span className="eq-visualizer" style={{ height: '16px' }}>
                    <span className="bar" /><span className="bar" /><span className="bar" /><span className="bar" /><span className="bar" />
                  </span>
                  Guitar & Bass Tabs
                </p>
                <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold font-rock text-gradient-gold neon-underline pb-2">
                  {artistName}
                </h1>
              </div>
              <div className="flex items-center gap-4 flex-shrink-0">
                <div className="stat-badge px-5 py-3 rounded-2xl text-center">
                  <div className="text-3xl font-bold text-amber-500 font-rock">{videos.length}</div>
                  <div className="text-xs text-zinc-400 uppercase tracking-wider">{t.artistLessons || 'lessons'}</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* About Artist — Shown ABOVE lessons */}
        <div className="mb-10 p-6 sm:p-8 bg-zinc-900/50 rounded-2xl border border-zinc-800 section-accent reveal-section">
          <h2 className="text-2xl font-bold mb-4 text-amber-500 flex items-center gap-2">
            <Star className="w-6 h-6" />
            {t.about || 'About'} {artistName}
          </h2>
          <div className="text-zinc-300 space-y-4 leading-relaxed">
            {aiContent?.bio ? (
              aiContent.bio.split('\n').filter(Boolean).map((p, i) => <p key={i}>{p}</p>)
            ) : (
              <>
                <p>{(t.defaultBioP1 || '').replace(/\{artist\}/g, artistName)}</p>
                <p>{t.defaultBioP2 || ''}</p>
              </>
            )}
          </div>
        </div>

        {/* Hint to scroll for gear/playing style — only show if AI content has extra sections */}
        {aiContent?.playing_style && (
          <div className="mb-8 p-4 bg-gradient-to-r from-amber-500/10 to-zinc-900/30 rounded-xl border border-amber-500/20 text-center">
            <p className="text-zinc-300 text-sm sm:text-base">
              🎸 {t.scrollHintGear || 'Want to know what'} <strong className="text-amber-400">{t.scrollHintGearWord || 'gear'}</strong> {artistName} {t.scrollHintUsed || 'used, their'} <strong className="text-amber-400">{t.scrollHintStyle || 'playing style'}</strong>{t.scrollHintAnd || ', and'} <strong className="text-amber-400">{t.scrollHintFacts || 'fun facts'}</strong>{t.scrollHintEnd || '? Scroll below the lessons!'}
            </p>
          </div>
        )}

        {/* Video Player (if selected) */}
        {selectedVideo && (
          <div className="mb-10 bg-zinc-900 rounded-2xl border border-zinc-800 overflow-hidden">
            <div className="aspect-video">
              <iframe
                src={getEmbedUrl(selectedVideo)}
                title={selectedVideo.song || selectedVideo.title}
                className="w-full h-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                allowFullScreen
                style={{ border: 'none' }}
              />
            </div>
            <div className="p-4 border-t border-zinc-800">
              <h2 className="text-xl font-bold text-white">{selectedVideo.song || selectedVideo.title}</h2>
              <p className="text-zinc-400">{artistName}</p>
              <button
                onClick={() => setSelectedVideo(null)}
                className="mt-3 flex items-center gap-2 text-amber-500 hover:text-amber-400 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                {t.backToAllLessons || 'Back to all lessons'}
              </button>
            </div>
          </div>
        )}

        {/* Section Title */}
        <h2 className="text-2xl font-bold mb-6 text-white">
          {selectedVideo ? t.moreLessons : t.watchLesson}
        </h2>

        {/* Video Grid — Enhanced with lesson numbers and glow effects */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video, index) => (
            <div
              key={video.id || video.video_id}
              className={`group glow-card spotlight-sweep bg-zinc-900/80 rounded-xl border border-zinc-800 overflow-hidden cursor-pointer card-enter bass-drop-hover ${
                selectedVideo?.id === video.id ? 'ring-2 ring-amber-500 border-amber-500/50' : ''
              }`}
              style={{ animationDelay: `${Math.min(index * 0.05, 0.5)}s` }}
              onClick={() => handleVideoClick(video)}
            >
              {/* Thumbnail */}
              <div className="relative aspect-video overflow-hidden">
                <img
                  src={video.thumbnail || `https://img.youtube.com/vi/${video.video_id}/mqdefault.jpg`}
                  alt={video.song || video.title}
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                  loading="lazy"
                />
                {/* Dark overlay */}
                <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                
                {/* Play button */}
                <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-all duration-300">
                  <div className="w-16 h-16 bg-amber-500 rounded-full flex items-center justify-center shadow-lg shadow-amber-500/30 scale-90 group-hover:scale-100 transition-transform duration-300">
                    <Play className="w-8 h-8 text-black ml-1" fill="black" />
                  </div>
                </div>
                
                {/* Lesson number badge */}
                <div className="absolute top-3 left-3 lesson-badge text-xs font-bold text-black px-2.5 py-1 rounded-lg">
                  #{index + 1}
                </div>
                
                {/* Now Playing indicator */}
                {selectedVideo?.id === video.id && (
                  <div className="absolute top-3 right-3 bg-amber-500 text-black text-xs font-bold px-3 py-1.5 rounded-lg flex items-center gap-1.5">
                    <div className="flex items-end gap-0.5 h-4">
                      <div className="w-1 bg-black rounded-full eq-bar-1" />
                      <div className="w-1 bg-black rounded-full eq-bar-2" />
                      <div className="w-1 bg-black rounded-full eq-bar-3" />
                      <div className="w-1 bg-black rounded-full eq-bar-4" />
                    </div>
                    PLAYING
                  </div>
                )}
              </div>
              
              {/* Video Info */}
              <div className="p-4">
                <h3 className="font-semibold text-white group-hover:text-amber-500 transition-colors line-clamp-2">
                  {video.song || video.title}
                </h3>
                <p className="text-sm text-zinc-500 mt-1">{artistName}</p>
              </div>
            </div>
          ))}
        </div>

        {/* SEO Content Section — AI-Enhanced (below lessons) */}
        <section className="mt-16 space-y-8 reveal-section">
          {/* Section Divider */}
          <div className="flex items-center gap-4 mb-8">
            <div className="h-px flex-1 bg-gradient-to-r from-transparent via-amber-500/30 to-transparent" />
            <span className="text-amber-500 text-sm font-bold uppercase tracking-widest font-rock-alt">Deep Dive</span>
            <div className="h-px flex-1 bg-gradient-to-r from-transparent via-amber-500/30 to-transparent" />
          </div>

          {/* Playing Style & Gear — only show if AI content available */}
          {aiContent?.playing_style && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800 section-accent hover:border-zinc-700 transition-colors">
                <h3 className="text-xl font-bold mb-3 text-white flex items-center gap-2">
                  <Music className="w-5 h-5 text-amber-500" />
                  {t.playingStyle || 'Playing Style'}
                </h3>
                <p className="text-zinc-300 leading-relaxed">{aiContent.playing_style}</p>
              </div>
              {aiContent?.gear_info && (
                <div className="p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800 section-accent hover:border-zinc-700 transition-colors">
                  <h3 className="text-xl font-bold mb-3 text-white flex items-center gap-2">
                    🎸 {t.gearEquipment || 'Gear & Equipment'}
                  </h3>
                  <p className="text-zinc-300 leading-relaxed">{aiContent.gear_info}</p>
                </div>
              )}
            </div>
          )}

          {/* Why Learn This Artist */}
          {aiContent?.why_learn && (
            <div className="p-6 bg-gradient-to-r from-amber-500/10 via-amber-500/5 to-zinc-900/50 rounded-2xl border border-amber-500/20 section-accent">
              <h3 className="text-xl font-bold mb-3 text-amber-500 flex items-center gap-2">
                <Lightbulb className="w-5 h-5" />
                {t.whyLearn || 'Why Learn'} {artistName} {t.whyLearnSuffix || 'Songs?'}
              </h3>
              <p className="text-zinc-300 leading-relaxed">{aiContent.why_learn}</p>
            </div>
          )}

          {/* Fun Facts */}
          {aiContent?.fun_facts && aiContent.fun_facts.length > 0 && (
            <div className="p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800 section-accent">
              <h3 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-amber-500" />
                {t.didYouKnow || 'Did You Know?'}
              </h3>
              <ul className="space-y-3">
                {aiContent.fun_facts.map((fact, i) => (
                  <li key={i} className="flex items-start gap-3 text-zinc-300">
                    <span className="flex-shrink-0 w-6 h-6 bg-amber-500/10 border border-amber-500/30 rounded-full flex items-center justify-center text-amber-500 text-xs font-bold mt-0.5">
                      {i + 1}
                    </span>
                    <span>{fact}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Available Lessons Count */}
          <div className="text-center p-8 rounded-2xl border border-zinc-800 hero-gradient-bg relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-amber-500/5 rounded-full blur-2xl" />
            <div className="absolute bottom-0 left-0 w-24 h-24 bg-red-500/5 rounded-full blur-2xl" />
            <p className="text-amber-500 font-semibold text-xl relative z-10 font-rock">
              <Music className="w-6 h-6 inline mr-2" />
              {videos.length} {artistName} {t.lessonsAvailableCta || 'lesson(s) available — Start learning today!'}
            </p>
          </div>
        </section>


        {/* FAQ Section — For Google Featured Snippets */}
        {faqItems.length > 0 && (
          <section className="mt-10 reveal-section">
            <div className="flex items-center gap-4 mb-6">
              <div className="h-px flex-1 bg-gradient-to-r from-transparent via-zinc-700 to-transparent" />
              <h2 className="text-xl font-bold text-white flex items-center gap-2 font-rock-alt uppercase tracking-wider text-sm">
                <BookOpen className="w-5 h-5 text-amber-500" />
                Frequently Asked Questions
              </h2>
              <div className="h-px flex-1 bg-gradient-to-r from-transparent via-zinc-700 to-transparent" />
            </div>
            <div className="space-y-3">
              {faqItems.map((faq, i) => (
                <div
                  key={i}
                  className="bg-zinc-900/50 rounded-xl border border-zinc-800 overflow-hidden transition-colors hover:border-zinc-700"
                >
                  <button
                    onClick={() => setOpenFaq(openFaq === i ? null : i)}
                    className="w-full flex items-center justify-between p-5 text-left"
                  >
                    <span className="font-medium text-white pr-4">{faq.question}</span>
                    <span className={`text-amber-500 text-xl font-bold transition-transform duration-200 ${openFaq === i ? 'rotate-45' : ''}`}>
                      +
                    </span>
                  </button>
                  {openFaq === i && (
                    <div className="px-5 pb-5 text-zinc-400 leading-relaxed border-t border-zinc-800 pt-4">
                      {faq.answer}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Related Artists Section - Internal Linking */}
        <section className="mt-10 p-8 rounded-2xl border border-zinc-800 relative overflow-hidden hero-gradient-bg">
          <div className="absolute top-0 left-0 w-48 h-48 bg-amber-500/3 rounded-full blur-3xl" />
          <div className="relative z-10">
            <h2 className="text-2xl font-bold mb-2 text-white flex items-center gap-2 font-rock">
              <Users className="w-6 h-6 text-amber-500" />
              {t.ifYouLike || 'If You Like'} {artistName}{t.youllLove || ', You\'ll Love...'}
            </h2>
            <p className="text-zinc-500 mb-6 text-sm">
              {t.checkOutSimilar || 'Check out guitar and bass tabs from these similar classic rock artists:'}
            </p>
            <div className="flex flex-wrap gap-3">
              {getRelatedArtists(artistName).map((relatedArtist) => (
                <Link
                  key={relatedArtist}
                  href={`/artist/${artistToSlug(relatedArtist)}`}
                  className="group/pill flex items-center gap-2 px-5 py-3 bg-zinc-800/80 hover:bg-amber-500 rounded-full font-medium transition-all border border-zinc-700 hover:border-amber-500 hover:text-black hover:shadow-lg hover:shadow-amber-500/20 hover:-translate-y-0.5"
                >
                  <span className="w-7 h-7 rounded-full bg-zinc-700 group-hover/pill:bg-amber-600 flex items-center justify-center text-xs font-bold text-zinc-300 group-hover/pill:text-black transition-colors">
                    {relatedArtist.charAt(0)}
                  </span>
                  {relatedArtist}
                </Link>
              ))}
            </div>
          </div>
        </section>

        {/* Back to Home */}
        <div className="mt-12 text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-3 px-8 py-4 bg-amber-500 hover:bg-amber-400 text-black font-bold rounded-full transition-colors"
          >
            <Home className="w-5 h-5" />
            {t.backToHome2 || 'Back to Home'}
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-zinc-800">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <img src={LOGO_URL} alt="DadRock Tabs" className="w-8 h-8 opacity-50" />
              <p className="text-zinc-500 text-sm">{t.footer}</p>
            </div>
            <div className="flex items-center gap-6">
              <Link href="/" className="text-zinc-500 hover:text-amber-500 transition-colors text-sm">{t.home}</Link>
              <a 
                href="https://youtube.com/@dadrockytofficial?si=AM8uj6DTefJcP8oZ" 
                target="_blank" 
                rel="noopener noreferrer"
                className="text-zinc-500 hover:text-red-500 transition-colors flex items-center gap-1.5 text-sm"
              >
                <Youtube className="w-4 h-4" />
                YouTube
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
