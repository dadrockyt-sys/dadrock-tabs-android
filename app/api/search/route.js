import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';

function getVideoId(video) {
  const directId = String(video?.videoId || video?.video_id || '').trim();
  if (/^[a-zA-Z0-9_-]{11}$/.test(directId)) return directId;

  const rawUrl = String(video?.youtube_url || '').trim();
  if (!rawUrl) return '';

  try {
    const url = new URL(rawUrl);
    const host = url.hostname.replace(/^www\./, '');

    if (host === 'youtu.be') {
      const id = url.pathname.split('/').filter(Boolean)[0] || '';
      return /^[a-zA-Z0-9_-]{11}$/.test(id) ? id : '';
    }

    if (host === 'youtube.com' || host === 'm.youtube.com') {
      const watchId = url.searchParams.get('v') || '';
      if (/^[a-zA-Z0-9_-]{11}$/.test(watchId)) return watchId;

      const parts = url.pathname.split('/').filter(Boolean);
      if (['embed', 'shorts', 'live'].includes(parts[0])) {
        const id = parts[1] || '';
        if (/^[a-zA-Z0-9_-]{11}$/.test(id)) return id;
      }
    }
  } catch {
    // Ignore malformed URLs.
  }

  return '';
}

function normalizeText(value) {
  return String(value || '').toLowerCase().trim();
}

function songRelevance(song, query) {
  const q = normalizeText(query);
  const title = normalizeText(song.title);
  const artist = normalizeText(song.artist);

  if (title === q) return 0;
  if (title.startsWith(q)) return 1;
  if (title.includes(q)) return 2;
  if (artist === q) return 3;
  if (artist.startsWith(q)) return 4;
  if (artist.includes(q)) return 5;
  return 6;
}

export async function GET(request) {
  try {
    const { searchParams } = new URL(request.url);
    const query = searchParams.get('q')?.trim();

    if (!query || query.length < 2) {
      return NextResponse.json({ artists: [], songs: [] });
    }

    const db = await getDb();

    // Escape regex special characters for safe matching.
    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(escapedQuery, 'i');

    // Search artists from the complete videos catalog.
    const allArtists = await db.collection('videos').distinct('artist');

    const junkPatterns = ['#', 'Coming Soon', 'coming soon', 'Memorial', 'Original Song',
      'Greatest Drummers', 'DadRock Tabs', 'The DadRock', '80\'s Fretmasters'];

    const matchedArtists = allArtists
      .filter(a => {
        if (!a) return false;
        if (junkPatterns.some(p => a.includes(p))) return false;
        const cleanName = a.replace(/ -$/, '').trim();
        return regex.test(cleanName);
      })
      .map(a => {
        const cleanName = a.replace(/ -$/, '').trim();
        return { name: cleanName, slug: artistToSlug(a) };
      })
      .filter((artist, index, self) =>
        index === self.findIndex(t => t.slug === artist.slug)
      )
      .slice(0, 8);

    // Search the COMPLETE lesson catalog. Artist pages also use the videos
    // collection, so searching only song_pages caused valid lessons to be missed.
    const [videoMatches, directSongPageMatches] = await Promise.all([
      db.collection('videos')
        .find({
          $or: [
            { song: { $regex: regex } },
            { title: { $regex: regex } },
            { artist: { $regex: regex } }
          ]
        })
        .limit(40)
        .project({
          id: 1,
          videoId: 1,
          video_id: 1,
          song: 1,
          title: 1,
          artist: 1,
          thumbnail: 1,
          youtube_url: 1
        })
        .toArray(),
      db.collection('song_pages')
        .find({
          $or: [
            { title: { $regex: regex } },
            { slug: { $regex: regex } },
            { artist: { $regex: regex } }
          ]
        })
        .limit(16)
        .project({ title: 1, artist: 1, slug: 1, thumbnail: 1, videoId: 1 })
        .toArray()
    ]);

    const videoIds = [...new Set(videoMatches.map(getVideoId).filter(Boolean))];
    const songPagesForVideos = videoIds.length
      ? await db.collection('song_pages')
          .find({ videoId: { $in: videoIds } })
          .project({ title: 1, artist: 1, slug: 1, thumbnail: 1, videoId: 1 })
          .toArray()
      : [];

    const songPageByVideoId = new Map(
      songPagesForVideos
        .filter(s => s.videoId)
        .map(s => [String(s.videoId), s])
    );

    const videoSongs = videoMatches.map(video => {
      const videoId = getVideoId(video);
      const songPage = videoId ? songPageByVideoId.get(videoId) : null;
      const cleanArtist = video.artist?.replace(/ -$/, '').trim() || '';
      const title = video.song || video.title || '';

      return {
        title,
        artist: cleanArtist,
        slug: songPage?.slug || null,
        videoId: videoId || null,
        href: songPage?.slug
          ? `/songs/${songPage.slug}`
          : `/artist/${artistToSlug(cleanArtist)}`,
        thumbnail:
          video.thumbnail ||
          songPage?.thumbnail ||
          (videoId ? `https://img.youtube.com/vi/${videoId}/mqdefault.jpg` : '')
      };
    }).filter(song => song.title && song.artist);

    // Preserve any dedicated song pages that happen not to exist in videos,
    // then rank title matches ahead of artist-only matches.
    const mergedSongs = [...videoSongs];

    for (const song of directSongPageMatches) {
      const duplicate = mergedSongs.some(existing =>
        (song.slug && existing.slug === song.slug) ||
        (song.videoId && existing.videoId === String(song.videoId))
      );

      if (duplicate) continue;

      mergedSongs.push({
        title: song.title,
        artist: song.artist?.replace(/ -$/, '').trim() || '',
        slug: song.slug,
        videoId: song.videoId ? String(song.videoId) : null,
        href: `/songs/${song.slug}`,
        thumbnail:
          song.thumbnail ||
          (song.videoId ? `https://img.youtube.com/vi/${song.videoId}/mqdefault.jpg` : '')
      });
    }

    const songs = mergedSongs
      .sort((a, b) => songRelevance(a, query) - songRelevance(b, query))
      .slice(0, 8);

    return NextResponse.json({
      artists: matchedArtists,
      songs,
      total: matchedArtists.length + songs.length
    });
  } catch (error) {
    console.error('Search error:', error);
    return NextResponse.json({ artists: [], songs: [], error: 'Search failed' }, { status: 500 });
  }
}
