import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';

export async function GET() {
  try {
    const db = await getDb();
    const baseUrl = 'https://dadrocktabs.com';
    
    // Get all song pages (they have the best video data)
    const songPages = await db.collection('song_pages')
      .find({})
      .project({ slug: 1, title: 1, artist: 1, videoId: 1, thumbnail: 1, duration: 1, publishedAt: 1, viewCount: 1 })
      .toArray();
    
    // Also get videos from the main collection (for artist page videos)
    const videos = await db.collection('videos')
      .find({})
      .project({ artist: 1, song: 1, title: 1, youtube_url: 1, thumbnail: 1, created_at: 1, duration: 1 })
      .toArray();
    
    // Junk patterns to skip
    const junkPatterns = ['#', 'Coming Soon', 'coming soon', 'Memorial', 'Original Song', 
      'Greatest Drummers', 'DadRock Tabs', 'The DadRock', "80's Fretmasters"];
    
    // Helper to extract video ID from YouTube URL
    function getVideoId(url) {
      if (!url) return null;
      const match = url.match(/(?:v=|\/embed\/|youtu\.be\/)([a-zA-Z0-9_-]{11})/);
      return match ? match[1] : null;
    }
    
    let xml = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">
`;

    // Add song pages with full video data
    for (const song of songPages) {
      const cleanArtist = song.artist?.replace(/ -$/, '').trim() || 'DadRock Tabs';
      const videoTitle = `${song.title} - ${cleanArtist} Guitar & Bass Tab Tutorial`;
      const description = `Learn to play "${song.title}" by ${cleanArtist} with free guitar and bass tablature. Step-by-step video lesson from DadRock Tabs.`;
      const thumbnailUrl = song.thumbnail || `https://img.youtube.com/vi/${song.videoId}/maxresdefault.jpg`;
      const contentUrl = `https://www.youtube.com/watch?v=${song.videoId}`;
      const playerUrl = `https://www.youtube.com/embed/${song.videoId}`;
      const pubDate = song.publishedAt ? new Date(song.publishedAt).toISOString().split('T')[0] : '2024-01-01';
      
      xml += `  <url>
    <loc>${baseUrl}/songs/${song.slug}</loc>
    <video:video>
      <video:thumbnail_loc>${escapeXml(thumbnailUrl)}</video:thumbnail_loc>
      <video:title>${escapeXml(videoTitle)}</video:title>
      <video:description>${escapeXml(description)}</video:description>
      <video:content_loc>${escapeXml(contentUrl)}</video:content_loc>
      <video:player_loc>${escapeXml(playerUrl)}</video:player_loc>
${song.duration ? `      <video:duration>${song.duration}</video:duration>\n` : ''}      <video:publication_date>${pubDate}</video:publication_date>
      <video:family_friendly>yes</video:family_friendly>
      <video:live>no</video:live>
    </video:video>
  </url>
`;
    }

    // Add artist page videos (deduplicated by video_id)
    const seenVideoIds = new Set(songPages.map(s => s.videoId));
    const seenArtistSlugs = new Set();
    
    for (const video of videos) {
      if (!video.artist || !video.youtube_url) continue;
      
      const videoId = getVideoId(video.youtube_url);
      if (!videoId) continue;
      if (seenVideoIds.has(videoId)) continue;
      if (junkPatterns.some(p => video.artist.includes(p))) continue;
      
      seenVideoIds.add(videoId);
      
      const cleanArtist = video.artist.replace(/ -$/, '').trim();
      const artistSlug = artistToSlug(video.artist);
      const songName = video.song || video.title || 'Guitar Tab Lesson';
      const videoTitle = `${songName} - ${cleanArtist} Guitar Tab Tutorial`;
      const description = `Learn "${songName}" by ${cleanArtist} with this free guitar and bass tab video lesson from DadRock Tabs.`;
      const thumbnailUrl = video.thumbnail || `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`;
      const contentUrl = video.youtube_url;
      const playerUrl = `https://www.youtube.com/embed/${videoId}`;
      const pubDate = video.created_at ? new Date(video.created_at).toISOString().split('T')[0] : '2024-01-01';
      
      xml += `  <url>
    <loc>${baseUrl}/artist/${artistSlug}</loc>
    <video:video>
      <video:thumbnail_loc>${escapeXml(thumbnailUrl)}</video:thumbnail_loc>
      <video:title>${escapeXml(videoTitle)}</video:title>
      <video:description>${escapeXml(description)}</video:description>
      <video:content_loc>${escapeXml(contentUrl)}</video:content_loc>
      <video:player_loc>${escapeXml(playerUrl)}</video:player_loc>
${video.duration ? `      <video:duration>${video.duration}</video:duration>\n` : ''}      <video:publication_date>${pubDate}</video:publication_date>
      <video:family_friendly>yes</video:family_friendly>
      <video:live>no</video:live>
    </video:video>
  </url>
`;
    }

    xml += `</urlset>`;

    return new Response(xml, {
      headers: {
        'Content-Type': 'application/xml',
        'Cache-Control': 'public, max-age=3600, s-maxage=3600',
      },
    });
  } catch (error) {
    console.error('Video sitemap error:', error);
    return new Response('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>', {
      headers: { 'Content-Type': 'application/xml' },
      status: 500,
    });
  }
}

function escapeXml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;');
}
