import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY;
const CHANNEL_ID = 'UCl9DFhCasFrFOD_5HjlUmwQ'; // DadRock Tabs channel

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const limit = parseInt(searchParams.get('limit') || '10');

  try {
    // First try to get from our database (most reliable)
    const db = await getDb();
    const dbVideos = await db.collection('videos')
      .find({})
      .sort({ viewCount: -1 })
      .limit(limit * 2) // Get more to filter
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

    // Fallback: Try YouTube API
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
