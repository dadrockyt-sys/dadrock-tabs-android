import { del, list } from '@vercel/blob';
import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const maxDuration = 60;

const BTS_AUDIO_PREFIX = 'bts-audio/';
const MAX_RETENTION_MS = 24 * 60 * 60 * 1000;
const PAGE_SIZE = 1000;
const MAX_PAGES_PER_RUN = 10;

function isAuthorizedCron(request) {
  const cronSecret = process.env.CRON_SECRET;

  if (!cronSecret) {
    return false;
  }

  return (
    request.headers.get('authorization') ===
    `Bearer ${cronSecret}`
  );
}

export async function GET(request) {
  if (!isAuthorizedCron(request)) {
    return NextResponse.json(
      { error: 'Unauthorized BTS cleanup request.' },
      { status: 401 }
    );
  }

  const blobToken = process.env.BLOB_READ_WRITE_TOKEN;

  if (!blobToken) {
    return NextResponse.json(
      { error: 'BTS Blob cleanup is not configured.' },
      { status: 503 }
    );
  }

  const cutoff = Date.now() - MAX_RETENTION_MS;
  const expiredUrls = [];
  let cursor;
  let pagesScanned = 0;
  let blobsScanned = 0;

  try {
    do {
      const page = await list({
        token: blobToken,
        prefix: BTS_AUDIO_PREFIX,
        cursor,
        limit: PAGE_SIZE,
      });

      pagesScanned += 1;
      blobsScanned += page.blobs.length;

      for (const blob of page.blobs) {
        const uploadedAt = new Date(
          blob.uploadedAt
        ).getTime();

        if (
          Number.isFinite(uploadedAt) &&
          uploadedAt <= cutoff
        ) {
          expiredUrls.push(blob.url);
        }
      }

      cursor = page.hasMore
        ? page.cursor
        : undefined;
    } while (
      cursor &&
      pagesScanned < MAX_PAGES_PER_RUN
    );

    if (expiredUrls.length > 0) {
      await del(expiredUrls, {
        token: blobToken,
      });
    }

    return NextResponse.json({
      success: true,
      retentionHours: 24,
      pagesScanned,
      blobsScanned,
      deleted: expiredUrls.length,
      morePagesRemaining: Boolean(cursor),
    });
  } catch (error) {
    console.error('BTS 24-hour cleanup failed:', error);

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to clean up expired BTS audio.',
      },
      { status: 500 }
    );
  }
}
