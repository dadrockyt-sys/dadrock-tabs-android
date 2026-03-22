import { getDb } from '@/lib/mongodb';
import { generateSeoContent } from '@/lib/artistData';
import { generateAlternates } from '@/lib/seo';
import SongPageClient from './SongPageClient';
import { notFound } from 'next/navigation';

// Generate metadata for SEO
export async function generateMetadata({ params }) {
  const { slug } = await params;
  
  try {
    const db = await getDb();
    const song = await db.collection('song_pages').findOne({ slug });
    
    if (!song) {
      return { title: 'Song Not Found | DadRock Tabs' };
    }

    const cleanArtist = song.artist?.replace(/ -$/, '').trim() || 'DadRock Tabs';
    const title = `${song.title} by ${cleanArtist} - Guitar & Bass Tab Lesson | DadRock Tabs`;
    const description = `Learn to play ${song.title} by ${cleanArtist} with free guitar and bass tablature video lesson. Step-by-step tutorial with synchronized tabs from DadRock Tabs.`;

    return {
      title,
      description,
      keywords: `${song.title} guitar tab, ${cleanArtist} bass tab, ${song.title} lesson, ${cleanArtist} guitar tutorial, free guitar tabs, DadRock Tabs`,
      openGraph: {
        title,
        description,
        type: 'video.other',
        url: `https://dadrocktabs.com/songs/${slug}`,
        images: [{ url: song.thumbnail }],
      },
      twitter: {
        card: 'summary_large_image',
        title,
        description,
        images: [song.thumbnail],
      },
      alternates: generateAlternates(`/songs/${slug}`),
    };
  } catch {
    return { title: 'Song | DadRock Tabs' };
  }
}

export default async function SongPage({ params }) {
  const { slug } = await params;
  
  let song = null;
  let adSettings = null;

  try {
    const db = await getDb();
    song = await db.collection('song_pages').findOne({ slug });
    
    if (!song) {
      notFound();
    }

    // Fetch ad settings
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
    console.error('Song page error:', err);
    notFound();
  }

  const cleanArtist = song.artist?.replace(/ -$/, '').trim() || 'DadRock Tabs';
  const seoContent = generateSeoContent(song.title, song.artist);

  // JSON-LD Schema
  const schema = {
    '@context': 'https://schema.org',
    '@type': 'VideoObject',
    name: `${song.title} - ${cleanArtist} Guitar Tab Tutorial`,
    description: `Learn to play ${song.title} by ${cleanArtist} with this guitar and bass tablature video tutorial. Free lesson from DadRock Tabs.`,
    thumbnailUrl: song.thumbnail,
    uploadDate: song.publishedAt || new Date().toISOString(),
    contentUrl: `https://www.youtube.com/watch?v=${song.videoId}`,
    embedUrl: `https://www.youtube.com/embed/${song.videoId}`,
    interactionStatistic: {
      '@type': 'InteractionCounter',
      interactionType: { '@type': 'WatchAction' },
      userInteractionCount: song.viewCount || 0,
    },
    publisher: {
      '@type': 'Organization',
      name: 'DadRock Tabs',
      url: 'https://dadrocktabs.com',
    },
  };

  const songData = {
    videoId: song.videoId,
    title: song.title,
    artist: cleanArtist,
    fullTitle: song.fullTitle,
    slug: song.slug,
    thumbnail: song.thumbnail,
    viewCount: song.viewCount || 0,
    likeCount: song.likeCount || 0,
    duration: song.duration || 0,
  };

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(schema) }}
      />
      <SongPageClient
        song={songData}
        seoContent={seoContent}
        adSettings={adSettings}
      />
    </>
  );
}
