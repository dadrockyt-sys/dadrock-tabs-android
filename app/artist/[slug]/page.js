import { getDb } from '@/lib/mongodb';
import { notFound } from 'next/navigation';
import { generateAlternates } from '@/lib/seo';
import { slugToArtistPattern, artistToSlug } from '@/lib/slugify';
import ArtistPageClient from './ArtistPageClient';

// Find artist name from slug by checking the database
// This handles cases where slugToArtistPattern can't reverse the slug correctly
async function findArtistBySlug(db, slug) {
  // First try the direct slug-to-pattern mapping
  const directPattern = slugToArtistPattern(slug);
  const escapedDirect = directPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const directCount = await db.collection('videos').countDocuments({
    artist: { $regex: new RegExp(`^${escapedDirect}`, 'i') }
  });
  
  if (directCount > 0) {
    return { artistPattern: directPattern, method: 'direct' };
  }
  
  // Fallback: get all unique artists, generate their slugs, find the match
  const allArtists = await db.collection('videos').distinct('artist');
  for (const artist of allArtists) {
    const generatedSlug = artistToSlug(artist);
    if (generatedSlug === slug) {
      return { artistPattern: artist.replace(/ -$/, '').trim(), method: 'slug-match' };
    }
  }
  
  return null;
}

// Generate metadata for SEO
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
  
  const title = `Learn ${artistPattern} Songs - Free Guitar & Bass Tabs | DadRock Tabs`;
  
  // Try to use AI-generated meta description if available
  let description;
  try {
    const aiContent = await db.collection('artist_seo_content').findOne({ artist: artistPattern });
    if (aiContent?.content?.meta_description) {
      description = aiContent.content.meta_description;
    }
  } catch { /* ignore */ }
  
  if (!description) {
    description = `Learn how to play songs by ${artistPattern} with step-by-step guitar and bass tutorials. These riffs are some of the most recognizable classic rock riffs ever written and perfect for beginner and intermediate players. ${videoCount} lessons available.`;
  }
  
  return {
    title,
    description,
    keywords: `${artistPattern} tabs, ${artistPattern} guitar tabs, ${artistPattern} bass tabs, ${artistPattern} tutorial, learn ${artistPattern} songs, ${artistPattern} lessons, classic rock tabs`,
    openGraph: {
      title,
      description,
      type: 'website',
      url: `https://dadrocktabs.com/artist/${slug}`,
      siteName: 'DadRock Tabs',
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
    },
    alternates: generateAlternates(`/artist/${slug}`),
  };
}

// Server component to fetch data
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
  
  // Fetch ad settings
  const settings = await db.collection('settings').findOne({ type: 'site' });
  const adSettings = {
    ad_link: settings?.ad_link || 'https://my-store-b8bb42.creator-spring.com/',
    ad_image: settings?.ad_image || '',
    ad_headline: settings?.ad_headline || 'Check Out Our Merchandise!',
    ad_description: settings?.ad_description || 'Support DadRock Tabs by grabbing some awesome gear',
    ad_button_text: settings?.ad_button_text || 'Shop Now',
    ad_duration: settings?.ad_duration || 5,
  };

  // Get the display name (use the clean version without " -")
  const displayArtistName = artistPattern;
  
  // Fetch AI-generated SEO content (server-side for SSR)
  let aiSeoContent = null;
  try {
    const aiDoc = await db.collection('artist_seo_content').findOne({ artist: artistPattern });
    if (aiDoc?.content) {
      aiSeoContent = aiDoc.content;
    }
  } catch { /* ignore */ }
  
  // Convert MongoDB documents to plain objects
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
  
  // JSON-LD structured data for SEO
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    'name': `${displayArtistName} Guitar & Bass Tabs`,
    'description': `Learn how to play songs by ${displayArtistName} with step-by-step guitar and bass tutorials.`,
    'url': `https://dadrocktabs.com/artist/${slug}`,
    'publisher': {
      '@type': 'Organization',
      'name': 'DadRock Tabs',
      'url': 'https://dadrocktabs.com'
    },
    'mainEntity': {
      '@type': 'MusicGroup',
      'name': displayArtistName,
      'genre': 'Rock'
    },
    'numberOfItems': plainVideos.length,
    'itemListElement': plainVideos.slice(0, 10).map((video, index) => ({
      '@type': 'ListItem',
      'position': index + 1,
      'item': {
        '@type': 'VideoObject',
        'name': video.song || video.title,
        'description': `Guitar and bass tutorial for ${video.song || video.title} by ${displayArtistName}`,
        'thumbnailUrl': video.thumbnail,
        'uploadDate': video.created_at,
        'contentUrl': video.youtube_url
      }
    }))
  };
  
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <ArtistPageClient 
        artistName={displayArtistName} 
        videos={plainVideos} 
        slug={slug}
        adSettings={adSettings}
        initialAiContent={aiSeoContent}
      />
    </>
  );
}
