import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { NextResponse } from 'next/server';
import {
  PDFDocument,
  StandardFonts,
  degrees,
  rgb,
} from 'pdf-lib';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const ALLOWED_TRANSCRIPTION_TYPES = [
  'lead',
  'rhythm',
  'bass',
];

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

function wrapText(text, maximumCharacters) {
  const words = String(text || '')
    .trim()
    .split(/\s+/)
    .filter(Boolean);

  if (!words.length) {
    return [''];
  }

  const lines = [];
  let currentLine = '';

  for (const word of words) {
    const candidate = currentLine
      ? `${currentLine} ${word}`
      : word;

    if (
      candidate.length <= maximumCharacters
    ) {
      currentLine = candidate;
      continue;
    }

    if (currentLine) {
      lines.push(currentLine);
    }

    currentLine = word;
  }

  if (currentLine) {
    lines.push(currentLine);
  }

  return lines;
}

function getPreviewTabLines(generatedTab) {
  const allLines = cleanTabText(generatedTab)
    .split('\n');

  const previewLines = [];
  let completedStringRows = 0;

  for (const line of allLines) {
    previewLines.push(line);

    const trimmedLine = line.trim();

    if (
      /^(e|B|G|D|A|E)\|/i.test(
        trimmedLine
      )
    ) {
      completedStringRows += 1;
    }

    if (completedStringRows >= 24) {
      break;
    }

    if (previewLines.length >= 32) {
      break;
    }
  }

  return previewLines;
}

async function loadBrandLogo(pdfDoc) {
  try {
    const logoPath = path.join(
      process.cwd(),
      'public',
      'dadrock-logo.png'
    );

    const logoBytes = await readFile(
      logoPath
    );

    return await pdfDoc.embedPng(
      logoBytes
    );
  } catch (error) {
    console.warn(
      'Preview logo could not be loaded:',
      error
    );

    return null;
  }
}
async function createPreviewPdf({
  song,
  artist,
  transcriptionType,
  generatedTab,
}) {
  const pdfDoc =
    await PDFDocument.create();

  const regularFont =
    await pdfDoc.embedFont(
      StandardFonts.Helvetica
    );

  const boldFont =
    await pdfDoc.embedFont(
      StandardFonts.HelveticaBold
    );

  const tabFont =
    await pdfDoc.embedFont(
      StandardFonts.Courier
    );

  const logo = await loadBrandLogo(
    pdfDoc
  );

  const pageWidth = 612;
  const pageHeight = 792;
  const margin = 48;
  const tabFontSize = 9;
  const tabLineHeight = 12;

  const page = pdfDoc.addPage([
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

  if (logo) {
    const logoDimensions =
      logo.scale(0.18);

    page.drawImage(logo, {
      x: margin,
      y:
        pageHeight -
        82,
      width: logoDimensions.width,
      height: logoDimensions.height,
    });
  } else {
    page.drawText('DADROCK TABS', {
      x: margin,
      y: pageHeight - 47,
      size: 23,
      font: boldFont,
      color: rgb(1, 1, 1),
    });
  }

  page.drawText(
    'AI GUITAR TRANSCRIPTION',
    {
      x: margin,
      y: pageHeight - 70,
      size: 9,
      font: boldFont,
      color: rgb(
        0.96,
        0.55,
        0.08
      ),
    }
  );

  let y = pageHeight - 124;

  const songLines = wrapText(
    song,
    36
  );

  for (const line of songLines) {
    page.drawText(line, {
      x: margin,
      y,
      size: 21,
      font: boldFont,
      color: rgb(
        0.05,
        0.05,
        0.05
      ),
    });

    y -= 25;
  }

  page.drawText(artist, {
    x: margin,
    y,
    size: 14,
    font: regularFont,
    color: rgb(
      0.35,
      0.35,
      0.35
    ),
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
    color: rgb(
      0.18,
      0.18,
      0.18
    ),
  });

  y -= 22;

  page.drawLine({
    start: {
      x: margin,
      y,
    },
    end: {
      x: pageWidth - margin,
      y,
    },
    thickness: 1.5,
    color: rgb(
      0.1,
      0.1,
      0.1
    ),
  });

  y -= 24;

  const tabLines =
    getPreviewTabLines(
      generatedTab
    );

  for (const line of tabLines) {
    if (y < 190) {
      break;
    }

    const safeLine = line
      .replace(/[^\x20-\x7E]/g, '')
      .slice(0, 88);

    page.drawText(
      safeLine || ' ',
      {
        x: margin,
        y,
        size: tabFontSize,
        font: tabFont,
        color: rgb(0, 0, 0),
      }
    );

    y -= tabLineHeight;
  }
    page.drawText(
    'DADROCK TABS PREVIEW',
    {
      x: 78,
      y: 330,
      size: 38,
      font: boldFont,
      color: rgb(
        0.72,
        0.72,
        0.72
      ),
      rotate: degrees(34),
      opacity: 0.32,
    }
  );

  page.drawRectangle({
    x: margin,
    y: 72,
    width: pageWidth - margin * 2,
    height: 82,
    color: rgb(
      0.98,
      0.95,
      0.9
    ),
    borderColor: rgb(
      0.96,
      0.55,
      0.08
    ),
    borderWidth: 1.5,
  });

  page.drawText(
    'PREVIEW ONLY',
    {
      x: margin + 20,
      y: 124,
      size: 11,
      font: boldFont,
      color: rgb(
        0.96,
        0.45,
        0.05
      ),
    }
  );

  page.drawText(
    'Unlock the complete unwatermarked tablature PDF below.',
    {
      x: margin + 20,
      y: 101,
      size: 10,
      font: boldFont,
      color: rgb(
        0.12,
        0.12,
        0.12
      ),
    }
  );

  page.drawText(
    'The full version includes the complete transcription and PDF download.',
    {
      x: margin + 20,
      y: 83,
      size: 8,
      font: regularFont,
      color: rgb(
        0.35,
        0.35,
        0.35
      ),
    }
  );

  page.drawText(
    'DadRock Tabs • AI-generated educational preview',
    {
      x: margin,
      y: 28,
      size: 7,
      font: regularFont,
      color: rgb(
        0.45,
        0.45,
        0.45
      ),
    }
  );

  return pdfDoc.save();
}

export async function POST(request) {
  try {
    const body = await request.json();

    const song = cleanText(
      body?.song,
      120
    );

    const artist = cleanText(
      body?.artist,
      120
    );

    const transcriptionType =
      cleanText(
        body?.transcriptionType,
        40
      ).toLowerCase();

    const generatedTab =
      cleanTabText(
        body?.generatedTab
      );

    if (
      !song ||
      !artist ||
      !transcriptionType ||
      !generatedTab
    ) {
      return NextResponse.json(
        {
          error:
            'Song, artist, transcription type, and generated tab are required.',
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

    const pdfBytes =
      await createPreviewPdf({
        song,
        artist,
        transcriptionType,
        generatedTab,
      });

    return new NextResponse(
      Buffer.from(pdfBytes),
      {
        status: 200,
        headers: {
          'Content-Type':
            'application/pdf',
          'Content-Disposition':
            'inline; filename="dadrock-tab-preview.pdf"',
          'Cache-Control':
            'no-store, max-age=0',
        },
      }
    );
  } catch (error) {
    console.error(
      'Generate tab preview error:',
      error
    );

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to generate the PDF preview.',
      },
      { status: 500 }
    );
  }
}
