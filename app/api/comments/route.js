import { getDb } from '@/lib/mongodb';
import { NextResponse } from 'next/server';
import { v4 as uuidv4 } from 'uuid';

// GET comments for a song
export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const songSlug = searchParams.get('slug');
    if (!songSlug) {
      return NextResponse.json({ error: 'slug parameter required' }, { status: 400 });
    }

    const db = await getDb();
    const comments = await db.collection('comments')
      .find({ songSlug, approved: true })
      .sort({ createdAt: -1 })
      .limit(50)
      .toArray();

    return NextResponse.json({ comments });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to fetch comments' }, { status: 500 });
  }
}

// POST a new comment
export async function POST(request) {
  try {
    const body = await request.json();
    const { songSlug, name, comment, rating } = body;

    if (!songSlug || !name || !comment) {
      return NextResponse.json({ error: 'songSlug, name, and comment are required' }, { status: 400 });
    }

    if (name.length > 50 || comment.length > 500) {
      return NextResponse.json({ error: 'Name max 50 chars, comment max 500 chars' }, { status: 400 });
    }

    const ratingNum = Math.min(5, Math.max(1, parseInt(rating) || 5));

    const db = await getDb();
    const newComment = {
      id: uuidv4(),
      songSlug,
      name: name.trim(),
      comment: comment.trim(),
      rating: ratingNum,
      approved: true,
      createdAt: new Date(),
    };

    await db.collection('comments').insertOne(newComment);

    // Update song average rating
    const allRatings = await db.collection('comments')
      .find({ songSlug, approved: true })
      .project({ rating: 1 })
      .toArray();
    
    const avgRating = allRatings.reduce((sum, r) => sum + r.rating, 0) / allRatings.length;
    await db.collection('song_pages').updateOne(
      { slug: songSlug },
      { $set: { avgRating: Math.round(avgRating * 10) / 10, ratingCount: allRatings.length } }
    );

    return NextResponse.json({ success: true, comment: newComment });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to post comment' }, { status: 500 });
  }
}
