import { getDb } from '@/lib/mongodb';
import { notFound } from 'next/navigation';
import { slugToArtistPattern, artistToSlug } from '@/lib/slugify';
import ArtistPageClient from './ArtistPageClient';
import { locales } from '@/lib/i18n';
import { getSubPageTranslation } from '@/lib/subPageI18n';
import { generateAlternates } from '@/lib/seo';
import { getSeoMeta } from '@/lib/seoTranslations';

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

function normalizeArtistSeoCounts(content, slug, lessonCount) {
  if (!content || slug !== 'black-sabbath' || !Number.isFinite(lessonCount)) {
    return content;
  }

  try {
    return JSON.parse(
      JSON.stringify(content).replace(/\b75\b/g, String(lessonCount))
    );
  } catch {
    return content;
  }
}

function extractYouTubeVideoId(video) {
  const directId = String(video?.video_id || '').trim();
  if (/^[a-zA-Z0-9_-]{11}$/.test(directId)) return directId;

  const rawUrl = String(video?.youtube_url || '').trim();
  if (!rawUrl) return '';

  try {
    const url = new URL(rawUrl);
    const host = url.hostname.replace(/^www\./, '');

    if (host === 'youtu.be') {
      const id = url.pathname.split('/').filter(Boolean)[0] || '';
      return /^[a-zA-Z0-9_-]{11}$/.test(id) ? id : '';
    }

    if (host === 'youtube.com' || host === 'm.youtube.com') {
      const watchId = url.searchParams.get('v') || '';
      if (/^[a-zA-Z0-9_-]{11}$/.test(watchId)) return watchId;

      const parts = url.pathname.split('/').filter(Boolean);
      if (['embed', 'shorts', 'live'].includes(parts[0])) {
        const id = parts[1] || '';
        if (/^[a-zA-Z0-9_-]{11}$/.test(id)) return id;
      }
    }
  } catch { /* ignore malformed URLs */ }

  return '';
}

