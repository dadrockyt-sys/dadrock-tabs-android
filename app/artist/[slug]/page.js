import { getDb } from '@/lib/mongodb';
import { notFound } from 'next/navigation';
import { generateAlternates } from '@/lib/seo';
import { slugToArtistPattern, artistToSlug } from '@/lib/slugify';
import ArtistPageClient from './ArtistPageClient';

// Find artist name from slug by checking the database
async function findArtistBySlug(db, slug) {
  const directPattern = slugToArtistPattern(slug);
  const escapedDirect = directPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  const directCount = await db.collection('videos').countDocuments({
    artist: { $regex: new RegExp(`^${escapedDirect}`, 'i') }
  });

  if (directCount > 0) {
    return { artistPattern: directPattern, method: 'direct' };
  }

  const allArtists = await db.collection('videos').distinct('artist');

  for (const artist of allArtists) {
    const generatedSlug = artistToSlug(artist);
    if (generatedSlug === slug) {
      return { artistPattern: artist.replace(/ -$/, '').trim(), method: 'slug-match' };
    }
  }

  return null;
}

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const slug = resolvedParams.slug;

  const db = await getDb();
  const result = await findArtistBySlug(db, slug);

  if (!result) {
    return {
      title: 'Artist Not Found | DadRock Tabs',
      description: 'This artist page could not be found.',
    };
  }

  const artistPattern = result.artistPattern;
  const escapedPattern = artistPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  const videoCount = await db.collection('videos').countDocuments({
    artist: { $regex: new RegExp(`^${escapedPattern}`, 'i') }
  });

  const title = `${artistPattern} Guitar & Bass Tabs - ${videoCount} Free Lessons | DadRock Tabs`;

  const description = `Learn ${videoCount} songs by ${artistPattern} with free guitar and bass tab video lessons. Step-by-step tutorials perfect for beginner and intermediate players.`;

  return {
    title,
    description,
    alternates: generateAlternates(`/artist/${slug}`),
  };
}

export default async function ArtistPage({ params }) {
  const resolvedParams = await params;
  const slug = resolvedParams.slug;

  const db = await getDb();
  const result = await findArtistBySlug(db, slug);

  if (!result) {
    notFound();
  }

  const artistPattern = result.artistPattern;
  const escapedPattern = artistPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

  const videos = await db.collection('videos')
    .find({ artist: { $regex: new RegExp(`^${escapedPattern}`, 'i') } })
    .sort({ created_at: -1 })
    .toArray();

  if (videos.length === 0) {
    notFound();
  }

  const settings = await db.collection('settings').findOne({ type: 'site' });

  const adSettings = {
    ad_link: settings?.ad_link || 'https://my-store-b8bb42.creator-spring.com/',
    ad_image: settings?.ad_image || '',
    ad_headline: settings?.ad_headline || 'Check Out Our Merchandise!',
    ad_description: settings?.ad_description || 'Support DadRock Tabs by grabbing some awesome gear',
    ad_button_text: settings?.ad_button_text || 'Shop Now',
    ad_duration: settings?.ad_duration || 5,
  };

  let aiSeoContent = null;

  try {
    const aiDoc = await db.collection('artist_seo_content').findOne({ slug });
    if (aiDoc?.content) {
      aiSeoContent = aiDoc.content;
    }
  } catch {
    // ignore
  }

  const plainVideos = videos.map(video => ({
    id: video.id,
    video_id: video.video_id,
    title: video.title,
    song: video.song,
    artist: video.artist,
    thumbnail: video.thumbnail,
    youtube_url: video.youtube_url,
    created_at: video.created_at,
  }));

  return (
    <ArtistPageClient
      artistName={artistPattern}
      videos={plainVideos}
      slug={slug}
      adSettings={adSettings}
      initialAiContent={aiSeoContent}
    />
  );
        }
