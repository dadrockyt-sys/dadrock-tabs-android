import { NextResponse } from 'next/server';
import { getDb } from '@/lib/mongodb';
import { artistToSlug } from '@/lib/slugify';
import OpenAI from 'openai';

const ADMIN_PASSWORD = process.env.ADMIN_PASSWORD || 'Babyty99';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';

function verifyAdmin(request) {
  const authHeader = request.headers.get('authorization');
  if (!authHeader || !authHeader.startsWith('Basic ')) return false;
  const decoded = atob(authHeader.split(' ')[1]);
  return decoded === `admin:${ADMIN_PASSWORD}`;
}

// Initialize OpenAI client
function getOpenAI() {
  if (!OPENAI_API_KEY) throw new Error('OPENAI_API_KEY not configured');
  return new OpenAI({ apiKey: OPENAI_API_KEY });
}

// Generate SEO content for an artist page
async function generateArtistContent(artistName, songCount, songTitles) {
  const openai = getOpenAI();
  const sampleSongs = songTitles.slice(0, 10).join(', ');

  const prompt = `You are a music journalist and guitar education expert writing for DadRock Tabs, a website that teaches people to play classic rock songs on guitar and bass.

Write rich, educational SEO content for the artist page of "${artistName}". They have ${songCount} lessons available on the site. Sample songs: ${sampleSongs}.

Write the following sections in JSON format:
{
  "bio": "A 2-3 paragraph biography focusing on the band/artist's musical legacy, formation story, and impact on rock music. Include key facts, years active, and notable achievements.",
  "playing_style": "A paragraph about their distinctive guitar/bass playing style, common techniques they use (power chords, palm muting, sweep picking, etc.), and what makes their sound unique.",
  "gear_info": "A brief paragraph about the iconic guitars, amps, and effects pedals associated with this artist/band.",
  "why_learn": "A motivational paragraph about why guitarists should learn their songs — what skills they'll develop, difficulty level, and how these songs build foundational rock skills.",
  "fun_facts": ["3-4 interesting fun facts about the artist as a JSON array of strings"],
  "meta_description": "A compelling 150-160 character meta description for SEO that includes the artist name and keywords about guitar tabs/lessons."
}

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no code blocks. Write naturally and enthusiastically — this is for guitar enthusiasts who love classic rock.`;

  const response = await openai.responses.create({
    model: 'gpt-5-nano',
    input: prompt,
  });

  const text = response.output_text || '';

  // Parse JSON from response (handle potential markdown wrapping)
  let content;
  try {
    // Try direct parse
    content = JSON.parse(text);
  } catch {
    // Try extracting JSON from markdown code block
    const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/) || text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      content = JSON.parse(jsonMatch[1] || jsonMatch[0]);
    } else {
      throw new Error('Failed to parse AI response as JSON');
    }
  }

  return content;
}

// Generate SEO content for a song page
async function generateSongContent(songTitle, artistName, videoType) {
  const openai = getOpenAI();

  const prompt = `You are a guitar teacher and music journalist writing for DadRock Tabs, a website that teaches people to play classic rock songs.

Write rich, educational SEO content for a lesson page teaching "${songTitle}" by ${artistName}. The lesson is a ${videoType || 'guitar'} tutorial.

Write the following sections in JSON format:
{
  "song_story": "A 1-2 paragraph backstory of this song — when it was released, what album it's from, any interesting recording or writing history, and its cultural impact.",
  "lesson_overview": "A paragraph describing what students will learn in this lesson — specific riffs, chord progressions, techniques, and any tricky parts to watch out for.",
  "difficulty_info": "A sentence about the difficulty level (beginner/intermediate/advanced) and what prior skills are helpful.",
  "techniques": ["An array of 3-5 specific guitar/bass techniques used in this song, e.g. 'Palm Muting', 'Hammer-ons', 'Power Chords'"],
  "pro_tips": ["An array of 2-3 practice tips specific to this song"],
  "meta_description": "A compelling 150-160 character meta description for SEO that includes the song title, artist name, and 'guitar tab/lesson' keywords."
}

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no code blocks. Write naturally and enthusiastically.`;

  const response = await openai.responses.create({
    model: 'gpt-5-nano',
    input: prompt,
  });

  const text = response.output_text || '';

  let content;
  try {
    content = JSON.parse(text);
  } catch {
    const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/) || text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      content = JSON.parse(jsonMatch[1] || jsonMatch[0]);
    } else {
      throw new Error('Failed to parse AI response as JSON');
    }
  }

  return content;
}

