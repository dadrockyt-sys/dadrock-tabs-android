import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

// YouTube OAuth configuration
const YOUTUBE_CLIENT_ID = process.env.YOUTUBE_CLIENT_ID;
const YOUTUBE_CLIENT_SECRET = process.env.YOUTUBE_CLIENT_SECRET;

// Helper to refresh access token
async function getValidAccessToken(db) {
  const tokens = await db.collection('settings').findOne({ type: 'youtube_oauth' });
  
  if (!tokens?.access_token) {
    return null;
  }

  // Check if token is expired (with 5 min buffer)
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

export async function GET(request) {
  try {
    const db = await getDb();
    
    // Auto-cleanup: Delete past scheduled videos that have already gone live
    const now = new Date();
    const deleteResult = await db.collection('upcoming_videos').deleteMany({
      scheduled_date: { $lt: now.toISOString() }
    });
    
    if (deleteResult.deletedCount > 0) {
      console.log(`Auto-cleaned ${deleteResult.deletedCount} past scheduled videos`);
    }
    
    // Get all upcoming videos
    const upcoming = await db.collection('upcoming_videos')
      .find({})
      .sort({ scheduled_date: 1 })
      .toArray();
    
    // Filter to only show future videos (extra safety)
    let upcomingVideos = upcoming.filter(v => new Date(v.scheduled_date) >= now);
    
    // Check if we need to refresh thumbnails (if any are older than 20 hours)
    const twentyHoursAgo = Date.now() - (20 * 60 * 60 * 1000);
    const needsRefresh = upcomingVideos.some(v => {
      const updatedAt = v.updated_at ? new Date(v.updated_at).getTime() : 0;
      return updatedAt < twentyHoursAgo && v.youtube_video_id;
    });
    
    // If thumbnails need refresh and we have OAuth, refresh them
    if (needsRefresh) {
      const accessToken = await getValidAccessToken(db);
      
      if (accessToken) {
        // Get video IDs that need refresh
        const videoIdsToRefresh = upcomingVideos
          .filter(v => v.youtube_video_id)
          .map(v => v.youtube_video_id);
        
        if (videoIdsToRefresh.length > 0) {
          try {
            // Fetch fresh video details from YouTube
            const videosResponse = await fetch(
              `https://www.googleapis.com/youtube/v3/videos?part=snippet&id=${videoIdsToRefresh.join(',')}`,
              { headers: { 'Authorization': `Bearer ${accessToken}` } }
            );
            const videosData = await videosResponse.json();
            
            if (videosData.items) {
              // Update thumbnails in database
              for (const video of videosData.items) {
                const freshThumbnail = video.snippet?.thumbnails?.high?.url || 
                                       video.snippet?.thumbnails?.default?.url || '';
                
                if (freshThumbnail) {
                  await db.collection('upcoming_videos').updateOne(
                    { youtube_video_id: video.id },
                    { 
                      $set: { 
                        thumbnail: freshThumbnail,
                        updated_at: new Date().toISOString()
                      } 
                    }
                  );
                }
              }
              
              // Re-fetch updated videos
              const refreshedUpcoming = await db.collection('upcoming_videos')
                .find({})
                .sort({ scheduled_date: 1 })
                .toArray();
              
              upcomingVideos = refreshedUpcoming.filter(v => new Date(v.scheduled_date) >= now);
            }
          } catch (err) {
            console.error('Failed to refresh thumbnails:', err);
            // Continue with stale thumbnails
          }
        }
      }
    }
    
    // Format response - prefer base64 thumbnails (never expire)
    const formattedUpcoming = upcomingVideos.map(v => ({
      id: v.id,
      title: v.title,
      artist: v.artist,
      scheduled_date: v.scheduled_date,
      thumbnail: v.thumbnail_base64 || v.thumbnail, // Prefer stored base64
      youtube_video_id: v.youtube_video_id,
      description: v.description
    }));
    
    return NextResponse.json({ 
      upcoming: formattedUpcoming,
      total: formattedUpcoming.length,
      refreshed: needsRefresh
    });
    
  } catch (err) {
    console.error('Upcoming videos error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
