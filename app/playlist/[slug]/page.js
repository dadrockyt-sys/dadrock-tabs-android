import { PLAYLISTS } from '@/lib/playlistData';
import { notFound } from 'next/navigation';
import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';
import Link from 'next/link';

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const playlist = PLAYLISTS[slug];
  if (!playlist) return { title: 'Not Found | DadRock Tabs' };

  return {
    title: `${playlist.name} - Curated Guitar Tab Collection | DadRock Tabs`,
    description: playlist.description,
    keywords: `${playlist.name.toLowerCase()}, guitar playlist, curated guitar tabs, ${playlist.difficulty.toLowerCase()} guitar songs, rock guitar collection`,
    openGraph: {
      title: `${playlist.name} - Curated Guitar Tab Collection`,
      description: playlist.description,
      type: 'website',
      url: `https://dadrocktabs.com/playlist/${slug}`,
      siteName: 'DadRock Tabs',
      images: [{ url: `https://dadrocktabs.com/api/og?title=${encodeURIComponent(playlist.name)}&type=genre`, width: 1200, height: 630 }],
    },
  };
}

export function generateStaticParams() {
  return Object.keys(PLAYLISTS).map(slug => ({ slug }));
}

export default async function PlaylistPage({ params }) {
  const { slug } = await params;
  const playlist = PLAYLISTS[slug];

  if (!playlist) {
    notFound();
  }

  const db = await getDb();
  const matchedSongs = [];

  // Try to match each song hint against the database
  for (const item of playlist.songs) {
    const escapedArtist = item.artist.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const escapedHint = item.songHint.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    // Try to find in song_pages first
    const song = await db.collection('song_pages').findOne({
      artist: { $regex: new RegExp(escapedArtist, 'i') },
      title: { $regex: new RegExp(escapedHint, 'i') },
    });

    if (song) {
      matchedSongs.push({
        slug: song.slug,
        title: song.title,
        artist: song.artist?.replace(/ -$/, '').trim() || item.artist,
        thumbnail: song.thumbnail,
        videoId: song.videoId,
        duration: song.duration || 0,
      });
    } else {
      // Fallback: find in videos collection
      const video = await db.collection('videos').findOne({
        artist: { $regex: new RegExp(escapedArtist, 'i') },
        $or: [
          { song: { $regex: new RegExp(escapedHint, 'i') } },
          { title: { $regex: new RegExp(escapedHint, 'i') } },
        ],
      });

      if (video) {
        const artistSlug = artistToSlug(video.artist);
        matchedSongs.push({
          slug: null, // no song page, link to artist
          artistSlug,
          title: video.song || video.title || item.songHint,
          artist: video.artist?.replace(/ -$/, '').trim() || item.artist,
          thumbnail: video.thumbnail,
          duration: video.duration || 0,
        });
      }
    }
  }

  const totalDuration = matchedSongs.reduce((sum, s) => sum + (s.duration || 0), 0);
  const durationMin = Math.floor(totalDuration / 60);

  // JSON-LD ItemList schema
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'ItemList',
    'name': playlist.name,
    'description': playlist.description,
    'url': `https://dadrocktabs.com/playlist/${slug}`,
    'numberOfItems': matchedSongs.length,
    'itemListElement': matchedSongs.map((song, i) => ({
      '@type': 'ListItem',
      'position': i + 1,
      'item': {
        '@type': 'MusicRecording',
        'name': song.title,
        'byArtist': { '@type': 'MusicGroup', 'name': song.artist },
        'url': song.slug
          ? `https://dadrocktabs.com/songs/${song.slug}`
          : `https://dadrocktabs.com/artist/${song.artistSlug}`,
      }
    })),
  };

  const otherPlaylists = Object.entries(PLAYLISTS)
    .filter(([s]) => s !== slug)
    .map(([s, p]) => ({ slug: s, ...p }));

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <div className="min-h-screen bg-zinc-950 text-white">
        {/* Header */}
        <header className="sticky top-0 z-50 bg-zinc-950/90 backdrop-blur-md border-b border-zinc-800">
          <div className="container mx-auto px-4 py-3 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
              <img
                src="https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png"
                alt="DadRock Tabs"
                className="h-9 w-auto"
              />
              <span className="text-lg font-bold text-amber-500 hidden sm:block">DadRock Tabs</span>
            </Link>
            <Link
              href="/"
              className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-full text-sm transition-colors"
            >
              Home
            </Link>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8 max-w-4xl">
          {/* Breadcrumb */}
          <nav className="mb-6 text-sm text-zinc-400">
            <Link href="/" className="hover:text-amber-500 transition-colors">Home</Link>
            <span className="mx-2">/</span>
            <span className="text-white">{playlist.name}</span>
          </nav>

          {/* Hero */}
          <div className="relative mb-8 p-8 sm:p-10 rounded-3xl overflow-hidden bg-zinc-900/50 border border-zinc-800">
            <div className={`absolute inset-0 bg-gradient-to-br ${playlist.color} opacity-10`} />
            <div className="relative">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-4xl">{playlist.icon}</span>
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                  playlist.difficulty === 'Beginner' ? 'bg-green-500/20 text-green-400' :
                  playlist.difficulty === 'Intermediate' ? 'bg-amber-500/20 text-amber-400' :
                  'bg-red-500/20 text-red-400'
                }`}>
                  {playlist.difficulty}
                </span>
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-3">{playlist.name}</h1>
              <p className="text-zinc-300 text-lg max-w-2xl leading-relaxed mb-4">{playlist.description}</p>
              <div className="flex items-center gap-4 text-sm text-zinc-500">
                <span>{matchedSongs.length} songs</span>
                {durationMin > 0 && <span>• ~{durationMin} min total</span>}
              </div>
            </div>
          </div>

          {/* Song List */}
          <section className="mb-12">
            <div className="space-y-3">
              {matchedSongs.map((song, index) => {
                const href = song.slug ? `/songs/${song.slug}` : `/artist/${song.artistSlug}`;
                return (
                  <Link
                    key={index}
                    href={href}
                    className="group flex items-center gap-4 p-4 bg-zinc-900/60 rounded-xl border border-zinc-800 hover:border-amber-500/50 hover:bg-zinc-900 transition-all"
                  >
                    {/* Track number */}
                    <div className="w-8 text-center text-zinc-500 font-mono text-sm group-hover:text-amber-500 transition-colors flex-shrink-0">
                      {index + 1}
                    </div>

                    {/* Thumbnail */}
                    {song.thumbnail && (
                      <div className="w-16 h-12 rounded-lg overflow-hidden flex-shrink-0">
                        <img
                          src={song.thumbnail}
                          alt={song.title}
                          className="w-full h-full object-cover"
                          loading="lazy"
                        />
                      </div>
                    )}

                    {/* Song info */}
                    <div className="flex-1 min-w-0">
                      <h3 className="font-medium text-white group-hover:text-amber-500 transition-colors truncate">
                        {song.title}
                      </h3>
                      <p className="text-sm text-zinc-500 truncate">{song.artist}</p>
                    </div>

                    {/* Duration */}
                    {song.duration > 0 && (
                      <span className="text-xs text-zinc-600 flex-shrink-0">
                        {Math.floor(song.duration / 60)}:{String(song.duration % 60).padStart(2, '0')}
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          </section>

          {/* More Playlists */}
          <section className="mt-12 p-8 rounded-2xl border border-zinc-800 bg-zinc-900/30">
            <h2 className="text-xl font-bold mb-4">More Curated Collections</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {otherPlaylists.map(p => (
                <Link
                  key={p.slug}
                  href={`/playlist/${p.slug}`}
                  className="group flex items-center gap-3 p-4 bg-zinc-800/50 rounded-xl border border-zinc-700 hover:border-amber-500/50 transition-all"
                >
                  <span className="text-2xl">{p.icon}</span>
                  <div>
                    <h3 className="font-medium group-hover:text-amber-500 transition-colors">{p.name}</h3>
                    <p className="text-xs text-zinc-500">{p.difficulty} • {p.songs.length} songs</p>
                  </div>
                </Link>
              ))}
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer className="mt-16 border-t border-zinc-800">
          <div className="container mx-auto px-4 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-zinc-500 text-sm">© {new Date().getFullYear()} DadRock Tabs. Free guitar & bass lessons.</p>
            <Link href="/" className="text-zinc-500 hover:text-amber-500 text-sm transition-colors">Home</Link>
          </div>
        </footer>
      </div>
    </>
  );
}
