import { getDb } from '@/lib/mongodb';
import { generateSeoContent } from '@/lib/artistData';
import { generateAlternates } from '@/lib/seo';
import { getSeoMeta } from '@/lib/seoTranslations';
import { getSubPageTranslation } from '@/lib/subPageI18n';
import SongPageClient from '../../../songs/[slug]/SongPageClient';
import { permanentRedirect, notFound } from 'next/navigation';
import { artistToSlug } from '@/lib/slugify';

function cleanLocalizedDescription(lang, value) {
  if (!value) return value;
  if (lang === 'es') {
    return value.replace(/lezión/gi, 'lección');
  }
  return value;
}

export async function generateMetadata({ params }) {
  const { lang, slug } = await params;

  try {
    const db = await getDb();
    const song = await db.collection('song_pages').findOne({ slug });

    if (!song) {
      return { title: 'Song Not Found | DadRock Tabs' };
    }

    const cleanArtist = song.artist?.replace(/\s*-\s*$/, '').trim() || 'DadRock Tabs';
    const localizedMeta = getSeoMeta(lang, 'song', {
      song: song.title,
      artist: cleanArtist,
    });
    const title = localizedMeta.title;

    // Localized route metadata must stay in the route language. Some older
    // song translation records contain an untranslated English meta_description,
    // so do not let database prose override the vetted language template here.
    const description = cleanLocalizedDescription(lang, localizedMeta.description);

    const thumbUrl = song.thumbnail || `https://img.youtube.com/vi/${song.videoId}/maxresdefault.jpg`;
    const ogImage = `https://dadrocktabs.com/api/og?title=${encodeURIComponent(song.title)}&artist=${encodeURIComponent(cleanArtist)}&type=song&thumb=${encodeURIComponent(thumbUrl)}`;

    return {
      title,
      description,
      keywords: `${song.title}, ${cleanArtist}, guitar tab, bass tab, guitar lesson, bass lesson, DadRock Tabs`,
      openGraph: {
        title,
        description,
        type: 'video.other',
        url: `https://dadrocktabs.com/${lang}/songs/${slug}`,
        siteName: 'DadRock Tabs',
        images: [{ url: ogImage, width: 1200, height: 630, alt: title }],
      },
      twitter: {
        card: 'summary_large_image',
        title,
        description,
        images: [ogImage],
      },
      alternates: generateAlternates(`/songs/${slug}`, lang),
    };
  } catch {
    return { title: 'Song | DadRock Tabs' };
  }
}

async function findArtistFromSongSlug(db, songSlug) {
  const allArtists = await db.collection('videos').distinct('artist');
  const artistSlugs = allArtists
    .map(a => ({ name: a, slug: artistToSlug(a) }))
    .filter(a => a.slug)
    .sort((a, b) => b.slug.length - a.slug.length);

  for (const { slug: aSlug } of artistSlugs) {
    if (songSlug.startsWith(aSlug + '-') || songSlug === aSlug) {
      return aSlug;
    }
  }
  return null;
}

