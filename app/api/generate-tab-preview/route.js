import { NextResponse } from 'next/server';
import { createAiTabPdf } from '@/lib/createAiTabPdf';
import { projectV143RenderEvents } from '@/lib/v143RenderContract';

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

export async function POST(request) {
  try {
    const body = await request.json();

    const song = cleanText(body?.song, 120);
    const artist = cleanText(body?.artist, 120);
    const transcriptionType = cleanText(
      body?.transcriptionType,
      40
    ).toLowerCase();
    const generatedTab = cleanTabText(body?.generatedTab);
    const tuning = cleanText(body?.tuning, 80) || 'Standard Tuning';
    const tempo = Math.min(
      300,
      Math.max(20, Number(body?.tempo) || 120)
    );
    const timeSignature =
      cleanText(body?.timeSignature, 20) || '4/4';
    const keySignature = cleanText(body?.keySignature, 40);
    const analysisEngine = cleanText(body?.analysisEngine, 80);
    const renderEvents = projectV143RenderEvents(body?.renderEvents);
    const previewSystems = Math.min(
      4,
      Math.max(1, Number(body?.previewSystems) || 4)
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

    if (!ALLOWED_TRANSCRIPTION_TYPES.includes(transcriptionType)) {
      return NextResponse.json(
        {
          error:
            'Transcription type must be lead, rhythm, or bass.',
        },
        { status: 400 }
      );
    }

    const pdfBytes = await createAiTabPdf({
      song,
      artist,
      transcriptionType,
      generatedTab,
      tuning,
      tempo,
      timeSignature,
      keySignature,
      analysisEngine,
      renderEvents,
      preview: true,
      previewSystems,
    });

    return new NextResponse(Buffer.from(pdfBytes), {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition':
          'inline; filename="dadrock-tab-preview.pdf"',
        'Cache-Control': 'no-store, max-age=0',
      },
    });
  } catch (error) {
    console.error('Generate tab preview error:', error);

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to create the tab preview.',
      },
      { status: 500 }
    );
  }
}
