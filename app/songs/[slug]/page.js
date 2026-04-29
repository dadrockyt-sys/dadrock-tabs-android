import { getDb } from '@/lib/mongodb';
import { generateSeoContent } from '@/lib/artistData';
import { generateAlternates } from '@/lib/seo';
import SongPageClient from './SongPageClient';
import { permanentRedirect } from 'next/navigation';
import { artistToSlug } from '@/lib/slugify';

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
    const title = `${song.title} - ${cleanArtist} | Free Guitar & Bass Tab Lesson`;
    const description = `Learn to play "${song.title}" by ${cleanArtist} with our free guitar and bass tab video lesson. Step-by-step tutorial with synchronized tablature — perfect for all skill levels!`;
    const thumbUrl = song.thumbnail || `https://img.youtube.com/vi/${song.videoId}/maxresdefault.jpg`;
    const ogImage = `https://dadrocktabs.com/api/og?title=${encodeURIComponent(song.title)}&artist=${encodeURIComponent(cleanArtist)}&type=song&thumb=${encodeURIComponent(thumbUrl)}`;

    return {
      title,
      description,
      keywords: `${song.title} tab, ${song.title} guitar tab, ${cleanArtist} ${song.title}, how to play ${song.title}, ${cleanArtist} bass tab, ${song.title} lesson, ${cleanArtist} guitar tutorial, free guitar tabs, DadRock Tabs`,
      openGraph: {
        title: `Learn "${song.title}" by ${cleanArtist} - Guitar & Bass Tab`,
        description,
        type: 'video.other',
        url: `https://dadrocktabs.com/songs/${slug}`,
        siteName: 'DadRock Tabs',
        images: [{ url: ogImage, width: 1200, height: 630, alt: `${song.title} by ${cleanArtist} - Guitar Tab` }],
      },
      twitter: {
        card: 'summary_large_image',
        title: `${song.title} - ${cleanArtist} | Guitar & Bass Tab`,
        description,
        images: [ogImage],
      },
      alternates: generateAlternates(`/songs/${slug}`),
    };
  } catch {
    return { title: 'Song | DadRock Tabs' };
  }
}

// Helper: try to find artist slug from a song slug like "van-halen-best-of-both-worlds"
async function findArtistFromSongSlug(db, songSlug) {
  const allArtists = await db.collection('videos').distinct('artist');
  // Generate slugs for all artists and find which one the song slug starts with
  // Sort by slug length descending so we match the longest (most specific) artist first
  const artistSlugs = allArtists
    .map(a => ({ name: a, slug: artistToSlug(a) }))
    .filter(a => a.slug) // remove empty
    .sort((a, b) => b.slug.length - a.slug.length);
  
  for (const { slug: aSlug } of artistSlugs) {
    if (songSlug.startsWith(aSlug + '-') || songSlug === aSlug) {
      return aSlug;
    }
  }
  return null;
}

