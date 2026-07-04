#!/usr/bin/env node

const { MongoClient } = require('mongodb');

const MONGO_URL = process.env.MONGO_URL || 'mongodb://localhost:27017';
const DB_NAME = process.env.DB_NAME || 'dadrock_tabs';

function normalize(value) {
  return String(value || '').trim().toLowerCase();
}

async function main() {
  const client = await MongoClient.connect(MONGO_URL);
  const db = client.db(DB_NAME);

  const docs = await db.collection('artist_seo_content').find({}).toArray();

  const byArtist = new Map();
  const bySlug = new Map();

  for (const doc of docs) {
    const artist = normalize(doc.artist);
    const slug = normalize(doc.slug);

    if (!byArtist.has(artist)) byArtist.set(artist, []);
    byArtist.get(artist).push(doc);

    if (!bySlug.has(slug)) bySlug.set(slug, []);
    bySlug.get(slug).push(doc);
  }

  console.log(`Total documents: ${docs.length}`);
  console.log(`Unique artist names: ${byArtist.size}`);
  console.log(`Unique slugs: ${bySlug.size}`);

  console.log('\nDuplicate artist names:');
  for (const [artist, items] of byArtist.entries()) {
    if (items.length > 1) {
      console.log(`\n${artist} (${items.length})`);
      for (const item of items) {
        console.log(`  artist="${item.artist}" slug="${item.slug}" id=${item._id}`);
      }
    }
  }

  console.log('\nDuplicate slugs:');
  for (const [slug, items] of bySlug.entries()) {
    if (items.length > 1) {
      console.log(`\n${slug} (${items.length})`);
      for (const item of items) {
        console.log(`  artist="${item.artist}" slug="${item.slug}" id=${item._id}`);
      }
    }
  }

  await client.close();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
