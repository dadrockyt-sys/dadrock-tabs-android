'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Calendar, Clock, Music, Youtube, Home, Facebook, Twitter, Share2, Mail, ExternalLink } from 'lucide-react';

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";
const YOUTUBE_CHANNEL = 'https://www.youtube.com/@dadrocktabs';

// Convert artist name to URL slug
function artistToSlug(artist) {
  if (!artist) return '';
  
  // Clean up artist name (remove trailing dash, etc.)
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
    'REO Speedwagon': 'reo-speedwagon',
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
    'Green Day': 'green-day',
    'Red Hot Chilli Peppers': 'red-hot-chilli-peppers',
    'Red Hot Chili Peppers': 'red-hot-chili-peppers',
    'Rage Against The Machine': 'rage-against-the-machine',
  };
  
  if (specialSlugs[cleanArtist]) {
    return specialSlugs[cleanArtist];
  }
  
  return cleanArtist.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/-+/g, '-').replace(/^-|-$/g, '');
}

export default function ComingSoonClient({ initialVideos, initialTotal }) {
  const [upcomingVideos, setUpcomingVideos] = useState(initialVideos || []);
  const [total, setTotal] = useState(initialTotal || 0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Refresh videos on mount to get latest
  useEffect(() => {
    const refreshVideos = async () => {
      try {
        const res = await fetch('/api/upcoming');
        if (res.ok) {
          const data = await res.json();
          setUpcomingVideos(data.upcoming || []);
          setTotal(data.total || 0);
        }
      } catch (err) {
        console.error('Failed to refresh upcoming videos:', err);
      }
    };
    refreshVideos();
  }, []);

  // Share URLs
  const shareUrl = 'https://dadrocktabs.com/coming-soon';
  const shareText = 'Check out the upcoming guitar lessons at DadRock Tabs! 🎸';
  
  const facebookShareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(shareUrl)}`;
  const twitterShareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(shareUrl)}&text=${encodeURIComponent(shareText)}`;
  const emailShareUrl = `mailto:?subject=${encodeURIComponent('Upcoming Guitar Lessons - DadRock Tabs')}&body=${encodeURIComponent(`${shareText}\n\n${shareUrl}`)}`;

  // Clean artist name for display
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
          <div className="text-center mb-8">
            <Link href="/">
              <img 
                src={LOGO_URL} 
                alt="DadRock Tabs - Free Guitar and Bass Tabs" 
                className="max-w-md mx-auto w-full drop-shadow-2xl hover:scale-105 transition-transform duration-300"
              />
            </Link>
          </div>

          {/* Page Title */}
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-4 bg-gradient-to-r from-amber-400 via-orange-500 to-red-500 bg-clip-text text-transparent">
              Upcoming Guitar Lessons
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              See what classic rock and heavy metal songs are coming to DadRock Tabs. 
              Subscribe to never miss a lesson!
            </p>
            <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-purple-600/20 border border-purple-500/30 rounded-full">
              <Calendar className="w-5 h-5 text-purple-400" />
              <span className="text-purple-300 font-medium">{total} Lessons Scheduled</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 py-12">
        {/* Upcoming Videos Grid */}
        {upcomingVideos.length === 0 ? (
          <div className="text-center py-16">
            <Calendar className="w-20 h-20 mx-auto mb-6 text-zinc-600" />
            <h2 className="text-2xl font-bold text-zinc-400 mb-2">No Upcoming Lessons Scheduled</h2>
            <p className="text-zinc-500 mb-8">Check back soon for new content!</p>
            <a
              href={YOUTUBE_CHANNEL}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-500 rounded-full font-bold transition-colors"
            >
              <Youtube className="w-5 h-5" />
              Subscribe for Updates
            </a>
          </div>
        ) : (
          <div className="grid gap-6">
            {upcomingVideos.map((video, index) => {
              const artistSlug = artistToSlug(video.artist);
              const cleanArtist = cleanArtistName(video.artist);
              
              return (
                <article 
                  key={video.id} 
                  className="flex flex-col md:flex-row gap-6 p-6 bg-zinc-900/80 rounded-2xl border border-zinc-800 hover:border-zinc-700 transition-all group"
                >
                  {/* Thumbnail */}
                  <div className="flex-shrink-0 w-full md:w-64 h-40 rounded-xl overflow-hidden bg-zinc-800">
                    {video.thumbnail ? (
                      <img 
                        src={video.thumbnail}
                        alt={`${video.title} by ${cleanArtist} - Guitar Tab Lesson`}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        onError={(e) => {
                          e.target.style.display = 'none';
                          e.target.nextSibling.style.display = 'flex';
                        }}
                      />
                    ) : null}
                    <div 
                      className="w-full h-full bg-gradient-to-br from-purple-600/30 to-zinc-800 items-center justify-center"
                      style={{ display: video.thumbnail ? 'none' : 'flex' }}
                    >
                      <div className="text-center">
                        <Music className="w-10 h-10 text-purple-400 mx-auto" />
                        <span className="text-sm text-purple-300 mt-2 block">Coming Soon</span>
                      </div>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div>
                        <h2 className="text-2xl font-bold text-white mb-1 group-hover:text-amber-400 transition-colors">
                          {video.title}
                        </h2>
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
                      <div className="flex-shrink-0 hidden md:block">
                        <span className="inline-flex items-center gap-1 px-3 py-1 bg-purple-600/20 border border-purple-500/30 rounded-full text-purple-300 text-sm font-medium">
                          #{index + 1}
                        </span>
                      </div>
                    </div>

                    {/* Scheduled Date */}
                    <div className="mt-4 flex items-center gap-2 text-purple-400">
                      <Clock className="w-5 h-5" />
                      <time dateTime={video.scheduled_date} className="font-medium">
                        {new Date(video.scheduled_date).toLocaleDateString('en-US', {
                          weekday: 'long',
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </time>
                    </div>

                    {/* Description */}
                    {video.description && (
                      <p className="mt-3 text-zinc-500 text-sm line-clamp-2">
                        {video.description}
                      </p>
                    )}
                  </div>
                </article>
              );
            })}
          </div>
        )}

        {/* Social Share Section */}
        <section className="mt-16 p-8 bg-zinc-900/50 rounded-2xl border border-zinc-800 text-center">
          <h2 className="text-2xl font-bold text-white mb-4 flex items-center justify-center gap-2">
            <Share2 className="w-6 h-6 text-amber-500" />
            Share the Schedule
          </h2>
          <p className="text-zinc-400 mb-6">
            Know someone who would love these upcoming lessons? Share the schedule with them!
          </p>
          <div className="flex items-center justify-center gap-4 flex-wrap">
            <a
              href={facebookShareUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 rounded-full font-medium transition-colors"
            >
              <Facebook className="w-5 h-5" />
              Share on Facebook
            </a>
            <a
              href={twitterShareUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-6 py-3 bg-sky-500 hover:bg-sky-400 rounded-full font-medium transition-colors"
            >
              <Twitter className="w-5 h-5" />
              Share on Twitter
            </a>
            <a
              href={emailShareUrl}
              className="flex items-center gap-2 px-6 py-3 bg-zinc-700 hover:bg-zinc-600 rounded-full font-medium transition-colors"
            >
              <Mail className="w-5 h-5" />
              Share via Email
            </a>
          </div>
        </section>

        {/* SEO Content Section */}
        <section className="mt-16 p-8 bg-zinc-900/50 rounded-2xl border border-zinc-800">
          <h2 className="text-3xl font-bold text-amber-500 mb-6">
            About DadRock Tabs Upcoming Lessons Schedule
          </h2>
          <div className="prose prose-invert prose-lg max-w-none text-zinc-300 space-y-4">
            <p>
              Welcome to the DadRock Tabs upcoming lessons schedule – your preview of the latest guitar and bass 
              tablature tutorials coming to our channel. We specialize in teaching classic rock, heavy metal, 
              hair metal, and blues songs from the greatest era of rock music. Our schedule is regularly updated 
              with new lessons featuring legendary artists like Van Halen, Metallica, AC/DC, Led Zeppelin, 
              Black Sabbath, Ozzy Osbourne, Def Leppard, Iron Maiden, Judas Priest, and many more iconic bands.
            </p>
            <p>
              Every lesson on DadRock Tabs is completely free and designed to help guitarists and bass players 
              of all skill levels master their favorite songs. Whether you're a beginner looking to learn your 
              first power chord riff or an experienced player wanting to tackle complex solos, our step-by-step 
              video tutorials break down every note, technique, and nuance so you can play along with confidence. 
              We cover everything from simple rhythm parts to intricate lead guitar work and thundering bass lines.
            </p>
            <p>
              The "Coming Soon" schedule above shows all the lessons we have queued up and ready to release. 
              Each entry includes the song title, artist name, and exact release date and time so you know 
              exactly when to tune in. Click on any artist name to explore our existing library of tutorials 
              for that band – chances are we already have dozens of lessons ready for you to learn right now!
            </p>
            <p>
              Don't miss a single lesson! Subscribe to the DadRock Tabs YouTube channel and turn on notifications 
              to get alerted the moment each new tutorial goes live. Our community of rock guitarists spans the 
              globe, united by our love for the timeless music that defined generations. Join us and keep the 
              spirit of classic rock alive – one riff at a time.
            </p>
            <p>
              DadRock Tabs is more than just a guitar lesson channel – it's a celebration of the music that 
              dads everywhere have been passing down to their kids for decades. From the explosive energy of 
              80s hair metal to the raw power of 70s hard rock, from the precision of thrash metal to the 
              soulful bends of blues rock, we cover it all. Bookmark this page and check back regularly to 
              see what's coming next. Your next favorite song to learn might be just days away!
            </p>
          </div>
        </section>

        {/* Subscribe CTA */}
        <section className="mt-16 text-center p-12 bg-gradient-to-r from-red-600/20 via-orange-600/20 to-amber-600/20 rounded-2xl border border-red-500/30">
          <Youtube className="w-16 h-16 mx-auto mb-6 text-red-500" />
          <h2 className="text-3xl font-bold text-white mb-4">
            Never Miss a Lesson
          </h2>
          <p className="text-xl text-zinc-300 mb-8 max-w-2xl mx-auto">
            Subscribe to DadRock Tabs on YouTube and turn on notifications to get alerted 
            the moment each new guitar lesson goes live!
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
