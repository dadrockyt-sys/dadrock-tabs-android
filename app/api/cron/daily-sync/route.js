import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';
import { v4 as uuidv4 } from 'uuid';

// This endpoint is called by Vercel Cron every 24 hours
// It syncs both published videos and scheduled videos

const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY;
const YOUTUBE_CLIENT_ID = process.env.YOUTUBE_CLIENT_ID;
const YOUTUBE_CLIENT_SECRET = process.env.YOUTUBE_CLIENT_SECRET;
const CHANNEL_ID = 'UCl9DFhCasFrFOD_5HjlUmwQ'; // DadRock Tabs channel

// Verify cron secret to prevent unauthorized access
function verifyCronSecret(request) {
  const authHeader = request.headers.get('authorization');
  const cronSecret = process.env.CRON_SECRET;
  
  // If no CRON_SECRET is set, allow the request (for testing)
  if (!cronSecret) return true;
  
  return authHeader === `Bearer ${cronSecret}`;
}

// Helper to refresh access token
async function getValidAccessToken(db) {
  const tokens = await db.collection('settings').findOne({ type: 'youtube_oauth' });
  
  if (!tokens?.access_token) {
    return null;
  }

  // Check if token is expired
  if (tokens.expires_at && Date.now() > tokens.expires_at - 300000) {
    if (!tokens.refresh_token) return null;

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
        {
          $set: {
            access_token: newTokens.access_token,
            expires_at: Date.now() + (newTokens.expires_in * 1000),
            updated_at: new Date().toISOString()
          }
        }
      );

      return newTokens.access_token;
    } catch (err) {
      console.error('Token refresh failed:', err);
      return null;
    }
  }

  return tokens.access_token;
}

// Helper to parse video title
function parseVideoTitle(title) {
  let cleanTitle = title.replace(/\s*(Guitar|Bass|TAB|TABS|Lesson|Tutorial|\+|\(|\)|\[|\]|HD|Official).*/gi, '').trim();
  
  if (cleanTitle.includes(' - ')) {
    const parts = cleanTitle.split(' - ', 2);
    return { song: parts[0].trim(), artist: parts[1]?.trim() || 'DadRock Tabs' };
  }
  
  const byMatch = cleanTitle.match(/(.+?)\s+by\s+(.+)/i);
  if (byMatch) {
    return { song: byMatch[1].trim(), artist: byMatch[2].trim() };
  }
  
  return { song: cleanTitle, artist: 'DadRock Tabs' };
}

// Sync published videos using API key
async function syncPublishedVideos(db) {
  let videosAdded = 0;
  let videosSkipped = 0;
  let nextPageToken = '';

  do {
    const url = `https://www.googleapis.com/youtube/v3/search?key=${YOUTUBE_API_KEY}&channelId=${CHANNEL_ID}&part=snippet&type=video&maxResults=50&order=date${nextPageToken ? `&pageToken=${nextPageToken}` : ''}`;
    
    const response = await fetch(url);
    const data = await response.json();

    if (data.error) {
      console.error('YouTube API error:', data.error);
      break;
    }

    for (const item of data.items || []) {
      const videoId = item.id.videoId;
      const snippet = item.snippet;

      // Check if video already exists
      const existing = await db.collection('videos').findOne({ videoId });
      if (existing) {
        videosSkipped++;
        continue;
      }

      const { song, artist } = parseVideoTitle(snippet.title);

      const video = {
        id: uuidv4(),
        videoId: videoId,
        title: snippet.title,
        song: song,
        artist: artist,
        thumbnail: snippet.thumbnails?.high?.url || snippet.thumbnails?.default?.url,
        publishedAt: snippet.publishedAt,
        created_at: new Date().toISOString()
      };

      await db.collection('videos').insertOne(video);
      videosAdded++;
    }

    nextPageToken = data.nextPageToken || '';
  } while (nextPageToken);

  return { videosAdded, videosSkipped };
}

