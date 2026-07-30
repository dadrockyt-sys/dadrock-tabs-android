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

export async function GET() {
  try {
    const pdfBytes = await createJimmyPaigeV8Pdf({
      songTitle: 'Are You Gonna Go My Way',
      artistName: 'Lenny Kravitz',
      transcriptionType: 'Rhythm Guitar',
      totalMeasures: 113,
      tuning: 'Standard Tuning',
      timeSignature: '4/4',
      bpm: 129,
      sections: GOMYWAY_V8_SECTIONS,
    });

    return new Response(Buffer.from(pdfBytes), {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition': 'inline; filename="jimmy-paige-v8-preview.pdf"',
        'Cache-Control': 'no-store, no-cache, must-revalidate',
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
