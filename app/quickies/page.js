import { getDb } from '@/lib/mongodb';
import QuickiesClient from './QuickiesClient';

// Force dynamic rendering
export const dynamic = 'force-dynamic';

// SEO Metadata
export const metadata = {
  title: 'DadRock Tabs Quickies - Quick Guitar & Bass Lessons | DadRock Tabs',
  description: 'Quick guitar and bass tab lessons from DadRock Tabs. Short, focused tutorials that get you playing classic rock and heavy metal riffs fast. Perfect for beginners and intermediate players who want to learn legendary riffs in minutes.',
  keywords: 'quick guitar lessons, short bass tabs, fast guitar tutorials, classic rock riffs, quick tab lessons, DadRock Tabs Quickies, guitar quickies, bass quickies',
  openGraph: {
    title: 'DadRock Tabs Quickies - Quick Guitar & Bass Lessons',
    description: 'Quick guitar and bass tab lessons — short, sweet, and straight to the riff! Learn classic rock licks in minutes.',
    type: 'website',
    url: 'https://dadrocktabs.com/quickies',
    siteName: 'DadRock Tabs',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'DadRock Tabs Quickies - Quick Guitar & Bass Lessons',
    description: 'Quick guitar and bass tab lessons — short, sweet, and straight to the riff!',
  },
  alternates: {
    canonical: 'https://dadrocktabs.com/quickies',
  },
};

// JSON-LD Schema for SEO
function generateSchema(videoCount) {
  return {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: 'DadRock Tabs Quickies',
    description: 'Quick guitar and bass tab lessons from DadRock Tabs. Short, focused tutorials for classic rock and heavy metal riffs.',
    url: 'https://dadrocktabs.com/quickies',
    isPartOf: {
      '@type': 'WebSite',
      name: 'DadRock Tabs',
      url: 'https://dadrocktabs.com',
    },
    about: {
      '@type': 'Thing',
      name: 'Quick Guitar Tablature Lessons',
    },
    numberOfItems: videoCount,
  };
}

export default async function QuickiesPage() {
  let videos = [];
  let adSettings = null;

  // Fetch quickies videos from database
  try {
    const db = await getDb();
    const dbVideos = await db.collection('quickies_videos')
      .find({})
      .sort({ position: 1 })
      .toArray();

    videos = dbVideos.map(v => ({
      id: v.id,
      video_id: v.video_id,
      song: v.song,
      artist: v.artist,
      title: v.title,
      youtube_url: v.youtube_url,
      thumbnail: v.thumbnail,
      position: v.position,
      created_at: v.created_at,
    }));
  } catch (err) {
    console.error('Failed to fetch quickies videos:', err);
  }

  // If DB is empty, try fetching via the API (which triggers YouTube sync)
  if (videos.length === 0) {
    try {
      const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';
      const res = await fetch(`${baseUrl}/api/quickies`, { cache: 'no-store' });
      if (res.ok) {
        const data = await res.json();
        videos = data.videos || [];
      }
    } catch (err) {
      console.error('Failed to fetch quickies from API:', err);
    }
  }

  // Fetch ad settings
  try {
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
          __html: JSON.stringify(generateSchema(videos.length)),
        }}
      />
      <QuickiesClient initialVideos={videos} adSettings={adSettings} />
    </>
  );
}
