import { handleUpload } from '@vercel/blob/client';
import { NextResponse } from 'next/server';

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
            'Invalid audio upload information.'
          );
        }

        if (!payload.copyrightConfirmed) {
          throw new Error(
            'Copyright confirmation is required.'
          );
        }

        if (
          !['lead', 'rhythm', 'bass'].includes(
            payload.transcriptionType
          )
        ) {
          throw new Error(
            'Please select a valid instrument part.'
          );
        }

        return {
          // The browser uploads directly to Blob, so do not impose the old
          // 50 MB application ceiling here. Vercel Blob/platform limits remain
          // authoritative and are surfaced by the upload SDK.
          allowedContentTypes: ALLOWED_AUDIO_TYPES,
          addRandomSuffix: true,

          tokenPayload: JSON.stringify({
            song: String(payload.song || '')
              .trim()
              .slice(0, 120),

            artist: String(payload.artist || '')
              .trim()
              .slice(0, 120),

            transcriptionType:
              payload.transcriptionType,
          }),
        };
      },

      onUploadCompleted: async ({
        blob,
        tokenPayload,
      }) => {
        console.log('Audio upload completed:', {
          pathname: blob.pathname,
          tokenPayload,
        });
      },
    });

    return NextResponse.json(response);
  } catch (error) {
    console.error(
      'Audio upload authorization error:',
      error
    );

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to authorize the audio upload.',
      },
      { status: 400 }
    );
  }
}
