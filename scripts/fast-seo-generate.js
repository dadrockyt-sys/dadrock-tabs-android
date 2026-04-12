#!/usr/bin/env node
/**
 * Fast Parallel SEO Content Generator
 * Makes direct OpenAI API calls with concurrency control.
 */

const { MongoClient } = require('mongodb');
const MONGO_URL = 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'your_database_name';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';
const CONCURRENCY = 5; // 5 parallel OpenAI calls at a time

// Read API key from .env file if not in environment
function getApiKey() {
  if (OPENAI_API_KEY) return OPENAI_API_KEY;
  try {
    const fs = require('fs');
    const env = fs.readFileSync('/app/.env', 'utf8');
    const match = env.match(/OPENAI_API_KEY=(.+)/);
    return match ? match[1].trim() : '';
  } catch { return ''; }
}

const API_KEY = getApiKey();

async function callOpenAI(prompt) {
  const res = await fetch('https://api.openai.com/v1/responses', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: 'gpt-5-nano',
      input: prompt,
    }),
  });
  
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`OpenAI API error ${res.status}: ${err}`);
  }
  
  const data = await res.json();
  
  // Extract text from the nested response structure
  let text = '';
  for (const item of (data.output || [])) {
    if (item.type === 'message') {
      for (const c of (item.content || [])) {
        if (c.type === 'output_text' && c.text) {
          text = c.text;
          break;
        }
      }
    }
  }
  
  if (!text) throw new Error('No text in AI response');
  
  // Parse JSON from response
  try {
    return JSON.parse(text);
  } catch {
    const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/) || text.match(/\{[\s\S]*\}/);
    if (jsonMatch) {
      return JSON.parse(jsonMatch[1] || jsonMatch[0]);
    }
    throw new Error('Failed to parse AI response as JSON');
  }
}

function artistToSlug(name) {
  if (!name) return '';
  return name.replace(/ -$/, '').trim().toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '-').replace(/-+/g, '-')
    .replace(/^-|-$/g, '');
}

async function generateArtistContent(artistName, songCount, songTitles) {
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

  return callOpenAI(prompt);
}

async function generateSongContent(songTitle, artistName, videoType) {
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

  return callOpenAI(prompt);
}

// Process items with concurrency limit
async function processWithConcurrency(items, processFn, label) {
  let completed = 0;
  let failed = 0;
  const total = items.length;
  const startTime = Date.now();

  for (let i = 0; i < items.length; i += CONCURRENCY) {
    const batch = items.slice(i, i + CONCURRENCY);
    const results = await Promise.allSettled(batch.map(item => processFn(item)));
    
    for (const r of results) {
      if (r.status === 'fulfilled') completed++;
      else { failed++; console.error(`  ❌ Error: ${r.reason?.message?.slice(0, 100)}`); }
    }
    
    const elapsed = ((Date.now() - startTime) / 1000).toFixed(0);
    const rate = (completed / (elapsed || 1) * 60).toFixed(1);
    const eta = ((total - completed - failed) / (completed / (elapsed || 1))).toFixed(0);
    console.log(`[${label}] ${completed + failed}/${total} done (${completed}✅ ${failed}❌) | ${elapsed}s elapsed | ~${rate}/min | ETA: ${eta}s`);
  }

  return { completed, failed };
}

async function main() {
  if (!API_KEY) {
    console.error('No OPENAI_API_KEY found!');
    process.exit(1);
  }

  console.log('🎸 DadRock Tabs — Fast Parallel SEO Generator');
  console.log(`Started: ${new Date().toISOString()}`);
  console.log(`Concurrency: ${CONCURRENCY} parallel calls\n`);

  const client = await MongoClient.connect(MONGO_URL);
  const db = client.db(DB_NAME);

  // ═══════════════ ARTISTS ═══════════════
  console.log('═'.repeat(60));
  console.log('Phase 1: ARTISTS');
  console.log('═'.repeat(60));

  const allRawArtists = await db.collection('videos').distinct('artist');
  const existingArtistContent = await db.collection('artist_seo_content').find({}, { projection: { slug: 1 } }).toArray();
  const existingArtistSlugs = new Set(existingArtistContent.map(c => c.slug).filter(Boolean));

  // Deduplicate by slug
  const seenSlugs = new Set();
  const artistsToProcess = [];
  for (const raw of allRawArtists) {
    if (!raw) continue;
    const slug = artistToSlug(raw);
    if (slug && !seenSlugs.has(slug) && !existingArtistSlugs.has(slug)) {
      seenSlugs.add(slug);
      artistsToProcess.push({ name: raw, slug, displayName: raw.replace(/ -$/, '').trim() });
    }
  }

  console.log(`Artists to generate: ${artistsToProcess.length}\n`);

  // Pre-fetch video data for all artists
  const allVideos = await db.collection('videos').find({}, { projection: { artist: 1, song: 1 } }).toArray();
  const videosByArtist = {};
  for (const v of allVideos) {
    if (!v.artist) continue;
    const slug = artistToSlug(v.artist);
    if (!videosByArtist[slug]) videosByArtist[slug] = [];
    if (v.song) videosByArtist[slug].push(v.song);
  }

  const artistResults = await processWithConcurrency(artistsToProcess, async (artist) => {
    const songs = videosByArtist[artist.slug] || [];
    const content = await generateArtistContent(artist.displayName, songs.length, songs);
    
    await db.collection('artist_seo_content').updateOne(
      { slug: artist.slug },
      { $set: { slug: artist.slug, artist: artist.displayName, content, generated_at: new Date(), model: 'gpt-5-nano' } },
      { upsert: true }
    );
  }, 'Artists');

  // ═══════════════ SONGS ═══════════════
  console.log('\n' + '═'.repeat(60));
  console.log('Phase 2: SONGS');
  console.log('═'.repeat(60));

  const allSongs = await db.collection('song_pages').find({}).toArray();
  const existingSongContent = await db.collection('song_seo_content').find({}, { projection: { slug: 1 } }).toArray();
  const existingSongSlugs = new Set(existingSongContent.map(c => c.slug));

  const songsToProcess = allSongs.filter(s => s.slug && !existingSongSlugs.has(s.slug));
  console.log(`Songs to generate: ${songsToProcess.length}\n`);

  const songResults = await processWithConcurrency(songsToProcess, async (song) => {
    const content = await generateSongContent(song.title, song.artist, song.type);
    
    await db.collection('song_seo_content').updateOne(
      { slug: song.slug },
      { $set: { slug: song.slug, title: song.title, artist: song.artist, content, generated_at: new Date(), model: 'gpt-5-nano' } },
      { upsert: true }
    );
  }, 'Songs');

  // ═══════════════ SUMMARY ═══════════════
  console.log('\n' + '═'.repeat(60));
  console.log('🎉 COMPLETE!');
  console.log(`Artists: ${artistResults.completed}✅ ${artistResults.failed}❌`);
  console.log(`Songs: ${songResults.completed}✅ ${songResults.failed}❌`);
  console.log(`Finished: ${new Date().toISOString()}`);
  console.log('═'.repeat(60));

  await client.close();
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
