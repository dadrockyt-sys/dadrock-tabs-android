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
- Return valid JSON only.
- No markdown.

JSON format:
{
  "title": "...",
  "artist": "...",
  "description": "...",
  "seoContent": {
    "intro": "...",
    "techniques": "...",
    "practiceTips": "...",
    "gear": "..."
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

  const data = await res