export async function generateMetadata({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang;
  const slug = resolvedParams.slug;

  if (!locales.includes(lang)) {
    return {
      title: 'Page Not Found | DadRock Tabs',
      description: 'This language page could not be found.',
    };
  }

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
  const lessonCount = await db.collection('videos').countDocuments({
    artist: { $regex: new RegExp(`^${escapedPattern}`, 'i') }
  });

  let ogImage = 'https://customer-assets.emergentagent.com/job_music-tab-finder/artifacts/qsso7cx0_dadrockmetal.png';
  try {
    const firstVideo = await db.collection('videos').findOne(
      { artist: { $regex: new RegExp(`^${escapedPattern}`, 'i') } },
      { projection: { thumbnail: 1 } }
    );
    if (firstVideo?.thumbnail) ogImage = firstVideo.thumbnail;
  } catch { /* use default */ }

  const localizedMeta = getSeoMeta(lang, 'artist', { artist: artistPattern });
  const title = localizedMeta.title;
  let description = localizedMeta.description;

  try {
    const artistSlug = artistToSlug(artistPattern);
    const aiContent = await db.collection('artist_seo_content').findOne({ slug: artistSlug });
    const rawLocalizedContent =
      aiContent?.content?.[lang] ||
      (lang === 'en' ? aiContent?.content?.en || aiContent?.content : null);
    const localizedContent = normalizeArtistSeoCounts(rawLocalizedContent, slug, lessonCount);

    if (localizedContent?.meta_description) {
      description = localizedContent.meta_description;
    }
  } catch { /* use localized template */ }

  const localizedArtistUrl = `https://dadrocktabs.com/${lang}/artist/${slug}`;
  const dynamicOgImage = `https://dadrocktabs.com/api/og?title=${encodeURIComponent(artistPattern)}&type=artist&thumb=${encodeURIComponent(ogImage)}`;

  return {
    title,
    description,
    keywords: `${artistPattern}, guitar tabs, bass tabs, guitar lessons, bass lessons, rock tabs, DadRock Tabs`,
    openGraph: {
      title,
      description,
      type: 'website',
      url: localizedArtistUrl,
      siteName: 'DadRock Tabs',
      images: [{ url: dynamicOgImage, width: 1200, height: 630, alt: `${artistPattern} Guitar Tabs` }],
    },
    twitter: {
      card: 'summary_large_image',
      title,
      description,
      images: [dynamicOgImage],
    },
    alternates: generateAlternates(`/artist/${slug}`, lang),
  };
}

export default async function ArtistPage({ params }) {
  const resolvedParams = await params;
  const lang = resolvedParams.lang;
  const slug = resolvedParams.slug;
  const t = getSubPageTranslation(lang);

  if (!locales.includes(lang)) {
    notFound();
  }

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

  const displayArtistName = artistPattern;

  let aiSeoContent = null;
  try {
    const aiDoc = await db.collection('artist_seo_content').findOne({ slug });
    if (aiDoc?.content) {
      const rawAiSeoContent =
        aiDoc.content?.[lang] ||
        (lang === 'en' ? aiDoc.content?.en || aiDoc.content : null);
      aiSeoContent = normalizeArtistSeoCounts(rawAiSeoContent, slug, videos.length);
    }
  } catch { /* ignore */ }

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

  const localizedMeta = getSeoMeta(lang, 'artist', { artist: displayArtistName });
  const schemaDescription = aiSeoContent?.meta_description || localizedMeta.description;
  const localizedHomeUrl = `https://dadrocktabs.com/${lang}`;
  const localizedArtistUrl = `https://dadrocktabs.com/${lang}/artist/${slug}`;

  const jsonLd = {
    '@context': 'https://schema.org',
    '@graph': [
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
            'name': t.relatedArtists || 'Artists',
            'item': localizedHomeUrl
          },
          {
            '@type': 'ListItem',
            'position': 3,
            'name': localizedMeta.title,
            'item': localizedArtistUrl
          }
        ]
      },
      {
        '@type': 'MusicGroup',
        '@id': `${localizedArtistUrl}#artist`,
        'name': displayArtistName,
        'genre': 'Rock',
        'description': schemaDescription,
        'url': localizedArtistUrl,
        'inLanguage': lang,
      },
      {
        '@type': 'CollectionPage',
        'name': localizedMeta.title,
        'description': schemaDescription,
        'url': localizedArtistUrl,
        'inLanguage': lang,
        'isPartOf': { '@id': 'https://dadrocktabs.com/#website' },
        'about': { '@id': `${localizedArtistUrl}#artist` },
        'publisher': { '@id': 'https://dadrocktabs.com/#organization' },
        'numberOfItems': plainVideos.length,
        'mainEntity': {
          '@type': 'ItemList',
          'numberOfItems': plainVideos.length,
          'itemListElement': plainVideos.slice(0, 10).map((video, index) => {
            const videoId = extractYouTubeVideoId(video);
            const videoName = video.song || video.title || `${displayArtistName} video lesson`;

            return {
              '@type': 'ListItem',
              'position': index + 1,
              'item': {
                '@type': 'VideoObject',
                'name': videoName,
                'description': `${videoName}. ${schemaDescription}`,
                'thumbnailUrl': video.thumbnail || (videoId ? `https://img.youtube.com/vi/${videoId}/maxresdefault.jpg` : undefined),
                'uploadDate': video.created_at || undefined,
                'embedUrl': videoId ? `https://www.youtube.com/embed/${videoId}` : undefined,
                'inLanguage': lang,
                'publisher': { '@id': 'https://dadrocktabs.com/#organization' }
              }
            };
          })
        }
      }
    ]
  };

  const topSongs = plainVideos.slice(0, 5).map(v => v.song || v.title).filter(Boolean);
  const faqItems = [];

  if (lang === 'en') {
    faqItems.push(
      {
        question: t.faqLearnQuestion.replace('{artist}', displayArtistName),
        answer: `DadRock Tabs offers ${plainVideos.length} free video lessons for ${displayArtistName} songs with synchronized guitar and bass tablature. Simply select a lesson, watch the video tutorial, and follow along with the on-screen tabs. Popular lessons include ${topSongs.slice(0, 3).join(', ')}.`
      },
      {
        question: t.faqBeginnerQuestion.replace('{artist}', displayArtistName),
        answer: aiSeoContent?.why_learn || `Many ${displayArtistName} songs feature iconic riffs that are great for developing fundamental rock guitar skills. Start with simpler songs and work your way up to more complex pieces. Our video tutorials break down each song step-by-step.`
      },
      {
        question: t.faqGearQuestion.replace('{artist}', displayArtistName),
        answer: aiSeoContent?.gear_info || `${displayArtistName} is known for a distinctive rock tone. Visit our lesson pages to learn more about the gear and settings that can help you achieve a similar sound.`
      },
      {
        question: t.faqLessonsQuestion.replace('{artist}', displayArtistName),
        answer: `We currently have ${plainVideos.length} free ${displayArtistName} guitar and bass tab video lessons available on DadRock Tabs, including ${topSongs.slice(0, 3).join(', ')}${topSongs.length > 3 ? ' and more' : ''}.`
      },
      {
        question: t.faqStyleQuestion.replace('{artist}', displayArtistName),
        answer: aiSeoContent?.playing_style || `${displayArtistName} is known for their distinctive rock guitar style. Our tab lessons help you learn the key techniques and riffs that define their sound.`
      },
    );
  } else {
    if (aiSeoContent?.why_learn) {
      faqItems.push({
        question: t.faqBeginnerQuestion.replace('{artist}', displayArtistName),
        answer: aiSeoContent.why_learn,
      });
    }
    if (aiSeoContent?.gear_info) {
      faqItems.push({
        question: t.faqGearQuestion.replace('{artist}', displayArtistName),
        answer: aiSeoContent.gear_info,
      });
    }
    if (aiSeoContent?.playing_style) {
      faqItems.push({
        question: t.faqStyleQuestion.replace('{artist}', displayArtistName),
        answer: aiSeoContent.playing_style,
      });
    }
  }

  const faqJsonLd = faqItems.length > 0 ? {
    '@context': 'https://schema.org',
    '@type': 'FAQPage',
    'inLanguage': lang,
    'mainEntity': faqItems.map(faq => ({
      '@type': 'Question',
      'name': faq.question,
      'acceptedAnswer': {
        '@type': 'Answer',
        'text': faq.answer
      }
    }))
  } : null;

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      {faqJsonLd && (
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(faqJsonLd) }}
        />
      )}
      <ArtistPageClient
        artistName={displayArtistName}
        videos={plainVideos}
        slug={slug}
        lang={lang}
        adSettings={adSettings}
        initialAiContent={aiSeoContent}
        faqItems={faqItems}
      />
    </>
  );
}
