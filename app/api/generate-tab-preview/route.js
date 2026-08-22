import { NextResponse } from 'next/server';
import { createTabPdf } from '@/lib/createTabPdfPolished';
import { createJimmyPaigeProfessionalPdf } from '@/lib/createJimmyPaigeProfessionalPdf';

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

    const useProfessionalRenderer =
      process.env.JIMMY_PAIGE_PROFESSIONAL_PDF_V1 === 'true';

    let pdfBytes;
    let rendererMode = 'polished-current';

    if (useProfessionalRenderer) {
      const result =
        await createJimmyPaigeProfessionalPdf({
          song,
          artist,
          transcriptionType,
          generatedTab,
          tuning,
          tempo,
          timeSignature,
          keySignature,
          preview: true,
          previewSystems,
          renderEvents:
            Array.isArray(body?.renderEvents)
              ? body.renderEvents
              : [],
          measureGrid:
            body?.measureGrid || null,
          analysisEngine:
            body?.analysisEngine || '',
          confidence:
            body?.confidence ?? null,
          difficulty:
            body?.difficulty || null,
          techniques:
            Array.isArray(body?.techniques)
              ? body.techniques
              : [],
        });

      pdfBytes = result.pdfBytes;
      rendererMode =
        result.rendererContract?.mode ||
        'polished-safe-fallback';
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
        preview: true,
        previewSystems,
      });
    }

    return new NextResponse(Buffer.from(pdfBytes), {
      status: 200,
      headers: {
        'Content-Type': 'application/pdf',
        'Content-Disposition':
          'inline; filename="dadrock-tab-preview.pdf"',
        'Cache-Control': 'no-store, max-age=0',
        'X-Jimmy-PAIge-PDF-Renderer': rendererMode,
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
