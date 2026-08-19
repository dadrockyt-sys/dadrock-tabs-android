#!/usr/bin/env node

const { MongoClient } = require('mongodb');

const MONGO_URL = process.env.MONGO_URL;
const DB_NAME = process.env.DB_NAME || 'dadrock_tabs';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY;

const TARGET_LANG = process.env.TARGET_LANG || 'fr';
const MODEL = process.env.OPENAI_MODEL || 'gpt-5-nano';
const CONCURRENCY = Number(process.env.CONCURRENCY || 2);

const LANGUAGE_NAMES = {
  es: 'Spanish',
  fr: 'French',
  de: 'German',
  it: 'Italian',
  pt: 'Portuguese',
  'pt-br': 'Brazilian Portuguese',
  ja: 'Japanese',
  ko: 'Korean',
  zh: 'Chinese',
  ru: 'Russian',
  hi: 'Hindi',
  sv: 'Swedish',
  fi: 'Finnish',
};

function requireEnv() {
  if (!MONGO_URL) throw new Error('Missing MONGO_URL');
  if (!OPENAI_API_KEY) throw new Error('Missing OPENAI_API_KEY');
  if (!LANGUAGE_NAMES[TARGET_LANG]) throw new Error(`Unsupported TARGET_LANG: ${TARGET_LANG}`);
}

function normalizeForComparison(value) {
  return String(value || '')
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function containsUntranslatedEnglishChunk(translatedValue, englishValue) {
  const translated = String(translatedValue || '').trim();
  const english = String(englishValue || '').trim();
  if (!translated || !english) return false;
  if (translated === english) return true;

  const normalizedEnglish = normalizeForComparison(english);
  const englishWords = new Set(
    normalizedEnglish
      .split(/\s+/)
      .filter(word => word.length > 4)
  );

  const chunks = translated
    .split(/\n+/)
    .map(part => part.trim())
    .filter(Boolean);

  return chunks.some(chunk => {
    const normalizedChunk = normalizeForComparison(chunk);
    if (!normalizedChunk) return false;

    if (normalizedChunk.length >= 40 && normalizedEnglish.includes(normalizedChunk)) {
      return true;
    }

    const latinChars = (chunk.match(/[A-Za-z]/g) || []).length;
    const letterChars = (chunk.match(/\p{L}/gu) || []).length;
    const mostlyLatin = letterChars > 0 && latinChars / letterChars > 0.65;
    if (!mostlyLatin) return false;

    const candidateWords = normalizedChunk
      .split(/\s+/)
      .filter(word => word.length > 4);
    if (candidateWords.length < 8) return false;

    const matchingWords = candidateWords.filter(word => englishWords.has(word));
    return matchingWords.length / candidateWords.length >= 0.8;
  });
}

function hasMeaningfulTranslation(translatedContent, englishContent) {
  if (!translatedContent || typeof translatedContent !== 'object') return false;

  // If an older record has no English source object, require the key localized
  // content fields to at least be populated. New records should normally have
  // englishContent and will receive the stricter comparison below.
  if (!englishContent || typeof englishContent !== 'object') {
    return ['song_story', 'lesson_overview', 'difficulty_info', 'meta_description']
      .every(key => typeof translatedContent[key] === 'string' && translatedContent[key].trim().length >= 20);
  }

  const englishStringKeys = Object.keys(englishContent).filter(key =>
    typeof englishContent[key] === 'string' && englishContent[key].trim().length > 20
  );

  const stringsAreTranslated = englishStringKeys.every(key => {
    const englishValue = englishContent[key].trim();
    const translatedValue = translatedContent[key];

    if (typeof translatedValue !== 'string' || translatedValue.trim().length < 20) {
      return false;
    }

    return !containsUntranslatedEnglishChunk(translatedValue, englishValue);
  });

  if (!stringsAreTranslated) return false;

  const englishArrayKeys = Object.keys(englishContent).filter(key =>
    Array.isArray(englishContent[key]) && englishContent[key].some(item => typeof item === 'string')
  );

  return englishArrayKeys.every(key => {
    const englishArray = englishContent[key];
    const translatedArray = translatedContent[key];

    if (!Array.isArray(translatedArray) || translatedArray.length < englishArray.length) {
      return false;
    }

    return englishArray.every((englishItem, index) => {
      if (typeof englishItem !== 'string' || englishItem.trim().length < 5) return true;
      const translatedItem = translatedArray[index];
      if (typeof translatedItem !== 'string' || translatedItem.trim().length < 3) return false;
      return !containsUntranslatedEnglishChunk(translatedItem, englishItem);
    });
  });
}

async function translateSong(song, existingContent) {
  const languageName = LANGUAGE_NAMES[TARGET_LANG];

  const source = {
    title: song.title || '',
    artist: song.artist || '',
    fullTitle: song.fullTitle || '',
    description: song.description || '',
    seoContent: existingContent || null,
  };

  const prompt = `
Translate this DadRock Tabs song page SEO content into ${languageName}.

Rules:
- Keep artist names and song titles recognizable.
- Do not invent facts.
- Keep the meaning natural for guitar/bass lesson SEO.
- Translate EVERY sentence and paragraph in every prose field.
- Translate meta_description completely; do not leave English boilerplate in it.
- Translate every techniques and pro_tips array item where a natural localized term exists.
- Established music terms, song titles, artist names, album names and gear brands may remain unchanged where natural.
- Return valid JSON only.
- No markdown.

JSON format:
{
  "title": "...",
  "artist": "...",
  "description": "...",
  "seoContent": {
    "song_story": "...",
    "lesson_overview": "...",
    "difficulty_info": "...",
    "techniques": ["...", "..."],
    "pro_tips": ["...", "..."],
    "meta_description": "..."
  }
}

Source:
${JSON.stringify(source, null, 2)}
`;

  const res = await fetch('https://api.openai.com/v1/responses', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${OPENAI_API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: MODEL,
      input: prompt,
    }),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`OpenAI error ${res.status}: ${text}`);
  }

  const data = await res.json();

  const text =
    data.output_text ||
    data.output
      ?.flatMap(item => item.content || [])
      ?.map(content => content.text || '')
      ?.join('')
      ?.trim();

  if (!text) throw new Error('No translation text returned');

  return JSON.parse(text);
}

