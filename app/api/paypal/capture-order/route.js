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
    const orderId = String(body?.orderId || '').trim();

    if (!orderId) {
      return NextResponse.json(
        { error: 'PayPal order ID is required.' },
        { status: 400 }
      );
    }

    const accessToken = await getPayPalAccessToken();

    const response = await fetch(
      `${PAYPAL_BASE_URL}/v2/checkout/orders/${encodeURIComponent(
        orderId
      )}/capture`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
          'PayPal-Request-Id': crypto.randomUUID(),
        },
        body: JSON.stringify({}),
        cache: 'no-store',
      }
    );

    const data = await response.json();

    if (!response.ok) {
      console.error('PayPal capture-order error:', data);

      return NextResponse.json(
        {
          error: 'Unable to capture PayPal payment.',
          details: data,
        },
        { status: response.status || 500 }
      );
    }

    const capturedAmount =
      data?.purchase_units?.[0]?.payments?.captures?.[0]?.amount;

    const isCompleted =
      data?.status === 'COMPLETED' &&
      capturedAmount?.currency_code === 'USD' &&
      capturedAmount?.value === '2.99';

    if (!isCompleted) {
      console.error('Unexpected PayPal capture result:', data);

      return NextResponse.json(
        { error: 'Payment was not completed for the expected amount.' },
        { status: 400 }
      );
    }

    return NextResponse.json({
      success: true,
      orderId: data.id,
      status: data.status,
      payerName: data?.payer?.name?.given_name || '',
    });
  } catch (error) {
    console.error('PayPal capture-order route error:', error);

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
