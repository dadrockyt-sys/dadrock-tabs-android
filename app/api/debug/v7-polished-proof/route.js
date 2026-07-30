import fs from 'node:fs/promises';
import { NextResponse } from 'next/server';
import { createTabPdf } from '@/lib/createTabPdfPolishedV7';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const DEFAULT_GRID_PATH = '/tmp/gomyway-full-song-v7-measure-grid.json';

function buildBlankTabSystem(transcriptionType = 'lead') {
  const line = '------------------------------------------------------------';

  if (transcriptionType === 'bass') {
    return [
      `G|${line}`,
      `D|${line}`,
      `A|${line}`,
      `E|${line}`,
    ].join('\n');
  }

  return [
    `e|${line}`,
    `B|${line}`,
    `G|${line}`,
    `D|${line}`,
    `A|${line}`,
    `E|${line}`,
  ].join('\n');
}

function buildProofTab(rowCount, transcriptionType = 'lead') {
  const system = buildBlankTabSystem(transcriptionType);
  return Array.from(
    { length: Math.max(1, Number(rowCount) || 1) },
    (_, index) => `RIFF ${index + 1}\n${system}`
  ).join('\n\n');
}

export async function GET() {
  if (process.env.NODE_ENV === 'production') {
    return NextResponse.json(
      { error: 'This development proof route is disabled in production.' },
      { status: 404 }
    );
  }

  try {
    const measureGrid = JSON.parse(
      await fs.readFile(DEFAULT_GRID_PATH, 'utf8')
    );

    if (
      measureGrid?.passed !== true ||
      measureGrid?.measureGridVersion !== 7 ||
      Number(measureGrid?.measuresPerRow) !== 6
    ) {
      return NextResponse.json(
        { error: 'The V7 measure-grid file is missing or invalid.' },
        { status: 422 }
      );
    }

    const transcriptionType = 'lead';
    const generatedTab = buildProofTab(
      measureGrid.rowCount,
      transcriptionType
    );

    const pdfBytes = await createTabPdf({
      song: 'Go My Way',
      artist: 'DadRock Reference Test',
      transcriptionType,
      tuning: 'Standard Tuning',
      timeSignature: '4/4',
      tempo: measureGrid.tempoBpm || 129,
      generatedTab,
      preview: false,
      enableV7MeasureGrid: true,
      measureGrid,
    });

    return new NextResponse(pdfBytes, {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition':
          'inline; filename="gomyway-v7-polished-proof.pdf"',
        'Cache-Control': 'no-store, max-age=0',
      },
    });
  } catch (error) {
    console.error('V7 polished proof route failed:', error);

    return NextResponse.json(
      {
        error: 'Unable to generate the V7 polished proof PDF.',
        details:
          error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}
