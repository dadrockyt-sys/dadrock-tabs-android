import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function clean(value, maximumLength = 254) {
  return String(value || '').trim().slice(0, maximumLength);
}

export async function POST(request) {
  try {
    const body = await request.json();
    const tokenCode = clean(body.tokenCode, 40).toUpperCase();
    const customerEmail = clean(body.customerEmail).toLowerCase();
    const songTitle = clean(body.songTitle, 120);
    const artistName = clean(body.artistName, 120);
    const transcriptionType = clean(body.transcriptionType, 40).toLowerCase();

    if (!tokenCode) {
      return NextResponse.json(
        { error: 'Enter your free token code.' },
        { status: 400 }
      );
    }

    if (!/^DRT-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}$/.test(tokenCode)) {
      return NextResponse.json(
        { error: 'Enter a valid token in the format DRT-XXXX-XXXX-XXXX.' },
        { status: 400 }
      );
    }

    if (!customerEmail || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customerEmail)) {
      return NextResponse.json(
        { error: 'Enter the email address being used for this PDF.' },
        { status: 400 }
      );
    }

    if (!songTitle || !artistName || !['lead', 'rhythm', 'bass'].includes(transcriptionType)) {
      return NextResponse.json(
        { error: 'Song, artist, and transcription type are required.' },
        { status: 400 }
      );
    }

    const db = await getDb();
    const collection = db.collection('tab_tokens');
    const now = new Date();

    const token = await collection.findOne({
      code: tokenCode,
      active: true,
      usesRemaining: { $gt: 0 },
      $and: [
        {
          $or: [
            { assignedEmail: null },
            { assignedEmail: { $exists: false } },
            { assignedEmail: customerEmail },
          ],
        },
        {
          $or: [
            { expiresAt: null },
            { expiresAt: { $exists: false } },
            { expiresAt: { $gt: now } },
          ],
        },
      ],
    });

    if (!token) {
      return NextResponse.json(
        { error: 'This token is invalid, expired, already used, or assigned to another email.' },
        { status: 404 }
      );
    }

    const redemption = {
      redeemedAt: now,
      customerEmail,
      songTitle,
      artistName,
      transcriptionType,
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
      return NextResponse.json(
        { error: 'This token is no longer available.' },
        { status: 409 }
      );
    }

    return NextResponse.json({
      success: true,
      unlocked: true,
      tokenId: token.code,
      usesRemaining: result.usesRemaining,
    });
  } catch (error) {
    console.error('Free token redemption error:', error);
    return NextResponse.json(
      { error: 'Unable to redeem the free token.' },
      { status: 500 }
    );
  }
}
