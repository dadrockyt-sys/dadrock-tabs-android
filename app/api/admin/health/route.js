import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'Babyty99';
const YOUTUBE_API_KEY = process.env.YOUTUBE_API_KEY || '';
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL || 'https://dadrocktabs.com';

function verifyAdmin(request) {
  const authHeader = request.headers.get('authorization');
  if (!authHeader || !authHeader.startsWith('Basic ')) return false;
  const decoded = atob(authHeader.split(' ')[1]);
  return decoded === `admin:${ADMIN_PASSWORD}`;
}

// Extract YouTube video ID from URL
function extractVideoId(url) {
  if (!url) return null;
  let videoId = null;
  if (url.includes('youtube.com/watch?v=')) {
    videoId = url.split('v=')[1]?.split('&')[0];
  } else if (url.includes('youtu.be/')) {
    videoId = url.split('youtu.be/')[1]?.split('?')[0];
  } else if (url.includes('youtube.com/embed/')) {
    videoId = url.split('embed/')[1]?.split('?')[0];
  } else if (url.includes('youtube.com/shorts/')) {
    videoId = url.split('shorts/')[1]?.split('?')[0];
  }
  return videoId;
}

// Helper: check a single URL via HEAD then GET
async function checkUrl(url, timeoutMs = 8000) {
  try {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    // Try HEAD first (faster)
    let res = await fetch(url, { method: 'HEAD', signal: controller.signal, redirect: 'follow' });
    clearTimeout(timer);
    return { url, status: res.status, ok: res.ok };
  } catch (e) {
    // If HEAD fails, try GET as fallback
    try {
      const controller2 = new AbortController();
      const timer2 = setTimeout(() => controller2.abort(), timeoutMs);
      let res = await fetch(url, { method: 'GET', signal: controller2.signal, redirect: 'follow' });
      clearTimeout(timer2);
      return { url, status: res.status, ok: res.ok };
    } catch (e2) {
      return { url, status: 0, ok: false, error: e2.message || 'Connection failed' };
    }
  }
}

// Batch check URLs with concurrency limit
async function batchCheckUrls(urls, concurrency = 5) {
  const results = [];
  for (let i = 0; i < urls.length; i += concurrency) {
    const batch = urls.slice(i, i + concurrency);
    const batchResults = await Promise.all(batch.map(u => checkUrl(u)));
    results.push(...batchResults);
  }
  return results;
}

