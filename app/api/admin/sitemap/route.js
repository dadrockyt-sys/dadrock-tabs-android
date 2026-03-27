import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';
import { locales } from '@/lib/i18n';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'Babyty99';
const SITE_URL = 'https://dadrocktabs.com';

function verifyAdmin(request) {
  const authHeader = request.headers.get('Authorization');
  if (!authHeader || !authHeader.startsWith('Basic ')) return false;
  const decoded = atob(authHeader.split(' ')[1]);
  const [, password] = decoded.split(':');
  return password === ADMIN_PASSWORD;
}

function artistToSlug(artistName) {
  const specialCases = {
    'AC/DC': 'acdc',
    "Guns N' Roses": 'guns-n-roses',
    'Motörhead': 'motorhead',
    'Blue Öyster Cult': 'blue-oyster-cult',
    'Mötley Crüe': 'motley-crue',
  };
  if (specialCases[artistName]) return specialCases[artistName];
  return artistName.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-').trim();
}

// GET /api/admin/sitemap/scan - Scan all pages and compare with sitemap
export async function GET(request) {
  if (!verifyAdmin(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const db = await getDb();

    // Gather all known pages
    const pages = {
      homepage: [],
      coming_soon: [],
      top_lessons: [],
      quickies: [],
      artists: [],
      songs: [],
    };

    // Homepage language variants
    for (const lang of locales) {
      pages.homepage.push({
        url: lang === 'en' ? SITE_URL : `${SITE_URL}/${lang}`,
        type: 'homepage',
        lang,
      });
    }

    // Static pages
    pages.coming_soon.push({ url: `${SITE_URL}/coming-soon`, type: 'coming-soon' });
    pages.top_lessons.push({ url: `${SITE_URL}/top-lessons`, type: 'top-lessons' });
    pages.quickies.push({ url: `${SITE_URL}/quickies`, type: 'quickies' });

    // Artist pages from videos collection
    const artists = await db.collection('videos').distinct('artist');
    for (const artist of artists) {
      if (artist) {
        const slug = artistToSlug(artist);
        pages.artists.push({
          url: `${SITE_URL}/artist/${slug}`,
          type: 'artist',
          name: artist,
          slug,
        });
      }
    }

    // Song pages from song_pages collection
    const songPages = await db.collection('song_pages').find({}, { projection: { slug: 1, title: 1, artist: 1 } }).toArray();
    for (const song of songPages) {
      if (song.slug) {
        pages.songs.push({
          url: `${SITE_URL}/songs/${song.slug}`,
          type: 'song',
          title: song.title,
          artist: song.artist,
          slug: song.slug,
        });
      }
    }

    // Check the current sitemap for any missing pages
    let sitemapUrls = new Set();
    try {
      const sitemapRes = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/sitemap.xml`, { cache: 'no-store' });
      const sitemapText = await sitemapRes.text();
      const locRegex = /<loc>(.*?)<\/loc>/g;
      let match;
      while ((match = locRegex.exec(sitemapText)) !== null) {
        sitemapUrls.add(match[1]);
      }
    } catch (err) {
      console.error('Could not fetch current sitemap:', err);
    }

    // Find pages NOT in the sitemap
    const allPageUrls = [
      ...pages.homepage.map(p => p.url),
      ...pages.coming_soon.map(p => p.url),
      ...pages.top_lessons.map(p => p.url),
      ...pages.quickies.map(p => p.url),
      ...pages.artists.map(p => p.url),
      ...pages.songs.map(p => p.url),
    ];

    const missingFromSitemap = allPageUrls.filter(url => !sitemapUrls.has(url));
    const extraInSitemap = [...sitemapUrls].filter(url => !allPageUrls.includes(url) && url.startsWith(SITE_URL));

    const summary = {
      total_pages: allPageUrls.length,
      in_sitemap: sitemapUrls.size,
      homepage_variants: pages.homepage.length,
      artist_pages: pages.artists.length,
      song_pages: pages.songs.length,
      static_pages: 3, // coming-soon, top-lessons, quickies
      missing_from_sitemap: missingFromSitemap.length,
      extra_in_sitemap: extraInSitemap.length,
    };

    return NextResponse.json({
      success: true,
      summary,
      missing_from_sitemap: missingFromSitemap,
      extra_in_sitemap: extraInSitemap,
      pages_by_type: {
        homepage: pages.homepage.length,
        coming_soon: pages.coming_soon.length,
        top_lessons: pages.top_lessons.length,
        quickies: pages.quickies.length,
        artists: pages.artists.length,
        songs: pages.songs.length,
      },
    });
  } catch (error) {
    console.error('Sitemap scan error:', error);
    return NextResponse.json({ error: `Scan failed: ${error.message}` }, { status: 500 });
  }
}

// POST /api/admin/sitemap/ping - Ping Google to re-crawl sitemap
export async function POST(request) {
  if (!verifyAdmin(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const sitemapUrl = `${SITE_URL}/sitemap.xml`;
    
    // Ping Google
    const googlePingUrl = `https://www.google.com/ping?sitemap=${encodeURIComponent(sitemapUrl)}`;
    const googleRes = await fetch(googlePingUrl);
    
    // Ping Bing 
    const bingPingUrl = `https://www.bing.com/ping?sitemap=${encodeURIComponent(sitemapUrl)}`;
    let bingSuccess = false;
    try {
      const bingRes = await fetch(bingPingUrl);
      bingSuccess = bingRes.ok;
    } catch (e) {
      console.error('Bing ping failed:', e);
    }

    // Also fetch current sitemap stats
    let totalUrls = 0;
    try {
      const sitemapRes = await fetch(`${process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000'}/sitemap.xml`, { cache: 'no-store' });
      const sitemapText = await sitemapRes.text();
      totalUrls = (sitemapText.match(/<loc>/g) || []).length;
    } catch (e) {
      console.error('Could not count sitemap URLs:', e);
    }

    return NextResponse.json({
      success: true,
      message: `Sitemap ping sent successfully! Google: ${googleRes.ok ? '✓' : '✗'}, Bing: ${bingSuccess ? '✓' : '✗'}`,
      google_pinged: googleRes.ok,
      bing_pinged: bingSuccess,
      sitemap_url: sitemapUrl,
      total_urls_in_sitemap: totalUrls,
    });
  } catch (error) {
    console.error('Sitemap ping error:', error);
    return NextResponse.json({ error: `Ping failed: ${error.message}` }, { status: 500 });
  }
}
