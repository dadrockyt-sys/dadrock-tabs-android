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

function hasMeaningfulTranslation(translatedContent, englishContent) {
  if (!translatedContent || typeof translatedContent !== 'object') return false;
  if (!englishContent || typeof englishContent !== 'object') return false;

  const englishKeys = Object.keys(englishContent).filter(key => {
    return typeof englishContent[key] === 'string' && englishContent[key].trim().length > 20;
  });

  if (englishKeys.length === 0) return false;

  return englishKeys.every(key => {
    const englishValue = englishContent[key].trim();
    const translatedValue = translatedContent[key];

    if (typeof translatedValue !== 'string') return false;

    const cleanedTranslated = translatedValue.trim();

    if (cleanedTranslated.length < 20) return false;

    // If the translated field is exactly the same as English, it is NOT translated
    if (cleanedTranslated === englishValue) return false;

    // If most of the English text is still present, it is NOT translated
    const englishWords = englishValue
      .toLowerCase()
      .replace(/[^a-z0-9\s]/g, ' ')
      .split(/\s+/)
      .filter(word => word.length > 4);

    const translatedLower = cleanedTranslated.toLowerCase();

    const matchingWords = englishWords.filter(word => translatedLower.includes(word));

    if (englishWords.length > 10 && matchingWords.length / englishWords.length > 0.35) {
      return false;
    }

    return true;
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
- Translate ONLY the values.
- Artist names, album names, song titles, equipment brands, and guitar terminology stay unchanged.
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
      return !hasMeaningfulTranslation(doc.content?.[lang], englishContent);
    });
    if (artistName === ".38 Special") {
  console.log("FULL DOC:", JSON.stringify(doc, null, 2));
    }

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
      if (!translatedByLang?.[lang]) {
        console.warn(`⚠️ Missing ${lang} translation for ${artistName}`);
        continue;
      }

      updates[`content.${lang}`] = translatedByLang[lang];
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
