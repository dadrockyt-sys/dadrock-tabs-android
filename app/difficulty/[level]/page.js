import { DIFFICULTY_LEVELS, getArtistsByDifficulty } from '@/lib/difficultyData';
import { notFound } from 'next/navigation';
import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';
import Link from 'next/link';

export async function generateMetadata({ params }) {
  const { level } = await params;
  const difficulty = DIFFICULTY_LEVELS[level];
  if (!difficulty) return { title: 'Not Found | DadRock Tabs' };

  const title = `${difficulty.name} Guitar Tabs - Easy ${difficulty.name} Songs to Learn | DadRock Tabs`;
  const description = `${difficulty.longDescription.substring(0, 155)}...`;

  return {
    title,
    description,
    keywords: `${difficulty.name.toLowerCase()} guitar tabs, easy guitar songs, ${difficulty.name.toLowerCase()} rock songs, learn guitar ${difficulty.name.toLowerCase()}, free tabs for ${difficulty.name.toLowerCase()}s`,
    openGraph: {
      title: `${difficulty.name} Guitar & Bass Tabs`,
      description,
      type: 'website',
      url: `https://dadrocktabs.com/difficulty/${level}`,
      siteName: 'DadRock Tabs',
    },
  };
}

export function generateStaticParams() {
  return Object.keys(DIFFICULTY_LEVELS).map(level => ({ level }));
}

