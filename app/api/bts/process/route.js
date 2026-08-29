import { del, head } from '@vercel/blob';
import { NextResponse } from 'next/server';

import {
  BTS_REMOVAL_MODES,
  cleanBtsText,
  isValidBtsEmail,
  isValidBtsPathname,
  verifyBtsJobToken,
} from '@/lib/btsPayment';

export const runtime = 'nodejs';
export const maxDuration = 600;

function safeDownloadName(originalFilename, removalMode) {
  const base = cleanBtsText(originalFilename, 120)
    .replace(/\.[^/.]+$/, '')
    .replace(/[^a-zA-Z0-9._-]+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^[-_.]+|[-_.]+$/g, '');

  const suffix =
    removalMode === 'guitar-bass'
      ? 'no-guitars-no-bass'
      : removalMode === 'guitar'
        ? 'no-guitars'
        : 'no-bass';

  return `${base || 'dadrock-backing-track'}-${suffix}.mp3`;
}

export async function POST(request) {
  let resolvedAudioUrl = '';
  let blobToken = '';

  try {
    const body = await request.json();

    const orderId = cleanBtsText(
      body?.orderId,
      80
    );

    const jobToken = cleanBtsText(
      body?.jobToken,
      4000
    );

    const customerEmail = cleanBtsText(
      body?.customerEmail,
      254
    ).toLowerCase();

    const removalMode = cleanBtsText(
      body?.removalMode,
      40
    ).toLowerCase();

    const pathname = cleanBtsText(
      body?.pathname,
      500
    );

    const originalFilename = cleanBtsText(
      body?.originalFilename,
      160
    );

    if (
      !orderId ||
      !jobToken ||
      !isValidBtsEmail(customerEmail) ||
      !BTS_REMOVAL_MODES.includes(removalMode) ||
      !isValidBtsPathname(pathname)
    ) {
      return NextResponse.json(
        {
          error:
            'A verified BTS payment and uploaded audio are required.',
        },
        { status: 400 }
      );
    }

    const jobIsAuthorized = verifyBtsJobToken(
      jobToken,
      {
        orderId,
        customerEmail,
        removalMode,
        pathname,
      }
    );

    if (!jobIsAuthorized) {
      return NextResponse.json(
        {
          error:
            'This BTS processing authorization is invalid or expired.',
        },
        { status: 403 }
      );
    }

    const separatorUrl =
      process.env.BTS_SEPARATOR_API_URL;

    const separatorToken =
      process.env.BTS_SEPARATOR_API_TOKEN;

    blobToken =
      process.env.BLOB_READ_WRITE_TOKEN || '';

    if (
      !separatorUrl ||
      !separatorToken ||
      !blobToken
    ) {
      console.error(
        'BTS separator configuration missing:',
        {
          hasSeparatorUrl: Boolean(separatorUrl),
          hasSeparatorToken: Boolean(separatorToken),
          hasBlobToken: Boolean(blobToken),
        }
      );

      return NextResponse.json(
        {
          error:
            'Backing Track Studio processing is not configured yet.',
        },
        { status: 503 }
      );
    }

    let blobMetadata;

    try {
      blobMetadata = await head(pathname, {
        token: blobToken,
      });
    } catch (error) {
      console.error(
        'BTS private upload lookup failed:',
        error
      );

      return NextResponse.json(
        {
          error:
            'The uploaded BTS audio could not be found.',
        },
        { status: 404 }
      );
    }

    resolvedAudioUrl = String(
      blobMetadata?.url || ''
    );

    if (!resolvedAudioUrl.startsWith('https://')) {
      return NextResponse.json(
        {
          error:
            'The uploaded BTS audio could not be resolved.',
        },
        { status: 404 }
      );
    }

    const separatorResponse = await fetch(
      separatorUrl,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: separatorToken,
          blobToken,
          audioUrl: resolvedAudioUrl,
          pathname,
          removalMode,
        }),
        cache: 'no-store',
      }
    );

    if (!separatorResponse.ok) {
      const contentType =
        separatorResponse.headers.get(
          'content-type'
        ) || '';

      let detail = '';

      if (contentType.includes('application/json')) {
        const data = await separatorResponse
          .json()
          .catch(() => ({}));

        detail = String(
          data?.detail ||
          data?.error ||
          ''
        );
      } else {
        detail = await separatorResponse
          .text()
          .catch(() => '');
      }

      console.error(
        'BTS Modal separator error:',
        {
          status: separatorResponse.status,
          removalMode,
          detail,
        }
      );

      return NextResponse.json(
        {
          error:
            detail ||
            'The backing track could not be generated.',
        },
        {
          status: separatorResponse.status,
        }
      );
    }

    const returnedContentType =
      separatorResponse.headers.get(
        'content-type'
      ) || '';

    if (
      !returnedContentType.startsWith('audio/') ||
      !separatorResponse.body
    ) {
      return NextResponse.json(
        {
          error:
            'The BTS separator did not return an audio track.',
        },
        { status: 502 }
      );
    }

    return new Response(separatorResponse.body, {
      status: 200,
      headers: {
        'Content-Type': returnedContentType,
        'Content-Disposition':
          `attachment; filename="${safeDownloadName(
            originalFilename,
            removalMode
          )}"`,
        'Cache-Control':
          'private, no-store, max-age=0',
        'X-Content-Type-Options': 'nosniff',
        'X-BTS-Removal-Mode': removalMode,
      },
    });
  } catch (error) {
    console.error(
      'BTS process route error:',
      error
    );

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to generate the backing track.',
      },
      { status: 500 }
    );
  } finally {
    if (resolvedAudioUrl && blobToken) {
      try {
        await del(resolvedAudioUrl, {
          token: blobToken,
        });
      } catch (cleanupError) {
        console.warn(
          'BTS temporary upload cleanup failed:',
          cleanupError
        );
      }
    }
  }
}
