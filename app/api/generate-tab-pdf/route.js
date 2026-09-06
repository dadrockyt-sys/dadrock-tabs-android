import { createHash } from 'node:crypto';
import { resend } from '@/lib/resend';
import { createTabPdf } from '@/lib/createTabPdfPolished';
import { createJimmyPaigeProfessionalPdf } from '@/lib/createJimmyPaigeProfessionalPdf';
import { getJimmyPaigeProfessionalPdfFeatureState } from '@/lib/jimmyPaigeProfessionalPdfFeature';
import { getDb } from '@/lib/mongodb';
import { NextResponse } from 'next/server';
import {
  createSignedV143RhythmPdfDownload,
  isValidV143RhythmPdfArtifactId,
} from '@/lib/v143RhythmPdfArtifacts';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

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

function cleanTabText(value) {
  return String(value || '')
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .slice(0, 30000);
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

function createSafeFileName({
  song,
  artist,
  transcriptionType,
}) {
  const rawName = `${artist}-${song}-${transcriptionType}-tab`;
  const safeName = rawName
    .normalize('NFKD')
    .replace(/[^\w\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .toLowerCase()
    .slice(0, 100);

  return `${safeName || 'dadrock-ai-tab'}.pdf`;
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

async function verifyPayPalOrder({
  orderId,
  song,
  artist,
  transcriptionType,
}) {
  const accessToken = await getPayPalAccessToken();

  const response = await fetch(
    `${PAYPAL_BASE_URL}/v2/checkout/orders/${orderId}`,
    {
      method: 'GET',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      cache: 'no-store',
    }
  );

  const data = await response.json();

  if (!response.ok) {
    console.error('PayPal order verification error:', data);
    throw new Error('Unable to verify the PayPal order.');
  }

  const purchaseUnit = data.purchase_units?.[0];
  const capture = purchaseUnit?.payments?.captures?.[0];
  const expectedFingerprint = createPurchaseFingerprint({
    song,
    artist,
    transcriptionType,
  });
  const expectedCustomId = `drt-${expectedFingerprint}`;

  const paymentIsValid =
    data.status === 'COMPLETED' &&
    capture?.status === 'COMPLETED' &&
    capture?.amount?.currency_code === CURRENCY &&
    capture?.amount?.value === PRICE &&
    purchaseUnit?.custom_id === expectedCustomId;

  if (!paymentIsValid) {
    console.error('PDF payment verification failed:', {
      orderId,
      orderStatus: data.status,
      captureStatus: capture?.status,
      amount: capture?.amount,
      customId: purchaseUnit?.custom_id,
    });
    throw new Error('Payment could not be verified.');
  }
}

async function verifyFreeToken({
  tokenReference,
  customerEmail,
  song,
  artist,
  transcriptionType,
}) {
  const db = await getDb();
  const token = await db.collection('tab_tokens').findOne({
    code: tokenReference,
    $or: [
      { assignedEmail: null },
      { assignedEmail: { $exists: false } },
      { assignedEmail: customerEmail },
    ],
    redemptions: {
      $elemMatch: {
        customerEmail,
        songTitle: song,
        artistName: artist,
        transcriptionType,
      },
    },
  });

  if (!token) {
    throw new Error('Free token redemption could not be verified.');
  }
}

export async function POST(request) {
  try {
    const body = await request.json();

    const orderId = cleanText(body?.orderId, 40);
    const tokenReference = cleanText(body?.tokenReference, 100);
    const unlockMethod = cleanText(body?.unlockMethod, 20).toLowerCase();
    const song = cleanText(body?.song, 120);
    const artist = cleanText(body?.artist, 120);
    const transcriptionType = cleanText(
      body?.transcriptionType,
      40
    ).toLowerCase();
    const generatedTab = cleanTabText(body?.generatedTab);
    const pdfArtifactId = cleanText(body?.pdfArtifactId, 80);
    const customerEmail = cleanText(
      body?.customerEmail,
      254
    ).toLowerCase();
    const tuning =
      cleanText(body?.tuning, 80) || 'Standard Tuning';
    const tempo = Math.min(
      300,
      Math.max(20, Number(body?.tempo) || 120)
    );
    const timeSignature =
      cleanText(body?.timeSignature, 20) || '4/4';
    const keySignature = cleanText(body?.keySignature, 40);
    const analysisEngine = cleanText(body?.analysisEngine, 80);

    const emailIsValid =
      /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(customerEmail);

    if (
      (!orderId && !tokenReference) ||
      !song ||
      !artist ||
      !transcriptionType ||
      !generatedTab ||
      !customerEmail
    ) {
      return NextResponse.json(
        {
          error:
            'An unlock reference, song, artist, transcription type, tab, and customer email are required.',
        },
        { status: 400 }
      );
    }

    if (!emailIsValid) {
      return NextResponse.json(
        { error: 'Please provide a valid email address.' },
        { status: 400 }
      );
    }

    if (
      unlockMethod === 'paypal' &&
      !/^[A-Z0-9]+$/i.test(orderId)
    ) {
      return NextResponse.json(
        { error: 'Invalid PayPal order ID.' },
        { status: 400 }
      );
    }

    if (!['paypal', 'free-token'].includes(unlockMethod)) {
      return NextResponse.json(
        { error: 'Invalid PDF unlock method.' },
        { status: 400 }
      );
    }

    if (!ALLOWED_TRANSCRIPTION_TYPES.includes(transcriptionType)) {
      return NextResponse.json(
        {
          error:
            'Transcription type must be lead, rhythm, or bass.',
        },
        { status: 400 }
      );
    }

    if (unlockMethod === 'paypal') {
      await verifyPayPalOrder({
        orderId,
        song,
        artist,
        transcriptionType,
      });
    } else {
      await verifyFreeToken({
        tokenReference,
        customerEmail,
        song,
        artist,
        transcriptionType,
      });
    }

    if (
      transcriptionType === 'rhythm' &&
      pdfArtifactId
    ) {
      if (!isValidV143RhythmPdfArtifactId(pdfArtifactId)) {
        return NextResponse.json(
          { error: 'Invalid Rhythm PDF artifact reference.' },
          { status: 400 }
        );
      }

      const { downloadUrl, expiresAt } =
        await createSignedV143RhythmPdfDownload(pdfArtifactId);
      const fileName = createSafeFileName({
        song,
        artist,
        transcriptionType,
      });

      const emailResult = await resend.emails.send({
        from:
          process.env.RESEND_FROM_EMAIL ||
          'DadRock Tabs <onboarding@resend.dev>',
        to: customerEmail,
        subject: `${song} — ${transcriptionType} tab PDF`,
        html: `
          <h2>Your DadRock Tabs PDF is ready</h2>
          <p><strong>${song}</strong> by ${artist}</p>
          <p><a href="${downloadUrl}">Download your finished ${transcriptionType} tab PDF</a></p>
          <p>This private download link expires at ${expiresAt}.</p>
          <p>Thank you for supporting DadRock Tabs.</p>
        `,
      });

      if (emailResult.error) {
        console.error('Resend email error:', emailResult.error);
      }

      return NextResponse.json({
        downloadUrl,
        expiresAt,
        fileName,
      });
    }

    const professionalPdfFeature =
      getJimmyPaigeProfessionalPdfFeatureState();
    const useProfessionalRenderer =
      professionalPdfFeature.enabled;

    let pdfBytes;

    if (useProfessionalRenderer) {
      const result = await createJimmyPaigeProfessionalPdf({
        song,
        artist,
        transcriptionType,
        generatedTab,
        tuning,
        tempo,
        timeSignature,
        keySignature,
        analysisEngine,
        renderEvents:
          Array.isArray(body?.renderEvents)
            ? body.renderEvents
            : [],
        measureGrid:
          body?.measureGrid || null,
        confidence:
          body?.confidence ?? null,
        difficulty:
          body?.difficulty || null,
        techniques:
          Array.isArray(body?.techniques)
            ? body.techniques
            : [],
        preview: false,
      });
      pdfBytes = result.pdfBytes;
    } else {
      pdfBytes = await createTabPdf({
        song,
        artist,
        transcriptionType,
        generatedTab,
        tuning,
        tempo,
        timeSignature,
        keySignature,
        preview: false,
      });
    }

    const fileName = createSafeFileName({
      song,
      artist,
      transcriptionType,
    });

    const emailResult = await resend.emails.send({
      from:
        process.env.RESEND_FROM_EMAIL ||
        'DadRock Tabs <onboarding@resend.dev>',
      to: customerEmail,
      subject: `${song} — ${transcriptionType} tab PDF`,
      html: `
        <h2>Your DadRock Tabs PDF is ready</h2>
        <p><strong>${song}</strong> by ${artist}</p>
        <p>Your ${transcriptionType} transcription is attached.</p>
        <p>Thank you for supporting DadRock Tabs.</p>
      `,
      attachments: [
        {
          filename: fileName,
          content: Buffer.from(pdfBytes),
        },
      ],
    });

    if (emailResult.error) {
      console.error('Resend email error:', emailResult.error);
    }

    return new NextResponse(Buffer.from(pdfBytes), {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition':
          `attachment; filename="${fileName}"`,
        'Cache-Control': 'no-store, max-age=0',
        Pragma: 'no-cache',
        Expires: '0',
      },
    });
  } catch (error) {
    console.error('Generate tab PDF route error:', error);

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to generate the PDF.',
      },
      { status: 500 }
    );
  }
}
