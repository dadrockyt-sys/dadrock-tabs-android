import { getAllGuides } from '@/lib/guidesData';
import Link from 'next/link';

export const metadata = {
  title: 'Learn Guitar - Free Guides, Tips & Techniques | DadRock Tabs',
  description: 'Free guitar learning guides covering techniques, theory, and practice tips. Learn palm muting, read tabs, build speed, and master your favorite rock songs.',
  keywords: 'learn guitar, guitar techniques, guitar tips, how to play guitar, rock guitar guide, guitar lessons, guitar tutorial, free guitar guides',
  openGraph: {
    title: 'Learn Guitar - Free Guides & Techniques',
    description: 'Free guitar learning guides covering techniques, tips, and practice methods for rock and metal guitarists.',
    type: 'website',
    url: 'https://dadrocktabs.com/learn',
    siteName: 'DadRock Tabs',
  },
};

export default function LearnPage() {
  const guides = getAllGuides();
  const categories = [...new Set(guides.map(g => g.category))];

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    'name': 'Learn Guitar - Free Guides & Techniques',
    'description': 'Free guitar learning hub with guides on techniques, theory, and practice tips for rock and metal guitarists.',
    'url': 'https://dadrocktabs.com/learn',
    'isPartOf': { '@id': 'https://dadrocktabs.com/#website' },
    'mainEntity': {
      '@type': 'ItemList',
      'numberOfItems': guides.length,
      'itemListElement': guides.map((guide, i) => ({
        '@type': 'ListItem',
        'position': i + 1,
        'item': {
          '@type': 'Article',
          'name': guide.title,
          'url': `https://dadrocktabs.com/learn/${guide.slug}`,
          'description': guide.description,
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

        <main className="container mx-auto px-4 py-8 max-w-5xl">
          {/* Breadcrumb */}
          <nav className="mb-6 text-sm text-zinc-400">
            <Link href="/" className="hover:text-amber-500 transition-colors">Home</Link>
            <span className="mx-2">/</span>
            <span className="text-white">Learn Guitar</span>
          </nav>

          {/* Hero */}
          <div className="mb-12 text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold mb-4">
              <span className="text-amber-500">Learn</span> Guitar
            </h1>
            <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
              Free guides, techniques, and tips to level up your playing. From beginner riffs to advanced shredding.
            </p>
          </div>

          {/* Category Sections */}
          {categories.map(category => (
            <section key={category} className="mb-12">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-3">
                <span className={`px-3 py-1 rounded-lg text-sm font-semibold ${
                  category === 'Beginner' ? 'bg-green-500/20 text-green-400' :
                  category === 'Technique' ? 'bg-amber-500/20 text-amber-400' :
                  'bg-purple-500/20 text-purple-400'
                }`}>
                  {category}
                </span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
                {guides.filter(g => g.category === category).map(guide => (
                  <Link
                    key={guide.slug}
                    href={`/learn/${guide.slug}`}
                    className="group bg-zinc-900/80 rounded-xl border border-zinc-800 p-6 hover:border-amber-500/50 hover:bg-zinc-900 transition-all duration-300"
                  >
                    <div className="flex items-start gap-4">
                      <span className="text-3xl">{guide.icon}</span>
                      <div className="flex-1">
                        <h3 className="font-bold text-lg text-white group-hover:text-amber-500 transition-colors mb-2">
                          {guide.title}
                        </h3>
                        <p className="text-zinc-400 text-sm leading-relaxed mb-3">
                          {guide.description}
                        </p>
                        <span className="text-xs text-zinc-500">{guide.readTime}</span>
                      </div>
                    </div>
                  </Link>
                ))}
              </div>
            </section>
          ))}
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
