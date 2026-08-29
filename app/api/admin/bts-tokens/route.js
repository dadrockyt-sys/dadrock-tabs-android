import { randomBytes } from 'node:crypto';
import { ObjectId } from 'mongodb';
import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;
const TOKEN_TYPES = ['testing', 'giveaway', 'promotion', 'customer', 'support'];

function verifyAdmin(request) {
  if (!ADMIN_PASSWORD) return false;
  const authHeader = request.headers.get('authorization');
  if (!authHeader?.startsWith('Basic ')) return false;

  try {
    const decoded = Buffer.from(authHeader.slice(6), 'base64').toString('utf8');
    return decoded === `admin:${ADMIN_PASSWORD}`;
  } catch {
    return false;
  }
}

function makeToken() {
  const value = randomBytes(6).toString('hex').toUpperCase();
  return `BTS-${value.slice(0, 4)}-${value.slice(4, 8)}-${value.slice(8, 12)}`;
}

function serializeToken(token) {
  return {
    ...token,
    _id: token._id.toString(),
  };
}

export async function GET(request) {
  if (!verifyAdmin(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const db = await getDb();
    const collection = db.collection('bts_tokens');
    const tokens = await collection.find({}).sort({ createdAt: -1 }).limit(250).toArray();
    const now = new Date();

    const stats = {
      total: tokens.length,
      active: tokens.filter((token) => token.active && token.usesRemaining > 0 && (!token.expiresAt || new Date(token.expiresAt) > now)).length,
      used: tokens.filter((token) => token.usesRemaining <= 0).length,
      expired: tokens.filter((token) => token.expiresAt && new Date(token.expiresAt) <= now).length,
      disabled: tokens.filter((token) => !token.active).length,
      redemptions: tokens.reduce((total, token) => total + (Array.isArray(token.redemptions) ? token.redemptions.length : 0), 0),
    };

    return NextResponse.json(
      { success: true, stats, tokens: tokens.map(serializeToken) },
      { headers: { 'Cache-Control': 'no-store, max-age=0' } }
    );
  } catch (error) {
    console.error('BTS token list error:', error);
    return NextResponse.json({ error: 'Unable to load BTS tokens.' }, { status: 500 });
  }
}

export async function POST(request) {
  if (!verifyAdmin(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const action = String(body.action || 'generate');
    const db = await getDb();
    const collection = db.collection('bts_tokens');

    if (action === 'generate') {
      const type = TOKEN_TYPES.includes(body.type) ? body.type : 'testing';
      const quantity = Math.min(100, Math.max(1, Number(body.quantity) || 1));
      const uses = Math.min(100, Math.max(1, Number(body.uses) || 1));
      const assignedEmail = String(body.assignedEmail || '').trim().toLowerCase() || null;
      const notes = String(body.notes || '').trim().slice(0, 500);
      const expiresAt = body.expiresAt ? new Date(body.expiresAt) : null;

      if (expiresAt && Number.isNaN(expiresAt.getTime())) {
        return NextResponse.json({ error: 'Invalid expiration date.' }, { status: 400 });
      }

      const createdAt = new Date();
      const documents = Array.from({ length: quantity }, () => ({
        code: makeToken(),
        product: 'backing-track-studio',
        type,
        active: true,
        usesAllowed: uses,
        usesRemaining: uses,
        assignedEmail,
        notes,
        expiresAt,
        createdAt,
        updatedAt: createdAt,
        redemptions: [],
      }));

      await collection.insertMany(documents);
      return NextResponse.json({
        success: true,
        tokens: documents.map((token) => ({ ...token, _id: undefined })),
      });
    }

    const id = String(body.id || '');
    if (!ObjectId.isValid(id)) {
      return NextResponse.json({ error: 'Invalid token ID.' }, { status: 400 });
    }

    if (action === 'toggle') {
      const active = Boolean(body.active);
      await collection.updateOne(
        { _id: new ObjectId(id) },
        { $set: { active, updatedAt: new Date() } }
      );
      return NextResponse.json({ success: true });
    }

    if (action === 'delete') {
      await collection.deleteOne({ _id: new ObjectId(id) });
      return NextResponse.json({ success: true });
    }

    return NextResponse.json({ error: 'Unsupported action.' }, { status: 400 });
  } catch (error) {
    console.error('BTS token admin error:', error);
    return NextResponse.json({ error: 'Unable to update BTS tokens.' }, { status: 500 });
  }
}
