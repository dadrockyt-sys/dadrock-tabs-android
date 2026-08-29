import { handleUpload } from '@vercel/blob/client';
import { NextResponse } from 'next/server';

import {
  BTS_REMOVAL_MODES,
  isValidBtsEmail,
} from '@/lib/btsPayment';

export const runtime = 'nodejs';

const ALLOWED_AUDIO_TYPES = [
  'audio/mpeg',
  'audio/mp3',
  'audio/wav',
  'audio/x-wav',
  'audio/mp4',
  'audio/m4a',
  'audio/x-m4a',
  'audio/aac',
];

export async function POST(request) {
  try {
    const body = await request.json();

    const response = await handleUpload({
      body,
      request,

      onBeforeGenerateToken: async (
        pathname,
        clientPayload
      ) => {
        let payload = {};

        try {
          payload = clientPayload
            ? JSON.parse(clientPayload)
            : {};
        } catch {
          throw new Error(
            'Invalid BTS upload information.'
          );
        }

        const removalMode = String(
          payload.removalMode || ''
        )
          .trim()
          .toLowerCase();

        const customerEmail = String(
          payload.customerEmail || ''
        ).trim();

        if (!pathname.startsWith('bts-audio/')) {
          throw new Error(
            'Invalid BTS upload pathname.'
          );
        }

        if (!payload.copyrightConfirmed) {
          throw new Error(
            'Copyright confirmation is required.'
          );
        }

        if (
          !BTS_REMOVAL_MODES.includes(
            removalMode
          )
        ) {
          throw new Error(
            'Please select a valid BTS removal mode.'
          );
        }

        if (!isValidBtsEmail(customerEmail)) {
          throw new Error(
            'Please enter a valid email address.'
          );
        }

        return {
          allowedContentTypes: ALLOWED_AUDIO_TYPES,
          maximumSizeInBytes: 50 * 1024 * 1024,
          addRandomSuffix: true,

          tokenPayload: JSON.stringify({
            product: 'backing-track-studio',
            removalMode,
            customerEmail:
              customerEmail.toLowerCase(),
          }),
        };
      },

      onUploadCompleted: async ({
        blob,
        tokenPayload,
      }) => {
        console.log('BTS audio upload completed:', {
          pathname: blob.pathname,
          tokenPayload,
        });
      },
    });

    return NextResponse.json(response);
  } catch (error) {
    console.error(
      'BTS audio upload authorization error:',
      error
    );

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to authorize the BTS audio upload.',
      },
      { status: 400 }
    );
  }
}
