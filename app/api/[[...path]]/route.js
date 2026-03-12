import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';
import { v4 as uuidv4 } from 'uuid';

// Admin password from env
const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'Babyty99';
const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY || '';
const DADROCK_CHANNEL_ID = 'UCLN8LV-ojTQP2wPtDg1kvGQ'; // DadRock Tabs channel ID

// Helper to parse video title to extract song and artist
function parseVideoTitle(title) {
  // Remove common suffixes
  let cleanTitle = title.replace(/\s*(Guitar|Bass|TAB|TABS|Lesson|Tutorial|\+|\(|\)|\[|\]|HD|Official).*/gi, '').trim();
  
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
  
  return { song: cleanTitle, artist: 'DadRock Tabs' };
}

// Helper to extract YouTube thumbnail
function extractYouTubeThumbnail(url) {
  let videoId = null;
  if (url.includes('youtube.com/watch?v=')) {
    videoId = url.split('v=')[1]?.split('&')[0];
  } else if (url.includes('youtu.be/')) {
    videoId = url.split('youtu.be/')[1]?.split('?')[0];
  } else if (url.includes('youtube.com/embed/')) {
    videoId = url.split('embed/')[1]?.split('?')[0];
  } else if (url.includes('youtube.com/shorts/')) {
    videoId = url.split('shorts/')[1]?.split('?')[0];
  }
  return videoId ? `https://img.youtube.com/vi/${videoId}/mqdefault.jpg` : '';
}

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

// Helper to convert YouTube URL to embed format
function convertToEmbedUrl(url) {
  if (!url) return url;
  let videoId = null;
  if (url.includes('youtube.com/watch?v=')) {
    videoId = url.split('v=')[1]?.split('&')[0];
  } else if (url.includes('youtu.be/')) {
    videoId = url.split('youtu.be/')[1]?.split('?')[0];
  } else if (url.includes('youtube.com/shorts/')) {
    videoId = url.split('shorts/')[1]?.split('?')[0];
  } else if (url.includes('youtube.com/embed/')) {
    return url; // Already embed format
  }
  return videoId ? `https://www.youtube.com/embed/${videoId}` : url;
}

// Helper to extract video ID from YouTube URL
function extractVideoId(url) {
  if (!url) return '';
  let videoId = null;
  if (url.includes('youtube.com/watch?v=')) {
    videoId = url.split('v=')[1]?.split('&')[0];
  } else if (url.includes('youtu.be/')) {
    videoId = url.split('youtu.be/')[1]?.split('?')[0];
  } else if (url.includes('youtube.com/embed/')) {
    videoId = url.split('embed/')[1]?.split('?')[0];
  } else if (url.includes('youtube.com/shorts/')) {
    videoId = url.split('shorts/')[1]?.split('?')[0];
  }
  return videoId || '';
}

