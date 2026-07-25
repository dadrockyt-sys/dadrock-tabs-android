import { createHash, randomUUID } from 'node:crypto';
import { NextResponse } from 'next/server';

export const runtime = 'nodejs';

const PRICE = '2.99';
const CURRENCY = 'USD';

const ALLOWED_TRANSCRIPTION_TYPES = [
  'lead',
  'rhythm',
  'bass',
];

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
  const clientId =
    process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID;

  const clientSecret =
    process.env.PAYPAL_CLIENT_SECRET;

  if (!clientId || !clientSecret) {
    throw new Error(
      'PayPal credentials are not configured.'
    );
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

    const orderId = cleanText(body?.orderId, 40);
    const song = cleanText(body?.song, 120);
    const artist = cleanText(body?.artist, 120);

    const transcriptionType = cleanText(
      body?.transcriptionType,
      40
    ).toLowerCase();

    if (
      !orderId ||
      !song ||
      !artist ||
      !transcriptionType
    ) {
      return NextResponse.json(
        {
          error:
            'Order ID, song, artist, and transcription type are required.',
        },
        { status: 400 }
      );
    }

    if (!/^[A-Z0-9]+$/i.test(orderId)) {
      return NextResponse.json(
        {
          error: 'Invalid PayPal order ID.',
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

    const accessToken =
      await getPayPalAccessToken();

    const response = await fetch(
      `${PAYPAL_BASE_URL}/v2/checkout/orders/${orderId}/capture`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
          'PayPal-Request-Id': randomUUID(),
          Prefer: 'return=representation',
        },
        body: '{}',
        cache: 'no-store',
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.error(
        'PayPal capture-order error:',
        data
      );

      return NextResponse.json(
        {
          error: 'Unable to capture PayPal payment.',
        },
        {
          status: response.status || 500,
        }
      );
    }

    const purchaseUnit = data.purchase_units?.[0];

    const capture =
      purchaseUnit?.payments?.captures?.[0];

    const expectedFingerprint =
      createPurchaseFingerprint({
        song,
        artist,
        transcriptionType,
      });

    const expectedCustomId =
      `drt-${expectedFingerprint}`;

    const paymentIsValid =
      data.status === 'COMPLETED' &&
      capture?.status === 'COMPLETED' &&
      capture?.amount?.currency_code === CURRENCY &&
      capture?.amount?.value === PRICE &&
      purchaseUnit?.custom_id === expectedCustomId;

    if (!paymentIsValid) {
      console.error(
        'PayPal payment verification failed:',
        {
          orderId,
          orderStatus: data.status,
          captureStatus: capture?.status,
          amount: capture?.amount,
          customId: purchaseUnit?.custom_id,
        }
      );

      return NextResponse.json(
        {
          error:
            'Payment could not be verified.',
        },
        { status: 400 }
      );
    }

    return NextResponse.json({
      success: true,
      orderId: data.id,
      captureId: capture.id,
      status: capture.status,
      song,
      artist,
      transcriptionType,
    });
  } catch (error) {
    console.error(
      'PayPal capture-order route error:',
      error
    );

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to capture PayPal payment.',
      },
      { status: 500 }
    );
  }
}