export default async function DifficultyPage({ params }) {
  const { level } = await params;
  const difficulty = DIFFICULTY_LEVELS[level];

  if (!difficulty) {
    notFound();
  }

  const artistSlugs = getArtistsByDifficulty(level);
  const db = await getDb();
  const artistData = [];

  for (const slug of artistSlugs) {
    // Convert slug back to search pattern
    const pattern = slug.replace(/-/g, ' ');
    const escapedPattern = pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

    const count = await db.collection('videos').countDocuments({
      artist: { $regex: new RegExp(`^${escapedPattern}`, 'i') }
    });

    if (count > 0) {
      const video = await db.collection('videos').findOne(
        { artist: { $regex: new RegExp(`^${escapedPattern}`, 'i') } },
        { projection: { thumbnail: 1, artist: 1 } }
      );

      artistData.push({
        name: video?.artist?.replace(/ -$/, '').trim() || pattern,
        slug,
        lessonCount: count,
        thumbnail: video?.thumbnail || null,
      });
    }
  }

  artistData.sort((a, b) => b.lessonCount - a.lessonCount);
  const totalLessons = artistData.reduce((sum, a) => sum + a.lessonCount, 0);

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    'name': `${difficulty.name} Guitar Tabs`,
    'description': difficulty.longDescription,
    'url': `https://dadrocktabs.com/difficulty/${level}`,
    'isPartOf': { '@id': 'https://dadrocktabs.com/#website' },
    'mainEntity': {
      '@type': 'ItemList',
      'numberOfItems': artistData.length,
      'itemListElement': artistData.map((artist, i) => ({
        '@type': 'ListItem',
        'position': i + 1,
        'item': {
          '@type': 'MusicGroup',
          'name': artist.name,
          'url': `https://dadrocktabs.com/artist/${artist.slug}`,
        }
      }))
    }
  };

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

        <main className="container mx-auto px-4 py-8 max-w-6xl">
          {/* Breadcrumb */}
          <nav className="mb-6 text-sm text-zinc-400">
            <Link href="/" className="hover:text-amber-500 transition-colors">Home</Link>
            <span className="mx-2">/</span>
            <span className="text-white">{difficulty.name} Songs</span>
          </nav>

          {/* Hero */}
          <div className="relative mb-10 p-8 sm:p-12 rounded-3xl overflow-hidden bg-zinc-900/50 border border-zinc-800">
            <div className={`absolute inset-0 bg-gradient-to-br ${difficulty.color} opacity-10`} />
            <div className="relative z-10">
              <div className="flex flex-col sm:flex-row sm:items-end gap-4 sm:gap-8">
                <div className="flex-1">
                  <span className="text-4xl mb-3 block">{difficulty.icon}</span>
                  <p className="text-sm font-medium text-amber-500/80 uppercase tracking-widest mb-2">
                    Difficulty Level
                  </p>
                  <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4">
                    {difficulty.name} <span className="text-amber-500">Guitar Tabs</span>
                  </h1>
                  <p className="text-zinc-300 text-lg max-w-2xl leading-relaxed">
                    {difficulty.description}
                  </p>
                </div>
                <div className="flex items-center gap-4 flex-shrink-0">
                  <div className="px-5 py-3 rounded-2xl text-center bg-zinc-800/80 border border-zinc-700">
                    <div className="text-3xl font-bold text-amber-500">{artistData.length}</div>
                    <div className="text-xs text-zinc-400 uppercase tracking-wider">Artists</div>
                  </div>
                  <div className="px-5 py-3 rounded-2xl text-center bg-zinc-800/80 border border-zinc-700">
                    <div className="text-3xl font-bold text-amber-500">{totalLessons}</div>
                    <div className="text-xs text-zinc-400 uppercase tracking-wider">Lessons</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* About */}
          <div className="mb-10 p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800">
            <h2 className="text-xl font-bold mb-3 text-amber-500">What to Expect</h2>
            <p className="text-zinc-300 leading-relaxed">{difficulty.longDescription}</p>
            <p className="text-zinc-500 text-sm mt-3"><strong>Key criteria:</strong> {difficulty.criteria}</p>
          </div>

          {/* Artist Grid */}
          <section className="mb-12">
            <h2 className="text-2xl font-bold mb-6 text-white">
              {difficulty.name} Artists ({artistData.length})
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
              {artistData.map((artist, index) => (
                <Link
                  key={artist.slug}
                  href={`/artist/${artist.slug}`}
                  className="group bg-zinc-900/80 rounded-xl border border-zinc-800 overflow-hidden hover:border-amber-500/50 transition-all duration-300"
                >
                  <div className="relative h-36 overflow-hidden">
                    {artist.thumbnail ? (
                      <img
                        src={artist.thumbnail}
                        alt={`${artist.name} Guitar Tabs`}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                        loading="lazy"
                      />
                    ) : (
                      <div className={`w-full h-full bg-gradient-to-br ${difficulty.color} opacity-20`} />
                    )}
                    <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 via-zinc-900/50 to-transparent" />
                    <div className="absolute top-3 right-3 text-xs font-bold text-black px-2.5 py-1 rounded-lg bg-amber-500">
                      {artist.lessonCount} lessons
                    </div>
                  </div>
                  <div className="p-4">
                    <h3 className="font-bold text-lg text-white group-hover:text-amber-500 transition-colors">
                      {artist.name}
                    </h3>
                    <p className="text-sm text-zinc-500">{difficulty.name} • {artist.lessonCount} tabs</p>
                  </div>
                </Link>
              ))}
            </div>
          </section>

          {/* Other Difficulty Levels */}
          <section className="mt-12 p-8 rounded-2xl border border-zinc-800 bg-zinc-900/30">
            <h2 className="text-xl font-bold mb-4">Browse Other Difficulty Levels</h2>
            <div className="flex flex-wrap gap-4">
              {Object.entries(DIFFICULTY_LEVELS)
                .filter(([key]) => key !== level)
                .map(([key, diff]) => (
                  <Link
                    key={key}
                    href={`/difficulty/${key}`}
                    className="flex items-center gap-2 px-5 py-3 bg-zinc-800 hover:bg-amber-500 hover:text-black rounded-full font-medium transition-all border border-zinc-700 hover:border-amber-500"
                  >
                    <span>{diff.icon}</span>
                    {diff.name}
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
