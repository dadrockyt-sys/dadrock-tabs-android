import { GUIDES } from '@/lib/guidesData';
import { notFound } from 'next/navigation';
import Link from 'next/link';

export async function generateMetadata({ params }) {
  const { slug } = await params;
  const guide = GUIDES[slug];
  if (!guide) return { title: 'Guide Not Found | DadRock Tabs' };

  return {
    title: `${guide.title} | DadRock Tabs`,
    description: guide.description,
    keywords: guide.keywords,
    openGraph: {
      title: guide.title,
      description: guide.description,
      type: 'article',
      url: `https://dadrocktabs.com/learn/${slug}`,
      siteName: 'DadRock Tabs',
      images: [{ url: `https://dadrocktabs.com/api/og?title=${encodeURIComponent(guide.title)}&type=genre`, width: 1200, height: 630 }],
    },
    twitter: {
      card: 'summary_large_image',
      title: guide.title,
      description: guide.description,
    },
  };
}

export function generateStaticParams() {
  return Object.keys(GUIDES).map(slug => ({ slug }));
}

export default async function GuidePage({ params }) {
  const { slug } = await params;
  const guide = GUIDES[slug];

  if (!guide) {
    notFound();
  }

  // JSON-LD Article schema
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    'headline': guide.title,
    'description': guide.description,
    'url': `https://dadrocktabs.com/learn/${slug}`,
    'author': {
      '@type': 'Organization',
      'name': 'DadRock Tabs',
      'url': 'https://dadrocktabs.com',
    },
    'publisher': {
      '@type': 'Organization',
      'name': 'DadRock Tabs',
      'url': 'https://dadrocktabs.com',
      'logo': {
        '@type': 'ImageObject',
        'url': 'https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png',
      }
    },
    'mainEntityOfPage': {
      '@type': 'WebPage',
      '@id': `https://dadrocktabs.com/learn/${slug}`,
    },
    'articleSection': guide.category,
    'keywords': guide.keywords,
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
            <div className="flex items-center gap-3">
              <Link 
                href="/learn"
                className="text-sm text-zinc-400 hover:text-amber-500 transition-colors"
              >
                All Guides
              </Link>
              <Link 
                href="/"
                className="flex items-center gap-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-full text-sm transition-colors"
              >
                Home
              </Link>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8 max-w-3xl">
          {/* Breadcrumb */}
          <nav className="mb-6 text-sm text-zinc-400">
            <Link href="/" className="hover:text-amber-500 transition-colors">Home</Link>
            <span className="mx-2">/</span>
            <Link href="/learn" className="hover:text-amber-500 transition-colors">Learn</Link>
            <span className="mx-2">/</span>
            <span className="text-white">{guide.title}</span>
          </nav>

          {/* Article Header */}
          <article>
            <header className="mb-8">
              <div className="flex items-center gap-3 mb-4">
                <span className={`px-3 py-1 rounded-lg text-xs font-semibold ${
                  guide.category === 'Beginner' ? 'bg-green-500/20 text-green-400' :
                  guide.category === 'Technique' ? 'bg-amber-500/20 text-amber-400' :
                  'bg-purple-500/20 text-purple-400'
                }`}>
                  {guide.category}
                </span>
                <span className="text-zinc-500 text-sm">{guide.readTime}</span>
              </div>
              <h1 className="text-3xl sm:text-4xl lg:text-5xl font-bold mb-4 leading-tight">
                {guide.title}
              </h1>
              <p className="text-xl text-zinc-400 leading-relaxed">
                {guide.description}
              </p>
            </header>

            {/* Article Content */}
            <div 
              className="prose prose-invert prose-zinc max-w-none
                prose-headings:text-white prose-headings:font-bold
                prose-h2:text-2xl prose-h2:mt-10 prose-h2:mb-4 prose-h2:text-amber-500
                prose-h3:text-xl prose-h3:mt-6 prose-h3:mb-3
                prose-p:text-zinc-300 prose-p:leading-relaxed prose-p:mb-4
                prose-li:text-zinc-300
                prose-strong:text-white
                prose-pre:bg-zinc-900 prose-pre:border prose-pre:border-zinc-700 prose-pre:rounded-xl
                prose-a:text-amber-500 prose-a:no-underline hover:prose-a:underline"
              dangerouslySetInnerHTML={{ __html: guide.content }}
            />

            {/* Related Artists */}
            {guide.relatedArtists && guide.relatedArtists.length > 0 && (
              <section className="mt-12 p-6 bg-zinc-900/50 rounded-2xl border border-zinc-800">
                <h2 className="text-xl font-bold mb-4 text-amber-500">Related Artists on DadRock Tabs</h2>
                <div className="flex flex-wrap gap-3">
                  {guide.relatedArtists.map(artistSlug => (
                    <Link
                      key={artistSlug}
                      href={`/artist/${artistSlug}`}
                      className="px-4 py-2 bg-zinc-800 hover:bg-amber-500 hover:text-black rounded-full text-sm font-medium transition-all border border-zinc-700 hover:border-amber-500"
                    >
                      {artistSlug.replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                    </Link>
                  ))}
                </div>
              </section>
            )}
          </article>

          {/* More Guides */}
          <section className="mt-12">
            <h2 className="text-xl font-bold mb-4">More Guides</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {Object.entries(GUIDES)
                .filter(([s]) => s !== slug)
                .slice(0, 4)
                .map(([s, g]) => (
                  <Link
                    key={s}
                    href={`/learn/${s}`}
                    className="group p-4 bg-zinc-900/50 rounded-xl border border-zinc-800 hover:border-amber-500/50 transition-all"
                  >
                    <span className="text-2xl">{g.icon}</span>
                    <h3 className="font-medium text-sm mt-2 group-hover:text-amber-500 transition-colors">{g.title}</h3>
                  </Link>
                ))}
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer className="border-t border-zinc-800 mt-16">
          <div className="container mx-auto px-4 py-8 flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-zinc-500 text-sm">© {new Date().getFullYear()} DadRock Tabs. Free guitar & bass lessons.</p>
            <div className="flex gap-4">
              <Link href="/" className="text-zinc-500 hover:text-amber-500 text-sm transition-colors">Home</Link>
              <Link href="/learn" className="text-zinc-500 hover:text-amber-500 text-sm transition-colors">Learn</Link>
            </div>
          </div>
        </footer>
      </div>
    </>
  );
}
