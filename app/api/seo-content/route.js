import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

// GET: Fetch AI-generated SEO content for an artist or song
// Public endpoint — no auth needed, just reads cached content
export async function GET(request) {
  const url = new URL(request.url);
  const type = url.searchParams.get('type'); // 'artist' or 'song'
  const name = url.searchParams.get('name'); // artist name
  const slug = url.searchParams.get('slug'); // song slug

  if (!type || (type === 'artist' && !name) || (type === 'song' && !slug)) {
    return NextResponse.json({ error: 'Missing parameters. Need type=artist&name=... or type=song&slug=...' }, { status: 400 });
  }

  try {
    const db = await getDb();

    if (type === 'artist') {
      // Try exact match first, then case-insensitive
      let content = await db.collection('artist_seo_content').findOne({ artist: name });
      if (!content) {
        const escaped = name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
        content = await db.collection('artist_seo_content').findOne({
          artist: { $regex: new RegExp(`^${escaped}$`, 'i') }
        });
      }

      if (!content) {
        return NextResponse.json({ found: false, type: 'artist', name });
      }

      return NextResponse.json({
        found: true,
        type: 'artist',
        name: content.artist,
        content: content.content,
        generated_at: content.generated_at,
      });
    }

    if (type === 'song') {
      const content = await db.collection('song_seo_content').findOne({ slug });

      if (!content) {
        return NextResponse.json({ found: false, type: 'song', slug });
      }

      return NextResponse.json({
        found: true,
        type: 'song',
        title: content.title,
        artist: content.artist,
        content: content.content,
        generated_at: content.generated_at,
      });
    }

    return NextResponse.json({ error: 'Invalid type. Use "artist" or "song".' }, { status: 400 });

  } catch (e) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
