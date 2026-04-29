import { getDb } from '@/lib/mongodb';
import { permanentRedirect } from 'next/navigation';
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
  
  // Get first video thumbnail for OG image
  let ogImage = 'https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png';
  try {
    const firstVideo = await db.collection('videos').findOne(
      { artist: { $regex: new RegExp(`^${escapedPattern}`, 'i') } },
      { projection: { thumbnail: 1 } }
    );
    if (firstVideo?.thumbnail) ogImage = firstVideo.thumbnail;
  } catch { /* use default */ }
  
  const title = `${artistPattern} Guitar & Bass Tabs - ${videoCount} Free Lessons | DadRock Tabs`;
  
  // Try to use AI-generated meta description if available
  let description;
  try {
    const artistSlug = (await import('@/lib/slugify')).artistToSlug(artistPattern);
    const aiContent = await db.collection('artist_seo_content').findOne({ slug: artistSlug });
    if (aiContent?.content?.meta_description) {
      description = aiContent.content.meta_description;
    }
  } catch { /* ignore */ }
  
  if (!description) {
    description = `Learn ${videoCount} songs by ${artistPattern} with free guitar and bass tab video lessons. Step-by-step tutorials perfect for beginner and intermediate players. Start playing ${artistPattern} riffs today!`;
  }
  
  return {
    title,
    description,
    keywords: `${artistPattern} tabs, ${artistPattern} guitar tabs, ${artistPattern} bass tabs, learn ${artistPattern} songs, ${artistPattern} tab lessons, how to play ${artistPattern}, ${artistPattern} riffs, classic rock tabs, free guitar tabs`,
    openGraph: {
      title: `${artistPattern} - Free Guitar & Bass Tab Lessons`,
      description,
      type: 'website',
      url: `https://dadrocktabs.com/artist/${slug}`,
      siteName: 'DadRock Tabs',
      images: [{ url: ogImage, width: 480, height: 360, alt: `${artistPattern} Guitar Tabs` }],
    },
    twitter: {
      card: 'summary_large_image',
      title: `${artistPattern} Guitar & Bass Tabs - ${videoCount} Free Lessons`,
      description,
      images: [ogImage],
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
    // Artist not found — permanent redirect to homepage instead of 404
    // This resolves GSC "Not found (404)" errors for dead/invalid artist URLs
    permanentRedirect('/');
  }
  
  const artistPattern = result.artistPattern;
  const escapedPattern = artistPattern.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const videos = await db.collection('videos')
    .find({ artist: { $regex: new RegExp(`^${escapedPattern}`, 'i') } })
    .sort({ created_at: -1 })
    .toArray();
  
  if (videos.length === 0) {
    // Artist pattern matched but no videos found — redirect to homepage
    permanentRedirect('/');
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
  
  // Fetch AI-generated SEO content (server-side for SSR) — lookup by slug
  let aiSeoContent = null;
  try {
    const aiDoc = await db.collection('artist_seo_content').findOne({ slug });
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
  
  // JSON-LD structured data for SEO — MusicGroup + BreadcrumbList + CollectionPage
  const jsonLd = {
    '@context': 'https://schema.org',
    '@graph': [
      {
        '@type': 'BreadcrumbList',
        'itemListElement': [
          {
            '@type': 'ListItem',
            'position': 1,
            'name': 'Home',
            'item': 'https://dadrocktabs.com'
          },
          {
            '@type': 'ListItem',
            'position': 2,
            'name': 'Artists',
            'item': 'https://dadrocktabs.com'
          },
          {
            '@type': 'ListItem',
            'position': 3,
            'name': `${displayArtistName} Tabs`,
            'item': `https://dadrocktabs.com/artist/${slug}`
          }
        ]
      },
      {
        '@type': 'MusicGroup',
        '@id': `https://dadrocktabs.com/artist/${slug}#artist`,
        'name': displayArtistName,
        'genre': 'Rock',
        'description': `Learn how to play songs by ${displayArtistName} with free guitar and bass tablature video lessons.`,
        'url': `https://dadrocktabs.com/artist/${slug}`,
      },
      {
        '@type': 'CollectionPage',
        'name': `${displayArtistName} Guitar & Bass Tabs`,
        'description': `Learn how to play songs by ${displayArtistName} with step-by-step guitar and bass tutorials.`,
        'url': `https://dadrocktabs.com/artist/${slug}`,
        'isPartOf': { '@id': 'https://dadrocktabs.com/#website' },
        'about': { '@id': `https://dadrocktabs.com/artist/${slug}#artist` },
        'publisher': { '@id': 'https://dadrocktabs.com/#organization' },
        'numberOfItems': plainVideos.length,
        'mainEntity': {
          '@type': 'ItemList',
          'numberOfItems': plainVideos.length,
          'itemListElement': plainVideos.slice(0, 10).map((video, index) => ({
            '@type': 'ListItem',
            'position': index + 1,
            'item': {
              '@type': 'VideoObject',
              'name': video.song || video.title,
              'description': `Guitar and bass tab tutorial for ${video.song || video.title} by ${displayArtistName}`,
              'thumbnailUrl': video.thumbnail,
              'uploadDate': video.created_at,
              'contentUrl': video.youtube_url,
              'publisher': { '@id': 'https://dadrocktabs.com/#organization' }
            }
          }))
        }
      }
    ]
  };
  
  // Generate FAQ data for SEO (Featured Snippets in Google)
  const topSongs = plainVideos.slice(0, 5).map(v => v.song || v.title).filter(Boolean);
  const faqItems = [
    {
      question: `How do I learn ${displayArtistName} songs on guitar?`,
      answer: `DadRock Tabs offers ${plainVideos.length} free video lessons for ${displayArtistName} songs with synchronized guitar and bass tablature. Simply select a lesson, watch the video tutorial, and follow along with the on-screen tabs. Popular lessons include ${topSongs.slice(0, 3).join(', ')}.`
    },
    {
      question: `Are ${displayArtistName} songs good for beginners?`,
      answer: aiSeoContent?.why_learn || `Many ${displayArtistName} songs feature iconic riffs that are great for developing fundamental rock guitar skills. Start with simpler songs and work your way up to more complex pieces. Our video tutorials break down each song step-by-step.`
    },
    {
      question: `What guitar gear does ${displayArtistName} use?`,
      answer: aiSeoContent?.gear_info || `${displayArtistName} is known for a distinctive rock tone. Visit our lesson pages to learn more about the gear and settings that can help you achieve a similar sound.`
    },
    {
      question: `How many ${displayArtistName} tab lessons are available?`,
      answer: `We currently have ${plainVideos.length} free ${displayArtistName} guitar and bass tab video lessons available on DadRock Tabs, including ${topSongs.slice(0, 3).join(', ')}${topSongs.length > 3 ? ' and more' : ''}.`
    },
    {
      question: `What is ${displayArtistName}'s playing style?`,
      answer: aiSeoContent?.playing_style || `${displayArtistName} is known for their distinctive rock guitar style. Our tab lessons help you learn the key techniques and riffs that define their sound.`
    },
  ];
  
  // FAQ Schema (JSON-LD) for Google Featured Snippets
  const faqJsonLd = {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    'mainEntity': faqItems.map(faq => ({
      '@type': 'Question',
      'name': faq.question,
      'acceptedAnswer': {
        '@type': 'Answer',
        'text': faq.answer
      }
    }))
  };
  
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
      />
      <ArtistPageClient 
        artistName={displayArtistName} 
        videos={plainVideos} 
        slug={slug}
        adSettings={adSettings}
        initialAiContent={aiSeoContent}
        faqItems={faqItems}
      />
    </>
  );
}
