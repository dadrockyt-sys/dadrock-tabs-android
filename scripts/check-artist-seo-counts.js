#!/usr/bin/env node

const { MongoClient } = require('mongodb');

const MONGO_URL = process.env.MONGO_URL;
const DB_NAME = process.env.DB_NAME || 'dadrock_tabs';

function normalizeArtist(name) {
  return String(name || '')
    .trim()
    .toLowerCase()
    .replace(/\s+/g, ' ');
}

async function main() {
  const client = new MongoClient(MONGO_URL);
  await client.connect();

  const db = client.db(DB_NAME);
  const col = db.collection('artist_seo_content');

  const docs = await col.find({}).toArray();

  const total = docs.length;
  const withSlug = docs.filter(d => d.slug && d.slug !== 'undefined').length;
  const withoutSlug = docs.filter(d => !d.slug || d.slug === 'undefined').length;

  const artists = new Set(docs.map(d => normalizeArtist(d.artist)));
  const artistsWithGoodSlug = new Set(
    docs.filter(d => d.slug && d.slug !== 'undefined').map(d => normalizeArtist(d.artist))
  );

  console.log('Artist SEO count check');
  console.log('----------------------');
  console.log(`Total artistSeo docs: ${total}`);
  console.log(`Docs with valid slug: ${withSlug}`);
  console.log(`Docs missing/undefined slug: ${withoutSlug}`);
  console.log(`Unique normalized artists: ${artists.size}`);
  console.log(`Unique artists with valid slug: ${artistsWithGoodSlug.size}`);

  const bad = docs.find(d => !d.slug || d.slug === 'undefined');

  const legacy = docs.find(d => d.artist === '.38 Special -');
const current = docs.find(d => d.slug === '38-special');

console.log('\n=== LEGACY DOCUMENT ===\n');
console.log(JSON.stringify(legacy, null, 2));

console.log('\n=== CURRENT DOCUMENT ===\n');
console.log(JSON.stringify(current, null, 2));

  await client.close();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
