import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function clean(value, maximumLength = 254) {
  return String(value || '').trim().slice(0, maximumLength);
}

function tokenError(code, error, status) {
  return NextResponse.json(
    { code, error },
    { status }
  );
}

export async function POST(request) {
  try {
    const body = await request.json();
    const tokenCode = clean(body.tokenCode, 40).toUpperCase();
    const customerEmail = clean(body.customerEmail).toLowerCase();
    const songTitle = clean(body.songTitle || body.song, 120);
    const artistName = clean(body.artistName || body.artist, 120);
    const transcriptionType = clean(
      body.transcriptionType,
      40
    ).toLowerCase();

    if (!tokenCode) {
      return tokenError(
        'TOKEN_NOT_FOUND',
        'Enter your free token code.',
        400
      );
    }

    if (!/^DRT-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}$/.test(tokenCode)) {
      return tokenError(
        'TOKEN_NOT_FOUND',
        'Enter a valid token in the format DRT-XXXX-XXXX-XXXX.',
        400
      );
    }

    if (
      !customerEmail ||
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customerEmail)
    ) {
      return NextResponse.json(
        {
          error:
            'Enter the email address being used for this PDF.',
        },
        { status: 400 }
      );
    }

    if (
      !songTitle ||
      !artistName ||
      !['lead', 'rhythm', 'bass'].includes(transcriptionType)
    ) {
      return NextResponse.json(
        {
          error:
            'Song, artist, and transcription type are required.',
        },
        { status: 400 }
      );
    }

    const db = await getDb();
    const collection = db.collection('tab_tokens');
    const now = new Date();

    const token = await collection.findOne({
      code: tokenCode,
    });

    if (!token) {
      return tokenError(
        'TOKEN_NOT_FOUND',
        'We could not find a token with this code.',
        404
      );
    }

    if (token.active !== true) {
      return tokenError(
        'TOKEN_INACTIVE',
        'This token is inactive and cannot be used.',
        403
      );
    }

    if (Number(token.usesRemaining) <= 0) {
      return tokenError(
        'TOKEN_EXHAUSTED',
        'All available uses for this token have already been redeemed.',
        409
      );
    }

    const assignedEmail = clean(token.assignedEmail).toLowerCase();
    if (assignedEmail && assignedEmail !== customerEmail) {
      return tokenError(
        'TOKEN_EMAIL_MISMATCH',
        'This token is assigned to a different email address.',
        403
      );
    }

    if (
      token.expiresAt &&
      new Date(token.expiresAt).getTime() <= now.getTime()
    ) {
      return tokenError(
        'TOKEN_EXPIRED',
        'This token has expired.',
        410
      );
    }

    const redemption = {
      redeemedAt: now,
      customerEmail,
      songTitle,
      artistName,
      transcriptionType,
      youtubeUrl: body.youtubeUrl
        ? String(body.youtubeUrl)
        : null,
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
      return tokenError(
        'TOKEN_EXHAUSTED',
        'This token is no longer available. Its final use may have just been redeemed.',
        409
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
