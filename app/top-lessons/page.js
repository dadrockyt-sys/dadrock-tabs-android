import TopLessonsClient from './TopLessonsClient';
import { generateAlternates, generateCanonical } from '@/lib/seo';
import { getSeoMeta } from '@/lib/seoTranslations';

// Force dynamic rendering - this page fetches real-time data
export const dynamic = 'force-dynamic';

// SEO Metadata
export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams?.lang || 'en';
  const pageUrl = generateCanonical('/top-lessons', lang);
  const localizedMeta = getSeoMeta(lang, 'topLessons');

  return {
    title: localizedMeta.title,
    description: localizedMeta.description,
    keywords: 'most viewed guitar lessons, popular bass tabs, top guitar tutorials, best rock lessons, classic rock tabs, heavy metal guitar, free guitar lessons, DadRock Tabs',
    alternates: generateAlternates('/top-lessons', lang),
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
  };
}

// JSON-LD Schema for SEO
function generateSchema(lang = 'en') {
  const pageUrl = generateCanonical('/top-lessons', lang);
  const localizedMeta = getSeoMeta(lang, 'topLessons');

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
  };
}

export default async function TopLessonsPage({ params } = {}) {
  const resolvedParams = params ? await params : {};
  const lang = resolvedParams?.lang || 'en';

  // Fetch top videos on the server for SEO
  let topVideos = [];
  let adSettings = null;
  
  try {
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
    const res = await fetch(`${baseUrl}/api/top-videos?limit=10`, { 
      cache: 'no-store',
      next: { revalidate: 0 }
    });
    if (res.ok) {
      const data = await res.json();
      topVideos = data.videos || [];
    }
  } catch (err) {
    console.error('Failed to fetch top videos:', err);
  }

  // Fetch ad settings
  try {
    const { getDb } = await import('@/lib/mongodb');
    const db = await getDb();
    const settings = await db.collection('settings').findOne({ type: 'site' });
    adSettings = {
      ad_link: settings?.ad_link || 'https://my-store-b8bb42.creator-spring.com/',
      ad_image: settings?.ad_image || '',
      ad_headline: settings?.ad_headline || 'Check Out Our Merchandise!',
      ad_description: settings?.ad_description || 'Support DadRock Tabs by grabbing some awesome gear',
      ad_button_text: settings?.ad_button_text || 'Shop Now',
      ad_duration: settings?.ad_duration || 5,
    };
  } catch (err) {
    console.error('Failed to fetch ad settings:', err);
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify(generateSchema(lang)),
        }}
      />
      <TopLessonsClient initialVideos={topVideos} adSettings={adSettings} />
    </>
  );
}
