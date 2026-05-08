import { getDb } from '@/lib/mongodb';

export async function GET() {
  const db = await getDb();
  const songs = await db.collection('song_pages')
    .find({})
    .sort({ created_at: -1 })
    .limit(50)
    .project({ title: 1, artist: 1, slug: 1, created_at: 1, difficulty: 1 })
    .toArray();

  const baseUrl = process.env.NEXT_PUBLIC_BASE_URL || 'https://dadrocktabs.com';
  const now = new Date().toUTCString();

  const items = songs.map(song => {
    const pubDate = song.created_at ? new Date(song.created_at).toUTCString() : now;
    return `
    <item>
      <title>${escapeXml(song.title)} - ${escapeXml(song.artist)}</title>
      <link>${baseUrl}/songs/${song.slug}</link>
      <guid isPermaLink="true">${baseUrl}/songs/${song.slug}</guid>
      <description>Learn to play ${escapeXml(song.title)} by ${escapeXml(song.artist)} with guitar tabs and video tutorial on DadRock Tabs.</description>
      <pubDate>${pubDate}</pubDate>
      <category>${song.difficulty || 'Intermediate'}</category>
    </item>`;
  }).join('');

  const rss = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>DadRock Tabs - Classic Rock &amp; Metal Guitar Tutorials</title>
    <link>${baseUrl}</link>
    <description>Your go-to database for classic rock and heavy metal guitar and bass tutorials. New tabs added regularly.</description>
    <language>en-us</language>
    <lastBuildDate>${now}</lastBuildDate>
    <atom:link href="${baseUrl}/api/rss" rel="self" type="application/rss+xml"/>
    <image>
      <url>${baseUrl}/logo.png</url>
      <title>DadRock Tabs</title>
      <link>${baseUrl}</link>
    </image>${items}
  </channel>
</rss>`;

  return new Response(rss, {
    headers: {
      'Content-Type': 'application/rss+xml; charset=utf-8',
      'Cache-Control': 'public, max-age=3600',
    },
  });
}

function escapeXml(str) {
  if (!str) return '';
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&apos;');
}
