'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Home, Youtube, Facebook, Twitter, Mail, Play, Eye, ThumbsUp, ShoppingBag, Music, ExternalLink, ArrowLeft, BookOpen, Lightbulb, Star } from 'lucide-react';
import LanguageSelector, { useLanguage } from '@/components/LanguageSelector';
import { getSubPageTranslation } from '@/lib/subPageI18n';
import { getSeoMeta, updateDocumentMeta } from '@/lib/seoTranslations';
import { artistToSlug } from '@/lib/slugify';

const LOGO_URL = 'https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png';
const YOUTUBE_CHANNEL = 'https://youtube.com/@dadrockytofficial?si=AM8uj6DTefJcP8oZ';

function formatViewCount(count) {
  if (count >= 1000000) return (count / 1000000).toFixed(1) + 'M';
  if (count >= 1000) return (count / 1000).toFixed(1) + 'K';
  return count.toString();
}

export default function SongPageClient({ song, seoContent, adSettings, initialAiContent }) {
  const [lang] = useLanguage();
  const t = getSubPageTranslation(lang);
  const [showAd, setShowAd] = useState(false);
  const [videoPlaying, setVideoPlaying] = useState(false);
  const [aiContent, setAiContent] = useState(initialAiContent || null);

  // Fetch AI-generated SEO content for this song (client-side fallback)
  useEffect(() => {
    if (initialAiContent) return;
    async function fetchAiContent() {
      try {
        const res = await fetch(`/api/seo-content?type=song&slug=${encodeURIComponent(song?.slug || '')}`);
        const data = await res.json();
        if (data.found && data.content) {
          setAiContent(data.content);
        }
      } catch (e) { /* Silently fail */ }
    }
    if (song?.slug) fetchAiContent();
  }, [song?.slug, initialAiContent]);

  // Update SEO meta tags when language changes
  useEffect(() => {
    const seo = getSeoMeta(lang, 'song', { song: song?.title || '', artist: song?.artist || '' });
    updateDocumentMeta(seo.title, seo.description);
  }, [lang, song?.title, song?.artist]);
  const [adCountdown, setAdCountdown] = useState(adSettings?.ad_duration || 5);
  const adDuration = adSettings?.ad_duration || 5;

  const youtubeUrl = `https://www.youtube.com/watch?v=${song.videoId}`;
  const embedUrl = `https://www.youtube.com/embed/${song.videoId}?autoplay=1`;
  const artistSlug = artistToSlug(song.artist);

  const shareUrl = `https://dadrocktabs.com/songs/${song.slug}`;
  const shareText = `Learn to play ${song.title} by ${song.artist} with free guitar tabs! 🎸`;
  const facebookShareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
  const twitterShareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`;
  const emailShareUrl = `mailto:?subject=${encodeURIComponent(`${song.title} - ${song.artist} Guitar Tab | DadRock Tabs`)}&body=${encodeURIComponent(`${shareText}\n\n${shareUrl}`)}`;

  // Countdown effect for interstitial ad
  useEffect(() => {
    if (showAd && adCountdown > 0) {
      const timer = setTimeout(() => setAdCountdown(adCountdown - 1), 1000);
      return () => clearTimeout(timer);
    } else if (adCountdown === 0 && showAd) {
      setShowAd(false);
      setVideoPlaying(true);
    }
  }, [showAd, adCountdown]);

  // Interstitial Ad Screen
  if (showAd) {
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
              Loading: <span className="text-white font-semibold">{song.title}</span> by {song.artist}
            </p>
            <div className="w-64 h-2 bg-zinc-800 rounded-full overflow-hidden mx-auto">
              <div
                className="h-full bg-amber-500 transition-all duration-1000"
                style={{ width: `${((adDuration - adCountdown) / adDuration) * 100}%` }}
              />
            </div>
            <button
              onClick={() => { setShowAd(false); setVideoPlaying(true); }}
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

  // Main Song Page (after ad)
  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 text-white">
      {/* Header */}
      <header className="relative overflow-hidden">
        <div className="absolute inset-0 pointer-events-none bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMtNi42MjcgMC0xMiA1LjM3My0xMiAxMnM1LjM3MyAxMiAxMiAxMiAxMi01LjM3MyAxMi0xMi01LjM3My0xMi0xMi0xMnptMCAxOGMtMy4zMTQgMC02LTIuNjg2LTYtNnMyLjY4Ni02IDYtNiA2IDIuNjg2IDYgNi0yLjY4NiA2LTYgNnoiIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iLjAyIi8+PC9nPjwvc3ZnPg==')] opacity-30"></div>

        <div className="max-w-4xl mx-auto px-4 py-6">
          {/* Navigation */}
          <nav className="flex items-center justify-between mb-6">
            <Link href="/" className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors">
              <Home className="w-5 h-5" />
              <span>{t.backToHome}</span>
            </Link>
            <div className="flex items-center gap-3">
              <LanguageSelector />
              <a
                href={YOUTUBE_CHANNEL}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 rounded-full font-medium transition-colors"
              >
                <Youtube className="w-5 h-5" />
                Subscribe
              </a>
            </div>
          </nav>

          {/* Logo */}
          <div className="text-center mb-4">
            <Link href="/">
              <img
                src={LOGO_URL}
                alt="DadRock Tabs"
                className="max-w-xs mx-auto w-full drop-shadow-2xl hover:scale-105 transition-transform duration-300"
              />
            </Link>
          </div>

          {/* Social Share */}
          <div className="flex items-center justify-center gap-3 mb-6">
            <span className="text-zinc-400 text-sm font-medium">{t.shareThisPage}:</span>
            <a href={facebookShareUrl} target="_blank" rel="noopener noreferrer" className="flex items-center justify-center w-10 h-10 bg-blue-600 hover:bg-blue-500 rounded-full transition-all hover:scale-110" title="Share on Facebook">
              <Facebook className="w-5 h-5" />
            </a>
            <a href={twitterShareUrl} target="_blank" rel="noopener noreferrer" className="flex items-center justify-center w-10 h-10 bg-sky-500 hover:bg-sky-400 rounded-full transition-all hover:scale-110" title="Share on Twitter">
              <Twitter className="w-5 h-5" />
            </a>
            <a href={emailShareUrl} className="flex items-center justify-center w-10 h-10 bg-zinc-700 hover:bg-zinc-600 rounded-full transition-all hover:scale-110" title="Share via Email">
              <Mail className="w-5 h-5" />
            </a>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 py-8">
        {/* Song Title */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-5xl font-bold mb-3 bg-gradient-to-r from-amber-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
            {song.title}
          </h1>
          <div className="flex items-center justify-center gap-3 flex-wrap">
            <span className="text-xl text-zinc-300">{song.artist}</span>
            {artistSlug && (
              <Link
                href={`/artist/${artistSlug}`}
                className="inline-flex items-center gap-1 text-sm text-amber-500 hover:text-amber-400 transition-colors"
              >
                <ExternalLink className="w-4 h-4" />
                View all {song.artist} tabs
              </Link>
            )}
          </div>
          {/* Stats */}
          <div className="mt-4 flex items-center justify-center gap-6 flex-wrap">
            {song.viewCount > 0 && (
              <div className="flex items-center gap-2 text-amber-400">
                <Eye className="w-5 h-5" />
                <span className="font-bold text-lg">{formatViewCount(song.viewCount)}</span>
                <span className="text-zinc-500 text-sm">views</span>
              </div>
            )}
            {song.likeCount > 0 && (
              <div className="flex items-center gap-2 text-green-400">
                <ThumbsUp className="w-5 h-5" />
                <span className="font-bold">{formatViewCount(song.likeCount)}</span>
                <span className="text-zinc-500 text-sm">likes</span>
              </div>
            )}
          </div>
        </div>

        {/* SEO Content — AI-Enhanced (ABOVE video) */}
        <section className="space-y-6 mb-10">
          {/* Song Story */}
          <div className="p-8 bg-zinc-900/50 rounded-2xl border border-zinc-800">
            <h2 className="text-2xl font-bold text-amber-500 mb-4 flex items-center gap-2">
              <Star className="w-6 h-6" />
              {song.title} by {song.artist}
            </h2>
            <div className="text-zinc-300 space-y-4 leading-relaxed">
              {aiContent?.song_story ? (
                aiContent.song_story.split('\n').filter(Boolean).map((p, i) => <p key={i}>{p}</p>)
              ) : (
                <>
                  <p>{seoContent.paragraph1}</p>
                  <p>{seoContent.paragraph2}</p>
                  <p>{seoContent.paragraph3}</p>
                </>
              )}
            </div>
          </div>
        </section>

        {/* Video Section — Thumbnail with Play Button or Embedded Player */}
        <div className="relative mb-6">
          {videoPlaying ? (
            /* Embedded Video (after ad or direct play) */
            <div className="aspect-video rounded-xl overflow-hidden border border-zinc-800 bg-black">
              <iframe
                src={embedUrl}
                title={`${song.title} by ${song.artist} - Guitar Tab Lesson`}
                className="w-full h-full"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen"
                allowFullScreen
                style={{ border: 'none' }}
              />
            </div>
          ) : (
            /* Thumbnail with Play Button — Clicking triggers the ad */
            <button
              onClick={() => {
                if (adSettings?.ad_link) {
                  setAdCountdown(adSettings?.ad_duration || 5);
                  setShowAd(true);
                } else {
                  setVideoPlaying(true);
                }
              }}
              className="w-full aspect-video rounded-xl overflow-hidden border border-zinc-800 bg-black relative group cursor-pointer"
            >
              <img
                src={song.thumbnail || `https://img.youtube.com/vi/${song.videoId}/maxresdefault.jpg`}
                alt={`${song.title} by ${song.artist}`}
                className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                onError={(e) => {
                  e.target.src = `https://img.youtube.com/vi/${song.videoId}/hqdefault.jpg`;
                }}
              />
              <div className="absolute inset-0 bg-black/40 group-hover:bg-black/30 transition-colors flex items-center justify-center">
                <div className="w-20 h-20 bg-red-600 rounded-full flex items-center justify-center group-hover:scale-110 transition-transform shadow-2xl">
                  <Play className="w-10 h-10 text-white ml-1" fill="white" />
                </div>
              </div>
              <div className="absolute bottom-4 left-4 right-4 text-left">
                <p className="text-white font-bold text-lg drop-shadow-lg">{t.watchLesson || 'Watch the Lesson'}</p>
                <p className="text-zinc-300 text-sm drop-shadow-lg">{song.title} — {song.artist}</p>
              </div>
            </button>
          )}
        </div>

        {/* Open in YouTube */}
        <div className="flex justify-center gap-3 mb-12">
          <a
            href={youtubeUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-5 py-2.5 bg-zinc-800 hover:bg-zinc-700 text-white font-medium rounded-full transition-all border border-zinc-700"
          >
            <Youtube className="w-4 h-4 text-red-500" />
            Open in YouTube
          </a>
        </div>

        {/* Additional AI Content (below video) */}
        <section className="space-y-6 mb-12">
          {/* Lesson Overview & Difficulty — only show if AI content */}
          {aiContent?.lesson_overview && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800">
                <h3 className="text-xl font-bold mb-3 text-white flex items-center gap-2">
                  <BookOpen className="w-5 h-5 text-amber-500" />
                  What You'll Learn
                </h3>
                <p className="text-zinc-300 leading-relaxed">{aiContent.lesson_overview}</p>
                {aiContent.difficulty_info && (
                  <p className="mt-3 text-amber-400 text-sm font-medium">{aiContent.difficulty_info}</p>
                )}
              </div>

              {/* Techniques */}
              {aiContent?.techniques && aiContent.techniques.length > 0 && (
                <div className="p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800">
                  <h3 className="text-xl font-bold mb-3 text-white flex items-center gap-2">
                    🎸 Techniques Used
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {aiContent.techniques.map((tech, i) => (
                      <span key={i} className="px-3 py-1 bg-amber-500/20 text-amber-400 rounded-full text-sm font-medium">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Pro Tips */}
          {aiContent?.pro_tips && aiContent.pro_tips.length > 0 && (
            <div className="p-6 bg-gradient-to-r from-amber-500/10 to-zinc-900/50 rounded-2xl border border-amber-500/20">
              <h3 className="text-xl font-bold mb-4 text-amber-500 flex items-center gap-2">
                <Lightbulb className="w-5 h-5" />
                Practice Tips
              </h3>
              <ul className="space-y-3">
                {aiContent.pro_tips.map((tip, i) => (
                  <li key={i} className="flex items-start gap-3 text-zinc-300">
                    <span className="text-amber-500 font-bold text-lg mt-0.5">💡</span>
                    <span>{tip}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>

        {/* Subscribe CTA */}
        <section className="text-center p-10 bg-gradient-to-r from-red-600/20 via-orange-600/20 to-amber-600/20 rounded-2xl border border-red-500/30 mb-12">
          <Youtube className="w-12 h-12 mx-auto mb-4 text-red-500" />
          <h2 className="text-2xl font-bold text-white mb-3">Want More Lessons?</h2>
          <p className="text-lg text-zinc-300 mb-6 max-w-xl mx-auto">
            Subscribe to DadRock Tabs on YouTube for free guitar and bass lessons every week!
          </p>
          <a
            href={YOUTUBE_CHANNEL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 px-8 py-4 bg-red-600 hover:bg-red-500 rounded-full text-lg font-bold transition-all hover:scale-105"
          >
            <Youtube className="w-6 h-6" />
            Subscribe – It's Free!
          </a>
        </section>

        {/* Browse More Links */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link href="/top-lessons" className="text-amber-400 hover:text-amber-300 transition-colors font-medium">
            🏆 Top 10 Lessons
          </Link>
          <span className="text-zinc-700 hidden sm:inline">|</span>
          <Link href="/coming-soon" className="text-purple-400 hover:text-purple-300 transition-colors font-medium">
            📅 Coming Soon
          </Link>
          <span className="text-zinc-700 hidden sm:inline">|</span>
          <Link href="/" className="text-zinc-400 hover:text-white transition-colors font-medium">
            🏠 Back to Home
          </Link>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-12 py-8 border-t border-zinc-800">
        <div className="max-w-4xl mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <Link href="/" className="text-zinc-400 hover:text-white transition-colors">
              ← {t.backToHome}
            </Link>
            <p className="text-zinc-500 text-sm">
              {t.footer}
            </p>
            <a
              href={YOUTUBE_CHANNEL}
              target="_blank"
              rel="noopener noreferrer"
              className="text-zinc-400 hover:text-red-500 transition-colors"
            >
              <Youtube className="w-6 h-6" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
