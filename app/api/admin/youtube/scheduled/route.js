import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';
import { v4 as uuidv4 } from 'uuid';

// Admin password from env
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'Babyty99';
const YOUTUBE_CLIENT_ID = process.env.YOUTUBE_CLIENT_ID;
const YOUTUBE_CLIENT_SECRET = process.env.YOUTUBE_CLIENT_SECRET;

// Helper to verify admin auth
function verifyAdmin(request) {
  const authHeader = request.headers.get('authorization');
  if (!authHeader || !authHeader.startsWith('Basic ')) {
    return false;
  }
  try {
    const base64Credentials = authHeader.split(' ')[1];
    const credentials = Buffer.from(base64Credentials, 'base64').toString('utf8');
    const [, password] = credentials.split(':');
    return password === ADMIN_PASSWORD;
  } catch {
    return false;
  }
}

// Helper to refresh access token if expired
async function getValidAccessToken(db) {
  const tokens = await db.collection('settings').findOne({ type: 'youtube_oauth' });
  
  if (!tokens?.access_token) {
    return null;
  }

  // Check if token is expired (with 5 min buffer)
  if (tokens.expires_at && Date.now() > tokens.expires_at - 300000) {
    // Token expired or about to expire, refresh it
    if (!tokens.refresh_token) {
      return null;
    }

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

      if (newTokens.error) {
        console.error('Token refresh error:', newTokens);
        return null;
      }

      // Update stored tokens
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

export async function POST(request) {
  if (!verifyAdmin(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const db = await getDb();
    const accessToken = await getValidAccessToken(db);

    if (!accessToken) {
      return NextResponse.json({ 
        error: 'YouTube not connected or token expired. Please reconnect YouTube.',
        need_reconnect: true 
      }, { status: 401 });
    }

    // First get the channel's uploads playlist
    const channelResponse = await fetch(
      'https://www.googleapis.com/youtube/v3/channels?part=contentDetails&mine=true',
      { headers: { 'Authorization': `Bearer ${accessToken}` } }
    );
    const channelData = await channelResponse.json();

    if (channelData.error) {
      console.error('Channel fetch error:', channelData.error);
      return NextResponse.json({ error: channelData.error.message }, { status: 400 });
    }

    if (!channelData.items?.length) {
      return NextResponse.json({ error: 'No channel found' }, { status: 404 });
    }

    const uploadsPlaylistId = channelData.items[0].contentDetails.relatedPlaylists.uploads;

    // Fetch videos from the channel - this includes scheduled ones when using OAuth
    // We need to use the search endpoint with type=video and forMine=true to get scheduled videos
    const searchResponse = await fetch(
      `https://www.googleapis.com/youtube/v3/search?part=snippet&forMine=true&type=video&maxResults=50&order=date`,
      { headers: { 'Authorization': `Bearer ${accessToken}` } }
    );
    const searchData = await searchResponse.json();

    if (searchData.error) {
      console.error('Search fetch error:', searchData.error);
      return NextResponse.json({ error: searchData.error.message }, { status: 400 });
    }

    // Get video details to check privacy status and scheduled time
    const videoIds = searchData.items?.map(item => item.id.videoId).join(',') || '';
    
    if (!videoIds) {
      return NextResponse.json({ 
        success: true, 
        message: 'No videos found',
        scheduled_found: 0,
        upcoming_added: 0
      });
    }

    const videosResponse = await fetch(
      `https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id=${videoIds}`,
      { headers: { 'Authorization': `Bearer ${accessToken}` } }
    );
    const videosData = await videosResponse.json();

    if (videosData.error) {
      console.error('Videos fetch error:', videosData.error);
      return NextResponse.json({ error: videosData.error.message }, { status: 400 });
    }

    // Filter for scheduled (private with publishAt) videos
    const scheduledVideos = videosData.items?.filter(video => {
      const status = video.status;
      // Scheduled videos have privacyStatus 'private' and a publishAt date in the future
      return status?.privacyStatus === 'private' && status?.publishAt;
    }) || [];

    // Also check for upcoming live broadcasts / premieres
    const upcomingVideos = videosData.items?.filter(video => {
      const snippet = video.snippet;
      return snippet?.liveBroadcastContent === 'upcoming';
    }) || [];

    // Combine both types
    const allUpcoming = [...scheduledVideos, ...upcomingVideos];
    
    // Remove duplicates by video ID
    const uniqueUpcoming = allUpcoming.filter((video, index, self) =>
      index === self.findIndex(v => v.id === video.id)
    );

    let addedCount = 0;
    let skippedCount = 0;

    for (const video of uniqueUpcoming) {
      const snippet = video.snippet;
      const status = video.status;
      
      // Determine scheduled date
      let scheduledDate = status?.publishAt || snippet?.publishedAt;
      
      // Check if already exists
      const existing = await db.collection('upcoming_videos').findOne({
        $or: [
          { youtube_video_id: video.id },
          { title: snippet.title }
        ]
      });

      if (existing) {
        skippedCount++;
        continue;
      }

      const { song, artist } = parseVideoTitle(snippet.title);

      const upcomingVideo = {
        id: uuidv4(),
        youtube_video_id: video.id,
        title: song,
        artist: artist,
        scheduled_date: scheduledDate,
        thumbnail: snippet.thumbnails?.high?.url || snippet.thumbnails?.default?.url || '',
        description: snippet.description?.substring(0, 200) || '',
        created_at: new Date().toISOString()
      };

      await db.collection('upcoming_videos').insertOne(upcomingVideo);
      addedCount++;
    }

    return NextResponse.json({
      success: true,
      message: `Found ${uniqueUpcoming.length} scheduled videos. Added ${addedCount} new, ${skippedCount} already existed.`,
      scheduled_found: uniqueUpcoming.length,
      upcoming_added: addedCount,
      upcoming_skipped: skippedCount
    });

  } catch (err) {
    console.error('Scheduled videos sync error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
