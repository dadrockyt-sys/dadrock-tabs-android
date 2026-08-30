import { randomUUID } from 'node:crypto';
import { NextResponse } from 'next/server';

import {
  BTS_CURRENCY,
  BTS_PAYPAL_BASE_URL,
  BTS_PRICE,
  BTS_REMOVAL_MODES,
  cleanBtsText,
  createBtsPurchaseFingerprint,
  getBtsPayPalAccessToken,
  isValidBtsEmail,
  isValidBtsPathname,
} from '@/lib/btsPayment';

export const runtime = 'nodejs';

const REMOVAL_LABELS = {
  guitar: 'Remove Guitars',
  bass: 'Remove Bass',
  'guitar-bass': 'Remove Guitars + Bass',
};

export async function POST(request) {
  try {
    const body = await request.json();

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

    if (!isValidBtsEmail(customerEmail)) {
      return NextResponse.json(
        {
          error: 'A valid email address is required.',
        },
        { status: 400 }
      );
    }

    if (!BTS_REMOVAL_MODES.includes(removalMode)) {
      return NextResponse.json(
        {
          error: 'A valid BTS removal mode is required.',
        },
        { status: 400 }
      );
    }

    if (!isValidBtsPathname(pathname)) {
      return NextResponse.json(
        {
          error: 'A valid BTS audio upload is required.',
        },
        { status: 400 }
      );
    }

    const accessToken =
      await getBtsPayPalAccessToken();

    const fingerprint =
      createBtsPurchaseFingerprint({
        customerEmail,
        removalMode,
        pathname,
      });

    const description =
      `DadRock Backing Track Studio — ` +
      `${REMOVAL_LABELS[removalMode]}`;

    const response = await fetch(
      `${BTS_PAYPAL_BASE_URL}/v2/checkout/orders`,
      {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
          'PayPal-Request-Id': randomUUID(),
        },
        body: JSON.stringify({
          intent: 'CAPTURE',
          purchase_units: [
            {
              reference_id: 'dadrock-bts',
              custom_id: `bts-${fingerprint}`,
              description: description.slice(0, 127),
              amount: {
                currency_code: BTS_CURRENCY,
                value: BTS_PRICE,
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
        'BTS PayPal create-order error:',
        data
      );

      return NextResponse.json(
        {
          error: 'Unable to create the BTS PayPal order.',
        },
        { status: response.status || 500 }
      );
    }

    return NextResponse.json({
      orderId: data.id,
      price: BTS_PRICE,
      currency: BTS_CURRENCY,
      environment: 'live',
    });
  } catch (error) {
    console.error(
      'BTS PayPal create-order route error:',
      error
    );

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to create the BTS PayPal order.',
      },
      { status: 500 }
    );
  }
}
