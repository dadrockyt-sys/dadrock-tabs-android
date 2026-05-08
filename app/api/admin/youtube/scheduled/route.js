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

    // Fetch ALL videos from the channel using pagination
    let allVideoIds = [];
    let nextPageToken = '';
    let pageCount = 0;
    const maxPages = 5; // Fetch up to 250 videos (50 per page)

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

      if (searchData.error) {
        console.error('Search fetch error:', searchData.error);
        break;
      }

      const videoIds = searchData.items?.map(item => item.id.videoId) || [];
      allVideoIds = [...allVideoIds, ...videoIds];
      
      nextPageToken = searchData.nextPageToken || '';
      pageCount++;
    } while (nextPageToken && pageCount < maxPages);

    if (allVideoIds.length === 0) {
      return NextResponse.json({ 
        success: true, 
        message: 'No videos found',
        scheduled_found: 0,
        upcoming_added: 0
      });
    }

    // Fetch video details in batches of 50 (API limit)
    let allScheduledVideos = [];
    
    for (let i = 0; i < allVideoIds.length; i += 50) {
      const batchIds = allVideoIds.slice(i, i + 50).join(',');
      
      const videosResponse = await fetch(
        `https://www.googleapis.com/youtube/v3/videos?part=snippet,status&id=${batchIds}`,
        { headers: { 'Authorization': `Bearer ${accessToken}` } }
      );
      const videosData = await videosResponse.json();

      if (videosData.error) {
        console.error('Videos fetch error:', videosData.error);
        continue;
      }

      // Filter for scheduled (private with publishAt) videos
      const scheduledVideos = videosData.items?.filter(video => {
        const status = video.status;
        const snippet = video.snippet;
        
        // Method 1: Private videos with a publishAt date (scheduled)
        if (status?.privacyStatus === 'private' && status?.publishAt) {
          return true;
        }
        
        // Method 2: Upcoming premieres/live broadcasts
        if (snippet?.liveBroadcastContent === 'upcoming') {
          return true;
        }
        
        return false;
      }) || [];

      allScheduledVideos = [...allScheduledVideos, ...scheduledVideos];
    }

    // Remove duplicates by video ID
    const uniqueUpcoming = allScheduledVideos.filter((video, index, self) =>
      index === self.findIndex(v => v.id === video.id)
    );

    let addedCount = 0;
    let skippedCount = 0;
    let updatedCount = 0;

    // Helper function to download image and convert to base64
    async function downloadThumbnailAsBase64(imageUrl, accessToken) {
      try {
        const response = await fetch(imageUrl, {
          headers: accessToken ? { 'Authorization': `Bearer ${accessToken}` } : {}
        });
        
        if (!response.ok) return null;
        
        const arrayBuffer = await response.arrayBuffer();
        const base64 = Buffer.from(arrayBuffer).toString('base64');
        const contentType = response.headers.get('content-type') || 'image/jpeg';
        
        return `data:${contentType};base64,${base64}`;
      } catch (err) {
        console.error('Failed to download thumbnail:', err);
        return null;
      }
    }

    for (const video of uniqueUpcoming) {
      const snippet = video.snippet;
      const status = video.status;
      
      // Determine scheduled date
      let scheduledDate = status?.publishAt || snippet?.publishedAt;
      
      // Get the best available thumbnail URL
      const thumbnailUrl = snippet.thumbnails?.high?.url || 
                          snippet.thumbnails?.medium?.url ||
                          snippet.thumbnails?.default?.url || '';
      
      // Download and store thumbnail as base64 (never expires!)
      let storedThumbnail = null;
      if (thumbnailUrl) {
        storedThumbnail = await downloadThumbnailAsBase64(thumbnailUrl, accessToken);
      }
      
      // Check if already exists
      const existing = await db.collection('upcoming_videos').findOne({
        youtube_video_id: video.id
      });

      if (existing) {
        // Update with fresh thumbnail
        const updateData = { 
          scheduled_date: scheduledDate,
          updated_at: new Date().toISOString()
        };
        
        // Only update thumbnail if we successfully downloaded a new one
        if (storedThumbnail) {
          updateData.thumbnail_base64 = storedThumbnail;
          updateData.thumbnail = storedThumbnail; // Use base64 as primary
        }
        
        await db.collection('upcoming_videos').updateOne(
          { youtube_video_id: video.id },
          { $set: updateData }
        );
        updatedCount++;
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
        thumbnail: storedThumbnail || thumbnailUrl, // Prefer base64
        thumbnail_base64: storedThumbnail,
        thumbnail_url: thumbnailUrl, // Keep original URL as backup
        description: snippet.description?.substring(0, 200) || '',
        created_at: new Date().toISOString()
      };

      await db.collection('upcoming_videos').insertOne(upcomingVideo);
      addedCount++;
    }

    // Auto-cleanup: Delete past scheduled videos that have already gone live
    const now = new Date();
    const deleteResult = await db.collection('upcoming_videos').deleteMany({
      scheduled_date: { $lt: now.toISOString() }
    });

    return NextResponse.json({
      success: true,
      message: `Scanned ${allVideoIds.length} videos. Found ${uniqueUpcoming.length} scheduled. Added ${addedCount} new, updated ${updatedCount} existing.${deleteResult.deletedCount > 0 ? ` Removed ${deleteResult.deletedCount} past videos.` : ''}`,
      total_scanned: allVideoIds.length,
      scheduled_found: uniqueUpcoming.length,
      upcoming_added: addedCount,
      upcoming_updated: updatedCount,
      past_removed: deleteResult.deletedCount
    });

  } catch (err) {
    console.error('Scheduled videos sync error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
