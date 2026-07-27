import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const maxDuration = 150;

const ALLOWED_TRANSCRIPTION_TYPES = [
  'lead',
  'rhythm',
  'bass',
];

function cleanText(value, maximumLength) {
  return String(value || '')
    .trim()
    .slice(0, maximumLength);
}

export async function POST(request) {
  try {
    const body = await request.json();

    const audioUrl = cleanText(
      body?.audioUrl,
      2000
    );

    const pathname = cleanText(
      body?.pathname,
      1000
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
      20
    ).toLowerCase();

    if (
      !audioUrl ||
      !pathname ||
      !song ||
      !artist ||
      !transcriptionType
    ) {
      return NextResponse.json(
        {
          error:
            'Audio, song, artist, and transcription type are required.',
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

    const analyzerUrl =
      process.env.ANALYZER_API_URL;

    const analyzerToken =
      process.env.ANALYZER_API_TOKEN;

    const blobToken =
      process.env.BLOB_READ_WRITE_TOKEN;

    if (
      !analyzerUrl ||
      !analyzerToken ||
      !blobToken
    ) {
      console.error(
        'Analyzer configuration missing:',
        {
          hasAnalyzerUrl:
            Boolean(analyzerUrl),
          hasAnalyzerToken:
            Boolean(analyzerToken),
          hasBlobToken:
            Boolean(blobToken),
        }
      );

      return NextResponse.json(
        {
          error:
            'The audio analyzer is not configured.',
        },
        { status: 503 }
      );
    }

    const analyzerResponse = await fetch(
      analyzerUrl,
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify({
          token: analyzerToken,
          blobToken,
          audioUrl,
          pathname,
          song,
          artist,
          transcriptionType,
        }),
        cache: 'no-store',
      }
    );

    const analyzerData =
      await analyzerResponse
        .json()
        .catch(() => ({}));

    if (!analyzerResponse.ok) {
      console.error(
        'Modal analyzer error:',
        analyzerData
      );

      return NextResponse.json(
        {
          error:
            analyzerData?.detail ||
            analyzerData?.error ||
            'The audio could not be analyzed.',
        },
        {
          status:
            analyzerResponse.status,
        }
      );
    }

    const generatedTab = String(
      analyzerData?.generatedTab || ''
    ).trim();

    if (!generatedTab) {
      return NextResponse.json(
        {
          error:
            'The analyzer returned no tablature.',
        },
        { status: 502 }
      );
    }

    return NextResponse.json({
      generatedTab,
      tuning:
        analyzerData?.tuning || null,
      tempo:
        analyzerData?.tempo || null,
      timeSignature:
        analyzerData?.timeSignature ||
        null,
      keySignature:
        analyzerData?.keySignature ||
        null,
      difficulty:
        analyzerData?.difficulty ||
        null,
      techniques: Array.isArray(
        analyzerData?.techniques
      )
        ? analyzerData.techniques
        : [],
      confidence:
        analyzerData?.confidence ??
        null,
      noteCount:
        analyzerData?.noteCount ?? 0,
    });
  } catch (error) {
    console.error(
      'Analyze audio tab route error:',
      error
    );

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to analyze the audio.',
      },
      { status: 500 }
    );
  }
}
