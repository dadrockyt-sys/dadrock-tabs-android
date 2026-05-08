import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';
import { v4 as uuidv4 } from 'uuid';

const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY || '';
const QUICKIES_PLAYLIST_ID = 'PLEneI6e1FjBVRrw6FfSBK32RiT8N43v0H';

// Helper to parse video title to extract song and artist
function parseVideoTitle(title) {
  // Remove common suffixes like "Guitar TAB", "Bass Lesson", hashtags, etc.
  let cleanTitle = title
    .replace(/#\w+/g, '')
    .replace(/\s*(Guitar|Bass|TAB|TABS|Lesson|Tutorial|Quickie|Quickies|Quick|Cover|\+|\[|\]|HD|Official)\s*/gi, ' ')
    .replace(/\s*\(.*?\)\s*/g, ' ')
    .trim();
  
  // Try to split by " - "
  if (cleanTitle.includes(' - ')) {
    const parts = cleanTitle.split(' - ', 2);
    return { song: parts[0].trim(), artist: parts[1]?.trim() || 'DadRock Tabs' };
  }
  
  // Try to split by " by "
  const byMatch = cleanTitle.match(/(.+?)\s+by\s+(.+)/i);
  if (byMatch) {
    return { song: byMatch[1].trim(), artist: byMatch[2].trim() };
  }
  
  return { song: cleanTitle || title, artist: 'DadRock Tabs' };
}

// Sync function to fetch videos from YouTube playlist
async function syncFromYouTube(db) {
  if (!YOUTUBE_API_KEY) {
    return { success: false, error: 'YouTube API key not configured' };
  }

  try {
    const allItems = [];
    let nextPageToken = null;

    do {
      const url = `https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=${QUICKIES_PLAYLIST_ID}&maxResults=50&key=${YOUTUBE_API_KEY}${nextPageToken ? `&pageToken=${nextPageToken}` : ''}`;
      const res = await fetch(url);
      const data = await res.json();

      if (data.error) {
        console.error('YouTube API error:', data.error);
        return { success: false, error: data.error.message };
      }

      for (const item of (data.items || [])) {
        const snippet = item.snippet;
        if (!snippet || snippet.title === 'Private video' || snippet.title === 'Deleted video') continue;

        const videoId = snippet.resourceId?.videoId;
        if (!videoId) continue;

        const { song, artist } = parseVideoTitle(snippet.title);

        allItems.push({
          id: uuidv4(),
          video_id: videoId,
          song,
          artist,
          title: snippet.title,
          youtube_url: `https://www.youtube.com/watch?v=${videoId}`,
          thumbnail: snippet.thumbnails?.high?.url || snippet.thumbnails?.medium?.url || snippet.thumbnails?.default?.url || `https://img.youtube.com/vi/${videoId}/mqdefault.jpg`,
          position: snippet.position != null ? snippet.position : allItems.length,
          created_at: snippet.publishedAt || new Date().toISOString(),
        });
      }

      nextPageToken = data.nextPageToken;
    } while (nextPageToken);

    // Clear old data and insert fresh
    await db.collection('quickies_videos').deleteMany({});
    if (allItems.length > 0) {
      await db.collection('quickies_videos').insertMany(allItems);
    }

    return { success: true, count: allItems.length };
  } catch (e) {
    console.error('YouTube sync error:', e);
    return { success: false, error: e.message };
  }
}

// GET - Fetch quickies videos (auto-syncs from YouTube if DB is empty)
export async function GET(request) {
  try {
    const db = await getDb();
    const { searchParams } = new URL(request.url);
    const forceSync = searchParams.get('sync') === 'true';

    let videos = await db.collection('quickies_videos')
      .find({})
      .sort({ position: 1 })
      .toArray();

    // Auto-sync from YouTube if collection is empty or force sync requested
    if ((videos.length === 0 || forceSync) && YOUTUBE_API_KEY) {
      const syncResult = await syncFromYouTube(db);
      if (syncResult.success) {
        videos = await db.collection('quickies_videos')
          .find({})
          .sort({ position: 1 })
          .toArray();
      } else if (videos.length === 0) {
        return NextResponse.json({
          videos: [],
          total: 0,
          playlist_id: QUICKIES_PLAYLIST_ID,
          error: syncResult.error,
        });
      }
    }

    const plainVideos = videos.map(v => ({
      id: v.id,
      video_id: v.video_id,
      song: v.song,
      artist: v.artist,
      title: v.title,
      youtube_url: v.youtube_url,
      thumbnail: v.thumbnail,
      position: v.position,
      created_at: v.created_at,
    }));

    return NextResponse.json({
      videos: plainVideos,
      total: plainVideos.length,
      playlist_id: QUICKIES_PLAYLIST_ID,
    });
  } catch (error) {
    console.error('Quickies API Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
