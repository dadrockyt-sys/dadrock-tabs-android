import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

export async function POST(request) {
  try {
    const body = await request.json();
    const customerEmail = String(body.customerEmail || '').trim().toLowerCase();

    if (!customerEmail || !customerEmail.includes('@')) {
      return NextResponse.json({ error: 'Enter the email address assigned to the token.' }, { status: 400 });
    }

    const db = await getDb();
    const collection = db.collection('tab_tokens');
    const now = new Date();

    const token = await collection.findOne({
      assignedEmail: customerEmail,
      active: true,
      usesRemaining: { $gt: 0 },
      $or: [
        { expiresAt: null },
        { expiresAt: { $exists: false } },
        { expiresAt: { $gt: now } },
      ],
    }, { sort: { createdAt: 1 } });

    if (!token) {
      return NextResponse.json(
        { error: 'No active free token was found for this email address.' },
        { status: 404 }
      );
    }

    const redemption = {
      redeemedAt: now,
      customerEmail,
      songTitle: String(body.songTitle || '').trim(),
      artistName: String(body.artistName || '').trim(),
      transcriptionType: String(body.transcriptionType || '').trim(),
      youtubeUrl: body.youtubeUrl ? String(body.youtubeUrl) : null,
    };

    const result = await collection.findOneAndUpdate(
      {
        _id: token._id,
        active: true,
        usesRemaining: { $gt: 0 },
      },
      {
        $inc: { usesRemaining: -1 },
        $push: { redemptions: redemption },
        $set: { updatedAt: now },
      },
      { returnDocument: 'after' }
    );

    if (!result) {
      return NextResponse.json({ error: 'This token is no longer available.' }, { status: 409 });
    }

    return NextResponse.json({
      success: true,
      unlocked: true,
      tokenId: token.code,
      usesRemaining: result.usesRemaining,
    });
  } catch (error) {
    console.error('Free token redemption error:', error);
    return NextResponse.json({ error: 'Unable to redeem the free token.' }, { status: 500 });
  }
}
