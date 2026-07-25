import { createHash, randomUUID } from 'node:crypto';
import { NextResponse } from 'next/server';

export const runtime = 'nodejs';

const PRICE = '2.99';
const CURRENCY = 'USD';

const ALLOWED_TRANSCRIPTION_TYPES = ['lead', 'rhythm', 'bass'];

const PAYPAL_BASE_URL =
  process.env.PAYPAL_MODE === 'live'
    ? 'https://api-m.paypal.com'
    : 'https://api-m.sandbox.paypal.com';

function cleanText(value, maximumLength) {
  return String(value || '')
    .trim()
    .replace(/\s+/g, ' ')
    .slice(0, maximumLength);
}

function createPurchaseFingerprint({
  song,
  artist,
  transcriptionType,
}) {
  const purchaseData = [
    song.toLowerCase(),
    artist.toLowerCase(),
    transcriptionType.toLowerCase(),
    PRICE,
    CURRENCY,
  ].join('|');

  return createHash('sha256')
    .update(purchaseData)
    .digest('hex');
}

async function getPayPalAccessToken() {
  const clientId = process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID;
  const clientSecret = process.env.PAYPAL_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    throw new Error('PayPal credentials are not configured.');
  }

  const credentials = Buffer.from(
    `${clientId}:${clientSecret}`
  ).toString('base64');

  const response = await fetch(
    `${PAYPAL_BASE_URL}/v1/oauth2/token`,
    {
      method: 'POST',
      headers: {
        Authorization: `Basic ${credentials}`,
        'Content-Type':
          'application/x-www-form-urlencoded',
      },
      body: 'grant_type=client_credentials',
      cache: 'no-store',
    }
  );

  const data = await response.json();

  if (!response.ok || !data.access_token) {
    console.error('PayPal token error:', data);

    throw new Error(
      'Unable to authenticate with PayPal.'
    );
  }

  return data.access_token;
}

export async function POST(request) {
  try {
    const body = await request.json();

    const song = cleanText(body?.song, 120);
    const artist = cleanText(body?.artist, 120);
    const transcriptionType = cleanText(
      body?.transcriptionType,
      40
    ).toLowerCase();

    if (!song || !artist || !transcriptionType) {
      return NextResponse.json(
        {
          error:
            'Song, artist, and transcription type are required.',
        },
        { status: 400 }
      );
    }

    if (
      !ALLOWED_TRANSCRIPTION_TYPES.includes(
        transcriptionType
      )
    ) {
      return NextResponse.json(
        {
          error:
            'Transcription type must be lead, rhythm, or bass.',
        },
        { status: 400 }
      );
    }

    const accessToken = await getPayPalAccessToken();

    const fingerprint = createPurchaseFingerprint({
      song,
      artist,
      transcriptionType,
    });

    const description =
      `${song} by ${artist} — ` +
      `${transcriptionType} AI Tab PDF`;

    const response = await fetch(
      `${PAYPAL_BASE_URL}/v2/checkout/orders`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',

          /*
           * PayPal uses this value to help prevent
           * accidental duplicate POST operations.
           */
          'PayPal-Request-Id': randomUUID(),
        },
        body: JSON.stringify({
          intent: 'CAPTURE',

          purchase_units: [
            {
              reference_id: 'dadrock-ai-tab',

              /*
               * Stored inside the PayPal order.
               * We will verify this after capture.
               */
              custom_id: `drt-${fingerprint}`,

              description: description.slice(0, 127),

              amount: {
                currency_code: CURRENCY,
                value: PRICE,
              },
            },
          ],

          application_context: {
            shipping_preference: 'NO_SHIPPING',
            user_action: 'PAY_NOW',
          },
        }),
        cache: 'no-store',
      }
    );

    const data = await response.json();

    if (!response.ok || !data.id) {
      console.error(
        'PayPal create-order error:',
        data
      );

      return NextResponse.json(
        {
          error: 'Unable to create PayPal order.',
        },
        {
          status: response.status || 500,
        }
      );
    }

    return NextResponse.json({
      orderId: data.id,
    });
  } catch (error) {
    console.error(
      'PayPal create-order route error:',
      error
    );

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to create PayPal order.',
      },
      { status: 500 }
    );
  }
}
