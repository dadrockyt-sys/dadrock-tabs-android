import { del } from '@vercel/blob';
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

function safeDownloadName(removalMode) {
  const suffix =
    removalMode === 'guitar-bass'
      ? 'no-guitars-no-bass'
      : removalMode === 'guitar'
        ? 'no-guitars'
        : 'no-bass';

  return `dadrock-backing-track-${suffix}.mp3`;
}

export async function POST(request) {
  let audioUrl = '';
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

    audioUrl = cleanBtsText(
      body?.audioUrl,
      2000
    );

    const pathname = cleanBtsText(
      body?.pathname,
      500
    );

    if (
      !orderId ||
      !jobToken ||
      !isValidBtsEmail(customerEmail) ||
      !BTS_REMOVAL_MODES.includes(removalMode) ||
      !isValidBtsPathname(pathname) ||
      !audioUrl.startsWith('https://')
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
          audioUrl,
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

    if (!returnedContentType.startsWith('audio/')) {
      return NextResponse.json(
        {
          error:
            'The BTS separator did not return an audio track.',
        },
        { status: 502 }
      );
    }

    const trackBytes =
      await separatorResponse.arrayBuffer();

    if (!trackBytes.byteLength) {
      return NextResponse.json(
        {
          error:
            'The BTS separator returned an empty audio track.',
        },
        { status: 502 }
      );
    }

    return new Response(trackBytes, {
      status: 200,
      headers: {
        'Content-Type': returnedContentType,
        'Content-Disposition':
          `attachment; filename="${safeDownloadName(
            removalMode
          )}"`,
        'Cache-Control':
          'private, no-store, max-age=0',
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
    if (audioUrl && blobToken) {
      try {
        await del(audioUrl, {
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
