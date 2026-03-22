import ComingSoonClient from './ComingSoonClient';
import { generateAlternates } from '@/lib/seo';

// Force dynamic rendering - this page fetches real-time data
export const dynamic = 'force-dynamic';

// SEO Metadata
export const metadata = {
  title: 'Upcoming Guitar Lessons & Bass Tabs Schedule | DadRock Tabs',
  description: 'Check out the upcoming guitar and bass tab video lessons schedule at DadRock Tabs. See what classic rock, heavy metal, and hair metal songs are coming soon. Free video tutorials for Van Halen, Metallica, AC/DC, Led Zeppelin, and more legendary artists. Never miss a new lesson - view our complete release schedule!',
  keywords: 'upcoming guitar lessons, bass tabs schedule, new guitar tutorials, classic rock tabs, heavy metal lessons, hair metal guitar, free guitar tabs, DadRock Tabs schedule',
  openGraph: {
    title: 'Upcoming Guitar Lessons Schedule | DadRock Tabs',
    description: 'See what classic rock and metal guitar lessons are coming soon to DadRock Tabs. Free video tutorials for legendary artists.',
    type: 'website',
    url: 'https://dadrocktabs.com/coming-soon',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Upcoming Guitar Lessons Schedule | DadRock Tabs',
    description: 'See what classic rock and metal guitar lessons are coming soon to DadRock Tabs.',
  },
  alternates: generateAlternates('/coming-soon'),
};

// JSON-LD Schema for SEO
function generateSchema(upcomingCount) {
  return {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'Upcoming Guitar Lessons Schedule',
    description: 'Schedule of upcoming guitar and bass tab video lessons at DadRock Tabs',
    url: 'https://dadrocktabs.com/coming-soon',
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

export default async function ComingSoonPage() {
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
          __html: JSON.stringify(generateSchema(total)),
        }}
      />
      <ComingSoonClient initialVideos={upcomingVideos} initialTotal={total} />
    </>
  );
}
