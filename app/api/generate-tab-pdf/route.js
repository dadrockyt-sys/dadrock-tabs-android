import { createHash } from 'node:crypto';
import { resend } from '@/lib/resend';
import { NextResponse } from 'next/server';
import {
  PDFDocument,
  StandardFonts,
  rgb,
} from 'pdf-lib';

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
  const rawName =
    `${artist}-${song}-${transcriptionType}-tab`;

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

async function verifyPayPalOrder({
  orderId,
  song,
  artist,
  transcriptionType,
}) {
  const accessToken =
    await getPayPalAccessToken();

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
    console.error(
      'PayPal order verification error:',
      data
    );

    throw new Error(
      'Unable to verify the PayPal order.'
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
    capture?.amount?.currency_code ===
      CURRENCY &&
    capture?.amount?.value === PRICE &&
    purchaseUnit?.custom_id ===
      expectedCustomId;

  if (!paymentIsValid) {
    console.error(
      'PDF payment verification failed:',
      {
        orderId,
        orderStatus: data.status,
        captureStatus: capture?.status,
        amount: capture?.amount,
        customId: purchaseUnit?.custom_id,
      }
    );

    throw new Error(
      'Payment could not be verified.'
    );
  }

  return data;
}

function wrapText(text, maximumCharacters) {
  const words = String(text || '').split(/\s+/);
  const lines = [];
  let currentLine = '';

  for (const word of words) {
    const nextLine = currentLine
      ? `${currentLine} ${word}`
      : word;

    if (
      nextLine.length > maximumCharacters &&
      currentLine
    ) {
      lines.push(currentLine);
      currentLine = word;
    } else {
      currentLine = nextLine;
    }
  }

  if (currentLine) {
    lines.push(currentLine);
  }

  return lines;
}

async function createTabPdf({
  song,
  artist,
  transcriptionType,
  generatedTab,
}) {
  const pdfDoc = await PDFDocument.create();

  const regularFont = await pdfDoc.embedFont(
    StandardFonts.Helvetica
  );

  const boldFont = await pdfDoc.embedFont(
    StandardFonts.HelveticaBold
  );

  const tabFont = await pdfDoc.embedFont(
    StandardFonts.Courier
  );

  const pageWidth = 612;
  const pageHeight = 792;
  const margin = 48;
  const footerHeight = 38;
  const tabFontSize = 9;
  const tabLineHeight = 12;

  let page;
  let y;

  function addPage() {
    page = pdfDoc.addPage([
      pageWidth,
      pageHeight,
    ]);

    page.drawRectangle({
      x: 0,
      y: pageHeight - 92,
      width: pageWidth,
      height: 92,
      color: rgb(0.06, 0.06, 0.07),
    });

    page.drawRectangle({
      x: 0,
      y: pageHeight - 96,
      width: pageWidth,
      height: 4,
      color: rgb(0.96, 0.55, 0.08),
    });

    page.drawText('DADROCK TABS', {
      x: margin,
      y: pageHeight - 47,
      size: 23,
      font: boldFont,
      color: rgb(1, 1, 1),
    });

    page.drawText(
      'AI GUITAR TRANSCRIPTION',
      {
        x: margin,
        y: pageHeight - 70,
        size: 9,
        font: boldFont,
        color: rgb(0.96, 0.55, 0.08),
      }
    );

    page.drawText(
      'Educational personal-use transcription',
      {
        x: margin,
        y: 21,
        size: 7,
        font: regularFont,
        color: rgb(0.45, 0.45, 0.45),
      }
    );

    y = pageHeight - 124;
  }

  addPage();

  const songLines = wrapText(song, 36);

  for (const line of songLines) {
    page.drawText(line, {
      x: margin,
      y,
      size: 21,
      font: boldFont,
      color: rgb(0.05, 0.05, 0.05),
    });

    y -= 25;
  }

  page.drawText(artist, {
    x: margin,
    y,
    size: 14,
    font: regularFont,
    color: rgb(0.35, 0.35, 0.35),
  });

  y -= 34;

  const details =
    `Part: ${transcriptionType.toUpperCase()}` +
    '    Tuning: Standard' +
    '    Format: TAB';

  page.drawText(details, {
    x: margin,
    y,
    size: 9,
    font: boldFont,
    color: rgb(0.18, 0.18, 0.18),
  });

  y -= 22;

  page.drawLine({
    start: { x: margin, y },
    end: {
      x: pageWidth - margin,
      y,
    },
    thickness: 1.5,
    color: rgb(0.1, 0.1, 0.1),
  });

  y -= 24;

  const tabLines = generatedTab.split('\n');

  for (const line of tabLines) {
    if (
      y <
      margin + footerHeight + tabLineHeight
    ) {
      addPage();
    }

    const safeLine = line
      .replace(/[^\x20-\x7E]/g, '')
      .slice(0, 88);

    page.drawText(safeLine || ' ', {
      x: margin,
      y,
      size: tabFontSize,
      font: tabFont,
      color: rgb(0, 0, 0),
    });

    y -= tabLineHeight;
  }

  const pages = pdfDoc.getPages();

  pages.forEach((currentPage, index) => {
    const pageNumber =
      `Page ${index + 1} of ${pages.length}`;

    currentPage.drawText(pageNumber, {
      x: pageWidth - margin - 58,
      y: 21,
      size: 7,
      font: regularFont,
      color: rgb(0.45, 0.45, 0.45),
    });
  });

  return pdfDoc.save();
}

export async function POST(request) {
  try {
    const body = await request.json();

    const orderId = cleanText(
      body?.orderId,
      40
    );

    const song = cleanText(
      body?.song,
      120
    );

    const artist = cleanText(
      body?.artist,
      120
    );

    const transcriptionType = cleanText(
      body?.transcriptionType,
      40
    ).toLowerCase();

    const generatedTab = cleanTabText(
      body?.generatedTab
    );
    const customerEmail = cleanText(
  body?.customerEmail,
  254
).toLowerCase();

const emailIsValid =
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
    customerEmail
  );

    if (
  !orderId ||
  !song ||
  !artist ||
  !transcriptionType ||
  !generatedTab ||
  !customerEmail
) {
  return NextResponse.json(
    {
      error:
        'Order ID, song, artist, transcription type, tab, and customer email are required.',
    },
    { status: 400 }
  );
}

if (!emailIsValid) {
  return NextResponse.json(
    {
      error:
        'Please provide a valid email address.',
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

    await verifyPayPalOrder({
      orderId,
      song,
      artist,
      transcriptionType,
    });

    const pdfBytes = await createTabPdf({
      song,
      artist,
      transcriptionType,
      generatedTab,
    });

    const fileName = createSafeFileName({
      song,
      artist,
      transcriptionType,
    });

    return new NextResponse(pdfBytes, {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition':
          `attachment; filename="${fileName}"`,
        'Cache-Control':
          'no-store, max-age=0',
        Pragma: 'no-cache',
        Expires: '0',
      },
    });
  } catch (error) {
    console.error(
      'Generate tab PDF route error:',
      error
    );

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
