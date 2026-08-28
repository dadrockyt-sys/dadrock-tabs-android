import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD;

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

export async function GET(request) {
  if (!verifyAdmin(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  return NextResponse.json(
    { success: true },
    {
      status: 200,
      headers: {
        'Cache-Control': 'no-store, max-age=0',
      },
    }
  );
}
