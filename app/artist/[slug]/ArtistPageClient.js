'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Youtube, Music, Home, Users, ShoppingBag, BookOpen, Guitar, Lightbulb, Star } from 'lucide-react';
import LanguageSelector, { useLanguage } from '@/components/LanguageSelector';
import { getSubPageTranslation } from '@/lib/subPageI18n';
import { getSeoMeta, updateDocumentMeta } from '@/lib/seoTranslations';
import { artistToSlug } from '@/lib/slugify';

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";

// Related artists mapping for internal linking (SEO boost)
const relatedArtistsMap = {
  'AC/DC': ['Van Halen', 'Def Leppard', 'Aerosmith', 'Kiss', 'Scorpions'],
  'Metallica': ['Megadeth', 'Slayer', 'Anthrax', 'Iron Maiden', 'Black Sabbath'],
  'Van Halen': ['AC/DC', 'Def Leppard', 'Motley Crue', 'Bon Jovi', 'Whitesnake'],
  'Led Zeppelin': ['Deep Purple', 'Black Sabbath', 'Cream', 'The Who', 'Jimi Hendrix'],
  'Black Sabbath': ['Ozzy Osbourne', 'Dio', 'Iron Maiden', 'Judas Priest', 'Metallica'],
  'Ozzy Osbourne': ['Black Sabbath', 'Dio', 'Alice Cooper', 'Motley Crue', 'Quiet Riot'],
  'Def Leppard': ['AC/DC', 'Van Halen', 'Bon Jovi', 'Whitesnake', 'Scorpions'],
  'Guns N Roses': ['Motley Crue', 'Skid Row', 'Poison', 'Bon Jovi', 'Aerosmith'],
  'Aerosmith': ['AC/DC', 'Van Halen', 'Guns N Roses', 'Kiss', 'Bon Jovi'],
  'Iron Maiden': ['Judas Priest', 'Black Sabbath', 'Metallica', 'Megadeth', 'Dio'],
  'Judas Priest': ['Iron Maiden', 'Black Sabbath', 'Accept', 'Scorpions', 'Dio'],
  'Deep Purple': ['Led Zeppelin', 'Rainbow', 'Whitesnake', 'Uriah Heep', 'Black Sabbath'],
  'Kiss': ['AC/DC', 'Twisted Sister', 'Motley Crue', 'Alice Cooper', 'Aerosmith'],
  'Motley Crue': ['Poison', 'Ratt', 'Def Leppard', 'Van Halen', 'Guns N Roses'],
  'Bon Jovi': ['Def Leppard', 'Journey', 'Foreigner', 'Van Halen', 'Whitesnake'],
  'ZZ Top': ['Lynyrd Skynyrd', 'AC/DC', 'Allman Brothers', 'Stevie Ray Vaughan', 'Ted Nugent'],
  'Scorpions': ['Accept', 'Def Leppard', 'UFO', 'Judas Priest', 'Dokken'],
  'Whitesnake': ['Deep Purple', 'Def Leppard', 'Van Halen', 'Bon Jovi', 'Foreigner'],
  'Dio': ['Black Sabbath', 'Rainbow', 'Iron Maiden', 'Judas Priest', 'Ozzy Osbourne'],
  'Rainbow': ['Deep Purple', 'Dio', 'Whitesnake', 'Black Sabbath', 'Uriah Heep'],
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

export default function ArtistPageClient({ artistName, videos, slug, adSettings, initialAiContent }) {
  const [lang] = useLanguage();
  const t = getSubPageTranslation(lang);
  const [selectedVideo, setSelectedVideo] = useState(null);

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
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
              <img src={LOGO_URL} alt="DadRock Tabs" className="h-10 w-auto" />
              <span className="text-xl font-bold text-amber-500 hidden sm:block">DadRock Tabs</span>
            </Link>
            <div className="flex items-center gap-3">
              <LanguageSelector />
              <Link 
                href="/"
                className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-full text-sm transition-colors"
              >
                <Home className="w-4 h-4" />
                <span>{t.home}</span>
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

        {/* Artist Header */}
        <div className="mb-8">
          <h1 className="text-4xl sm:text-5xl font-bold mb-4 font-rock">
            <span className="text-amber-500">{artistName}</span>
            <span className="text-white"> Guitar & Bass Tabs</span>
          </h1>
          <p className="mt-2 text-amber-500 font-semibold">
            <Music className="w-5 h-5 inline mr-2" />
            {videos.length} lesson{videos.length !== 1 ? 's' : ''} available
          </p>
        </div>

        {/* About Artist — Shown ABOVE lessons */}
        <div className="mb-8 p-6 sm:p-8 bg-zinc-900/50 rounded-2xl border border-zinc-800">
          <h2 className="text-2xl font-bold mb-4 text-amber-500 flex items-center gap-2">
            <Star className="w-6 h-6" />
            About {artistName}
          </h2>
          <div className="text-zinc-300 space-y-4 leading-relaxed">
            {aiContent?.bio ? (
              aiContent.bio.split('\n').filter(Boolean).map((p, i) => <p key={i}>{p}</p>)
            ) : (
              <>
                <p>
                  Looking to learn {artistName} songs on guitar or bass? You've come to the right place! 
                  DadRock Tabs offers free video tutorials that break down every riff, chord, and solo 
                  so you can master your favorite {artistName} tracks.
                </p>
                <p>
                  Whether you're a beginner just starting out or an intermediate player looking to expand 
                  your repertoire, our step-by-step lessons make it easy to learn at your own pace.
                </p>
              </>
            )}
          </div>
        </div>

        {/* Hint to scroll for gear/playing style — only show if AI content has extra sections */}
        {aiContent?.playing_style && (
          <div className="mb-8 p-4 bg-gradient-to-r from-amber-500/10 to-zinc-900/30 rounded-xl border border-amber-500/20 text-center">
            <p className="text-zinc-300 text-sm sm:text-base">
              🎸 Want to know what <strong className="text-amber-400">gear</strong> {artistName} used, their <strong className="text-amber-400">playing style</strong>, and <strong className="text-amber-400">fun facts</strong>? Scroll below the lessons!
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
                Back to all lessons
              </button>
            </div>
          </div>
        )}

        {/* Section Title */}
        <h2 className="text-2xl font-bold mb-6 text-white">
          {selectedVideo ? t.moreLessons : t.watchLesson}
        </h2>

        {/* Video Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video) => (
            <div
              key={video.id || video.video_id}
              className={`group bg-zinc-900/80 rounded-xl border border-zinc-800 overflow-hidden hover:border-amber-500/50 transition-all cursor-pointer ${
                selectedVideo?.id === video.id ? 'ring-2 ring-amber-500' : ''
              }`}
              onClick={() => handleVideoClick(video)}
            >
              {/* Thumbnail */}
              <div className="relative aspect-video overflow-hidden">
                <img
                  src={video.thumbnail || `https://img.youtube.com/vi/${video.video_id}/mqdefault.jpg`}
                  alt={video.song || video.title}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                />
                <div className="absolute inset-0 bg-black/40 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="w-16 h-16 bg-amber-500 rounded-full flex items-center justify-center">
                    <Play className="w-8 h-8 text-black ml-1" fill="black" />
                  </div>
                </div>
              </div>
              
              {/* Video Info */}
              <div className="p-4">
                <h3 className="font-semibold text-white group-hover:text-amber-500 transition-colors line-clamp-2">
                  {video.song || video.title}
                </h3>
                <p className="text-sm text-zinc-400 mt-1">{artistName}</p>
              </div>
            </div>
          ))}
        </div>

        {/* SEO Content Section — AI-Enhanced (below lessons) */}
        <section className="mt-16 space-y-8">
          {/* Playing Style & Gear — only show if AI content available */}
          {aiContent?.playing_style && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800">
                <h3 className="text-xl font-bold mb-3 text-white flex items-center gap-2">
                  <Music className="w-5 h-5 text-amber-500" />
                  Playing Style
                </h3>
                <p className="text-zinc-300 leading-relaxed">{aiContent.playing_style}</p>
              </div>
              {aiContent?.gear_info && (
                <div className="p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800">
                  <h3 className="text-xl font-bold mb-3 text-white flex items-center gap-2">
                    🎸 Gear & Equipment
                  </h3>
                  <p className="text-zinc-300 leading-relaxed">{aiContent.gear_info}</p>
                </div>
              )}
            </div>
          )}

          {/* Why Learn This Artist */}
          {aiContent?.why_learn && (
            <div className="p-6 bg-gradient-to-r from-amber-500/10 to-zinc-900/50 rounded-2xl border border-amber-500/20">
              <h3 className="text-xl font-bold mb-3 text-amber-500 flex items-center gap-2">
                <Lightbulb className="w-5 h-5" />
                Why Learn {artistName} Songs?
              </h3>
              <p className="text-zinc-300 leading-relaxed">{aiContent.why_learn}</p>
            </div>
          )}

          {/* Fun Facts */}
          {aiContent?.fun_facts && aiContent.fun_facts.length > 0 && (
            <div className="p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800">
              <h3 className="text-xl font-bold mb-4 text-white flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-amber-500" />
                Did You Know?
              </h3>
              <ul className="space-y-3">
                {aiContent.fun_facts.map((fact, i) => (
                  <li key={i} className="flex items-start gap-3 text-zinc-300">
                    <span className="text-amber-500 font-bold text-lg mt-0.5">•</span>
                    <span>{fact}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Available Lessons Count */}
          <div className="text-center p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800">
            <p className="text-amber-500 font-semibold text-lg">
              <Music className="w-5 h-5 inline mr-2" />
              {videos.length} {artistName} lesson{videos.length !== 1 ? 's' : ''} available — Start learning today!
            </p>
          </div>
        </section>

        {/* Related Artists Section - Internal Linking for SEO */}
        <section className="mt-10 p-8 bg-zinc-900/50 rounded-2xl border border-zinc-800">
          <h2 className="text-2xl font-bold mb-4 text-white flex items-center gap-2">
            <Users className="w-6 h-6 text-amber-500" />
            If You Like {artistName}, You'll Love...
          </h2>
          <p className="text-zinc-400 mb-6">
            Check out guitar and bass tabs from these similar classic rock artists:
          </p>
          <div className="flex flex-wrap gap-3">
            {getRelatedArtists(artistName).map((relatedArtist) => (
              <Link
                key={relatedArtist}
                href={`/artist/${artistToSlug(relatedArtist)}`}
                className="px-5 py-3 bg-zinc-800 hover:bg-amber-500 hover:text-black rounded-full font-medium transition-all border border-zinc-700 hover:border-amber-500"
              >
                {relatedArtist}
              </Link>
            ))}
          </div>
        </section>

        {/* Back to Home */}
        <div className="mt-12 text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-3 px-8 py-4 bg-amber-500 hover:bg-amber-400 text-black font-bold rounded-full transition-colors"
          >
            <Home className="w-5 h-5" />
            Explore More Artists
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-zinc-800 py-8">
        <div className="container mx-auto px-4 text-center text-zinc-400">
          <p>{t.footer}</p>
          <div className="mt-4 flex justify-center gap-6">
            <Link href="/" className="hover:text-amber-500 transition-colors">{t.home}</Link>
            <a 
              href="https://youtube.com/@dadrockytofficial?si=AM8uj6DTefJcP8oZ" 
              target="_blank" 
              rel="noopener noreferrer"
              className="hover:text-amber-500 transition-colors flex items-center gap-1"
            >
              <Youtube className="w-4 h-4" />
              YouTube
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