export default async function SongPage({ params }) {
  const { slug } = await params;
  
  const db = await getDb();
  const song = await db.collection('song_pages').findOne({ slug });
  
  if (!song) {
    // Song not found — try to redirect to the artist page instead of 404
    const artistSlug = await findArtistFromSongSlug(db, slug);
    if (artistSlug) {
      permanentRedirect(`/artist/${artistSlug}`);
    }
    // No artist match either — redirect to homepage
    permanentRedirect('/');
  }

  let adSettings = null;
  let aiSeoContent = null;

  try {
    // Fetch AI-generated SEO content (server-side for SSR)
    try {
      const aiDoc = await db.collection('song_seo_content').findOne({ slug });
      if (aiDoc?.content) {
        aiSeoContent = aiDoc.content;
      }
    } catch { /* ignore */ }

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
    permanentRedirect('/');
  }

  const cleanArtist = song.artist?.replace(/ -$/, '').trim() || 'DadRock Tabs';
  const seoContent = generateSeoContent(song.title, song.artist);

  // JSON-LD Schema — MusicRecording + VideoObject + BreadcrumbList + HowTo
  const durationMinutes = song.duration ? Math.floor(song.duration / 60) : 5;
  const schema = {
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
            'name': `${cleanArtist} Tabs`,
            'item': `https://dadrocktabs.com/artist/${artistToSlug(cleanArtist)}`
          },
          {
            '@type': 'ListItem',
            'position': 3,
            'name': song.title,
            'item': `https://dadrocktabs.com/songs/${slug}`
          }
        ]
      },
      {
        '@type': 'MusicRecording',
        'name': song.title,
        'byArtist': {
          '@type': 'MusicGroup',
          'name': cleanArtist,
          'url': `https://dadrocktabs.com/artist/${artistToSlug(cleanArtist)}`
        },
        'genre': 'Rock',
        'url': `https://dadrocktabs.com/songs/${slug}`,
        'description': `Learn to play ${song.title} by ${cleanArtist} with free guitar and bass tablature.`
      },
      {
        '@type': 'VideoObject',
        'name': `${song.title} - ${cleanArtist} Guitar & Bass Tab Tutorial`,
        'description': `Learn to play ${song.title} by ${cleanArtist} with this step-by-step guitar and bass tablature video lesson. Free tutorial from DadRock Tabs.`,
        'thumbnailUrl': song.thumbnail,
        'uploadDate': song.publishedAt || new Date().toISOString(),
        'contentUrl': `https://www.youtube.com/watch?v=${song.videoId}`,
        'embedUrl': `https://www.youtube.com/embed/${song.videoId}`,
        'duration': song.duration ? `PT${Math.floor(song.duration / 60)}M${song.duration % 60}S` : undefined,
        'interactionStatistic': {
          '@type': 'InteractionCounter',
          'interactionType': { '@type': 'WatchAction' },
          'userInteractionCount': song.viewCount || 0,
        },
        'publisher': { '@id': 'https://dadrocktabs.com/#organization' },
      },
      {
        '@type': 'HowTo',
        'name': `How to Play "${song.title}" by ${cleanArtist} on Guitar`,
        'description': `Step-by-step guide to learning "${song.title}" by ${cleanArtist} using free guitar and bass tablature video lessons from DadRock Tabs.`,
        'totalTime': `PT${durationMinutes + 15}M`,
        'estimatedCost': { '@type': 'MonetaryAmount', 'currency': 'USD', 'value': '0' },
        'supply': [
          { '@type': 'HowToSupply', 'name': 'Electric or acoustic guitar' },
          { '@type': 'HowToSupply', 'name': 'Guitar pick' },
          { '@type': 'HowToSupply', 'name': 'Guitar amplifier (optional)' }
        ],
        'tool': [
          { '@type': 'HowToTool', 'name': 'Computer or smartphone for video playback' },
          { '@type': 'HowToTool', 'name': 'Guitar tuner' }
        ],
        'step': [
          {
            '@type': 'HowToStep',
            'position': 1,
            'name': 'Watch the Full Lesson',
            'text': `Start by watching the complete tab tutorial video for "${song.title}" by ${cleanArtist} to get familiar with the song structure, riffs, and overall feel.`,
            'url': `https://dadrocktabs.com/songs/${slug}`,
            'image': song.thumbnail || `https://img.youtube.com/vi/${song.videoId}/maxresdefault.jpg`,
          },
          {
            '@type': 'HowToStep',
            'position': 2,
            'name': 'Learn the Main Riff',
            'text': `Focus on the main guitar riff of "${song.title}". Follow the on-screen tablature notation, playing each note slowly. Pay attention to the picking pattern and timing.`,
            'url': `https://dadrocktabs.com/songs/${slug}`,
          },
          {
            '@type': 'HowToStep',
            'position': 3,
            'name': 'Practice at Slow Tempo',
            'text': `Use YouTube's playback speed controls to slow the video to 0.5x or 0.75x speed. Practice each section until you can play it cleanly without mistakes.`,
            'url': `https://dadrocktabs.com/songs/${slug}`,
          },
          {
            '@type': 'HowToStep',
            'position': 4,
            'name': 'Build Up to Full Speed',
            'text': `Gradually increase the playback speed as you get comfortable. Work through the verse, chorus, and bridge sections until you can play the full song at normal tempo.`,
            'url': `https://dadrocktabs.com/songs/${slug}`,
          },
          {
            '@type': 'HowToStep',
            'position': 5,
            'name': 'Play Along with the Recording',
            'text': `Once you've mastered the tab, play along with the original ${cleanArtist} recording to test your timing and feel. Congratulations — you've learned "${song.title}"!`,
            'url': `https://dadrocktabs.com/songs/${slug}`,
          }
        ],
        'image': song.thumbnail || `https://img.youtube.com/vi/${song.videoId}/maxresdefault.jpg`,
        'url': `https://dadrocktabs.com/songs/${slug}`,
      }
    ]
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

  // Fetch more songs by the same artist for internal linking
  let moreSongsByArtist = [];
  try {
    const artistSongs = await db.collection('song_pages')
      .find({ 
        artist: { $regex: new RegExp(`^${cleanArtist.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'i') },
        slug: { $ne: slug } // Exclude current song
      })
      .limit(6)
      .toArray();
    
    moreSongsByArtist = artistSongs.map(s => ({
      slug: s.slug,
      title: s.title,
      thumbnail: s.thumbnail,
      videoId: s.videoId,
    }));
  } catch { /* ignore */ }

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
        initialAiContent={aiSeoContent}
        moreSongs={moreSongsByArtist}
      />
    </>
  );
}
