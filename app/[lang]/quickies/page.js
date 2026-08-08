import { getDb } from '@/lib/mongodb';
import QuickiesClient from '../../quickies/QuickiesClient';
import { generateAlternates } from '@/lib/seo';

export const dynamic = 'force-dynamic';

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams?.lang || 'en';
  const pageUrl = lang === 'en'
    ? 'https://dadrocktabs.com/quickies'
    : `https://dadrocktabs.com/${lang}/quickies`;

  return {
    title: 'DadRock Tabs Quickies - Quick Guitar & Bass Lessons | DadRock Tabs',
    description: 'Quick guitar and bass tab lessons from DadRock Tabs. Short, focused tutorials that get you playing classic rock and heavy metal riffs fast.',
    openGraph: {
      title: 'DadRock Tabs Quickies - Quick Guitar & Bass Lessons',
      description: 'Quick guitar and bass tab lessons — short, sweet, and straight to the riff!',
      type: 'website',
      url: pageUrl,
      siteName: 'DadRock Tabs',
    },
    alternates: generateAlternates('/quickies', lang),
  };
}


export default async function QuickiesPage({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang || 'en';

  let videos = [];
  let adSettings = null;

  try {
    const db = await getDb();

    const dbVideos = await db
      .collection('quickies_videos')
      .find({})
      .sort({ position: 1 })
      .toArray();

    videos = dbVideos.map((v) => ({
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

  if (videos.length === 0) {
    try {
      const baseUrl =
        process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000';

      const res = await fetch(`${baseUrl}/api/quickies`, {
        cache: 'no-store',
      });

      if (res.ok) {
        const data = await res.json();
        videos = data.videos || [];
      }
    } catch (err) {
      console.error('Failed to fetch quickies from API:', err);
    }
  }

  try {
    const db = await getDb();
    const settings = await db
      .collection('settings')
      .findOne({ type: 'site' });

    adSettings = {
      ad_link:
        settings?.ad_link ||
        'https://my-store-b8bb42.creator-spring.com/',
      ad_image: settings?.ad_image || '',
      ad_headline:
        settings?.ad_headline || 'Check Out Our Merchandise!',
      ad_description:
        settings?.ad_description ||
        'Support DadRock Tabs by grabbing some awesome gear',
      ad_button_text: settings?.ad_button_text || 'Shop Now',
      ad_duration: settings?.ad_duration || 5,
    };
  } catch (err) {
    console.error('Failed to fetch ad settings:', err);
  }

  return (
    <QuickiesClient
      initialVideos={videos}
      initialTotal={videos.length}
      adSettings={adSettings}
      currentLang={lang}
    />
  );
}
