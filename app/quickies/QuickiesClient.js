'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Youtube, Music, Home, Zap, ShoppingBag } from 'lucide-react';
import LanguageSelector, { useLanguage } from '@/components/LanguageSelector';
import { getSubPageTranslation } from '@/lib/subPageI18n';
import { getSeoMeta, updateDocumentMeta } from '@/lib/seoTranslations';

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";
const YOUTUBE_CHANNEL = "https://youtube.com/@dadrockytofficial?si=AM8uj6DTefJcP8oZ";
const QUICKIES_PLAYLIST_URL = "https://www.youtube.com/playlist?list=PLEneI6e1FjBVRrw6FfSBK32RiT8N43v0H";

export default function QuickiesClient({ initialVideos, adSettings }) {
  const [lang] = useLanguage();
  const t = getSubPageTranslation(lang);
  const [selectedVideo, setSelectedVideo] = useState(null);

  // Update SEO meta tags when language changes
  useEffect(() => {
    const seo = getSeoMeta(lang, 'quickies');
    updateDocumentMeta(seo.title, seo.description);
  }, [lang]);
  const [showAd, setShowAd] = useState(false);
  const [adCountdown, setAdCountdown] = useState(adSettings?.ad_duration || 5);
  const [pendingVideo, setPendingVideo] = useState(null);
  const adDuration = adSettings?.ad_duration || 5;

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
              {t.videoStartsIn} <span className="text-amber-500 font-bold text-lg">{adCountdown}</span> {t.seconds}
            </div>
          </div>
        </header>

        <main className="flex-1 flex flex-col items-center justify-center px-4 py-8">
          <div className="text-center mb-8">
            <p className="text-zinc-500 text-sm uppercase tracking-wider mb-2">{t.sponsored}</p>
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
              Loading: <span className="text-white font-semibold">{pendingVideo.song || pendingVideo.title}</span>
              {pendingVideo.artist && pendingVideo.artist !== 'DadRock Tabs' && <span> by {pendingVideo.artist}</span>}
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
              {adCountdown > 0 ? `${t.skipIn} ${adCountdown}s` : t.skipAd}
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
          <span className="text-white">{t.quickiesTitle}</span>
        </nav>

        {/* Page Header */}
        <div className="mb-10">
          <h1 className="text-4xl sm:text-5xl font-bold mb-4 font-rock">
            <span className="text-amber-500">DadRock Tabs</span>
            <span className="text-white"> Quickies</span>
            <Zap className="inline w-10 h-10 ml-3 text-yellow-400" />
          </h1>
          <p className="text-lg text-zinc-300 max-w-3xl leading-relaxed">
            {t.quickiesSubtitle}
          </p>
          <div className="mt-4 flex items-center gap-4 flex-wrap">
            <p className="text-amber-500 font-semibold">
              <Music className="w-5 h-5 inline mr-2" />
              {initialVideos.length} {t.quickiesAvailable}
            </p>
            <a
              href={QUICKIES_PLAYLIST_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 text-red-400 hover:text-red-300 transition-colors font-medium"
            >
              <Youtube className="w-5 h-5" />
              {t.watchOnYouTube}
            </a>
          </div>
        </div>

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
              {selectedVideo.artist && selectedVideo.artist !== 'DadRock Tabs' && (
                <p className="text-zinc-400">{selectedVideo.artist}</p>
              )}
              <button
                onClick={() => setSelectedVideo(null)}
                className="mt-3 flex items-center gap-2 text-amber-500 hover:text-amber-400 transition-colors"
              >
                <ArrowLeft className="w-4 h-4" />
                Back to all quickies
              </button>
            </div>
          </div>
        )}

        {/* Section Title */}
        <h2 className="text-2xl font-bold mb-6 text-white">
          {selectedVideo ? 'More Quickies' : 'Watch Quick Lessons Below'}
        </h2>

        {/* Empty State */}
        {initialVideos.length === 0 && (
          <div className="text-center py-20">
            <Zap className="w-16 h-16 mx-auto mb-4 text-zinc-600" />
            <p className="text-zinc-400 text-lg">No quickies loaded yet.</p>
            <p className="text-zinc-500 text-sm mt-2">Videos will appear once synced from YouTube.</p>
            <a
              href={QUICKIES_PLAYLIST_URL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 mt-6 px-6 py-3 bg-red-600 hover:bg-red-500 text-white font-bold rounded-full transition-colors"
            >
              <Youtube className="w-5 h-5" />
              Watch on YouTube Instead
            </a>
          </div>
        )}

        {/* Video Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {initialVideos.map((video) => (
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
                {/* Quickie badge */}
                <div className="absolute top-2 right-2 bg-yellow-500 text-black text-xs font-bold px-2 py-1 rounded-full flex items-center gap-1">
                  <Zap className="w-3 h-3" />
                  Quickie
                </div>
              </div>
              
              {/* Video Info */}
              <div className="p-4">
                <h3 className="font-semibold text-white group-hover:text-amber-500 transition-colors line-clamp-2">
                  {video.song || video.title}
                </h3>
                {video.artist && video.artist !== 'DadRock Tabs' && (
                  <p className="text-sm text-zinc-400 mt-1">{video.artist}</p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* SEO Content Section */}
        <section className="mt-16 p-8 bg-zinc-900/50 rounded-2xl border border-zinc-800">
          <h2 className="text-2xl font-bold mb-4 text-amber-500">
            About DadRock Tabs Quickies
          </h2>
          <div className="text-zinc-300 space-y-4">
            <p>
              DadRock Tabs Quickies are short, focused guitar and bass tab tutorials designed 
              to get you playing fast. Each quickie breaks down a classic riff or lick in just 
              a few minutes — no lengthy intros, just straight to the music.
            </p>
            <p>
              Whether you're warming up before practice, learning something new during a break, 
              or just want to jam along to your favorite classic rock and heavy metal tunes, 
              these quickies are perfect for players of all levels.
            </p>
            <p>
              New quickies are added regularly from the DadRock Tabs YouTube channel. 
              Subscribe to never miss a new lesson!
            </p>
          </div>
        </section>

        {/* Subscribe CTA */}
        <div className="mt-10 text-center">
          <a
            href={YOUTUBE_CHANNEL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 px-8 py-4 bg-red-600 hover:bg-red-500 text-white font-bold rounded-full transition-colors"
          >
            <Youtube className="w-6 h-6" />
            Subscribe for More Quickies
          </a>
        </div>

        {/* Back to Home */}
        <div className="mt-8 text-center">
          <Link
            href="/"
            className="inline-flex items-center gap-3 px-8 py-4 bg-amber-500 hover:bg-amber-400 text-black font-bold rounded-full transition-colors"
          >
            <Home className="w-5 h-5" />
            Back to Home
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
              href={YOUTUBE_CHANNEL}
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
