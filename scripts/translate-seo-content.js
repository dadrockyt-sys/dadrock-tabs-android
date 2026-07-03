#!/usr/bin/env node

const { MongoClient } = require('mongodb');

const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'dadrock_tabs';
const OPENAI_API_KEY = process.env.OPENAI_API_KEY || '';
const TARGET_LANG = 'es';
const CONCURRENCY = 3;

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

async function callOpenAI(prompt) {
  const res = await fetch('https://api.openai.com/v1/responses', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${API_KEY}`,
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

  let text = '';
  for (const item of data.output || []) {
    if (item.type === 'message') {
      for (const c of item.content || []) {
        if (c.type === 'output_text' && c.text) {
          text = c.text;
          break;
        }
      }
    }
  }

  if (!text) throw new Error('No text returned from OpenAI');

  try {
    return JSON.parse(text);
  } catch {
    const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/) || text.match(/\{[\s\S]*\}/);
    if (jsonMatch) return JSON.parse(jsonMatch[1] || jsonMatch[0]);
    throw new Error('Could not parse translation JSON');
  }
}

async function translateArtistContent(artist, content) {
  const prompt = `
Translate this DadRock Tabs artist SEO content into Spanish.

Rules:
- Keep the same JSON keys.
- Translate naturally for Spanish-speaking guitar and bass players.
- Keep artist names, song titles, album titles, and brand names unchanged.
- Keep the tone enthusiastic and educational.
- Return ONLY valid JSON.

Original JSON:
${JSON.stringify(content, null, 2)}
`;

  return callOpenAI(prompt);
}

async function processWithConcurrency(items, processFn) {
  let completed = 0;
  let failed = 0;

  for (let i = 0; i < items.length; i += CONCURRENCY) {
    const batch = items.slice(i, i + CONCURRENCY);
    const results = await Promise.allSettled(batch.map(processFn));

    for (const result of results) {
      if (result.status === 'fulfilled') completed++;
      else {
        failed++;
        console.error('❌', result.reason?.message || result.reason);
      }
    }

    console.log(`Progress: ${completed + failed}/${items.length} (${completed}✅ ${failed}❌)`);
  }
}

async function main() {
  if (!API_KEY) {
    console.error('No OPENAI_API_KEY found');
    process.exit(1);
  }

  console.log('🌎 Translating artist SEO content to Spanish...');
  console.log(`Database: ${DB_NAME}`);

  const client = await MongoClient.connect(MONGO_URL);
  const db = client.db(DB_NAME);

  const docs = await db.collection('artist_seo_content').find({}).toArray();

  const toTranslate = docs.filter(doc => {
    if (!doc.content) return false;

    // Already new format and already has Spanish
    if (doc.content.es) return false;

    // Translate old flat format or new format with en only
    return true;
  });

  console.log(`Artists to translate: ${toTranslate.length}`);

  await processWithConcurrency(toTranslate, async (doc) => {
    const englishContent = doc.content.en || doc.content;

    const spanishContent = await translateArtistContent(doc.artist, englishContent);

    await db.collection('artist_seo_content').updateOne(
      { _id: doc._id },
      {
        $set: {
          'content.en': englishContent,
          [`content.${TARGET_LANG}`]: spanishContent,
          translated_at_es: new Date(),
        },
      }
    );

    console.log(`✅ Translated: ${doc.artist || doc.slug}`);
  });

  await client.close();

  console.log('🎉 Spanish translation complete!');
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
