#!/usr/bin/env node
/**
 * Batch SEO Content Generator
 * Runs batch_artists and batch_songs sequentially until all are done.
 */

const BASE_URL = 'http://localhost:3000';
const AUTH = 'Basic ' + Buffer.from('admin:Babyty99').toString('base64');
const BATCH_SIZE = 20;
const DELAY_BETWEEN_BATCHES_MS = 2000; // 2 second pause between batches

async function callBatch(action) {
  const res = await fetch(`${BASE_URL}/api/admin/generate-seo`, {
    method: 'POST',
    headers: {
      'Authorization': AUTH,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ action, batch_size: BATCH_SIZE }),
  });
  return res.json();
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function processAll(action, label) {
  let totalProcessed = 0;
  let batchNum = 0;
  let remaining = Infinity;

  console.log(`\n${'='.repeat(60)}`);
  console.log(`Starting ${label} generation...`);
  console.log(`${'='.repeat(60)}`);

  while (remaining > 0) {
    batchNum++;
    const startTime = Date.now();
    
    try {
      const result = await callBatch(action);
      
      if (!result.success) {
        console.error(`Batch ${batchNum} ERROR:`, result.error);
        // Wait longer on error, then retry
        await sleep(5000);
        continue;
      }

      const succeeded = result.results.filter(r => r.status === 'success').length;
      const failed = result.results.filter(r => r.status === 'error');
      totalProcessed += succeeded;
      remaining = result.remaining;
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);

      console.log(`[Batch ${batchNum}] ✅ ${succeeded} ${label} processed in ${elapsed}s | Remaining: ${remaining}`);
      
      if (failed.length > 0) {
        for (const f of failed) {
          console.log(`  ❌ Failed: ${f.artist || f.song} — ${f.error}`);
        }
      }

      // Show some names
      const names = result.results
        .filter(r => r.status === 'success')
        .map(r => r.artist || r.song)
        .join(', ');
      console.log(`  → ${names}`);

      if (result.processed === 0) {
        console.log('No more items to process.');
        break;
      }

      // Pause between batches to avoid rate limits
      if (remaining > 0) {
        await sleep(DELAY_BETWEEN_BATCHES_MS);
      }
    } catch (err) {
      console.error(`Batch ${batchNum} NETWORK ERROR:`, err.message);
      await sleep(5000);
    }
  }

  console.log(`\n✅ ${label} complete! Total processed: ${totalProcessed}`);
  return totalProcessed;
}

async function main() {
  console.log('🎸 DadRock Tabs — AI SEO Content Batch Generator');
  console.log(`Started at: ${new Date().toISOString()}`);

  // First: artists
  const artistCount = await processAll('batch_artists', 'artists');

  // Then: songs
  const songCount = await processAll('batch_songs', 'songs');

  console.log(`\n${'='.repeat(60)}`);
  console.log(`🎉 ALL DONE!`);
  console.log(`Artists generated: ${artistCount}`);
  console.log(`Songs generated: ${songCount}`);
  console.log(`Finished at: ${new Date().toISOString()}`);
  console.log(`${'='.repeat(60)}`);
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
