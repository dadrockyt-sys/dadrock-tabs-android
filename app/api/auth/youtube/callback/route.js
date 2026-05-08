import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

// YouTube OAuth configuration
const YOUTUBE_CLIENT_ID = process.env.YOUTUBE_CLIENT_ID;
const YOUTUBE_CLIENT_SECRET = process.env.YOUTUBE_CLIENT_SECRET;
const REDIRECT_URI = process.env.NEXT_PUBLIC_BASE_URL + '/api/auth/youtube/callback';

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const code = searchParams.get('code');
  const error = searchParams.get('error');

  // Handle errors from Google
  if (error) {
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || '';
    return NextResponse.redirect(`${baseUrl}/?youtube_error=${encodeURIComponent(error)}`);
  }

  if (!code) {
    return NextResponse.json({ error: 'No authorization code provided' }, { status: 400 });
  }

  try {
    // Exchange authorization code for tokens
    const tokenResponse = await fetch('https://oauth2.googleapis.com/token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        client_id: YOUTUBE_CLIENT_ID,
        client_secret: YOUTUBE_CLIENT_SECRET,
        code: code,
        grant_type: 'authorization_code',
        redirect_uri: REDIRECT_URI,
      }),
    });

    const tokens = await tokenResponse.json();

    if (tokens.error) {
      console.error('Token exchange error:', tokens);
      const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || '';
      return NextResponse.redirect(`${baseUrl}/?youtube_error=${encodeURIComponent(tokens.error_description || tokens.error)}`);
    }

    // Get channel info to verify connection
    const channelResponse = await fetch(
      'https://www.googleapis.com/youtube/v3/channels?part=snippet&mine=true',
      {
        headers: { 'Authorization': `Bearer ${tokens.access_token}` }
      }
    );
    const channelData = await channelResponse.json();
    const channelName = channelData.items?.[0]?.snippet?.title || 'Unknown Channel';

    // Store tokens in database
    const db = await getDb();
    await db.collection('settings').updateOne(
      { type: 'youtube_oauth' },
      {
        $set: {
          type: 'youtube_oauth',
          access_token: tokens.access_token,
          refresh_token: tokens.refresh_token,
          expires_at: Date.now() + (tokens.expires_in * 1000),
          channel_name: channelName,
          updated_at: new Date().toISOString()
        }
      },
      { upsert: true }
    );

    // Redirect back to admin with success
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || '';
    return NextResponse.redirect(`${baseUrl}/?youtube_connected=true&channel=${encodeURIComponent(channelName)}`);

  } catch (err) {
    console.error('OAuth callback error:', err);
    const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || '';
    return NextResponse.redirect(`${baseUrl}/?youtube_error=${encodeURIComponent('Connection failed. Please try again.')}`);
  }
}