export async function GET(request, context) {
  const params = await context.params;
  const pathSegments = params?.path || [];
  const path = '/' + pathSegments.join('/');
  const { searchParams } = new URL(request.url);

  try {
    // Health check
    if (path === '/health' || path === '/') {
      return NextResponse.json({ status: 'healthy', message: 'DadRock Tabs API' });
    }

    // Get site settings
    if (path === '/settings') {
      const db = await getDb();
      const settings = await db.collection('settings').findOne({ type: 'site' });
      return NextResponse.json({
        featured_video_url: settings?.featured_video_url || 'https://www.youtube.com/embed/BT4EyYXSKA',
        featured_video_title: settings?.featured_video_title || 'We Will Rock You',
        featured_video_artist: settings?.featured_video_artist || 'Queen',
        ad_link: settings?.ad_link || 'https://my-store-b8bb42.creator-spring.com/',
        ad_image: settings?.ad_image || '',
        ad_headline: settings?.ad_headline || 'Check Out Our Merchandise!',
        ad_description: settings?.ad_description || 'Support DadRock Tabs by grabbing some awesome gear',
        ad_button_text: settings?.ad_button_text || 'Shop Now',
        ad_duration: settings?.ad_duration || 5
      });
    }

    // Get all unique artists
    if (path === '/artists') {
      const db = await getDb();
      const artists = await db.collection('videos').aggregate([
        { $group: { _id: '$artist', count: { $sum: 1 } } },
        { $sort: { count: -1 } },
        { $project: { artist: '$_id', count: 1, _id: 0 } }
      ]).toArray();
      
      return NextResponse.json({
        artists: artists.filter(a => a.artist),
        total: artists.length
      });
    }

    // Get all videos with search
    if (path === '/videos') {
      const db = await getDb();
      const search = searchParams.get('search');
      const searchType = searchParams.get('search_type') || 'all';
      const skip = parseInt(searchParams.get('skip') || '0');
      const limit = parseInt(searchParams.get('limit') || '50');

      let query = {};
      if (search) {
        const searchRegex = { $regex: search, $options: 'i' };
        if (searchType === 'song') {
          query = { song: searchRegex };
        } else if (searchType === 'artist') {
          query = { artist: searchRegex };
        } else {
          query = { $or: [{ song: searchRegex }, { artist: searchRegex }] };
        }
      }

      const total = await db.collection('videos').countDocuments(query);
      const videos = await db.collection('videos')
        .find(query)
        .skip(skip)
        .limit(limit)
        .toArray();

      // Format videos for response
      const formattedVideos = videos.map(v => ({
        id: v.id,
        song: v.song,
        artist: v.artist,
        youtube_url: v.youtube_url,
        thumbnail: v.thumbnail,
        created_at: v.created_at || new Date().toISOString()
      }));

      return NextResponse.json({ videos: formattedVideos, total });
    }

    // Get single video
    if (path.startsWith('/videos/') && pathSegments.length === 2) {
      const videoId = pathSegments[1];
      const db = await getDb();
      const video = await db.collection('videos').findOne({ id: videoId });
      
      if (!video) {
        return NextResponse.json({ error: 'Video not found' }, { status: 404 });
      }

      return NextResponse.json({
        id: video.id,
        song: video.song,
        artist: video.artist,
        youtube_url: video.youtube_url,
        thumbnail: video.thumbnail,
        created_at: video.created_at || new Date().toISOString()
      });
    }

    // Admin stats
    if (path === '/admin/stats') {
      if (!verifyAdmin(request)) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }
      const db = await getDb();
      const totalVideos = await db.collection('videos').countDocuments({});
      const artists = await db.collection('videos').distinct('artist');
      return NextResponse.json({
        total_videos: totalVideos,
        total_artists: artists.length
      });
    }

    // Get upcoming videos - Now handled by /api/upcoming/route.js
    // (Keeping comment for reference)

    // Admin: Get all upcoming videos (includes past ones)
    if (path === '/admin/upcoming') {
      if (!verifyAdmin(request)) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }
      const db = await getDb();
      const upcoming = await db.collection('upcoming_videos')
        .find({})
        .sort({ scheduled_date: 1 })
        .toArray();
      
      return NextResponse.json({ 
        upcoming: upcoming.map(v => ({
          id: v.id,
          title: v.title,
          artist: v.artist,
          scheduled_date: v.scheduled_date,
          thumbnail: v.thumbnail,
          description: v.description
        })),
        total: upcoming.length 
      });
    }

    // Admin: Get top lessons configuration
    if (path === '/admin/top-lessons') {
      if (!verifyAdmin(request)) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }
      const db = await getDb();
      const config = await db.collection('settings').findOne({ type: 'top_lessons' });
      
      return NextResponse.json({ 
        lessons: config?.lessons || Array(10).fill(null).map((_, i) => ({ position: i + 1, youtubeUrl: '', title: '', artist: '' }))
      });
    }

    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function POST(request, context) {
  const params = await context.params;
  const pathSegments = params?.path || [];
  const path = '/' + pathSegments.join('/');

  try {
    // Admin login
    if (path === '/admin/login') {
      const body = await request.json();
      if (body.password === ADMIN_PASSWORD) {
        return NextResponse.json({ success: true, message: 'Login successful' });
      }
      return NextResponse.json({ error: 'Invalid password' }, { status: 401 });
    }

    // YouTube sync endpoint
    if (path === '/admin/youtube/sync') {
      if (!verifyAdmin(request)) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }

      const body = await request.json().catch(() => ({}));
      const apiKey = body.api_key || YOUTUBE_API_KEY;
      const channelId = body.channel_id || DADROCK_CHANNEL_ID;

      if (!apiKey) {
        return NextResponse.json({ error: 'YouTube API key not configured' }, { status: 400 });
      }

      try {
        // First, get the uploads playlist ID for the channel
        const channelResponse = await fetch(
          `https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id=${channelId}&key=${apiKey}`
        );
        const channelData = await channelResponse.json();

        if (channelData.error) {
          return NextResponse.json({ error: channelData.error.message }, { status: 400 });
        }

        if (!channelData.items || channelData.items.length === 0) {
          return NextResponse.json({ error: 'Channel not found' }, { status: 404 });
        }

        const uploadsPlaylistId = channelData.items[0].contentDetails.relatedPlaylists.uploads;
        const db = await getDb();

        let videosAdded = 0;
        let videosSkipped = 0;
        let nextPageToken = null;
        const errors = [];

        // Fetch all videos from uploads playlist (paginated)
        do {
          const playlistUrl = `https://www.googleapis.com/youtube/v3/playlistItems?part=snippet&playlistId=${uploadsPlaylistId}&maxResults=50&key=${apiKey}${nextPageToken ? `&pageToken=${nextPageToken}` : ''}`;
          
          const playlistResponse = await fetch(playlistUrl);
          const playlistData = await playlistResponse.json();

          if (playlistData.error) {
            errors.push(playlistData.error.message);
            break;
          }

          for (const item of playlistData.items || []) {
            const snippet = item.snippet;
            const videoId = snippet.resourceId.videoId;
            const title = snippet.title;
            const youtubeUrl = `https://www.youtube.com/watch?v=${videoId}`;
            const thumbnail = snippet.thumbnails?.high?.url || snippet.thumbnails?.default?.url || '';

            // Check if video already exists
            const existing = await db.collection('videos').findOne({ youtube_url: youtubeUrl });
            if (existing) {
              videosSkipped++;
              continue;
            }

            // Parse title to get song and artist
            const { song, artist } = parseVideoTitle(title);

            // Create video entry
            const video = {
              id: uuidv4(),
              song,
              artist,
              youtube_url: youtubeUrl,
              thumbnail,
              created_at: new Date().toISOString()
            };

            try {
              await db.collection('videos').insertOne(video);
              videosAdded++;
            } catch (e) {
              errors.push(`Failed to add '${title}': ${e.message}`);
            }
          }

          nextPageToken = playlistData.nextPageToken;
        } while (nextPageToken);

        return NextResponse.json({
          success: true,
          message: `Sync completed! ${videosAdded} videos added, ${videosSkipped} already existed.`,
          videos_added: videosAdded,
          videos_skipped: videosSkipped,
          errors
        });

      } catch (e) {
        console.error('YouTube sync error:', e);
        return NextResponse.json({ error: `Sync failed: ${e.message}` }, { status: 500 });
      }
    }

    // Create video (admin)
    if (path === '/admin/videos') {
      if (!verifyAdmin(request)) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }
      
      const body = await request.json();
      const db = await getDb();
      
      const video = {
        id: uuidv4(),
        song: body.song,
        artist: body.artist,
        youtube_url: body.youtube_url,
        thumbnail: body.thumbnail || extractYouTubeThumbnail(body.youtube_url),
        created_at: new Date().toISOString()
      };

      await db.collection('videos').insertOne(video);
      return NextResponse.json(video, { status: 201 });
    }

    // Create upcoming video (admin)
    if (path === '/admin/upcoming') {
      if (!verifyAdmin(request)) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }
      
      const body = await request.json();
      const db = await getDb();
      
      if (!body.title || !body.scheduled_date) {
        return NextResponse.json({ error: 'Title and scheduled_date are required' }, { status: 400 });
      }
      
      const upcoming = {
        id: uuidv4(),
        title: body.title,
        artist: body.artist || '',
        scheduled_date: body.scheduled_date,
        thumbnail: body.thumbnail || '',
        description: body.description || '',
        created_at: new Date().toISOString()
      };

      await db.collection('upcoming_videos').insertOne(upcoming);
      return NextResponse.json(upcoming, { status: 201 });
    }

    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function PUT(request, context) {
  const params = await context.params;
  const pathSegments = params?.path || [];
  const path = '/' + pathSegments.join('/');

  try {
    // Update site settings (admin)
    if (path === '/admin/settings') {
      if (!verifyAdmin(request)) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }

      const body = await request.json();
      const db = await getDb();

      const updateData = { type: 'site', updated_at: new Date().toISOString() };
      if (body.featured_video_url) {
        updateData.featured_video_url = convertToEmbedUrl(body.featured_video_url);
      }
      if (body.featured_video_title) {
        updateData.featured_video_title = body.featured_video_title;
      }
      if (body.featured_video_artist) {
        updateData.featured_video_artist = body.featured_video_artist;
      }
      if (body.ad_link) {
        updateData.ad_link = body.ad_link;
      }
      if (body.ad_image !== undefined) {
        updateData.ad_image = body.ad_image;
      }
      if (body.ad_headline) {
        updateData.ad_headline = body.ad_headline;
      }
      if (body.ad_description) {
        updateData.ad_description = body.ad_description;
      }
      if (body.ad_button_text) {
        updateData.ad_button_text = body.ad_button_text;
      }
      if (body.ad_duration !== undefined) {
        // Validate: min 5, max 30, default 5
        const duration = parseInt(body.ad_duration) || 5;
        updateData.ad_duration = Math.min(30, Math.max(5, duration));
      }

      await db.collection('settings').updateOne(
        { type: 'site' },
        { $set: updateData },
        { upsert: true }
      );

      return NextResponse.json({ success: true, message: 'Settings updated successfully' });
    }

    // Update video (admin)
    if (path.startsWith('/admin/videos/') && pathSegments.length === 3) {
      if (!verifyAdmin(request)) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }

      const videoId = pathSegments[2];
      const body = await request.json();
      const db = await getDb();

      const updateData = {};
      if (body.song) updateData.song = body.song;
      if (body.artist) updateData.artist = body.artist;
      if (body.youtube_url) {
        updateData.youtube_url = body.youtube_url;
        if (!body.thumbnail) {
          updateData.thumbnail = extractYouTubeThumbnail(body.youtube_url);
        }
      }
      if (body.thumbnail) updateData.thumbnail = body.thumbnail;

      const result = await db.collection('videos').updateOne(
        { id: videoId },
        { $set: updateData }
      );

      if (result.matchedCount === 0) {
        return NextResponse.json({ error: 'Video not found' }, { status: 404 });
      }

      const updatedVideo = await db.collection('videos').findOne({ id: videoId });
      return NextResponse.json(updatedVideo);
    }

    // Update top lessons (admin)
    if (path === '/admin/top-lessons') {
      if (!verifyAdmin(request)) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }

      const body = await request.json();
      const db = await getDb();

      // Validate and process the lessons array
      const lessons = (body.lessons || []).map((lesson, index) => ({
        position: index + 1,
        youtubeUrl: lesson.youtubeUrl || '',
        title: lesson.title || '',
        artist: lesson.artist || '',
        videoId: extractVideoId(lesson.youtubeUrl || ''),
        thumbnail: lesson.youtubeUrl ? `https://i.ytimg.com/vi/${extractVideoId(lesson.youtubeUrl)}/hqdefault.jpg` : ''
      }));

      await db.collection('settings').updateOne(
        { type: 'top_lessons' },
        { 
          $set: { 
            type: 'top_lessons',
            lessons: lessons,
            updated_at: new Date().toISOString()
          } 
        },
        { upsert: true }
      );

      return NextResponse.json({ success: true, message: 'Top lessons updated successfully' });
    }

    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function DELETE(request, context) {
  const params = await context.params;
  const pathSegments = params?.path || [];
  const path = '/' + pathSegments.join('/');

  try {
    // Delete video (admin)
    if (path.startsWith('/admin/videos/') && pathSegments.length === 3) {
      if (!verifyAdmin(request)) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }

      const videoId = pathSegments[2];
      const db = await getDb();

      const result = await db.collection('videos').deleteOne({ id: videoId });

      if (result.deletedCount === 0) {
        return NextResponse.json({ error: 'Video not found' }, { status: 404 });
      }

      return NextResponse.json({ message: 'Video deleted successfully' });
    }

    // Delete upcoming video (admin)
    if (path.startsWith('/admin/upcoming/') && pathSegments.length === 3) {
      if (!verifyAdmin(request)) {
        return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
      }

      const upcomingId = pathSegments[2];
      const db = await getDb();

      const result = await db.collection('upcoming_videos').deleteOne({ id: upcomingId });

      if (result.deletedCount === 0) {
        return NextResponse.json({ error: 'Upcoming video not found' }, { status: 404 });
      }

      return NextResponse.json({ message: 'Upcoming video deleted successfully' });
    }

    return NextResponse.json({ error: 'Not found' }, { status: 404 });
  } catch (error) {
    console.error('API Error:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
