import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';

const BASE_URL = 'https://dadrocktabs.com';
const VIDEO_ID_PATTERN = /^[a-zA-Z0-9_-]{11}$/;

function getVideoId(url) {
  if (!url) return null;
  const match = url.match(/(?:v=|\/embed\/|youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})/);
  return match ? match[1] : null;
}

function formatPublicationDate(value) {
  if (!value) return null;
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return null;
  return date.toISOString();
}

function validDuration(value) {
  const duration = Number(value);
  return Number.isFinite(duration) && duration >= 1 && duration <= 28800
    ? Math.round(duration)
    : null;
}

function buildVideoXml({
  thumbnailUrl,
  title,
  description,
  playerUrl,
  duration,
  publicationDate,
  viewCount,
}) {
  const safeDuration = validDuration(duration);
  const safeViewCount = Number(viewCount);

  return `    <video:video>
      <video:thumbnail_loc>${escapeXml(thumbnailUrl)}</video:thumbnail_loc>
      <video:title>${escapeXml(title)}</video:title>
      <video:description>${escapeXml(description)}</video:description>
      <video:player_loc>${escapeXml(playerUrl)}</video:player_loc>
${safeDuration ? `      <video:duration>${safeDuration}</video:duration>\n` : ''}${publicationDate ? `      <video:publication_date>${publicationDate}</video:publication_date>\n` : ''}${Number.isFinite(safeViewCount) && safeViewCount >= 0 ? `      <video:view_count>${Math.round(safeViewCount)}</video:view_count>\n` : ''}      <video:family_friendly>yes</video:family_friendly>
      <video:live>no</video:live>
    </video:video>
`;
}

export async function GET() {
  try {
    const db = await getDb();

    const songPages = await db
      .collection('song_pages')
      .find({})
      .project({
        slug: 1,
        title: 1,
        artist: 1,
        videoId: 1,
        thumbnail: 1,
        duration: 1,
        publishedAt: 1,
        viewCount: 1,
      })
      .toArray();

    const videos = await db
      .collection('videos')
      .find({})
      .project({
        artist: 1,
        song: 1,
        title: 1,
        youtube_url: 1,
        thumbnail: 1,
        created_at: 1,
        duration: 1,
        viewCount: 1,
      })
      .toArray();

    const junkPatterns = [
      '#',
      'Coming Soon',
      'coming soon',
      'Memorial',
      'Original Song',
      'Greatest Drummers',
      'DadRock Tabs',
      'The DadRock',
      "80's Fretmasters",
    ];

    let xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
`;

    // Song pages are dedicated watch pages: one host URL, one primary video.
    const seenVideoIds = new Set();

    for (const song of songPages) {
      if (!song.slug || !song.videoId || !VIDEO_ID_PATTERN.test(song.videoId)) {
        continue;
      }

      seenVideoIds.add(song.videoId);

      const cleanArtist = song.artist?.replace(/ -$/, '').trim() || 'DadRock Tabs';
      const thumbnailUrl =
        song.thumbnail ||
        `https://img.youtube.com/vi/${song.videoId}/maxresdefault.jpg`;

      const videoXml = buildVideoXml({
        thumbnailUrl,
        title: `${song.title} - ${cleanArtist} Guitar & Bass Tab Tutorial`,
        description: `Learn to play "${song.title}" by ${cleanArtist} with free guitar and bass tablature. Step-by-step video lesson from DadRock Tabs.`,
        playerUrl: `https://www.youtube.com/embed/${song.videoId}`,
        duration: song.duration,
        publicationDate: formatPublicationDate(song.publishedAt),
        viewCount: song.viewCount,
      });

      xml += `  <url>
    <loc>${BASE_URL}/songs/${song.slug}</loc>
${videoXml}  </url>
`;
    }

    // Artist pages can host many videos. Group all videos for the same artist
    // under one host-page <loc> with multiple <video:video> children.
    const artistGroups = new Map();

    for (const video of videos) {
      if (!video.artist || !video.youtube_url) continue;
      if (junkPatterns.some((pattern) => video.artist.includes(pattern))) continue;

      const videoId = getVideoId(video.youtube_url);
      if (!videoId || seenVideoIds.has(videoId)) continue;

      const artistSlug = artistToSlug(video.artist);
      if (!artistSlug) continue;

      seenVideoIds.add(videoId);

      const cleanArtist = video.artist.replace(/ -$/, '').trim();
      const songName = video.song || video.title || 'Guitar Tab Lesson';
      const thumbnailUrl =
        video.thumbnail || `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;

      const videoXml = buildVideoXml({
        thumbnailUrl,
        title: `${songName} - ${cleanArtist} Guitar Tab Tutorial`,
        description: `Learn "${songName}" by ${cleanArtist} with this free guitar and bass tab video lesson from DadRock Tabs.`,
        playerUrl: `https://www.youtube.com/embed/${videoId}`,
        duration: video.duration,
        publicationDate: formatPublicationDate(video.created_at),
        viewCount: video.viewCount,
      });

      if (!artistGroups.has(artistSlug)) {
        artistGroups.set(artistSlug, []);
      }
      artistGroups.get(artistSlug).push(videoXml);
    }

    for (const [artistSlug, videoEntries] of artistGroups) {
      xml += `  <url>
    <loc>${BASE_URL}/artist/${artistSlug}</loc>
${videoEntries.join('')}  </url>
`;
    }

    xml += '</urlset>';

    return new Response(xml, {
      headers: {
        'Content-Type': 'application/xml',
        'Cache-Control': 'public, max-age=3600, s-maxage=3600',
      },
    });
  } catch (error) {
    console.error('Video sitemap error:', error);
    return new Response(
      '<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>',
      {
        headers: { 'Content-Type': 'application/xml' },
        status: 500,
      }
    );
  }
}

function escapeXml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}
