import ComingSoonClient from '../../coming-soon/ComingSoonClient';
import { generateAlternates } from '@/lib/seo';
import { getSeoMeta } from '@/lib/seoTranslations';

// Force dynamic rendering - this page fetches real-time data
export const dynamic = 'force-dynamic';

// SEO Metadata
export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams?.lang || 'en';
  const pageUrl = lang === 'en'
    ? 'https://dadrocktabs.com/coming-soon'
    : `https://dadrocktabs.com/${lang}/coming-soon`;
  const localizedMeta = getSeoMeta(lang, 'comingSoon');

  return {
    title: localizedMeta.title,
    description: localizedMeta.description,
    keywords: 'upcoming guitar lessons, bass tabs schedule, new guitar tutorials, classic rock tabs, heavy metal lessons, hair metal guitar, free guitar tabs, DadRock Tabs schedule',
    openGraph: {
      title: localizedMeta.title,
      description: localizedMeta.description,
      type: 'website',
      url: pageUrl,
      siteName: 'DadRock Tabs',
    },
    twitter: {
      card: 'summary_large_image',
      title: localizedMeta.title,
      description: localizedMeta.description,
    },
    alternates: generateAlternates('/coming-soon', lang),
  };
}

// JSON-LD Schema for SEO
function generateSchema(upcomingCount, lang = 'en') {
  const pageUrl = lang === 'en'
    ? 'https://dadrocktabs.com/coming-soon'
    : `https://dadrocktabs.com/${lang}/coming-soon`;
  const localizedMeta = getSeoMeta(lang, 'comingSoon');

  return {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: localizedMeta.title,
    description: localizedMeta.description,
    url: pageUrl,
    inLanguage: lang === 'pt-br' ? 'pt-BR' : lang,
    isPartOf: {
      '@type': 'WebSite',
      name: 'DadRock Tabs',
      url: 'https://dadrocktabs.com',
    },
    about: {
      '@type': 'Thing',
      name: 'Guitar Tablature Lessons',
    },
    numberOfItems: upcomingCount,
  };
}

export default async function ComingSoonPage({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams?.lang || 'en';

  // Fetch upcoming videos on the server for SEO
  let upcomingVideos = [];
  let total = 0;
  
  try {
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    const res = await fetch(`${baseUrl}/api/upcoming`, { 
      cache: 'no-store',
      next: { revalidate: 0 }
    });
    if (res.ok) {
      const data = await res.json();
      upcomingVideos = data.upcoming || [];
      total = data.total || 0;
    }
  } catch (err) {
    console.error('Failed to fetch upcoming videos:', err);
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(generateSchema(total, lang)),
        }}
      />
      <ComingSoonClient initialVideos={upcomingVideos} initialTotal={total} currentLang={lang} />
    </>
  );
}