async function worker(items, db, workerId) {
  while (items.length) {
    const song = items.shift();

    try {
      const slug = song.slug;
      const seoCol = db.collection('song_seo_content');

      let seoDoc = await seoCol.findOne({ slug });
      const englishContent = seoDoc?.content || null;
      const existingTranslation = seoDoc?.translations?.[TARGET_LANG];

      if (hasMeaningfulTranslation(existingTranslation, englishContent)) {
        console.log(`⏭️  [${workerId}] Skipping ${slug} — verified ${TARGET_LANG} translation`);
        continue;
      }

      if (existingTranslation) {
        console.log(`🔧 [${workerId}] Repairing partial/mixed ${TARGET_LANG} translation for ${slug}`);
      }

      const translated = await translateSong(song, englishContent);
      const translatedSeoContent = translated.seoContent || translated;

      if (!hasMeaningfulTranslation(translatedSeoContent, englishContent)) {
        throw new Error(`Rejected partial/mixed ${TARGET_LANG} translation`);
      }

      await seoCol.updateOne(
        { slug },
        {
          $set: {
            slug,
            title: song.title,
            artist: song.artist,
            updated_at: new Date().toISOString(),
            [`translations.${TARGET_LANG}`]: translatedSeoContent,
          },
          $setOnInsert: {
            created_at: new Date().toISOString(),
          },
        },
        { upsert: true }
      );

      console.log(`✅ [${workerId}] Translated ${slug} to ${TARGET_LANG}`);
    } catch (err) {
      console.error(`❌ [${workerId}] Failed ${song.slug}:`, err.message);
    }
  }
}

async function main() {
  requireEnv();

  console.log('🎵 Translating song SEO content...');
  console.log(`Database: ${DB_NAME}`);
  console.log(`Language: ${TARGET_LANG}`);
  console.log(`Concurrency: ${CONCURRENCY}`);

  const client = new MongoClient(MONGO_URL);
  await client.connect();

  try {
    const db = client.db(DB_NAME);

    const songs = await db.collection('song_pages')
      .find({ slug: { $exists: true, $ne: '' } })
      .sort({ viewCount: -1 })
      .toArray();

    console.log(`Found ${songs.length} song pages`);

    const items = [...songs];

    await Promise.all(
      Array.from({ length: CONCURRENCY }, (_, i) => worker(items, db, i + 1))
    );

    console.log('🎉 Song translation complete');
  } finally {
    await client.close();
  }
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
