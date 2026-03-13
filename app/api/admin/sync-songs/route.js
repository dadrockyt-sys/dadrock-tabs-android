import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';
import { v4 as uuidv4 } from 'uuid';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'Babyty99';
const YOUTUBE_CLIENT_ID = process.env.YOUTUBE_CLIENT_ID;
const YOUTUBE_CLIENT_SECRET = process.env.YOUTUBE_CLIENT_SECRET;

function verifyAdmin(request) {
  const authHeader = request.headers.get('authorization');
  if (!authHeader || !authHeader.startsWith('Basic ')) return false;
  try {
    const base64Credentials = authHeader.split(' ')[1];
    const credentials = Buffer.from(base64Credentials, 'base64').toString('utf8');
    const [, password] = credentials.split(':');
    return password === ADMIN_PASSWORD;
  } catch {
    return false;
  }
}

async function getValidAccessToken(db) {
  const tokens = await db.collection('settings').findOne({ type: 'youtube_oauth' });
  if (!tokens?.access_token) return null;

  if (tokens.expires_at && Date.now() > tokens.expires_at - 300000) {
    if (!tokens.refresh_token || !YOUTUBE_CLIENT_ID || !YOUTUBE_CLIENT_SECRET) return null;
    try {
      const refreshResponse = await fetch('https://oauth2.googleapis.com/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams({
          client_id: YOUTUBE_CLIENT_ID,
          client_secret: YOUTUBE_CLIENT_SECRET,
          refresh_token: tokens.refresh_token,
          grant_type: 'refresh_token',
        }),
      });
      const newTokens = await refreshResponse.json();
      if (newTokens.error) return null;
      await db.collection('settings').updateOne(
        { type: 'youtube_oauth' },
        { $set: { access_token: newTokens.access_token, expires_at: Date.now() + (newTokens.expires_in * 1000), updated_at: new Date().toISOString() } }
      );
      return newTokens.access_token;
    } catch { return null; }
  }
  return tokens.access_token;
}

function parseVideoTitle(title) {
  let cleanTitle = title.replace(/\s*(Guitar|Bass|TAB|TABS|Lesson|Tutorial|\+|\(|\)|\[|\]|HD|Official|Full|Cover|Play Along|Playthrough).*/gi, '').trim();
  cleanTitle = cleanTitle.replace(/\s*[-|]\s*$/, '').trim();
  
  if (cleanTitle.includes(' - ')) {
    const parts = cleanTitle.split(' - ', 2);
    return { song: parts[0].trim(), artist: parts[1]?.trim() || 'DadRock Tabs' };
  }
  const byMatch = cleanTitle.match(/(.+?)\s+by\s+(.+)/i);
  if (byMatch) return { song: byMatch[1].trim(), artist: byMatch[2].trim() };
  return { song: cleanTitle, artist: 'DadRock Tabs' };
}

