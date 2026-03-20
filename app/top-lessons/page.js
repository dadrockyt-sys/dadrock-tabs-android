import TopLessonsClient from './TopLessonsClient';

// SEO Metadata
export const metadata = {
  title: 'Top 10 Most Viewed Guitar Lessons | DadRock Tabs',
  description: 'Discover the most popular guitar and bass tab video lessons at DadRock Tabs. Our top 10 most-watched tutorials feature classic rock, heavy metal, and hair metal songs from legendary artists like Van Halen, Metallica, AC/DC, Led Zeppelin, and more. Start learning the songs everyone loves!',
  keywords: 'most viewed guitar lessons, popular bass tabs, top guitar tutorials, best rock lessons, classic rock tabs, heavy metal guitar, free guitar lessons, DadRock Tabs',
  openGraph: {
    title: 'Top 10 Most Viewed Guitar Lessons | DadRock Tabs',
    description: 'Discover the most popular guitar lessons at DadRock Tabs. Learn the songs everyone loves!',
    type: 'website',
    url: 'https://dadrocktabs.com/top-lessons',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Top 10 Most Viewed Guitar Lessons | DadRock Tabs',
    description: 'Discover the most popular guitar lessons at DadRock Tabs.',
  },
  alternates: {
    canonical: 'https://dadrocktabs.com/top-lessons',
  },
};

// JSON-LD Schema for SEO
function generateSchema() {
  return {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'Top 10 Most Viewed Guitar Lessons',
    description: 'The most popular guitar and bass tab video lessons at DadRock Tabs',
    url: 'https://dadrocktabs.com/top-lessons',
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

export default async function TopLessonsPage() {
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
          __html: JSON.stringify(generateSchema()),
        }}
      />
      <TopLessonsClient initialVideos={topVideos} adSettings={adSettings} />
    </>
  );
}