export default async function SongPage({ params }) {
  const { lang, slug } = await params;
  const t = getSubPageTranslation(lang);

  const db = await getDb();
  const song = await db.collection('song_pages').findOne({ slug });

  if (!song) {
    const savedRedirect = await db.collection('song_redirects').findOne(
      { slug },
      { projection: { target: 1 } }
    );

    if (savedRedirect?.target?.startsWith('/')) {
      const localizedTarget =
        lang && lang !== 'en'
          ? `/${lang}${savedRedirect.target}`
          : savedRedirect.target;
      permanentRedirect(localizedTarget);
    }

    const artistSlug = await findArtistFromSongSlug(db, slug);
    if (artistSlug) {
      const target = lang && lang !== 'en'
        ? `/${lang}/artist/${artistSlug}`
        : `/artist/${artistSlug}`;
      permanentRedirect(target);
    }

    notFound();
  }

  let adSettings = null;
  let aiSeoContent = null;

  try {
    // English source content is only needed on the English route. Keeping it out
    // of translated page payloads also prevents stale English SEO prose from
    // becoming a fallback during hydration.
    if (lang === 'en') {
      try {
        const aiDoc = await db.collection('song_seo_content').findOne({ slug });
        if (aiDoc?.content) {
          aiSeoContent = aiDoc.content;
        }
      } catch { /* ignore */ }
    }

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

  const cleanArtist = song.artist?.replace(/\s*-\s*$/, '').trim() || 'DadRock Tabs';
  let seoContent = generateSeoContent(song.title, song.artist);

  if (lang !== 'en') {
    const songSeoDoc = await db.collection('song_seo_content').findOne({ slug: song.slug });
    if (songSeoDoc?.translations?.[lang]) {
      seoContent = songSeoDoc.translations[lang];
    }
  }

  if (seoContent?.meta_description) {
    if (lang === 'en') {
      seoContent = {
        ...seoContent,
        meta_description: cleanLocalizedDescription(lang, seoContent.meta_description),
      };
    } else {
      // Rich translated body content remains useful, but meta_description is
      // intentionally discarded because older records may contain English text.
      const { meta_description: _discardedMetaDescription, ...localizedSeoContent } = seoContent;
      seoContent = localizedSeoContent;
    }
  }

  const localizedMeta = getSeoMeta(lang, 'song', {
    song: song.title,
    artist: cleanArtist,
  });
  const schemaDescription = cleanLocalizedDescription(
    lang,
    lang === 'en'
      ? seoContent?.meta_description || localizedMeta.description
      : localizedMeta.description
  );

  const durationMinutes = song.duration ? Math.floor(song.duration / 60) : 5;
  const localizedHomeUrl = `https://dadrocktabs.com/${lang}`;
  const localizedArtistUrl = `https://dadrocktabs.com/${lang}/artist/${artistToSlug(cleanArtist)}`;
  const localizedSongUrl = `https://dadrocktabs.com/${lang}/songs/${slug}`;

  const schemaGraph = [
    {
      '@type': 'BreadcrumbList',
      'itemListElement': [
        {
          '@type': 'ListItem',
          'position': 1,
          'name': t.home,
          'item': localizedHomeUrl
        },
        {
          '@type': 'ListItem',
          'position': 2,
          'name': cleanArtist,
          'item': localizedArtistUrl
        },
        {
          '@type': 'ListItem',
          'position': 3,
          'name': song.title,
          'item': localizedSongUrl
        }
      ]
    },
    {
      '@type': 'MusicRecording',
      'name': song.title,
      'byArtist': {
        '@type': 'MusicGroup',
        'name': cleanArtist,
        'url': localizedArtistUrl
      },
      'genre': 'Rock',
      'url': localizedSongUrl,
      'description': schemaDescription,
      'inLanguage': lang,
    },
    {
      '@type': 'VideoObject',
      'name': localizedMeta.title,
      'description': schemaDescription,
      'thumbnailUrl': song.thumbnail,
      'uploadDate': song.publishedAt || undefined,
      'embedUrl': `https://www.youtube.com/embed/${song.videoId}`,
      'duration': song.duration ? `PT${Math.floor(song.duration / 60)}M${song.duration % 60}S` : undefined,
      'inLanguage': lang,
      'interactionStatistic': {
        '@type': 'InteractionCounter',
        'interactionType': { '@type': 'WatchAction' },
        'userInteractionCount': song.viewCount || 0,
      },
      'publisher': { '@id': 'https://dadrocktabs.com/#organization' },
    },
  ];

  // Keep the detailed HowTo schema on the English page only. The translated
  // pages use localized MusicRecording/VideoObject schema rather than mixing
  // English HowTo instructions into otherwise localized documents.
  if (lang === 'en') {
    schemaGraph.push({
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
          'url': localizedSongUrl,
          'image': song.thumbnail || `https://img.youtube.com/vi/${song.videoId}/maxresdefault.jpg`,
        },
        {
          '@type': 'HowToStep',
          'position': 2,
          'name': 'Learn the Main Riff',
          'text': `Focus on the main guitar riff of "${song.title}". Follow the on-screen tablature notation, playing each note slowly. Pay attention to the picking pattern and timing.`,
          'url': localizedSongUrl,
        },
        {
          '@type': 'HowToStep',
          'position': 3,
          'name': 'Practice at Slow Tempo',
          'text': `Use YouTube's playback speed controls to slow the video to 0.5x or 0.75x speed. Practice each section until you can play it cleanly without mistakes.`,
          'url': localizedSongUrl,
        },
        {
          '@type': 'HowToStep',
          'position': 4,
          'name': 'Build Up to Full Speed',
          'text': `Gradually increase the playback speed as you get comfortable. Work through the verse, chorus, and bridge sections until you can play the full song at normal tempo.`,
          'url': localizedSongUrl,
        },
        {
          '@type': 'HowToStep',
          'position': 5,
          'name': 'Play Along with the Recording',
          'text': `Once you've mastered the tab, play along with the original ${cleanArtist} recording to test your timing and feel. Congratulations — you've learned "${song.title}"!`,
          'url': localizedSongUrl,
        }
      ],
      'image': song.thumbnail || `https://img.youtube.com/vi/${song.videoId}/maxresdefault.jpg`,
      'url': localizedSongUrl,
    });
  }

  const schema = {
    '@context': 'https://schema.org',
    '@graph': schemaGraph,
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

  let moreSongsByArtist = [];
  try {
    const artistSongs = await db.collection('song_pages')
      .find({
        artist: { $regex: new RegExp(`^${cleanArtist.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}`, 'i') },
        slug: { $ne: slug }
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
        currentLang={lang}
      />
    </>
  );
}
