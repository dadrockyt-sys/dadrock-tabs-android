import { randomUUID } from 'node:crypto';
import { NextResponse } from 'next/server';

import {
  BTS_CURRENCY,
  BTS_PAYPAL_BASE_URL,
  BTS_PRICE,
  BTS_REMOVAL_MODES,
  cleanBtsText,
  createBtsJobToken,
  createBtsPurchaseFingerprint,
  getBtsPayPalAccessToken,
  isValidBtsEmail,
  isValidBtsPathname,
} from '@/lib/btsPayment';

export const runtime = 'nodejs';

export async function POST(request) {
  try {
    const body = await request.json();

    const orderId = cleanBtsText(
      body?.orderId,
      80
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

    if (!orderId || !/^[A-Z0-9]+$/i.test(orderId)) {
      return NextResponse.json(
        { error: 'Invalid PayPal order ID.' },
        { status: 400 }
      );
    }

    if (!isValidBtsEmail(customerEmail)) {
      return NextResponse.json(
        { error: 'A valid email address is required.' },
        { status: 400 }
      );
    }

    if (!BTS_REMOVAL_MODES.includes(removalMode)) {
      return NextResponse.json(
        { error: 'A valid BTS removal mode is required.' },
        { status: 400 }
      );
    }

    if (!isValidBtsPathname(pathname)) {
      return NextResponse.json(
        { error: 'A valid BTS audio upload is required.' },
        { status: 400 }
      );
    }

    const accessToken =
      await getBtsPayPalAccessToken();

    const response = await fetch(
      `${BTS_PAYPAL_BASE_URL}/v2/checkout/orders/${orderId}/capture`,
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
        'BTS PayPal capture-order error:',
        data
      );

      return NextResponse.json(
        { error: 'Unable to capture the BTS PayPal payment.' },
        { status: response.status || 500 }
      );
    }

    const purchaseUnit = data.purchase_units?.[0];
    const capture =
      purchaseUnit?.payments?.captures?.[0];

    const expectedFingerprint =
      createBtsPurchaseFingerprint({
        customerEmail,
        removalMode,
        pathname,
      });

    const expectedCustomId =
      `bts-${expectedFingerprint}`;

    const paymentIsValid =
      data.status === 'COMPLETED' &&
      capture?.status === 'COMPLETED' &&
      capture?.amount?.currency_code === BTS_CURRENCY &&
      capture?.amount?.value === BTS_PRICE &&
      purchaseUnit?.custom_id === expectedCustomId;

    if (!paymentIsValid) {
      console.error(
        'BTS PayPal payment verification failed:',
        {
          orderId,
          orderStatus: data.status,
          captureStatus: capture?.status,
          amount: capture?.amount,
          customId: purchaseUnit?.custom_id,
        }
      );

      return NextResponse.json(
        { error: 'BTS payment could not be verified.' },
        { status: 400 }
      );
    }

    const jobToken = createBtsJobToken({
      orderId: data.id,
      customerEmail,
      removalMode,
      pathname,
    });

    return NextResponse.json({
      success: true,
      orderId: data.id,
      captureId: capture.id,
      status: capture.status,
      removalMode,
      jobToken,
      environment: 'live',
    });
  } catch (error) {
    console.error(
      'BTS PayPal capture-order route error:',
      error
    );

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to capture the BTS PayPal payment.',
      },
      { status: 500 }
    );
  }
}
