import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY;
const YOUTUBE_CLIENT_ID = process.env.YOUTUBE_CLIENT_ID;
const YOUTUBE_CLIENT_SECRET = process.env.YOUTUBE_CLIENT_SECRET;
const CHANNEL_ID = 'UCl9DFhCasFrFOD_5HjlUmwQ'; // DadRock Tabs channel

// Helper to get a valid YouTube OAuth access token (with auto-refresh)
async function getValidAccessToken(db) {
  const tokens = await db.collection('settings').findOne({ type: 'youtube_oauth' });

  if (!tokens?.access_token) {
    return null;
  }

  // Check if token is expired (with 5 min buffer)
  if (tokens.expires_at && Date.now() > tokens.expires_at - 300000) {
    if (!tokens.refresh_token || !YOUTUBE_CLIENT_ID || !YOUTUBE_CLIENT_SECRET) {
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

// Fetch YouTube video statistics using OAuth token or API key
async function fetchVideoStats(videoIds, db) {
  const idsParam = videoIds.join(',');

  // Try OAuth token first (more reliable, no API key restrictions)
  const accessToken = await getValidAccessToken(db);
  if (accessToken) {
    try {
      const statsUrl = `https://www.googleapis.com/youtube/v3/videos?id=${idsParam}&part=statistics`;
      const res = await fetch(statsUrl, {
        headers: { 'Authorization': `Bearer ${accessToken}` }
      });
      const data = await res.json();

      if (data.items && !data.error) {
        const statsMap = {};
        for (const item of data.items) {
          statsMap[item.id] = {
            viewCount: parseInt(item.statistics?.viewCount || 0),
            likeCount: parseInt(item.statistics?.likeCount || 0),
          };
        }
        return statsMap;
      }
    } catch (err) {
      console.error('OAuth stats fetch failed:', err);
    }
  }

  // Fallback to API key
  if (YOUTUBE_API_KEY) {
    try {
      const statsUrl = `https://www.googleapis.com/youtube/v3/videos?key=${YOUTUBE_API_KEY}&id=${idsParam}&part=statistics`;
      const res = await fetch(statsUrl);
      const data = await res.json();

      if (data.items && !data.error) {
        const statsMap = {};
        for (const item of data.items) {
          statsMap[item.id] = {
            viewCount: parseInt(item.statistics?.viewCount || 0),
            likeCount: parseInt(item.statistics?.likeCount || 0),
          };
        }
        return statsMap;
      }
    } catch (err) {
      console.error('API key stats fetch failed:', err);
    }
  }

  return {}; // Return empty if both methods fail
}

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const limit = parseInt(searchParams.get('limit') || '10');

  try {
    const db = await getDb();

    // First, check for manually configured top lessons
    const topLessonsConfig = await db.collection('settings').findOne({ type: 'top_lessons' });

    if (topLessonsConfig?.lessons) {
      const manualLessons = topLessonsConfig.lessons
        .filter(lesson => lesson.youtubeUrl && lesson.videoId)
        .slice(0, limit)
        .map(lesson => ({
          id: lesson.videoId,
          videoId: lesson.videoId,
          title: lesson.title || 'Untitled',
          fullTitle: lesson.title,
          artist: lesson.artist || 'DadRock Tabs',
          thumbnail: lesson.thumbnail || `https://i.ytimg.com/vi/${lesson.videoId}/hqdefault.jpg`,
          viewCount: 0,
          likeCount: 0,
          publishedAt: null,
          description: '',
          position: lesson.position
        }));

      if (manualLessons.length > 0) {
        // Fetch real view/like counts from YouTube
        const videoIds = manualLessons.map(v => v.videoId);
        const statsMap = await fetchVideoStats(videoIds, db);

        // Enrich manual lessons with real stats
        for (const lesson of manualLessons) {
          if (statsMap[lesson.videoId]) {
            lesson.viewCount = statsMap[lesson.videoId].viewCount;
            lesson.likeCount = statsMap[lesson.videoId].likeCount;
          }
        }

        return NextResponse.json({
          videos: manualLessons,
          total: manualLessons.length,
          source: 'manual'
        });
      }
    }

    // Fallback: Try to get from database
    const dbVideos = await db.collection('videos')
      .find({})
      .sort({ viewCount: -1 })
      .limit(limit * 2)
      .toArray();

    // If we have videos in DB with view counts, use those
    if (dbVideos.length > 0 && dbVideos.some(v => v.viewCount)) {
      const sortedDbVideos = dbVideos
        .filter(v => v.viewCount)
        .sort((a, b) => (b.viewCount || 0) - (a.viewCount || 0))
        .slice(0, limit)
        .map(video => ({
          id: video.id || video.videoId,
          videoId: video.videoId,
          title: video.song || video.title,
          fullTitle: video.title,
          artist: video.artist || 'DadRock Tabs',
          thumbnail: video.thumbnail,
          viewCount: video.viewCount || 0,
          likeCount: video.likeCount || 0,
          publishedAt: video.publishedAt,
          description: ''
        }));

      if (sortedDbVideos.length >= limit) {
        return NextResponse.json({
          videos: sortedDbVideos,
          total: sortedDbVideos.length,
          source: 'database'
        });
      }
    }

    // Fallback: Try YouTube API search
    const searchUrl = `https://www.googleapis.com/youtube/v3/search?key=${YOUTUBE_API_KEY}&channelId=${CHANNEL_ID}&part=snippet&type=video&maxResults=50&order=viewCount`;

    const searchResponse = await fetch(searchUrl);
    const searchData = await searchResponse.json();

    if (searchData.error) {
      console.error('YouTube API error:', searchData.error);

      // If API fails, return most recent videos from DB as fallback
      const fallbackVideos = await db.collection('videos')
        .find({})
        .sort({ created_at: -1 })
        .limit(limit)
        .toArray();

      return NextResponse.json({
        videos: fallbackVideos.map(video => ({
          id: video.id || video.videoId,
          videoId: video.videoId,
          title: video.song || video.title,
          fullTitle: video.title,
          artist: video.artist || 'DadRock Tabs',
          thumbnail: video.thumbnail,
          viewCount: 0,
          likeCount: 0,
          publishedAt: video.publishedAt || video.created_at,
          description: ''
        })),
        total: fallbackVideos.length,
        source: 'database_fallback'
      });
    }

    if (!searchData.items || searchData.items.length === 0) {
      return NextResponse.json({ videos: [], total: 0 });
    }

    // Get video IDs to fetch statistics
    const videoIds = searchData.items.map(item => item.id.videoId).join(',');

    // Fetch video statistics (view counts)
    const statsUrl = `https://www.googleapis.com/youtube/v3/videos?key=${YOUTUBE_API_KEY}&id=${videoIds}&part=snippet,statistics`;

    const statsResponse = await fetch(statsUrl);
    const statsData = await statsResponse.json();

    if (statsData.error) {
      console.error('YouTube stats error:', statsData.error);
      return NextResponse.json({ error: statsData.error.message }, { status: 400 });
    }

    // Sort by view count and take top N
    const sortedVideos = (statsData.items || [])
      .sort((a, b) => parseInt(b.statistics?.viewCount || 0) - parseInt(a.statistics?.viewCount || 0))
      .slice(0, limit)
      .map(video => {
        const snippet = video.snippet;
        const stats = video.statistics;

        // Parse title for song and artist
        let title = snippet.title || '';
        let artist = 'DadRock Tabs';

        // Clean up title
        let cleanTitle = title.replace(/\s*(Guitar|Bass|TAB|TABS|Lesson|Tutorial|\+|\(|\)|\[|\]|HD|Official).*/gi, '').trim();

        if (cleanTitle.includes(' - ')) {
          const parts = cleanTitle.split(' - ', 2);
          cleanTitle = parts[0].trim();
          artist = parts[1]?.trim() || artist;
        }

        return {
          id: video.id,
          videoId: video.id,
          title: cleanTitle,
          fullTitle: title,
          artist: artist,
          thumbnail: snippet.thumbnails?.high?.url || snippet.thumbnails?.default?.url,
          viewCount: parseInt(stats?.viewCount || 0),
          likeCount: parseInt(stats?.likeCount || 0),
          publishedAt: snippet.publishedAt,
          description: snippet.description?.substring(0, 200) || ''
        };
      });

    return NextResponse.json({
      videos: sortedVideos,
      total: sortedVideos.length,
      source: 'youtube_api'
    });

  } catch (err) {
    console.error('Top videos error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
