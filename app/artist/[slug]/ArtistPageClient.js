'use client';

import { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Youtube, Music, Home } from 'lucide-react';

const LOGO_URL = "https://i.imgur.com/6hOgR0D.png";

export default function ArtistPageClient({ artistName, videos, slug }) {
  const [selectedVideo, setSelectedVideo] = useState(null);

  // Get YouTube embed URL
  const getEmbedUrl = (video) => {
    if (video.video_id) {
      return `https://www.youtube.com/embed/${video.video_id}`;
    }
    return video.youtube_url?.replace('watch?v=', 'embed/') || '';
  };

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
            <Link 
              href="/"
              className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-full text-sm transition-colors"
            >
              <Home className="w-4 h-4" />
              <span>Home</span>
            </Link>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Breadcrumb */}
        <nav className="mb-6 text-sm text-zinc-400">
          <Link href="/" className="hover:text-amber-500 transition-colors">Home</Link>
          <span className="mx-2">/</span>
          <span className="text-white">{artistName}</span>
        </nav>

        {/* Artist Header */}
        <div className="mb-10">
          <h1 className="text-4xl sm:text-5xl font-bold mb-4 font-rock">
            <span className="text-amber-500">{artistName}</span>
            <span className="text-white"> Guitar & Bass Tabs</span>
          </h1>
          <p className="text-lg text-zinc-300 max-w-3xl leading-relaxed">
            Learn how to play songs by <strong>{artistName}</strong> with step-by-step guitar and bass tutorials. 
            These riffs are some of the most recognizable classic rock riffs ever written and are perfect for 
            beginner and intermediate players.
          </p>
          <p className="mt-4 text-amber-500 font-semibold">
            <Music className="w-5 h-5 inline mr-2" />
            {videos.length} lesson{videos.length !== 1 ? 's' : ''} available
          </p>
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
          {selectedVideo ? 'More Lessons' : 'Watch Full Lessons Below'}
        </h2>

        {/* Video Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {videos.map((video) => (
            <div
              key={video.id || video.video_id}
              className={`group bg-zinc-900/80 rounded-xl border border-zinc-800 overflow-hidden hover:border-amber-500/50 transition-all cursor-pointer ${
                selectedVideo?.id === video.id ? 'ring-2 ring-amber-500' : ''
              }`}
              onClick={() => setSelectedVideo(video)}
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

        {/* SEO Content Section */}
        <section className="mt-16 p-8 bg-zinc-900/50 rounded-2xl border border-zinc-800">
          <h2 className="text-2xl font-bold mb-4 text-amber-500">
            About {artistName} Guitar Tabs
          </h2>
          <div className="text-zinc-300 space-y-4">
            <p>
              Looking to learn {artistName} songs on guitar or bass? You've come to the right place! 
              DadRock Tabs offers free video tutorials that break down every riff, chord, and solo 
              so you can master your favorite {artistName} tracks.
            </p>
            <p>
              Whether you're a beginner just starting out or an intermediate player looking to expand 
              your repertoire, our step-by-step lessons make it easy to learn at your own pace. 
              Each tutorial includes detailed tablature and demonstrations to help you nail every note.
            </p>
            <p>
              Start learning {artistName} today and add some classic rock to your playing! 🎸
            </p>
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
          <p>© 2026 DadRock Tabs. Made with ❤️ for rock lovers.</p>
          <div className="mt-4 flex justify-center gap-6">
            <Link href="/" className="hover:text-amber-500 transition-colors">Home</Link>
            <a 
              href="https://youtube.com/@dadrockytofficial" 
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