// GET: Check status of AI-generated content
// ?detail=artists — returns list of all unique artists with their AI content status
// ?detail=songs — returns list of all songs with their AI content status
export async function GET(request) {
  if (!verifyAdmin(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  try {
    const db = await getDb();
    const url = new URL(request.url);
    const detail = url.searchParams.get('detail');

    // ─── Detailed artist list ───
    if (detail === 'artists') {
      const allRawArtists = await db.collection('videos').distinct('artist');
      const existingContent = await db.collection('artist_seo_content').find({}, { projection: { slug: 1, artist: 1, generated_at: 1 } }).toArray();
      const contentBySlug = {};
      for (const c of existingContent) {
        if (c.slug) contentBySlug[c.slug] = { artist: c.artist, generated_at: c.generated_at };
      }

      // Deduplicate raw artist names by slug
      const seenSlugs = new Set();
      const artistList = [];
      for (const raw of allRawArtists) {
        if (!raw) continue;
        const slug = artistToSlug(raw);
        if (!slug || seenSlugs.has(slug)) continue;
        seenSlugs.add(slug);
        const displayName = raw.replace(/ -$/, '').trim();
        const hasContent = !!contentBySlug[slug];
        artistList.push({
          name: displayName,
          slug,
          has_content: hasContent,
          generated_at: hasContent ? contentBySlug[slug].generated_at : null,
        });
      }

      // Sort: artists without content first, then alphabetically
      artistList.sort((a, b) => {
        if (a.has_content !== b.has_content) return a.has_content ? 1 : -1;
        return a.name.localeCompare(b.name);
      });

      return NextResponse.json({
        success: true,
        total: artistList.length,
        with_content: artistList.filter(a => a.has_content).length,
        without_content: artistList.filter(a => !a.has_content).length,
        artists: artistList,
      });
    }

    // ─── Detailed song list ───
    if (detail === 'songs') {
      const allSongs = await db.collection('song_pages').find({}, { projection: { slug: 1, title: 1, artist: 1 } }).toArray();
      const existingContent = await db.collection('song_seo_content').find({}, { projection: { slug: 1, generated_at: 1 } }).toArray();
      const contentBySlug = {};
      for (const c of existingContent) {
        if (c.slug) contentBySlug[c.slug] = { generated_at: c.generated_at };
      }

      const songList = allSongs.map(s => ({
        title: s.title,
        artist: s.artist,
        slug: s.slug,
        has_content: !!contentBySlug[s.slug],
        generated_at: contentBySlug[s.slug]?.generated_at || null,
      }));

      songList.sort((a, b) => {
        if (a.has_content !== b.has_content) return a.has_content ? 1 : -1;
        return (a.title || '').localeCompare(b.title || '');
      });

      return NextResponse.json({
        success: true,
        total: songList.length,
        with_content: songList.filter(s => s.has_content).length,
        without_content: songList.filter(s => !s.has_content).length,
        songs: songList,
      });
    }

    // ─── Summary counts (default) ───
    // Deduplicate artists by slug for accurate counts
    const allRawArtists = await db.collection('videos').distinct('artist');
    const seenSlugs = new Set();
    for (const raw of allRawArtists) {
      if (!raw) continue;
      const slug = artistToSlug(raw);
      if (slug) seenSlugs.add(slug);
    }
    const uniqueArtistCount = seenSlugs.size;
    const artistsWithContent = await db.collection('artist_seo_content').countDocuments();

    const totalSongs = await db.collection('song_pages').countDocuments();
    const songsWithContent = await db.collection('song_seo_content').countDocuments();

    return NextResponse.json({
      success: true,
      artists: {
        total: uniqueArtistCount,
        with_ai_content: artistsWithContent,
        without_ai_content: uniqueArtistCount - artistsWithContent,
      },
      songs: {
        total: totalSongs,
        with_ai_content: songsWithContent,
        without_ai_content: totalSongs - songsWithContent,
      },
      api_configured: !!OPENAI_API_KEY,
    });
  } catch (e) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}

// POST: Generate AI content
export async function POST(request) {
  if (!verifyAdmin(request)) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  if (!OPENAI_API_KEY) {
    return NextResponse.json({ error: 'OpenAI API key not configured. Add OPENAI_API_KEY to .env' }, { status: 400 });
  }

  try {
    const body = await request.json();
    const { action, artist_name, song_slug, batch_size } = body;

    const db = await getDb();

    // ─── Generate content for a single artist ───
    if (action === 'generate_artist') {
      if (!artist_name) {
        return NextResponse.json({ error: 'artist_name required' }, { status: 400 });
      }

      // Check if already generated — check by slug
      const slug = artistToSlug(artist_name);
      const existing = await db.collection('artist_seo_content').findOne({ slug });
      if (existing && !body.force) {
        return NextResponse.json({
          success: true,
          message: `Content already exists for "${artist_name}". Use force:true to regenerate.`,
          content: existing,
          cached: true,
        });
      }

      // Get song info
      const escapedName = artist_name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const videos = await db.collection('videos')
        .find({ artist: { $regex: new RegExp(`^${escapedName}`, 'i') } })
        .project({ song: 1 })
        .toArray();

      const displayName = artist_name.replace(/ -$/, '').trim();
      const songTitles = videos.map(v => v.song).filter(Boolean);
      const content = await generateArtistContent(displayName, videos.length, songTitles);

      // Store in DB — use slug as the primary key
      await db.collection('artist_seo_content').updateOne(
        { slug },
        {
          $set: {
            slug,
            artist: displayName,
            content,
            generated_at: new Date(),
            model: 'gpt-5-nano',
          },
        },
        { upsert: true }
      );

      return NextResponse.json({ success: true, artist: displayName, content, cached: false });
    }

    // ─── Generate content for a single song ───
    if (action === 'generate_song') {
      if (!song_slug) {
        return NextResponse.json({ error: 'song_slug required' }, { status: 400 });
      }

      const songPage = await db.collection('song_pages').findOne({ slug: song_slug });
      if (!songPage) {
        return NextResponse.json({ error: `Song page not found: ${song_slug}` }, { status: 404 });
      }

      const existing = await db.collection('song_seo_content').findOne({ slug: song_slug });
      if (existing && !body.force) {
        return NextResponse.json({
          success: true,
          message: `Content already exists for "${songPage.title}". Use force:true to regenerate.`,
          content: existing,
          cached: true,
        });
      }

      const content = await generateSongContent(songPage.title, songPage.artist, songPage.type);

      await db.collection('song_seo_content').updateOne(
        { slug: song_slug },
        {
          $set: {
            slug: song_slug,
            title: songPage.title,
            artist: songPage.artist,
            content,
            generated_at: new Date(),
            model: 'gpt-5-nano',
          },
        },
        { upsert: true }
      );

      return NextResponse.json({ success: true, song: songPage.title, content, cached: false });
    }

    // ─── Batch generate for artists without content ───
    if (action === 'batch_artists') {
      const limit = Math.min(batch_size || 5, 20); // Max 20 at a time
      const allArtists = await db.collection('videos').distinct('artist');

      // Find artists without AI content — check by SLUG (the reliable key)
      const existingContent = await db.collection('artist_seo_content')
        .find({}, { projection: { slug: 1 } }).toArray();
      const existingSlugSet = new Set(existingContent.map(c => c.slug).filter(Boolean));

      // Deduplicate by slug and skip already-generated
      const seenSlugs = new Set();
      const uniqueArtists = [];
      for (const artist of allArtists) {
        if (!artist) continue;
        const slug = artistToSlug(artist);
        if (slug && !seenSlugs.has(slug) && !existingSlugSet.has(slug)) {
          seenSlugs.add(slug);
          uniqueArtists.push({ name: artist, slug });
        }
      }

      const batch = uniqueArtists.slice(0, limit);
      const results = [];

      for (const { name: artist, slug } of batch) {
        try {
          const escapedName = artist.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
          const videos = await db.collection('videos')
            .find({ artist: { $regex: new RegExp(`^${escapedName}`, 'i') } })
            .project({ song: 1 })
            .toArray();

          // Use clean display name (strip trailing " -")
          const displayName = artist.replace(/ -$/, '').trim();
          const songTitles = videos.map(v => v.song).filter(Boolean);
          const content = await generateArtistContent(displayName, videos.length, songTitles);

          await db.collection('artist_seo_content').updateOne(
            { slug },
            { $set: { slug, artist: displayName, content, generated_at: new Date(), model: 'gpt-5-nano' } },
            { upsert: true }
          );

          results.push({ artist: displayName, status: 'success' });
        } catch (err) {
          results.push({ artist, status: 'error', error: err.message });
        }
      }

      return NextResponse.json({
        success: true,
        processed: results.length,
        remaining: uniqueArtists.length - batch.length,
        results,
      });
    }

    // ─── Batch generate for songs without content ───
    if (action === 'batch_songs') {
      const limit = Math.min(batch_size || 5, 20);
      const allSongs = await db.collection('song_pages').find({}).toArray();

      const existingContent = await db.collection('song_seo_content')
        .find({}, { projection: { slug: 1 } }).toArray();
      const existingSet = new Set(existingContent.map(c => c.slug));

      const songsNeedingContent = allSongs.filter(s => s.slug && !existingSet.has(s.slug));
      const batch = songsNeedingContent.slice(0, limit);
      const results = [];

      for (const song of batch) {
        try {
          const content = await generateSongContent(song.title, song.artist, song.type);

          await db.collection('song_seo_content').updateOne(
            { slug: song.slug },
            {
              $set: {
                slug: song.slug,
                title: song.title,
                artist: song.artist,
                content,
                generated_at: new Date(),
                model: 'gpt-5-nano',
              },
            },
            { upsert: true }
          );

          results.push({ song: song.title, status: 'success' });
        } catch (err) {
          results.push({ song: song.title, status: 'error', error: err.message });
        }
      }

      return NextResponse.json({
        success: true,
        processed: results.length,
        remaining: songsNeedingContent.length - batch.length,
        results,
      });
    }

    return NextResponse.json({ error: 'Unknown action' }, { status: 400 });

  } catch (e) {
    console.error('AI SEO generation error:', e);
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
