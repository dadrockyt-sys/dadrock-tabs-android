import fs from 'node:fs/promises';
import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

// No-op trigger for repaired V143 protected Preview verification.
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

function cleanLabel(value) {
  return String(value || '')
    .replace(/[^\x20-\x7E]/g, '')
    .replace(/\s+/g, ' ')
    .trim();
}

function buildReadableProofGrid(measureGrid) {
  const rows = Array.isArray(measureGrid?.rows)
    ? measureGrid.rows
    : [];

  const readableRows = rows.map((row) => {
    const fragments = Array.isArray(row?.fragments)
      ? [...row.fragments]
      : [];

    fragments.sort((a, b) => {
      const measureDifference =
        Number(a?.measureNumber || 0) -
        Number(b?.measureNumber || 0);

      if (measureDifference !== 0) {
        return measureDifference;
      }

      return (
        Number(a?.rowStartRatio || 0) -
        Number(b?.rowStartRatio || 0)
      );
    });

    const kept = [];
    const chordMeasures = new Set();
    const pointMarkerKeys = new Set();

    for (const fragment of fragments) {
      const type = cleanLabel(fragment?.markerType);
      const measureNumber = Number(fragment?.measureNumber || 0);
      const label = cleanLabel(fragment?.label);

      if (type === 'chord-label') {
        if (!label || chordMeasures.has(measureNumber)) {
          continue;
        }

        chordMeasures.add(measureNumber);
        kept.push(fragment);
        continue;
      }

      const isPointMarker =
        type === 'muted-attack' ||
        type === 'rest' ||
        type === 'slide';

      if (isPointMarker) {
        const key = `${measureNumber}:${type}:${label}`;

        if (pointMarkerKeys.has(key)) {
          continue;
        }

        pointMarkerKeys.add(key);
      }

      kept.push(fragment);
    }

    return {
      ...row,
      fragments: kept,
      fragmentCount: kept.length,
      markerTypes: [...new Set(
        kept.map((fragment) => cleanLabel(fragment?.markerType))
      )].filter(Boolean),
    };
  });

  return {
    ...measureGrid,
    rows: readableRows,
    proofDisplayMode: 'first-chord-per-measure-deduplicated',
  };
}

export async function GET() {
  if (process.env.NODE_ENV === 'production') {
    return NextResponse.json(
      { error: 'This development proof route is disabled in production.' },
      { status: 404 }
    );
  }

  try {
    // This route is development-only. Keep the heavy V7 PDF stack out of
    // production/Preview function tracing by loading it only after the
    // production guard above has passed.
    const { createTabPdf } = await import('@/lib/createTabPdfPolishedV7');

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
    const readableMeasureGrid = buildReadableProofGrid(measureGrid);

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
      measureGrid: readableMeasureGrid,
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
