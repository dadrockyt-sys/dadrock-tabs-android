import { getDb } from '@/lib/mongodb';
import { NextResponse } from 'next/server';

export async function GET() {
  try {
    const db = await getDb();
    
    // Use today's date as a seed for deterministic "random" selection
    const today = new Date();
    const dateStr = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;
    
    // Simple hash from date string
    let hash = 0;
    for (let i = 0; i < dateStr.length; i++) {
      const char = dateStr.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    hash = Math.abs(hash);
    
    // Get total count of song pages
    const totalSongs = await db.collection('song_pages').countDocuments({});
    
    if (totalSongs === 0) {
      return NextResponse.json({ song: null });
    }
    
    // Pick a song based on hash
    const skipIndex = hash % totalSongs;
    const song = await db.collection('song_pages')
      .find({})
      .skip(skipIndex)
      .limit(1)
      .project({ slug: 1, title: 1, artist: 1, videoId: 1, thumbnail: 1, duration: 1 })
      .toArray();
    
    if (!song || song.length === 0) {
      return NextResponse.json({ song: null });
    }
    
    const cleanArtist = song[0].artist?.replace(/ -$/, '').trim() || 'DadRock Tabs';
    
    return NextResponse.json({
      song: {
        slug: song[0].slug,
        title: song[0].title,
        artist: cleanArtist,
        videoId: song[0].videoId,
        thumbnail: song[0].thumbnail,
        duration: song[0].duration || 0,
      },
      date: dateStr,
    }, {
      headers: {
        'Cache-Control': 'public, max-age=3600, s-maxage=3600',
      }
    });
  } catch (error) {
    console.error('Song of the day error:', error);
    return NextResponse.json({ song: null, error: 'Failed to fetch' }, { status: 500 });
  }
}
