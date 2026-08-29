import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

import {
  BTS_REMOVAL_MODES,
  cleanBtsText,
  createBtsJobToken,
  isValidBtsEmail,
  isValidBtsPathname,
} from '@/lib/btsPayment';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

function tokenError(code, error, status) {
  return NextResponse.json({ code, error }, { status });
}

export async function POST(request) {
  try {
    const body = await request.json();
    const tokenCode = cleanBtsText(body?.tokenCode, 40).toUpperCase();
    const customerEmail = cleanBtsText(body?.customerEmail, 254).toLowerCase();
    const removalMode = cleanBtsText(body?.removalMode, 40).toLowerCase();
    const pathname = cleanBtsText(body?.pathname, 500);

    if (!tokenCode) {
      return tokenError('TOKEN_NOT_FOUND', 'Enter your free BTS token code.', 400);
    }

    if (!/^BTS-[A-F0-9]{4}-[A-F0-9]{4}-[A-F0-9]{4}$/.test(tokenCode)) {
      return tokenError(
        'TOKEN_NOT_FOUND',
        'Enter a valid BTS token in the format BTS-XXXX-XXXX-XXXX.',
        400
      );
    }

    if (!isValidBtsEmail(customerEmail)) {
      return NextResponse.json(
        { error: 'Enter the email address being used for this backing track.' },
        { status: 400 }
      );
    }

    if (!BTS_REMOVAL_MODES.includes(removalMode) || !isValidBtsPathname(pathname)) {
      return NextResponse.json(
        { error: 'A valid BTS removal choice and uploaded audio are required.' },
        { status: 400 }
      );
    }

    const db = await getDb();
    const collection = db.collection('bts_tokens');
    const now = new Date();

    const token = await collection.findOne({ code: tokenCode });

    if (!token) {
      return tokenError('TOKEN_NOT_FOUND', 'We could not find a BTS token with this code.', 404);
    }

    if (token.active !== true) {
      return tokenError('TOKEN_INACTIVE', 'This BTS token is inactive and cannot be used.', 403);
    }

    if (Number(token.usesRemaining) <= 0) {
      return tokenError(
        'TOKEN_EXHAUSTED',
        'All available uses for this BTS token have already been redeemed.',
        409
      );
    }

    const assignedEmail = cleanBtsText(token.assignedEmail, 254).toLowerCase();
    if (assignedEmail && assignedEmail !== customerEmail) {
      return tokenError(
        'TOKEN_EMAIL_MISMATCH',
        'This BTS token is assigned to a different email address.',
        403
      );
    }

    if (token.expiresAt && new Date(token.expiresAt).getTime() <= now.getTime()) {
      return tokenError('TOKEN_EXPIRED', 'This BTS token has expired.', 410);
    }

    const redemption = {
      redeemedAt: now,
      customerEmail,
      removalMode,
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
        'This BTS token is no longer available. Its final use may have just been redeemed.',
        409
      );
    }

    const jobToken = createBtsJobToken({
      orderId: token.code,
      customerEmail,
      removalMode,
      pathname,
    });

    return NextResponse.json(
      {
        success: true,
        unlocked: true,
        tokenId: token.code,
        orderId: token.code,
        jobToken,
        usesRemaining: result.usesRemaining,
      },
      { headers: { 'Cache-Control': 'no-store, max-age=0' } }
    );
  } catch (error) {
    console.error('BTS free token redemption error:', error);
    return NextResponse.json({ error: 'Unable to redeem the BTS token.' }, { status: 500 });
  }
}
