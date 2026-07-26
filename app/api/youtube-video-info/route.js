import { NextResponse } from 'next/server';

export const runtime = 'nodejs';

function formatYouTubeDuration(duration = '') {
  const match = duration.match(
    /P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/
  );

  if (!match) return '';

  const days = Number(match[1] || 0);
  const hours = Number(match[2] || 0) + days * 24;
  const minutes = Number(match[3] || 0);
  const seconds = Number(match[4] || 0);

  const paddedSeconds = String(seconds).padStart(2, '0');

  if (hours > 0) {
    return `${hours}:${String(minutes).padStart(2, '0')}:${paddedSeconds}`;
  }

  return `${minutes}:${paddedSeconds}`;
}

export async function GET(request) {
  try {
    const videoId = request.nextUrl.searchParams.get('videoId')?.trim();

    if (!videoId || !/^[A-Za-z0-9_-]{11}$/.test(videoId)) {
      return NextResponse.json(
        { error: 'A valid YouTube video ID is required.' },
        { status: 400 }
      );
    }

    const apiKey = process.env.YOUTUBE_API_KEY;

    if (!apiKey) {
      console.error('YOUTUBE_API_KEY is not configured.');

      return NextResponse.json(
        { error: 'YouTube video lookup is not configured.' },
        { status: 500 }
      );
    }

    const youtubeUrl = new URL(
      'https://www.googleapis.com/youtube/v3/videos'
    );

    youtubeUrl.searchParams.set('part', 'snippet,contentDetails');
    youtubeUrl.searchParams.set('id', videoId);
    youtubeUrl.searchParams.set('key', apiKey);

    const response = await fetch(youtubeUrl, {
      cache: 'no-store',
    });

    const data = await response.json();

    if (!response.ok) {
      console.error('YouTube API error:', data);

      return NextResponse.json(
        { error: 'YouTube could not retrieve this video.' },
        { status: response.status }
      );
    }

    const video = data.items?.[0];

    if (!video) {
      return NextResponse.json(
        {
          error:
            'Video not found. It may be private, deleted, or unavailable.',
        },
        { status: 404 }
      );
    }

    const snippet = video.snippet || {};
    const contentDetails = video.contentDetails || {};

    return NextResponse.json({
      videoId,
      title: snippet.title || 'Untitled video',
      channelTitle: snippet.channelTitle || 'Unknown channel',
      thumbnail:
        snippet.thumbnails?.maxres?.url ||
        snippet.thumbnails?.standard?.url ||
        snippet.thumbnails?.high?.url ||
        snippet.thumbnails?.medium?.url ||
        snippet.thumbnails?.default?.url ||
        '',
      duration: formatYouTubeDuration(contentDetails.duration),
      durationIso: contentDetails.duration || '',
    });
  } catch (error) {
    console.error('YouTube video information error:', error);

    return NextResponse.json(
      { error: 'Unable to retrieve YouTube video information.' },
      { status: 500 }
    );
  }
}
