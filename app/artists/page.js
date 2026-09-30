import Link from 'next/link';
import { getDb } from '@/lib/mongodb';
import { artistToSlug, SLUG_TO_ARTIST } from '@/lib/slugify';
import { generateAlternates } from '@/lib/seo';

export const dynamic = 'force-dynamic';

export const metadata = {
  title: 'All Rock Artists - Guitar & Bass Lessons | DadRock Tabs',
  description: 'Browse every artist on DadRock Tabs and jump directly to free guitar and bass lesson collections for classic rock, hard rock, metal, grunge, blues rock, and more.',
  alternates: generateAlternates('/artists'),
  robots: { index: true, follow: true },
  openGraph: {
    title: 'All Rock Artists - Guitar & Bass Lessons | DadRock Tabs',
    description: 'Browse the complete DadRock Tabs artist directory and find free guitar and bass video lessons.',
    type: 'website',
    url: 'https://dadrocktabs.com/artists',
    siteName: 'DadRock Tabs',
  },
};

const LOGO_URL = 'https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png';

const junkPatterns = [
  '#',
  'Coming Soon',
  'coming soon',
  'Memorial Video',
  'Original Song',
  'Greatest Drummers',
  'Lead Singers',
  'Welcome To The Jungle 2022',
  'Highway To Hell',
  'Hold On Loosely',
  'Cities On Flame',
  'Face The Slayer',
  'The Great 80',
  'The DadRock',
  'DadRock Tabs',
  'Steppenwolf Be The First',
  'Children Of The Grave',
  "80's Fretmasters",
];

function isJunkArtist(label) {
  return junkPatterns.some((pattern) => label.includes(pattern));
}

function groupKey(name) {
  const first = name.trim().charAt(0).toUpperCase();
  return /[A-Z]/.test(first) ? first : '#';
}

export default async function ArtistsPage() {
  const db = await getDb();
  const labels = await db.collection('videos').distinct('artist');
  const artistsBySlug = new Map();

  for (const rawLabel of labels) {
    if (!rawLabel) continue;

    const cleanLabel = rawLabel.replace(/\s*-\s*$/, '').trim();
    if (!cleanLabel || isJunkArtist(cleanLabel)) continue;

    const slug = artistToSlug(cleanLabel);
    if (!slug) continue;

    const name = SLUG_TO_ARTIST[slug] || cleanLabel;

    if (!artistsBySlug.has(slug)) {
      artistsBySlug.set(slug, { slug, name });
    }
  }

  const artists = [...artistsBySlug.values()].sort((a, b) =>
    a.name.localeCompare(b.name, 'en', { sensitivity: 'base' })
  );

  const groups = artists.reduce((acc, artist) => {
    const key = groupKey(artist.name);
    if (!acc[key]) acc[key] = [];
    acc[key].push(artist);
    return acc;
  }, {});

  const letters = Object.keys(groups).sort((a, b) => {
    if (a === '#') return 1;
    if (b === '#') return -1;
    return a.localeCompare(b);
  });

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'DadRock Tabs Artist Directory',
    description: 'Complete artist directory for DadRock Tabs guitar and bass lesson collections.',
    url: 'https://dadrocktabs.com/artists',
    isPartOf: { '@id': 'https://dadrocktabs.com/#website' },
    numberOfItems: artists.length,
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 text-white">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <header className="sticky top-0 z-50 bg-zinc-950/90 backdrop-blur-md border-b border-zinc-800">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between gap-4">
          <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
            <img src={LOGO_URL} alt="DadRock Tabs" className="h-9 w-auto" />
            <span className="text-lg font-bold text-amber-500 hidden sm:block">DadRock Tabs</span>
          </Link>
          <Link
            href="/"
            className="px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-sm transition-colors"
          >
            Home
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 sm:py-12">
        <nav className="mb-6 text-sm text-zinc-400">
          <Link href="/" className="hover:text-amber-500 transition-colors">Home</Link>
          <span className="mx-2">/</span>
          <span className="text-white">All Artists</span>
        </nav>

        <section className="mb-10 p-6 sm:p-8 rounded-3xl border border-zinc-800 bg-zinc-900/60">
          <p className="text-amber-500 uppercase tracking-widest text-sm font-semibold mb-2">
            Artist Directory
          </p>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">All Guitar & Bass Artists</h1>
          <p className="text-zinc-300 text-lg max-w-3xl leading-relaxed">
            Browse every canonical artist collection on DadRock Tabs. Each artist page links to the free
            guitar and bass video lessons currently available in the library.
          </p>
          <p className="text-zinc-500 mt-4">{artists.length} artists</p>
        </section>

        <div className="flex flex-wrap gap-2 mb-10" aria-label="Artist directory letters">
          {letters.map((letter) => (
            <a
              key={letter}
              href={`#artists-${letter === '#' ? 'other' : letter.toLowerCase()}`}
              className="w-9 h-9 rounded-lg border border-zinc-700 bg-zinc-900 hover:border-amber-500 hover:text-amber-500 flex items-center justify-center text-sm font-semibold transition-colors"
            >
              {letter}
            </a>
          ))}
        </div>

        <div className="space-y-10">
          {letters.map((letter) => (
            <section
              key={letter}
              id={`artists-${letter === '#' ? 'other' : letter.toLowerCase()}`}
              className="scroll-mt-24"
            >
              <h2 className="text-2xl font-bold text-amber-500 mb-4 border-b border-zinc-800 pb-2">
                {letter}
              </h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {groups[letter].map((artist) => (
                  <Link
                    key={artist.slug}
                    href={`/artist/${artist.slug}`}
                    className="px-4 py-3 rounded-xl border border-zinc-800 bg-zinc-900/50 hover:border-amber-500/60 hover:bg-zinc-900 transition-colors"
                  >
                    <span className="font-medium">{artist.name}</span>
                  </Link>
                ))}
              </div>
            </section>
          ))}
        </div>
      </main>

      <footer className="mt-16 border-t border-zinc-800">
        <div className="max-w-6xl mx-auto px-4 py-8 text-center text-sm text-zinc-500">
          DadRock Tabs — free guitar & bass lessons.
        </div>
      </footer>
    </div>
  );
}
