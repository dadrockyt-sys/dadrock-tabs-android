'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Trophy, Eye, ThumbsUp, Play, Youtube, Home, Facebook, Twitter, Mail, ExternalLink, Music } from 'lucide-react';

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";
const YOUTUBE_CHANNEL = 'https://www.youtube.com/@dadrocktabs';

// Convert artist name to URL slug
function artistToSlug(artist) {
  if (!artist) return '';
  
  const cleanArtist = artist.replace(/ -$/, '').trim();
  
  const specialSlugs = {
    'AC/DC': 'acdc',
    "Guns N' Roses": 'guns-n-roses',
    'Guns N Roses': 'guns-n-roses',
    'Mötley Crüe': 'motley-crue',
    'Motley Crue': 'motley-crue',
    'Motörhead': 'motorhead',
    'Motorhead': 'motorhead',
    'Blue Öyster Cult': 'blue-oyster-cult',
    'Blue Oyster Cult': 'blue-oyster-cult',
    "Jane's Addiction": 'janes-addiction',
    'ZZ Top': 'zz-top',
    'UFO': 'ufo',
    'Van Halen': 'van-halen',
    'Led Zeppelin': 'led-zeppelin',
    'Black Sabbath': 'black-sabbath',
    'Iron Maiden': 'iron-maiden',
    'Judas Priest': 'judas-priest',
    'Deep Purple': 'deep-purple',
    'Ozzy Osbourne': 'ozzy-osbourne',
    'Def Leppard': 'def-leppard',
    'Bon Jovi': 'bon-jovi',
    'Thin Lizzy': 'thin-lizzy',
  };
  
  if (specialSlugs[cleanArtist]) {
    return specialSlugs[cleanArtist];
  }
  
  return cleanArtist.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
}

// Format view count
function formatViewCount(count) {
  if (count >= 1000000) {
    return (count / 1000000).toFixed(1) + 'M';
  }
  if (count >= 1000) {
    return (count / 1000).toFixed(1) + 'K';
  }
  return count.toString();
}

