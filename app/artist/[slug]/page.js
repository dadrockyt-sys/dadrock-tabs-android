import { getDb } from '@/lib/mongodb';
import { notFound } from 'next/navigation';
import { generateAlternates } from '@/lib/seo';
import { slugToArtistPattern, artistToSlug, artistPatternsForSlug } from '@/lib/slugify';
import ArtistPageClient from './ArtistPageClient';

const INVALID_ARTIST_SLUGS = new Set([
  'memorial-video-neverforget-johnlennon-bobmarley',
  'face-the-slayer',
  'children-of-the-grave',
  'heart-roger-fisher-learn',
]);

// Build one Mongo query for a canonical artist plus any known database aliases.
function buildArtistQuery(patterns) {
  const clauses = patterns.map((pattern) => {
    const escaped = pattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    return { artist: { $regex: new RegExp(`^${escaped}`, 'i') } };
  });

  return clauses.length === 1 ? clauses[0] : { $or: clauses };
}

function normalizeLessonCountMentions(content, lessonCount) {
  if (!content || !Number.isFinite(lessonCount)) return content;

  try {
    return JSON.parse(
      JSON.stringify(content).replace(
        /\b\d+(?=\s+lessons?\b)/gi,
        String(lessonCount)
      )
    );
  } catch {
    return content;
  }
}

// Find artist name from slug by checking the database.
async function findArtistBySlug(db, slug) {
  if (INVALID_ARTIST_SLUGS.has(slug)) {
    return null;
  }

  const directPatterns = artistPatternsForSlug(slug);
  const directCount = await db.collection('videos').countDocuments(
    buildArtistQuery(directPatterns)
  );

  if (directCount > 0) {
    return {
      artistPattern: slugToArtistPattern(slug),
      artistPatterns: directPatterns,
      method: directPatterns.length > 1 ? 'alias-group' : 'direct',
    };
  }

  const allArtists = await db.collection('videos').distinct('artist');
  const matchedArtists = allArtists
    .filter((artist) => artistToSlug(artist) === slug)
    .map((artist) => artist.replace(/ -$/, '').trim());

  if (matchedArtists.length > 0) {
    return {
      artistPattern: matchedArtists[0],
      artistPatterns: [...new Set(matchedArtists)],
      method: 'slug-match',
    };
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
  const artistQuery = buildArtistQuery(result.artistPatterns || [artistPattern]);

  const videoCount = await db.collection('videos').countDocuments(artistQuery);
  const lessonLabel = videoCount === 1 ? 'Lesson' : 'Lessons';
  const songPhrase = videoCount === 1 ? 'a song' : `${videoCount} songs`;

  const title = `${artistPattern} Guitar & Bass Tabs - ${videoCount} Free ${lessonLabel} | DadRock Tabs`;
  const description = `Learn ${songPhrase} by ${artistPattern} with free guitar and bass tab video lessons. Step-by-step tutorials perfect for beginner and intermediate players.`;
  const canonicalUrl = `https://dadrocktabs.com/artist/${slug}`;

  let thumbnail = 'https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png';
  try {
    const firstVideo = await db.collection('videos').findOne(
      artistQuery,
      { projection: { thumbnail: 1 } }
    );
    if (firstVideo?.thumbnail) thumbnail = firstVideo.thumbnail;
  } catch { /* use default */ }

  const dynamicOgImage = `https://dadrocktabs.com/api/og?title=${encodeURIComponent(artistPattern)}&type=artist&thumb=${encodeURIComponent(thumbnail)}`;

  return {
    title,
    description,
    alternates: generateAlternates(`/artist/${slug}`),
    openGraph: {
      title,
      description,
      type: 'website',
      url: canonicalUrl,
      siteName: 'DadRock Tabs',
      images: [{
        url: dynamicOgImage,
        width: 1200,
        height: 630,
        alt: title,
      }],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [dynamicOgImage],
    },
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
  const artistQuery = buildArtistQuery(result.artistPatterns || [artistPattern]);

  const videos = await db.collection('videos')
    .find(artistQuery)
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
      aiSeoContent = normalizeLessonCountMentions(aiDoc.content, videos.length);
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
