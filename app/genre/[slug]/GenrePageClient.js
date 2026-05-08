'use client';

import Link from 'next/link';
import { Home, Music, Play, ArrowRight } from 'lucide-react';
import SearchBar from '@/components/SearchBar';
import { GENRES, ERAS } from '@/lib/genreData';

const LOGO_URL = "https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png";

export default function GenrePageClient({ genre, slug, artists, type = 'genre' }) {
  const allGenres = Object.entries(GENRES).map(([s, g]) => ({ slug: s, ...g, type: 'genre' }));
  const allEras = Object.entries(ERAS).map(([s, e]) => ({ slug: s, ...e, type: 'era' }));
  const totalLessons = artists.reduce((sum, a) => sum + a.lessonCount, 0);

  return (
    <div className="min-h-screen bg-zinc-950 text-white">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-zinc-950/90 backdrop-blur-md border-b border-zinc-800">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between gap-4">
            <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity flex-shrink-0">
              <img src={LOGO_URL} alt="DadRock Tabs" className="h-9 w-auto" />
              <span className="text-lg font-bold text-amber-500 hidden sm:block font-rock">DadRock Tabs</span>
            </Link>
            <div className="hidden md:block flex-1 max-w-sm mx-4">
              <SearchBar variant="compact" placeholder="Search artists & songs..." />
            </div>
            <Link 
              href="/"
              className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-full text-sm transition-colors"
            >
              <Home className="w-4 h-4" />
              <span className="hidden sm:inline">Home</span>
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Breadcrumb */}
        <nav className="mb-6 text-sm text-zinc-400">
          <Link href="/" className="hover:text-amber-500 transition-colors">Home</Link>
          <span className="mx-2">/</span>
          <span className="capitalize">{type === 'genre' ? 'Genres' : 'Eras'}</span>
          <span className="mx-2">/</span>
          <span className="text-white">{genre.name}</span>
        </nav>

        {/* Hero Section */}
        <div className="relative mb-10 p-8 sm:p-12 rounded-3xl overflow-hidden hero-gradient-bg">
          <div className="absolute top-0 right-0 w-64 h-64 bg-amber-500/5 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-48 h-48 bg-red-500/5 rounded-full blur-3xl" />
          
          <div className="relative z-10">
            <div className="flex flex-col sm:flex-row sm:items-end gap-4 sm:gap-8">
              <div className="flex-1">
                <div className="text-4xl mb-3">{genre.icon}</div>
                <p className="text-sm font-medium text-amber-500/80 uppercase tracking-widest mb-2">
                  {type === 'genre' ? 'Genre' : 'Era'} Collection
                </p>
                <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold font-rock text-gradient-gold neon-underline pb-2">
                  {genre.name}
                </h1>
                <p className="mt-4 text-zinc-300 text-lg max-w-2xl leading-relaxed">
                  {genre.description}
                </p>
              </div>
              <div className="flex items-center gap-4 flex-shrink-0">
                <div className="stat-badge px-5 py-3 rounded-2xl text-center">
                  <div className="text-3xl font-bold text-amber-500 font-rock">{artists.length}</div>
                  <div className="text-xs text-zinc-400 uppercase tracking-wider">Artists</div>
                </div>
                <div className="stat-badge px-5 py-3 rounded-2xl text-center">
                  <div className="text-3xl font-bold text-amber-500 font-rock">{totalLessons}</div>
                  <div className="text-xs text-zinc-400 uppercase tracking-wider">Lessons</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* About Section */}
        <div className="mb-10 p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800 section-accent">
          <p className="text-zinc-300 leading-relaxed text-lg">{genre.longDescription}</p>
        </div>

        {/* Artist Grid */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold mb-6 text-white flex items-center gap-2">
            <Music className="w-6 h-6 text-amber-500" />
            {genre.name} Artists
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
            {artists.map((artist, index) => (
              <Link
                key={artist.slug}
                href={`/artist/${artist.slug}`}
                className="group glow-card bg-zinc-900/80 rounded-xl border border-zinc-800 overflow-hidden card-enter"
                style={{ animationDelay: `${index * 0.05}s` }}
              >
                {/* Thumbnail */}
                <div className="relative h-40 overflow-hidden">
                  {artist.thumbnail ? (
                    <img
                      src={artist.thumbnail}
                      alt={`${artist.name} Guitar Tabs`}
                      className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                      loading="lazy"
                    />
                  ) : (
                    <div className={`w-full h-full bg-gradient-to-br ${genre.color} opacity-30`} />
                  )}
                  <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 via-zinc-900/50 to-transparent" />
                  
                  {/* Lesson count badge */}
                  <div className="absolute top-3 right-3 lesson-badge text-xs font-bold text-black px-2.5 py-1 rounded-lg">
                    {artist.lessonCount} lessons
                  </div>
                  
                  {/* Play icon */}
                  <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <div className="w-12 h-12 bg-amber-500 rounded-full flex items-center justify-center shadow-lg shadow-amber-500/30">
                      <Play className="w-6 h-6 text-black ml-0.5" fill="black" />
                    </div>
                  </div>
                </div>
                
                {/* Info */}
                <div className="p-4 flex items-center justify-between">
                  <div>
                    <h3 className="font-bold text-lg text-white group-hover:text-amber-500 transition-colors">
                      {artist.name}
                    </h3>
                    <p className="text-sm text-zinc-500">{artist.lessonCount} tab lessons</p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-zinc-600 group-hover:text-amber-500 group-hover:translate-x-1 transition-all" />
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Browse Other Genres/Eras */}
        <section className="mt-16 p-8 rounded-2xl border border-zinc-800 hero-gradient-bg relative overflow-hidden">
          <div className="relative z-10">
            <h2 className="text-2xl font-bold mb-6 text-white font-rock">
              Browse More {type === 'genre' ? 'Genres' : 'Eras'}
            </h2>
            <div className="flex flex-wrap gap-3">
              {(type === 'genre' ? allGenres : allEras)
                .filter(item => item.slug !== slug)
                .map(item => (
                  <Link
                    key={item.slug}
                    href={`/${item.type}/${item.slug}`}
                    className="group/pill flex items-center gap-2 px-5 py-3 bg-zinc-800/80 hover:bg-amber-500 rounded-full font-medium transition-all border border-zinc-700 hover:border-amber-500 hover:text-black hover:shadow-lg hover:shadow-amber-500/20"
                  >
                    <span>{item.icon}</span>
                    {item.name}
                  </Link>
                ))}
            </div>
            
            {/* Also show the other type */}
            <h3 className="text-xl font-bold mt-8 mb-4 text-white font-rock">
              Browse by {type === 'genre' ? 'Era' : 'Genre'}
            </h3>
            <div className="flex flex-wrap gap-3">
              {(type === 'genre' ? allEras : allGenres).map(item => (
                <Link
                  key={item.slug}
                  href={`/${item.type}/${item.slug}`}
                  className="group/pill flex items-center gap-2 px-5 py-3 bg-zinc-800/80 hover:bg-amber-500 rounded-full font-medium transition-all border border-zinc-700 hover:border-amber-500 hover:text-black hover:shadow-lg hover:shadow-amber-500/20"
                >
                  <span>{item.icon}</span>
                  {item.name}
                </Link>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-zinc-800">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-zinc-500 text-sm">© {new Date().getFullYear()} DadRock Tabs. Free guitar & bass lessons.</p>
            <Link href="/" className="text-zinc-500 hover:text-amber-500 transition-colors text-sm">Home</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