export default function TopLessonsClient({ initialVideos }) {
  const [videos, setVideos] = useState(initialVideos || []);
  const [isLoading, setIsLoading] = useState(!initialVideos || initialVideos.length === 0);
  const [error, setError] = useState(null);

  // Refresh videos on mount
  useEffect(() => {
    const refreshVideos = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const res = await fetch('/api/top-videos?limit=10');
        if (res.ok) {
          const data = await res.json();
          setVideos(data.videos || []);
        } else {
          setError('Unable to load top lessons. Please check the admin panel to configure them.');
        }
      } catch (err) {
        console.error('Failed to refresh top videos:', err);
        setError('Unable to load top lessons. Please try again later.');
      } finally {
        setIsLoading(false);
      }
    };
    refreshVideos();
  }, []);

  // Share URLs
  const shareUrl = 'https://dadrocktabs.com/top-lessons';
  const shareText = 'Check out the most popular guitar lessons at DadRock Tabs! 🎸🔥';
  
  const facebookShareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
  const twitterShareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`;
  const emailShareUrl = `mailto:?subject=${encodeURIComponent('Top Guitar Lessons - DadRock Tabs')}&body=${encodeURIComponent(`${shareText}\n\n${shareUrl}`)}`;

  // Clean artist name
  const cleanArtistName = (artist) => {
    if (!artist) return 'Various Artists';
    return artist.replace(/ -$/, '').trim();
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 text-white">
      {/* Header with Logo */}
      <header className="relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMtNi42MjcgMC0xMiA1LjM3My0xMiAxMnM1LjM3MyAxMiAxMiAxMiAxMi01LjM3MyAxMi0xMi01LjM3My0xMi0xMi0xMnptMCAxOGMtMy4zMTQgMC02LTIuNjg2LTYtNnMyLjY4Ni02IDYtNiA2IDIuNjg2IDYgNi0yLjY4NiA2LTYgNnoiIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iLjAyIi8+PC9nPjwvc3ZnPg==')] opacity-30"></div>
        
        <div className="max-w-6xl mx-auto px-4 py-8">
          {/* Navigation */}
          <nav className="flex items-center justify-between mb-8">
            <Link href="/" className="flex items-center gap-2 text-zinc-400 hover:text-white transition-colors">
              <Home className="w-5 h-5" />
              <span>Back to Home</span>
            </Link>
            <a
              href={YOUTUBE_CHANNEL}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-4 py-2 bg-red-600 hover:bg-red-500 rounded-full font-medium transition-colors"
            >
              <Youtube className="w-5 h-5" />
              Subscribe
            </a>
          </nav>

          {/* Logo */}
          <div className="text-center mb-6">
            <Link href="/">
              <img 
                src={LOGO_URL} 
                alt="DadRock Tabs - Free Guitar and Bass Tabs" 
                className="max-w-md mx-auto w-full drop-shadow-2xl hover:scale-105 transition-transform duration-300"
              />
            </Link>
          </div>

          {/* Social Share - Prominent Position */}
          <div className="flex items-center justify-center gap-3 mb-8">
            <span className="text-zinc-400 text-sm font-medium">Share:</span>
            <a
              href={facebookShareUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center w-10 h-10 bg-blue-600 hover:bg-blue-500 rounded-full transition-all hover:scale-110"
              title="Share on Facebook"
            >
              <Facebook className="w-5 h-5" />
            </a>
            <a
              href={twitterShareUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center w-10 h-10 bg-sky-500 hover:bg-sky-400 rounded-full transition-all hover:scale-110"
              title="Share on Twitter"
            >
              <Twitter className="w-5 h-5" />
            </a>
            <a
              href={emailShareUrl}
              className="flex items-center justify-center w-10 h-10 bg-zinc-700 hover:bg-zinc-600 rounded-full transition-all hover:scale-110"
              title="Share via Email"
            >
              <Mail className="w-5 h-5" />
            </a>
          </div>

          {/* Page Title */}
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-amber-400 via-orange-500 to-red-500 bg-clip-text text-transparent flex items-center justify-center gap-3">
              <Trophy className="w-10 h-10 text-amber-500" />
              Top 10 Most Viewed Lessons
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              Our most popular guitar and bass tutorials that rock fans love. 
              Start with the hits!
            </p>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-12">
        {/* Top Videos Grid */}
        {isLoading ? (
          <div className="text-center py-16">
            <Trophy className="w-20 h-20 mx-auto mb-6 text-zinc-600 animate-pulse" />
            <h2 className="text-2xl font-bold text-zinc-400 mb-2">Loading Top Lessons...</h2>
            <p className="text-zinc-500">Please wait while we fetch the most viewed videos.</p>
          </div>
        ) : error ? (
          <div className="text-center py-16">
            <Trophy className="w-20 h-20 mx-auto mb-6 text-zinc-600" />
            <h2 className="text-2xl font-bold text-zinc-400 mb-2">Top Lessons Coming Soon</h2>
            <p className="text-zinc-500 mb-6">Our most popular lessons are being configured.</p>
            <p className="text-zinc-600 text-sm mb-8">{error}</p>
            <a
              href={YOUTUBE_CHANNEL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-500 rounded-full font-bold transition-colors"
            >
              <Youtube className="w-5 h-5" />
              Visit Our YouTube Channel
            </a>
          </div>
        ) : videos.length === 0 ? (
          <div className="text-center py-16">
            <Trophy className="w-20 h-20 mx-auto mb-6 text-zinc-600" />
            <h2 className="text-2xl font-bold text-zinc-400 mb-2">No Top Lessons Configured</h2>
            <p className="text-zinc-500 mb-6">Check back soon for our most popular lessons!</p>
            <a
              href={YOUTUBE_CHANNEL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-500 rounded-full font-bold transition-colors"
            >
              <Youtube className="w-5 h-5" />
              Visit Our YouTube Channel
            </a>
          </div>
        ) : (
          <div className="grid gap-6">
            {videos.map((video, index) => {
              const artistSlug = artistToSlug(video.artist);
              const cleanArtist = cleanArtistName(video.artist);
              const youtubeUrl = `https://www.youtube.com/watch?v=${video.videoId}`;
              
              // Medal colors for top 3
              const medalColors = ['text-amber-400', 'text-zinc-300', 'text-orange-600'];
              const bgColors = ['bg-amber-500/10 border-amber-500/30', 'bg-zinc-400/10 border-zinc-400/30', 'bg-orange-600/10 border-orange-600/30'];
              
              return (
                <article 
                  key={video.id} 
                  className={`flex flex-col md:flex-row gap-6 p-6 rounded-2xl border transition-all group hover:scale-[1.01] ${
                    index < 3 ? bgColors[index] : 'bg-zinc-900/80 border-zinc-800 hover:border-zinc-700'
                  }`}
                >
                  {/* Rank Badge */}
                  <div className="flex-shrink-0 flex items-center justify-center">
                    <div className={`w-16 h-16 rounded-full flex items-center justify-center text-2xl font-bold ${
                      index < 3 ? `${medalColors[index]} bg-zinc-900` : 'text-zinc-500 bg-zinc-800'
                    }`}>
                      {index === 0 && '🥇'}
                      {index === 1 && '🥈'}
                      {index === 2 && '🥉'}
                      {index > 2 && `#${index + 1}`}
                    </div>
                  </div>

                  {/* Thumbnail */}
                  <a 
                    href={youtubeUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex-shrink-0 w-full md:w-72 aspect-video rounded-xl overflow-hidden bg-zinc-800 relative group/thumb"
                  >
                    {video.thumbnail ? (
                      <img 
                        src={video.thumbnail}
                        alt={`${video.title} by ${cleanArtist} - Guitar Tab Lesson`}
                        className="w-full h-full object-contain bg-black group-hover/thumb:scale-105 transition-transform duration-300"
                      />
                    ) : (
                      <div className="w-full h-full bg-gradient-to-br from-amber-600/30 to-zinc-800 flex items-center justify-center">
                        <Music className="w-10 h-10 text-amber-400" />
                      </div>
                    )}
                    {/* Play overlay */}
                    <div className="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover/thumb:opacity-100 transition-opacity">
                      <Play className="w-16 h-16 text-white" fill="white" />
                    </div>
                  </a>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <a 
                          href={youtubeUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="block"
                        >
                          <h2 className="text-2xl font-bold text-white mb-1 group-hover:text-amber-400 transition-colors">
                            {video.title}
                          </h2>
                        </a>
                        <div className="flex items-center gap-3 flex-wrap">
                          <span className="text-lg text-zinc-400">{cleanArtist}</span>
                          {artistSlug && (
                            <Link
                              href={`/artist/${artistSlug}`}
                              className="inline-flex items-center gap-1 text-sm text-amber-500 hover:text-amber-400 transition-colors"
                            >
                              <ExternalLink className="w-4 h-4" />
                              View all {cleanArtist} tabs
                            </Link>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="mt-4 flex items-center gap-6 flex-wrap">
                      <div className="flex items-center gap-2 text-amber-400">
                        <Eye className="w-5 h-5" />
                        <span className="font-bold text-lg">{formatViewCount(video.viewCount)}</span>
                        <span className="text-zinc-500 text-sm">views</span>
                      </div>
                      {video.likeCount > 0 && (
                        <div className="flex items-center gap-2 text-green-400">
                          <ThumbsUp className="w-5 h-5" />
                          <span className="font-bold">{formatViewCount(video.likeCount)}</span>
                          <span className="text-zinc-500 text-sm">likes</span>
                        </div>
                      )}
                    </div>

                    {/* Watch Button */}
                    <div className="mt-4">
                      <a
                        href={youtubeUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center gap-2 px-5 py-2 bg-red-600 hover:bg-red-500 rounded-full font-medium transition-colors"
                      >
                        <Play className="w-4 h-4" fill="currentColor" />
                        Watch Lesson
                      </a>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        )}

        {/* SEO Content Section */}
        <section className="mt-16 p-8 bg-zinc-900/50 rounded-2xl border border-zinc-800">
          <h2 className="text-3xl font-bold text-amber-500 mb-6">
            About DadRock Tabs Top Guitar Lessons
          </h2>
          <div className="prose prose-invert prose-lg max-w-none text-zinc-300 space-y-4">
            <p>
              Welcome to the DadRock Tabs hall of fame – our top 10 most-viewed guitar and bass lessons of all time! 
              These tutorials have resonated with thousands of guitarists worldwide, becoming the go-to resources 
              for learning iconic classic rock and heavy metal songs. From face-melting solos to thundering bass 
              lines, these lessons represent the best of what DadRock Tabs has to offer.
            </p>
            <p>
              Each lesson in our top 10 has been watched, rewatched, and mastered by guitarists at every skill level. 
              These aren't just any songs – they're the tracks that define classic rock and heavy metal: the riffs 
              that made legends, the solos that inspired generations, and the grooves that get your head banging. 
              Artists like Van Halen, Metallica, AC/DC, Led Zeppelin, Black Sabbath, and Ozzy Osbourne are heavily 
              featured because their music is timeless.
            </p>
            <p>
              What makes these lessons so popular? It's our step-by-step approach that breaks down complex parts 
              into manageable chunks. Whether you're tackling your first power chord or perfecting a sweep-picked 
              arpeggio, our video tutorials guide you through every note with clear demonstrations and on-screen 
              tablature. Plus, they're completely free – no subscriptions, no paywalls, just pure rock education.
            </p>
            <p>
              If you're new to DadRock Tabs, starting with our most-viewed lessons is a great way to dive in. 
              These songs are popular for a reason – they're fun to play, they sound impressive, and they'll 
              build your skills for more challenging material. Many of our viewers return to these lessons 
              multiple times as they improve, discovering new nuances and techniques with each viewing.
            </p>
            <p>
              Don't forget to subscribe to our YouTube channel to stay updated when new lessons drop. Who knows – 
              the next video we upload might become a future top 10 contender! In the meantime, grab your guitar, 
              crank up your amp, and start learning from the best. These are the lessons that made DadRock Tabs 
              what it is today, and we're proud to share them with rock guitarists around the world.
            </p>
          </div>
        </section>

        {/* Subscribe CTA */}
        <section className="mt-16 text-center p-12 bg-gradient-to-r from-red-600/20 via-orange-600/20 to-amber-600/20 rounded-2xl border border-red-500/30">
          <Youtube className="w-16 h-16 mx-auto mb-6 text-red-500" />
          <h2 className="text-3xl font-bold text-white mb-4">
            Want More Lessons Like These?
          </h2>
          <p className="text-xl text-zinc-300 mb-8 max-w-2xl mx-auto">
            Subscribe to DadRock Tabs on YouTube and join thousands of guitarists 
            learning classic rock and metal!
          </p>
          <a
            href={YOUTUBE_CHANNEL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 px-8 py-4 bg-red-600 hover:bg-red-500 rounded-full text-xl font-bold transition-all hover:scale-105"
          >
            <Youtube className="w-7 h-7" />
            Subscribe Now – It's Free!
          </a>
        </section>
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-zinc-800">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <Link href="/" className="text-zinc-400 hover:text-white transition-colors">
              ← Back to DadRock Tabs Home
            </Link>
            <p className="text-zinc-500 text-sm">
              © {new Date().getFullYear()} DadRock Tabs. Made with ❤️ for rock lovers.
            </p>
            <div className="flex items-center gap-4">
              <Link href="/coming-soon" className="text-zinc-400 hover:text-purple-400 transition-colors">
                Coming Soon
              </Link>
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
        </div>
      </footer>
    </div>
  );
}
