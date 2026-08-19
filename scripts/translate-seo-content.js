#!/usr/bin/env node

const { MongoClient } = require('mongodb');

const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'dadrock_tabs';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';

const CONCURRENCY = Number(process.env.CONCURRENCY || 2);
const LIMIT = Number(process.env.LIMIT || 25);
const MODEL = process.env.OPENAI_MODEL || 'gpt-5-nano';

const TARGET_LANGS = (process.env.TARGET_LANGS || 'fr')
  .split(',')
  .map(lang => lang.trim())
  .filter(Boolean);

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

function getApiKey() {
  if (OPENAI_API_KEY) return OPENAI_API_KEY;

  try {
    const fs = require('fs');
    const env = fs.readFileSync('/app/.env', 'utf8');
    const match = env.match(/OPENAI_API_KEY=(.+)/);
    return match ? match[1].trim() : '';
  } catch {
    return '';
  }
}

const API_KEY = getApiKey();

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
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

    // Catch whole English paragraphs/sentences copied unchanged into a translation.
    if (normalizedChunk.length >= 40 && normalizedEnglish.includes(normalizedChunk)) {
      return true;
    }

    // For Latin-script translations, catch chunks where nearly all meaningful
    // words are still English source words. This remains tolerant of artist names,
    // album/song titles, gear brands, and common guitar terminology.
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
  if (!englishContent || typeof englishContent !== 'object') return false;

  const englishStringKeys = Object.keys(englishContent).filter(key => {
    return typeof englishContent[key] === 'string' && englishContent[key].trim().length > 20;
  });

  if (englishStringKeys.length === 0) return false;

  const stringsAreTranslated = englishStringKeys.every(key => {
    const englishValue = englishContent[key].trim();
    const translatedValue = translatedContent[key];

    if (typeof translatedValue !== 'string') return false;

    const cleanedTranslated = translatedValue.trim();
    if (cleanedTranslated.length < 20) return false;
    if (containsUntranslatedEnglishChunk(cleanedTranslated, englishValue)) return false;

    return true;
  });

  if (!stringsAreTranslated) return false;

  // Validate array fields such as fun_facts as well. The old validator ignored
  // them, which allowed fully English facts to survive in localized records.
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
      if (typeof englishItem !== 'string' || englishItem.trim().length < 10) return true;

      const translatedItem = translatedArray[index];
      if (typeof translatedItem !== 'string' || translatedItem.trim().length < 5) return false;

      return !containsUntranslatedEnglishChunk(translatedItem, englishItem);
    });
  });
}

function extractOutputText(data) {
  let text = '';

  for (const item of data.output || []) {
    if (item.type === 'message') {
      for (const content of item.content || []) {
        if (content.type === 'output_text' && content.text) {
          text += content.text;
        }
      }
    }
  }

  return text.trim();
}

function parseJsonFromText(text) {
  try {
    return JSON.parse(text);
  } catch {
    const codeBlockMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/);
    if (codeBlockMatch) {
      return JSON.parse(codeBlockMatch[1]);
    }

    const objectMatch = text.match(/\{[\s\S]*\}/);
    if (objectMatch) {
      return JSON.parse(objectMatch[0]);
    }

    throw new Error('Could not parse translation JSON');
  }
}

async function callOpenAI(prompt) {
  const response = await fetch('https://api.openai.com/v1/responses', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      model: MODEL,
      input: prompt,
    }),
  });

  if (!response.ok) {
    const err = await response.text();
    throw new Error(`OpenAI API error ${response.status}: ${err}`);
  }

  const data = await response.json();
  const text = extractOutputText(data);

  if (!text) {
    throw new Error('OpenAI returned no text.');
  }

  return parseJsonFromText(text);
}

