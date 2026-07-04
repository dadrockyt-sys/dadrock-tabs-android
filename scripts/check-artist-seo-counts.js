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

console.log('\nOne complete legacy document:\n');

if (bad) {
  console.log(JSON.stringify(bad, null, 2));
} else {
  console.log('No legacy documents found.');
}

  await client.close();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
