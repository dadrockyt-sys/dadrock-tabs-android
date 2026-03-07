import { getDb } from '@/lib/mongodb';
import { notFound } from 'next/navigation';
import ArtistPageClient from './ArtistPageClient';

// Convert slug to artist name for database lookup
function slugToArtistName(slug) {
  // Handle special cases
  const specialCases = {
    'acdc': 'AC/DC',
    'guns-n-roses': "Guns N' Roses",
    'motorhead': 'Motörhead',
    'blue-oyster-cult': 'Blue Öyster Cult',
    'motley-crue': 'Mötley Crüe',
  };
  
  if (specialCases[slug]) {
    return specialCases[slug];
  }
  
  // Convert slug back to name (replace hyphens with spaces, title case)
  return slug
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

// Generate metadata for SEO
export async function generateMetadata({ params }) {
  const slug = params.slug;
  const artistName = slugToArtistName(slug);
  
  const db = await getDb();
  const videoCount = await db.collection('videos').countDocuments({
    artist: { $regex: new RegExp(`^${artistName}$`, 'i') }
  });
  
  if (videoCount === 0) {
    return {
      title: 'Artist Not Found | DadRock Tabs',
      description: 'This artist page could not be found.',
    };
  }
  
  const title = `Learn ${artistName} Songs - Free Guitar & Bass Tabs | DadRock Tabs`;
  const description = `Learn how to play songs by ${artistName} with step-by-step guitar and bass tutorials. These riffs are some of the most recognizable classic rock riffs ever written and perfect for beginner and intermediate players. ${videoCount} lessons available.`;
  
  return {
    title,
    description,
    keywords: `${artistName} tabs, ${artistName} guitar tabs, ${artistName} bass tabs, ${artistName} tutorial, learn ${artistName} songs, ${artistName} lessons, classic rock tabs`,
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
    alternates: {
      canonical: `https://dadrocktabs.com/artist/${slug}`,
    },
  };
}

// Server component to fetch data
export default async function ArtistPage({ params }) {
  const slug = params.slug;
  const artistName = slugToArtistName(slug);
  
  const db = await getDb();
  
  // Find all videos for this artist (case-insensitive)
  const videos = await db.collection('videos')
    .find({ artist: { $regex: new RegExp(`^${artistName}$`, 'i') } })
    .sort({ created_at: -1 })
    .toArray();
  
  if (videos.length === 0) {
    notFound();
  }
  
  // Get the actual artist name from the first video (preserves original casing)
  const actualArtistName = videos[0].artist;
  
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
    'name': `${actualArtistName} Guitar & Bass Tabs`,
    'description': `Learn how to play songs by ${actualArtistName} with step-by-step guitar and bass tutorials.`,
    'url': `https://dadrocktabs.com/artist/${slug}`,
    'publisher': {
      '@type': 'Organization',
      'name': 'DadRock Tabs',
      'url': 'https://dadrocktabs.com'
    },
    'mainEntity': {
      '@type': 'MusicGroup',
      'name': actualArtistName,
      'genre': 'Rock'
    },
    'numberOfItems': plainVideos.length,
    'itemListElement': plainVideos.slice(0, 10).map((video, index) => ({
      '@type': 'ListItem',
      'position': index + 1,
      'item': {
        '@type': 'VideoObject',
        'name': video.song || video.title,
        'description': `Guitar and bass tutorial for ${video.song || video.title} by ${actualArtistName}`,
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
        artistName={actualArtistName} 
        videos={plainVideos} 
        slug={slug}
      />
    </>
  );
}
