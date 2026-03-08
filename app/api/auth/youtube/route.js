import { NextResponse } from 'next/server';

// YouTube OAuth configuration
const YOUTUBE_CLIENT_ID = process.env.YOUTUBE_CLIENT_ID;
const YOUTUBE_CLIENT_SECRET = process.env.YOUTUBE_CLIENT_SECRET;
const REDIRECT_URI = process.env.NEXT_PUBLIC_BASE_URL + '/api/auth/youtube/callback';

// Scopes needed to read scheduled/private videos
// Using only youtube.readonly for unverified apps
const SCOPES = 'https://www.googleapis.com/auth/youtube.readonly';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action');

  // Start OAuth flow - redirect to Google
  if (action === 'connect') {
    const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
    authUrl.searchParams.set('client_id', YOUTUBE_CLIENT_ID);
    authUrl.searchParams.set('redirect_uri', REDIRECT_URI);
    authUrl.searchParams.set('response_type', 'code');
    authUrl.searchParams.set('scope', SCOPES);
    authUrl.searchParams.set('access_type', 'offline');
    authUrl.searchParams.set('prompt', 'consent');
    
    return NextResponse.redirect(authUrl.toString());
  }

  // Check connection status
  if (action === 'status') {
    const { getDb } = await import('@/lib/mongodb');
    const db = await getDb();
    const tokens = await db.collection('settings').findOne({ type: 'youtube_oauth' });
    
    return NextResponse.json({
      connected: !!(tokens?.access_token),
      channel_name: tokens?.channel_name || null,
      expires_at: tokens?.expires_at || null
    });
  }

  return NextResponse.json({ error: 'Invalid action' }, { status: 400 });
}