export async function GET(request) {
  if (!verifyAdmin(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const url = new URL(request.url);
  const mode = url.searchParams.get('mode') || 'full'; // 'full', 'quick', 'videos_only', 'urls_only'

  const report = {
    success: true,
    timestamp: new Date().toISOString(),
    overall_status: 'healthy',
    checks: {},
  };

  const issues = [];

  try {
    const db = await getDb();

    // ─── 1. Database Health ───
    try {
      const videoCount = await db.collection('videos').countDocuments();
      const songPageCount = await db.collection('song_pages').countDocuments();
      const settingsCount = await db.collection('settings').countDocuments();
      const upcomingCount = await db.collection('upcoming_videos').countDocuments();

      // Get unique artists
      const artists = await db.collection('videos').distinct('artist');

      report.checks.database = {
        status: 'ok',
        details: {
          connected: true,
          videos: videoCount,
          song_pages: songPageCount,
          artists: artists.length,
          upcoming_videos: upcomingCount,
          settings_entries: settingsCount,
        },
      };
    } catch (e) {
      report.checks.database = { status: 'error', details: { connected: false, error: e.message } };
      issues.push('Database connection failed');
    }

    // ─── 2. API Endpoints Health ───
    if (mode === 'full' || mode === 'quick') {
      const apiEndpoints = [
        `${BASE_URL}/api/health`,
        `${BASE_URL}/api/settings`,
        `${BASE_URL}/api/videos`,
      ];
      const apiResults = await batchCheckUrls(apiEndpoints);
      const failedApis = apiResults.filter(r => !r.ok);
      report.checks.api_endpoints = {
        status: failedApis.length === 0 ? 'ok' : 'error',
        details: {
          total_checked: apiResults.length,
          passed: apiResults.filter(r => r.ok).length,
          failed: failedApis.length,
          results: apiResults.map(r => ({ url: r.url.replace(BASE_URL, ''), status: r.status, ok: r.ok, ...(r.error ? { error: r.error } : {}) })),
        },
      };
      if (failedApis.length > 0) issues.push(`${failedApis.length} API endpoints failing`);
    }

    // ─── 3. Sitemap & Robots Check ───
    if (mode === 'full' || mode === 'quick') {
      // Sitemap
      try {
        const sitemapRes = await checkUrl(`${BASE_URL}/sitemap.xml`);
        let pageCount = 0;
        if (sitemapRes.ok) {
          const sitemapFetch = await fetch(`${BASE_URL}/sitemap.xml`);
          const sitemapText = await sitemapFetch.text();
          pageCount = (sitemapText.match(/<url>/g) || []).length;
        }
        report.checks.sitemap = {
          status: sitemapRes.ok ? 'ok' : 'error',
          details: { accessible: sitemapRes.ok, status_code: sitemapRes.status, page_count: pageCount },
        };
        if (!sitemapRes.ok) issues.push('Sitemap not accessible');
      } catch (e) {
        report.checks.sitemap = { status: 'error', details: { accessible: false, error: e.message } };
        issues.push('Sitemap check failed');
      }

      // Robots.txt
      try {
        const robotsRes = await checkUrl(`${BASE_URL}/robots.txt`);
        report.checks.robots = {
          status: robotsRes.ok ? 'ok' : 'warning',
          details: { accessible: robotsRes.ok, status_code: robotsRes.status },
        };
      } catch (e) {
        report.checks.robots = { status: 'warning', details: { accessible: false, error: e.message } };
      }
    }

    // ─── 4. Internal Page Routes Check ───
    if (mode === 'full' || mode === 'urls_only') {
      const internalUrls = [];

      // Static pages
      const staticPages = ['/', '/coming-soon', '/top-lessons', '/quickies'];
      staticPages.forEach(p => internalUrls.push(`${BASE_URL}${p}`));

      // Artist pages (from DB)
      try {
        const artists = await db.collection('videos').distinct('artist');
        for (const artist of artists) {
          if (artist) {
            const slug = artist.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
            if (slug) internalUrls.push(`${BASE_URL}/artist/${slug}`);
          }
        }
      } catch (e) { /* skip */ }

      // Song pages (from DB)
      try {
        const songPages = await db.collection('song_pages').find({}, { projection: { slug: 1 } }).toArray();
        for (const sp of songPages) {
          if (sp.slug) internalUrls.push(`${BASE_URL}/songs/${sp.slug}`);
        }
      } catch (e) { /* skip */ }

      // Check a sample of localized URLs (one per locale for a static page)
      const locales = ['es', 'pt', 'de', 'fr', 'it', 'ja', 'ko', 'zh', 'ru', 'hi', 'sv', 'fi', 'pt-br'];
      locales.forEach(lang => internalUrls.push(`${BASE_URL}/${lang}/coming-soon`));

      const urlResults = await batchCheckUrls(internalUrls, 8);
      const deadUrls = urlResults.filter(r => !r.ok);

      report.checks.internal_urls = {
        status: deadUrls.length === 0 ? 'ok' : 'warning',
        details: {
          total_checked: urlResults.length,
          alive: urlResults.filter(r => r.ok).length,
          dead: deadUrls.length,
          dead_urls: deadUrls.map(r => ({ url: r.url.replace(BASE_URL, ''), status: r.status, ...(r.error ? { error: r.error } : {}) })),
        },
      };
      if (deadUrls.length > 0) issues.push(`${deadUrls.length} internal URLs returning non-200`);
    }

    // ─── 5. Dead YouTube Video Check ───
    if (mode === 'full' || mode === 'videos_only') {
      try {
        const allVideos = await db.collection('videos').find({}).toArray();

        if (allVideos.length === 0) {
          report.checks.dead_videos = {
            status: 'ok',
            details: { total_checked: 0, alive: 0, dead: 0, dead_videos: [], message: 'No videos in database' },
          };
        } else {
          // Build map of YouTube IDs to videos
          const videoMap = {};
          for (const video of allVideos) {
            const ytId = extractVideoId(video.youtube_url);
            if (ytId) {
              if (!videoMap[ytId]) videoMap[ytId] = [];
              videoMap[ytId].push(video);
            }
          }

          const allYtIds = Object.keys(videoMap);
          const aliveIds = new Set();
          let apiUsed = false;
          let apiError = null;

          // Method 1: YouTube Data API (if available)
          if (YOUTUBE_API_KEY) {
            try {
              for (let i = 0; i < allYtIds.length; i += 50) {
                const batch = allYtIds.slice(i, i + 50);
                const idsParam = batch.join(',');
                const apiUrl = `https://www.googleapis.com/youtube/v3/videos?part=id,status&id=${idsParam}&key=${YOUTUBE_API_KEY}`;
                const res = await fetch(apiUrl);
                const data = await res.json();

                if (data.error) {
                  apiError = data.error.message;
                  break;
                }

                for (const item of (data.items || [])) {
                  if (item.status && (item.status.privacyStatus === 'public' || item.status.privacyStatus === 'unlisted')) {
                    aliveIds.add(item.id);
                  }
                }
              }
              if (!apiError) apiUsed = true;
            } catch (e) {
              apiError = e.message;
            }
          }

          // Method 2: HTTP fallback (if API failed or not configured)
          if (!apiUsed) {
            // Check YouTube oEmbed endpoint as fallback (no API key needed)
            for (let i = 0; i < allYtIds.length; i += 10) {
              const batch = allYtIds.slice(i, i + 10);
              const checks = await Promise.all(batch.map(async (ytId) => {
                try {
                  const oembedUrl = `https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v=${ytId}&format=json`;
                  const r = await fetch(oembedUrl, { method: 'GET' });
                  return { ytId, alive: r.ok };
                } catch {
                  return { ytId, alive: false };
                }
              }));
              for (const c of checks) {
                if (c.alive) aliveIds.add(c.ytId);
              }
            }
          }

          const deadYtIds = allYtIds.filter(id => !aliveIds.has(id));
          const deadVideosList = [];
          for (const deadId of deadYtIds) {
            const dbVideos = videoMap[deadId];
            for (const v of dbVideos) {
              deadVideosList.push({
                id: v.id,
                song: v.song,
                artist: v.artist,
                youtube_url: v.youtube_url,
              });
            }
          }

          report.checks.dead_videos = {
            status: deadYtIds.length === 0 ? 'ok' : 'warning',
            details: {
              total_checked: allYtIds.length,
              alive: aliveIds.size,
              dead: deadYtIds.length,
              dead_videos: deadVideosList,
              method: apiUsed ? 'YouTube Data API' : 'HTTP oEmbed fallback',
              ...(apiError ? { api_error: apiError } : {}),
            },
          };
          if (deadYtIds.length > 0) issues.push(`${deadYtIds.length} dead YouTube videos found`);
        }
      } catch (e) {
        report.checks.dead_videos = { status: 'error', details: { error: e.message } };
        issues.push('Dead video check failed');
      }
    }

    // ─── Overall Status ───
    const statuses = Object.values(report.checks).map(c => c.status);
    if (statuses.includes('error')) {
      report.overall_status = 'critical';
    } else if (statuses.includes('warning')) {
      report.overall_status = 'warning';
    } else {
      report.overall_status = 'healthy';
    }
    report.issues = issues;
    report.total_checks = Object.keys(report.checks).length;

    return NextResponse.json(report);

  } catch (e) {
    return NextResponse.json({ success: false, error: e.message }, { status: 500 });
  }
}

// POST: Remove dead videos found by the scan
export async function POST(request) {
  if (!verifyAdmin(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const body = await request.json();
    const { action } = body;

    if (action === 'remove_dead_videos') {
      const { video_ids } = body;
      if (!video_ids || !Array.isArray(video_ids) || video_ids.length === 0) {
        return NextResponse.json({ error: 'No video IDs provided' }, { status: 400 });
      }

      const db = await getDb();
      let removedCount = 0;

      for (const vid of video_ids) {
        const result = await db.collection('videos').deleteOne({ id: vid });
        if (result.deletedCount > 0) removedCount++;
      }

      // Also clean up from song_pages
      // Get the youtube URLs of removed videos to find their IDs
      for (const vid of video_ids) {
        // Remove song pages that reference deleted videos
        await db.collection('song_pages').deleteMany({ videoId: vid });
      }

      return NextResponse.json({
        success: true,
        message: `Removed ${removedCount} dead videos from database.`,
        removed_count: removedCount,
      });
    }

    return NextResponse.json({ error: 'Unknown action' }, { status: 400 });

  } catch (e) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
