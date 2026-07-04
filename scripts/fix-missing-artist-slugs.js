#!/usr/bin/env node

const { MongoClient } = require('mongodb');
const { artistToSlug } = require('../lib/slugify');

const MONGO_URL = process.env.MONGO_URL;
const DB_NAME = process.env.DB_NAME || 'dadrock_tabs';

async function main() {
  const client = new MongoClient(MONGO_URL);
  await client.connect();

  const db = client.db(DB_NAME);
  const col = db.collection('artist_seo_content');

  const docs = await col.find({
    $or: [
      { slug: { $exists: false } },
      { slug: null },
      { slug: "" }
    ]
  }).toArray();

  console.log(`Found ${docs.length} artist records missing slugs`);

  for (const doc of docs) {
    if (!doc.artist) continue;

    const slug = artistToSlug(doc.artist);

    await col.updateOne(
      { _id: doc._id },
      { $set: { slug } }
    );

    console.log(`${doc.artist} -> ${slug}`);
  }

  console.log("Done.");
  await client.close();
}

main().catch(console.error);