function generateSlug(artist, song) {
  const artistSlug = artist.toLowerCase()
    .replace(/\//g, '')
    .replace(/['']/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
  const songSlug = song.toLowerCase()
    .replace(/['']/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');
  return `${artistSlug}-${songSlug}`;
}

function parseDuration(duration) {
  if (!duration) return 0;
  const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  if (!match) return 0;
  return parseInt(match[1] || 0) * 3600 + parseInt(match[2] || 0) * 60 + parseInt(match[3] || 0);
}

export async function POST(request) {
  if (!verifyAdmin(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const db = await getDb();
    const accessToken = await getValidAccessToken(db);

    if (!accessToken) {
      return NextResponse.json({ error: 'YouTube not connected. Please reconnect YouTube in the admin panel.', need_reconnect: true }, { status: 401 });
    }

    // Fetch ALL videos from channel using pagination
    let allVideoIds = [];
    let nextPageToken = '';
    let pageCount = 0;
    const maxPages = 10; // Up to 500 videos

    do {
      const searchUrl = new URL('https://www.googleapis.com/youtube/v3/search');
      searchUrl.searchParams.set('part', 'snippet');
      searchUrl.searchParams.set('forMine', 'true');
      searchUrl.searchParams.set('type', 'video');
      searchUrl.searchParams.set('maxResults', '50');
      searchUrl.searchParams.set('order', 'viewCount');
      if (nextPageToken) searchUrl.searchParams.set('pageToken', nextPageToken);

      const searchResponse = await fetch(searchUrl.toString(), {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      const searchData = await searchResponse.json();
      if (searchData.error) {
        console.error('Search error:', searchData.error);
        break;
      }

      const videoIds = searchData.items?.map(item => item.id.videoId) || [];
      allVideoIds = [...allVideoIds, ...videoIds];
      nextPageToken = searchData.nextPageToken || '';
      pageCount++;
    } while (nextPageToken && pageCount < maxPages);

    if (allVideoIds.length === 0) {
      return NextResponse.json({ error: 'No videos found on channel' }, { status: 404 });
    }

    // Fetch video details in batches of 50 (with statistics + contentDetails for duration)
    let allVideos = [];
    for (let i = 0; i < allVideoIds.length; i += 50) {
      const batchIds = allVideoIds.slice(i, i + 50).join(',');
      const detailsUrl = `https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id=${batchIds}`;
      const detailsResponse = await fetch(detailsUrl, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      const detailsData = await detailsResponse.json();
      if (detailsData.items) {
        allVideos = [...allVideos, ...detailsData.items];
      }
    }

    // Filter out shorts (duration < 90 seconds) and private videos
    const regularVideos = allVideos.filter(video => {
      const duration = parseDuration(video.contentDetails?.duration);
      const isShort = duration > 0 && duration < 90;
      const isPublic = video.status?.privacyStatus !== 'private' || true; // include all for now
      return !isShort;
    });

    // Sort by view count descending
    regularVideos.sort((a, b) => {
      const viewsA = parseInt(a.statistics?.viewCount || 0);
      const viewsB = parseInt(b.statistics?.viewCount || 0);
      return viewsB - viewsA;
    });

    // Take top 100
    const top100 = regularVideos.slice(0, 100);

    // Process and store each video
    let addedCount = 0;
    let updatedCount = 0;

    for (const video of top100) {
      const snippet = video.snippet;
      const stats = video.statistics;
      const { song, artist } = parseVideoTitle(snippet.title);
      const slug = generateSlug(artist, song);
      const viewCount = parseInt(stats?.viewCount || 0);
      const likeCount = parseInt(stats?.likeCount || 0);
      const duration = parseDuration(video.contentDetails?.duration);

      const songData = {
        videoId: video.id,
        title: song,
        artist: artist,
        fullTitle: snippet.title,
        slug: slug,
        thumbnail: snippet.thumbnails?.high?.url || snippet.thumbnails?.default?.url || `https://i.ytimg.com/vi/${video.id}/hqdefault.jpg`,
        viewCount: viewCount,
        likeCount: likeCount,
        duration: duration,
        publishedAt: snippet.publishedAt,
        description: snippet.description?.substring(0, 500) || '',
        updated_at: new Date().toISOString()
      };

      // Upsert by videoId
      const result = await db.collection('song_pages').updateOne(
        { videoId: video.id },
        { $set: songData, $setOnInsert: { id: uuidv4(), created_at: new Date().toISOString() } },
        { upsert: true }
      );

      if (result.upsertedCount > 0) addedCount++;
      else updatedCount++;
    }

    // Remove songs not in top 100 anymore
    const top100VideoIds = top100.map(v => v.id);
    const removeResult = await db.collection('song_pages').deleteMany({
      videoId: { $nin: top100VideoIds }
    });

    return NextResponse.json({
      success: true,
      message: `Synced top ${top100.length} songs. Added ${addedCount} new, updated ${updatedCount}. Removed ${removeResult.deletedCount} old entries.`,
      total_scanned: allVideos.length,
      shorts_filtered: allVideos.length - regularVideos.length,
      songs_synced: top100.length,
      added: addedCount,
      updated: updatedCount,
      removed: removeResult.deletedCount
    });

  } catch (err) {
    console.error('Sync songs error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
