import { getDb } from '@/lib/mongodb';
import { notFound } from 'next/navigation';
import ArtistPageClient from './ArtistPageClient';

// Convert slug to artist name pattern for database lookup
function slugToArtistPattern(slug) {
  // Handle special cases - must match exactly what's in the database
  const specialCases = {
    // Symbols and special characters
    'acdc': 'AC/DC',
    
    // Plain text versions (database doesn't use special chars like ö, ü)
    'motorhead': 'Motorhead',
    'blue-oyster-cult': 'Blue Oyster Cult',
    'motley-crue': 'Motley Crue',
    
    // Apostrophe handling - database uses apostrophes
    'janes-addiction': "Jane's Addiction",
    'enuff-znuff': "Enuff Z'Nuff",
    'drivin-n-cryin': "Drivin' 'N' Cryin'",
    
    // LA vs L.A. - database uses "LA Guns"
    'la-guns': 'LA Guns',
    
    // Case sensitivity fixes
    'zz-top': 'ZZ Top',
    'ufo': 'UFO',
    'reo-speedwagon': 'REO Speedwagon',
    'elo': 'ELO',
    'bto': 'BTO',
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
  const resolvedParams = await params;
  const slug = resolvedParams.slug;
  const artistPattern = slugToArtistPattern(slug);
  
  const db = await getDb();
  // Search for artist name at the start of the field (handles "Metallica -" and "Metallica")
  const videoCount = await db.collection('videos').countDocuments({
    artist: { $regex: new RegExp(`^${artistPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'i') }
  });
  
  if (videoCount === 0) {
    return {
      title: 'Artist Not Found | DadRock Tabs',
      description: 'This artist page could not be found.',
    };
  }
  
  const title = `Learn ${artistPattern} Songs - Free Guitar & Bass Tabs | DadRock Tabs`;
  const description = `Learn how to play songs by ${artistPattern} with step-by-step guitar and bass tutorials. These riffs are some of the most recognizable classic rock riffs ever written and perfect for beginner and intermediate players. ${videoCount} lessons available.`;
  
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
    alternates: {
      canonical: `https://dadrocktabs.com/artist/${slug}`,
    },
  };
}

// Server component to fetch data
export default async function ArtistPage({ params }) {
  const resolvedParams = await params;
  const slug = resolvedParams.slug;
  const artistPattern = slugToArtistPattern(slug);
  
  const db = await getDb();
  
  // Find all videos for this artist (matches "Metallica", "Metallica -", etc.)
  // Use regex to match artist names that START with the pattern
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
      />
    </>
  );
}
