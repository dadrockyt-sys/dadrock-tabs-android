import { getDb } from '@/lib/mongodb';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const db = await getDb();

    // Use MongoDB's $sample to get a truly random song
    const songs = await db.collection('song_pages')
      .aggregate([{ $sample: { size: 1 } }])
      .project({ slug: 1 })
      .toArray();

    if (!songs || songs.length === 0) {
      return NextResponse.json({ error: 'No songs found' }, { status: 404 });
    }

    return NextResponse.json({ slug: songs[0].slug }, {
      headers: { 'Cache-Control': 'no-store' },
    });
  } catch (error) {
    console.error('Random song error:', error);
    return NextResponse.json({ error: 'Failed' }, { status: 500 });
  }
}