async function translateArtistContent(artistName, englishContent, missingLangs) {
  const languages = missingLangs
    .map(code => `${code}: ${LANGUAGE_NAMES[code] || code}`)
    .join('\n');

  const prompt = `
Translate this DadRock Tabs SEO content for artist "${artistName}".

Languages:
${languages}

Rules:
- Return ONE JSON object.
- Top level keys must be the language codes.
- Keep every JSON key exactly the same.
- Translate EVERY sentence and EVERY paragraph in every prose field.
- Do not leave English sentences, paragraphs, introductions, or meta-description boilerplate in a translated value.
- Translate every fun_facts array item too.
- Artist names, album names, song titles, equipment brands, and established guitar terminology may stay unchanged where natural.
- Preserve paragraph breaks with \n where present.
- Return ONLY valid JSON.

Example format:

{
  "fr": { ... }
}

English JSON:

${JSON.stringify(englishContent, null, 2)}
`;

  return await callOpenAI(prompt);
}

async function processQueue(items, worker) {
  let completed = 0;
  let failed = 0;

  for (let i = 0; i < items.length; i += CONCURRENCY) {
    const batch = items.slice(i, i + CONCURRENCY);

    const results = await Promise.allSettled(batch.map(worker));

    for (const result of results) {
      if (result.status === 'fulfilled') {
        completed++;
      } else {
        failed++;
        console.error(result.reason);
      }
    }

    console.log(
      `Progress ${completed + failed}/${items.length} (${completed} complete, ${failed} failed)`
    );

    await sleep(1000);
  }
}

async function main() {
  if (!API_KEY) {
    console.error('No OPENAI_API_KEY found.');
    process.exit(1);
  }

  console.log('🌎 Translating artist SEO content...');
  console.log(`Database: ${DB_NAME}`);
  console.log(`Languages: ${TARGET_LANGS.join(', ')}`);
  console.log(`Limit: ${LIMIT}`);
  console.log(`Concurrency: ${CONCURRENCY}`);

  const client = await MongoClient.connect(MONGO_URL);
  const db = client.db(DB_NAME);

  const docs = await db
    .collection('artist_seo_content')
    .find({})
    .sort({ artist: 1, slug: 1 })
    .toArray();

  const jobs = [];
  let skipped = 0;

  for (const doc of docs) {
    if (!doc.content) continue;

    const artistName = doc.artist || doc.slug || 'Unknown Artist';
    const englishContent = doc.content.en || doc.content;

    const missingLangs = TARGET_LANGS.filter(lang => {
      const translatedContent = doc.content?.[lang];
      return !hasMeaningfulTranslation(translatedContent, englishContent);
    });

    if (missingLangs.length === 0) {
      skipped++;
      console.log(`⏭️ Skipping ${artistName} — already translated`);
      continue;
    }

    jobs.push({
      doc,
      artistName,
      englishContent,
      missingLangs,
    });

    if (jobs.length >= LIMIT) break;
  }

  console.log(`Skipped already translated artists: ${skipped}`);
  console.log(`Artist translation jobs this run: ${jobs.length}`);

  if (jobs.length === 0) {
    console.log('✅ Nothing to translate.');
    await client.close();
    return;
  }

  await processQueue(jobs, async ({ doc, artistName, englishContent, missingLangs }) => {
    const translatedByLang = await translateArtistContent(
      artistName,
      englishContent,
      missingLangs
    );

    const updates = {
      'content.en': englishContent,
    };

    for (const lang of missingLangs) {
      const translatedContent = translatedByLang?.[lang];
      if (!translatedContent) {
        console.warn(`⚠️ Missing ${lang} translation for ${artistName}`);
        continue;
      }

      if (!hasMeaningfulTranslation(translatedContent, englishContent)) {
        console.warn(`⚠️ Rejected partial/mixed ${lang} translation for ${artistName}`);
        continue;
      }

      updates[`content.${lang}`] = translatedContent;
      updates[`translated_at_${lang}`] = new Date();
    }

    await db.collection('artist_seo_content').updateOne(
      { _id: doc._id },
      { $set: updates }
    );

    console.log(`✅ ${artistName} → ${missingLangs.join(', ')}`);
  });

  await client.close();

  console.log('🎉 Translation complete!');
}

main().catch((err) => {
  console.error('Fatal error:', err);
  process.exit(1);
});
