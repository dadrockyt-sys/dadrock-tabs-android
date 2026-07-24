import { NextResponse } from 'next/server';

export const runtime = 'nodejs';

const PAYPAL_BASE_URL =
  process.env.PAYPAL_MODE === 'live'
    ? 'https://api-m.paypal.com'
    : 'https://api-m.sandbox.paypal.com';

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
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: 'grant_type=client_credentials',
      cache: 'no-store',
    }
  );

  const data = await response.json();

  if (!response.ok || !data.access_token) {
    console.error('PayPal token error:', data);
    throw new Error('Unable to authenticate with PayPal.');
  }

  return data.access_token;
}

export async function POST(request) {
  try {
    const body = await request.json();
    const song = String(body?.song || 'Selected Song').slice(0, 120);
    const artist = String(body?.artist || 'Unknown Artist').slice(0, 120);
    const transcriptionType = String(
      body?.transcriptionType || 'guitar'
    ).slice(0, 40);

    const accessToken = await getPayPalAccessToken();

    const response = await fetch(
      `${PAYPAL_BASE_URL}/v2/checkout/orders`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
          'PayPal-Request-Id': crypto.randomUUID(),
        },
        body: JSON.stringify({
          intent: 'CAPTURE',
          purchase_units: [
            {
              reference_id: 'dadrock-ai-tab',
              description: `${song} by ${artist} — ${transcriptionType} AI Tab PDF`.slice(
                0,
                127
              ),
              amount: {
                currency_code: 'USD',
                value: '2.99',
              },
            },
          ],
        }),
        cache: 'no-store',
      }
    );

    const data = await response.json();

    if (!response.ok || !data.id) {
      console.error('PayPal create-order error:', data);

      return NextResponse.json(
        {
          error: 'Unable to create PayPal order.',
          details: data,
        },
        { status: response.status || 500 }
      );
    }

    return NextResponse.json({
      orderId: data.id,
    });
  } catch (error) {
    console.error('PayPal create-order route error:', error);

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
