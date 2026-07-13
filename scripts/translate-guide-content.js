import fs from 'node:fs/promises';
import path from 'node:path';
import OpenAI from 'openai';
import { GUIDES } from '../lib/guidesData.js';

const TARGET_LANGUAGES = {
  pt: 'European Portuguese',
  'pt-br': 'Brazilian Portuguese',
  de: 'German',
  fr: 'French',
  it: 'Italian',
  ja: 'Japanese',
  ko: 'Korean',
  zh: 'Simplified Chinese',
  ru: 'Russian',
  hi: 'Hindi',
  sv: 'Swedish',
  fi: 'Finnish',
};

const GUIDE_SLUGS = Object.keys(GUIDES);

const OUTPUT_FILE = path.join(
  process.cwd(),
  'lib',
  'generatedGuideContentTranslations.json'
);

const languageCode = process.argv[2] || process.env.LANGUAGE;

if (!languageCode || !TARGET_LANGUAGES[languageCode]) {
  console.error(
    `Choose a language: ${Object.keys(TARGET_LANGUAGES).join(', ')}`
  );
  console.error('Example: node scripts/translate-guide-content.js fr');
  process.exit(1);
}

if (!process.env.OPENAI_API_KEY) {
  console.error('Missing OPENAI_API_KEY.');
  process.exit(1);
}

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});
function cleanTranslation(value) {
  let cleaned = value.trim();

  if (cleaned.startsWith('```html')) {
    cleaned = cleaned.slice(7);
  } else if (cleaned.startsWith('```')) {
    cleaned = cleaned.slice(3);
  }

  if (cleaned.endsWith('```')) {
    cleaned = cleaned.slice(0, -3);
  }

  return cleaned.trim();
}

function validateTranslation(source, translated, slug) {
  const sourcePreCount = (source.match(/<pre>/g) || []).length;
  const translatedPreCount = (translated.match(/<pre>/g) || []).length;

  const sourcePreCloseCount = (source.match(/<\/pre>/g) || []).length;
  const translatedPreCloseCount =
    (translated.match(/<\/pre>/g) || []).length;

  if (!translated.includes('<h2>')) {
    throw new Error(`${slug}: translated content has no <h2> heading.`);
  }

  if (
    sourcePreCount !== translatedPreCount ||
    sourcePreCloseCount !== translatedPreCloseCount
  ) {
    throw new Error(`${slug}: <pre> block count changed during translation.`);
  }

  if (translated.includes('```')) {
    throw new Error(`${slug}: translation still contains code fences.`);
  }
}

async function translateGuide(slug, html, targetLanguage) {
  console.log(`Translating ${slug} into ${targetLanguage}...`);

  const response = await client.responses.create({
    model: process.env.OPENAI_MODEL || 'gpt-5-nano',
        instructions: `
You are a professional website localization translator.

Translate the supplied guitar-learning HTML into ${targetLanguage}.

Strict requirements:
- Return only the translated HTML.
- Do not add Markdown code fences.
- Preserve every HTML tag and the exact HTML structure.
- Preserve song titles, artist names, band names and album names.
- Preserve guitar tuning notes such as E A D G B E and D A D G B E.
- Preserve chord names, BPM values, numbers, tablature and diagrams.
- Preserve all text inside <pre> blocks exactly.
- Translate headings, paragraphs, list descriptions and instructional text.
- Use natural terminology understood by guitar players.
- Do not shorten, summarize or add new information.
    `.trim(),
    input: html,
  });

  const translated = cleanTranslation(response.output_text || '');

  if (!translated) {
    throw new Error(`${slug}: OpenAI returned an empty translation.`);
  }

  validateTranslation(html, translated, slug);

  return translated;
}

async function readExistingTranslations() {
  try {
    const existing = await fs.readFile(OUTPUT_FILE, 'utf8');
    return JSON.parse(existing);
  } catch (error) {
    if (error.code === 'ENOENT') {
      return {};
    }

    throw error;
  }
}
async function main() {
  const targetLanguage = TARGET_LANGUAGES[languageCode];
  const translations = await readExistingTranslations();

  if (!translations[languageCode]) {
    translations[languageCode] = {};
  }

  for (const slug of GUIDE_SLUGS) {
    const guide = GUIDES[slug];

    if (!guide) {
      throw new Error(`Guide not found in GUIDES: ${slug}`);
    }

    if (!guide.content || typeof guide.content !== 'string') {
      throw new Error(`Guide has no valid content field: ${slug}`);
    }

    const translated = await translateGuide(
      slug,
      guide.content,
      targetLanguage
    );

    translations[languageCode][slug] = translated;

    // Save after every guide so progress is not lost if a later call fails.
    await fs.writeFile(
      OUTPUT_FILE,
      `${JSON.stringify(translations, null, 2)}\n`,
      'utf8'
    );

    console.log(`Saved ${slug}.`);
  }

  console.log('');
  console.log(`Completed ${targetLanguage}.`);
  console.log(`Output: ${OUTPUT_FILE}`);
}

main().catch((error) => {
  console.error('');
  console.error('Guide translation failed:');
  console.error(error);
  process.exit(1);
});

