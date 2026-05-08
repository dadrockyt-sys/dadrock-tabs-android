import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const limit = parseInt(searchParams.get('limit') || '100');
  const page = parseInt(searchParams.get('page') || '1');
  const skip = (page - 1) * limit;

  try {
    const db = await getDb();
    
    const songs = await db.collection('song_pages')
      .find({})
      .sort({ viewCount: -1 })
      .skip(skip)
      .limit(limit)
      .toArray();

    const total = await db.collection('song_pages').countDocuments();

    return NextResponse.json({
      songs: songs.map(s => ({
        id: s.id,
        videoId: s.videoId,
        title: s.title,
        artist: s.artist,
        slug: s.slug,
        thumbnail: s.thumbnail,
        viewCount: s.viewCount,
        likeCount: s.likeCount,
        duration: s.duration
      })),
      total,
      page,
      limit
    });
  } catch (err) {
    console.error('Songs list error:', err);
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
