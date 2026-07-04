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

  const docsByArtist = new Map();

  for (const doc of docs) {
    const key = normalizeArtist(doc.artist);
    if (!docsByArtist.has(key)) docsByArtist.set(key, []);
    docsByArtist.get(key).push(doc);
  }

  const toDelete = [];

  for (const legacy of docs) {
    const artistKey = normalizeArtist(legacy.artist);

    if (!artistKey.endsWith('-')) continue;
    if (legacy.slug && legacy.slug !== 'undefined') continue;

    const cleanedArtist = artistKey.replace(/\s*-\s*$/, '');
    const modernMatches = docsByArtist.get(cleanedArtist) || [];

    const hasModernSluggedMatch = modernMatches.some(
      d => d.slug && d.slug !== 'undefined'
    );

    if (hasModernSluggedMatch) {
      toDelete.push(legacy);
    }
  }

  console.log(`Confirmed duplicates to delete: ${toDelete.length}`);

  for (const doc of toDelete) {
    console.log(`DELETE artist="${doc.artist}" slug="${doc.slug}" id=${doc._id}`);
  }

  if (process.env.DRY_RUN !== 'false') {
    console.log('\nDRY RUN ONLY. Nothing was deleted.');
    console.log('To actually delete, run with DRY_RUN=false.');
    await client.close();
    return;
  }

  const ids = toDelete.map(d => d._id);
  const result = await col.deleteMany({ _id: { $in: ids } });

console.log(`\nDeleted ${result.deletedCount} confirmed duplicate records.`);

const remaining = await col.countDocuments();

console.log(`Documents remaining: ${remaining}`);

await client.close();
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
