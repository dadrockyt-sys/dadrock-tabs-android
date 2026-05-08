import { getDb } from '@/lib/mongodb';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const db = await getDb();
    
    // Get recently added songs
    const recentSongs = await db.collection('song_pages')
      .find({})
      .sort({ created_at: -1 })
      .limit(20)
      .project({ title: 1, artist: 1, slug: 1, created_at: 1, difficulty: 1, avgRating: 1 })
      .toArray();

    // Get total counts
    const totalSongs = await db.collection('song_pages').countDocuments();
    const totalComments = await db.collection('comments').countDocuments();

    return NextResponse.json({
      recentSongs,
      stats: { totalSongs, totalComments },
    });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch data' }, { status: 500 });
  }
}
