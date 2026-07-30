import fs from 'node:fs/promises';
import path from 'node:path';
import { createJimmyPaigeV8Pdf } from '@/lib/tabRenderer/pdfV8';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const GOMYWAY_V8_SECTIONS = [
  { label: 'Intro', startMeasure: 1, endMeasure: 17 },
  { label: 'Verse 1', startMeasure: 18, endMeasure: 32 },
  { label: 'Chorus', startMeasure: 33, endMeasure: 37 },
  { label: 'Riff', startMeasure: 38, endMeasure: 46 },
  { label: 'Verse 2', startMeasure: 47, endMeasure: 61 },
  { label: 'Chorus', startMeasure: 62, endMeasure: 70 },
  { label: 'Bridge', startMeasure: 71, endMeasure: 77 },
  { label: 'Solo', startMeasure: 78, endMeasure: 94 },
  { label: 'Riff', startMeasure: 95, endMeasure: 102 },
  { label: 'Ending', startMeasure: 103, endMeasure: 113 },
];

async function loadNotationBenchmark() {
  const notationPath = path.join(
    process.cwd(),
    'public',
    'gomyway-full-song-v8-notation.json'
  );

  try {
    const raw = await fs.readFile(notationPath, 'utf8');
    const report = JSON.parse(raw);
    const renderEvents = Array.isArray(report.renderEvents)
      ? report.renderEvents
      : [];
    const rhythmEvents = Array.isArray(report.rhythmEvents)
      ? report.rhythmEvents
      : [];
    const selectedEvents = renderEvents.length > 0
      ? renderEvents
      : rhythmEvents;
    const cleanup = report.cleanupDiagnostics || {};

    return {
      selectedEvents,
      rawEventCount: rhythmEvents.length,
      renderEventCount: selectedEvents.length,
      usedCleanedEvents: renderEvents.length > 0,
      passed: report.passed === true,
      nearbyRetriggersRemoved: Number(
        cleanup.nearbyRetriggerEventsRemoved || 0
      ),
    };
  } catch (error) {
    if (error?.code === 'ENOENT') {
      return {
        selectedEvents: [],
        rawEventCount: 0,
        renderEventCount: 0,
        usedCleanedEvents: false,
        passed: false,
        nearbyRetriggersRemoved: 0,
      };
    }
    throw error;
  }
}

export async function GET() {
  try {
    const notation = await loadNotationBenchmark();
    const pdfBytes = await createJimmyPaigeV8Pdf({
      songTitle: 'Are You Gonna Go My Way',
      artistName: 'Lenny Kravitz',
      transcriptionType: 'Rhythm Guitar',
      totalMeasures: 113,
      tuning: 'Standard Tuning',
      timeSignature: '4/4',
      bpm: 129,
      sections: GOMYWAY_V8_SECTIONS,
      rhythmEvents: notation.selectedEvents,
    });

    return new Response(Buffer.from(pdfBytes), {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition':
          'inline; filename="jimmy-paige-v8-notation-cleanup-pass-2.pdf"',
        'Cache-Control': 'no-store, no-cache, must-revalidate',
        'X-Jimmy-Paige-Notation-Raw-Events': String(
          notation.rawEventCount
        ),
        'X-Jimmy-Paige-Notation-Render-Events': String(
          notation.renderEventCount
        ),
        'X-Jimmy-Paige-Notation-Cleaned': String(
          notation.usedCleanedEvents
        ),
        'X-Jimmy-Paige-Retriggers-Removed': String(
          notation.nearbyRetriggersRemoved
        ),
        'X-Jimmy-Paige-Notation-Passed': String(notation.passed),
      },
    });
  } catch (error) {
    console.error('PDF preview error:', error);

    return Response.json(
      {
        error: 'Failed to generate Jimmy PAIge V8 PDF preview',
        details: error instanceof Error ? error.message : String(error),
      },
      { status: 500 }
    );
  }
}