// Sync scheduled videos using OAuth
async function syncScheduledVideos(db, accessToken) {
  if (!accessToken) {
    return { scheduledFound: 0, scheduledAdded: 0, error: 'No OAuth token' };
  }

  let allVideoIds = [];
  let nextPageToken = '';
  let pageCount = 0;

  do {
    const searchUrl = new URL('https://www.googleapis.com/youtube/v3/search');
    searchUrl.searchParams.set('part', 'snippet');
    searchUrl.searchParams.set('forMine', 'true');
    searchUrl.searchParams.set('type', 'video');
    searchUrl.searchParams.set('maxResults', '50');
    searchUrl.searchParams.set('order', 'date');
    if (nextPageToken) {
      searchUrl.searchParams.set('pageToken', nextPageToken);
    }

    const searchResponse = await fetch(searchUrl.toString(), {
      headers: { 'Authorization': `Bearer ${accessToken}` }
    });
    const searchData = await searchResponse.json();

    if (searchData.error) break;

    const videoIds = searchData.items?.map(item => item.id.videoId) || [];
    allVideoIds = [...allVideoIds, ...videoIds];
    
    nextPageToken = searchData.nextPageToken || '';
    pageCount++;
  } while (nextPageToken && pageCount < 5);

  if (allVideoIds.length === 0) {
    return { scheduledFound: 0, scheduledAdded: 0 };
  }

  // Fetch video details
  let allScheduledVideos = [];
  
  for (let i = 0; i < allVideoIds.length; i += 50) {
    const batchIds = allVideoIds.slice(i, i + 50).join(',');
    
    const videosResponse = await fetch(
      `https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id=${batchIds}`,
      { headers: { 'Authorization': `Bearer ${accessToken}` } }
    );
    const videosData = await videosResponse.json();

    if (videosData.error) continue;

    const scheduledVideos = videosData.items?.filter(video => {
      const status = video.status;
      const snippet = video.snippet;
      return (status?.privacyStatus === 'private' && status?.publishAt) ||
             snippet?.liveBroadcastContent === 'upcoming';
    }) || [];

    allScheduledVideos = [...allScheduledVideos, ...scheduledVideos];
  }

  // Remove duplicates
  const uniqueUpcoming = allScheduledVideos.filter((video, index, self) =>
    index === self.findIndex(v => v.id === video.id)
  );

  let scheduledAdded = 0;

  for (const video of uniqueUpcoming) {
    const snippet = video.snippet;
    const status = video.status;
    
    const existing = await db.collection('upcoming_videos').findOne({
      youtube_video_id: video.id
    });

    if (existing) continue;

    const { song, artist } = parseVideoTitle(snippet.title);

    const upcomingVideo = {
      id: uuidv4(),
      youtube_video_id: video.id,
      title: song,
      artist: artist,
      scheduled_date: status?.publishAt || snippet?.publishedAt,
      thumbnail: snippet.thumbnails?.high?.url || snippet.thumbnails?.default?.url || '',
      description: snippet.description?.substring(0, 200) || '',
      created_at: new Date().toISOString()
    };

    await db.collection('upcoming_videos').insertOne(upcomingVideo);
    scheduledAdded++;
  }

  // Clean up past scheduled videos that are now published
  const now = new Date();
  await db.collection('upcoming_videos').deleteMany({
    scheduled_date: { $lt: now.toISOString() }
  });

  return { scheduledFound: uniqueUpcoming.length, scheduledAdded };
}

export async function GET(request) {
  // Verify this is a legitimate cron request
  if (!verifyCronSecret(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const startTime = Date.now();
  
  try {
    const db = await getDb();
    
    // Sync published videos
    const publishedResult = await syncPublishedVideos(db);
    
    // Sync scheduled videos (requires OAuth)
    const accessToken = await getValidAccessToken(db);
    const scheduledResult = await syncScheduledVideos(db, accessToken);

    // Log the sync
    await db.collection('cron_logs').insertOne({
      id: uuidv4(),
      type: 'daily_sync',
      timestamp: new Date().toISOString(),
      duration_ms: Date.now() - startTime,
      published_added: publishedResult.videosAdded,
      published_skipped: publishedResult.videosSkipped,
      scheduled_found: scheduledResult.scheduledFound,
      scheduled_added: scheduledResult.scheduledAdded,
      oauth_available: !!accessToken
    });

    return NextResponse.json({
      success: true,
      message: 'Daily sync completed',
      published: {
        added: publishedResult.videosAdded,
        skipped: publishedResult.videosSkipped
      },
      scheduled: {
        found: scheduledResult.scheduledFound,
        added: scheduledResult.scheduledAdded,
        oauth_connected: !!accessToken
      },
      duration_ms: Date.now() - startTime
    });

  } catch (err) {
    console.error('Cron sync error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
