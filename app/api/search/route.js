import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q')?.trim();
    
    if (!query || query.length < 2) {
      return NextResponse.json({ artists: [], songs: [] });
    }
    
    const db = await getDb();
    
    // Escape regex special characters for safe matching
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escapedQuery, 'i');
    
    // Search artists — get distinct artist names that match
    const allArtists = await db.collection('videos').distinct('artist');
    
    // Filter out junk entries and match against query
    const junkPatterns = ['#', 'Coming Soon', 'coming soon', 'Memorial', 'Original Song', 
      'Greatest Drummers', 'DadRock Tabs', 'The DadRock', '80\'s Fretmasters'];
    
    const matchedArtists = allArtists
      .filter(a => {
        if (!a) return false;
        // Skip junk entries
        if (junkPatterns.some(p => a.includes(p))) return false;
        // Match against query
        const cleanName = a.replace(/ -$/, '').trim();
        return regex.test(cleanName);
      })
      .map(a => {
        const cleanName = a.replace(/ -$/, '').trim();
        return { name: cleanName, slug: artistToSlug(a) };
      })
      // Deduplicate by slug
      .filter((artist, index, self) => 
        index === self.findIndex(t => t.slug === artist.slug)
      )
      .slice(0, 8);
    
    // Search songs — match title or slug
    const matchedSongs = await db.collection('song_pages')
      .find({
        $or: [
          { title: { $regex: regex } },
          { slug: { $regex: regex } },
          { artist: { $regex: regex } }
        ]
      })
      .limit(8)
      .project({ title: 1, artist: 1, slug: 1, thumbnail: 1, videoId: 1 })
      .toArray();
    
    const songs = matchedSongs.map(s => ({
      title: s.title,
      artist: s.artist?.replace(/ -$/, '').trim() || '',
      slug: s.slug,
      thumbnail: s.thumbnail || `https://img.youtube.com/vi/${s.videoId}/mqdefault.jpg`,
    }));
    
    return NextResponse.json({ 
      artists: matchedArtists, 
      songs,
      total: matchedArtists.length + songs.length
    });
  } catch (error) {
    console.error('Search error:', error);
    return NextResponse.json({ artists: [], songs: [], error: 'Search failed' }, { status: 500 });
  }
}
