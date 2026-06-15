import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

export async function GET() {
  try {
    const db = await getDb();
    
    // Get top 50 videos by view count
    const topVideos = await db.collection('videos')
      .find({ view_count: { $exists: true, $ne: null } })
      .sort({ view_count: -1 })
      .limit(50)
      .toArray();
    
    // Get all song pages
    const songPages = await db.collection('song_pages')
      .find({}, { projection: { slug: 1, artist: 1, title: 1 } })
      .limit(100)
      .toArray();
    
    return NextResponse.json({
      topVideos: topVideos.map(v => ({
        artist: v.artist,
        song: v.song,
        views: v.view_count || 0,
        slug: v.slug
      })),
      songPages: songPages.map(s => ({
        slug: s.slug,
        artist: s.artist,
        title: s.title
      }))
    });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
