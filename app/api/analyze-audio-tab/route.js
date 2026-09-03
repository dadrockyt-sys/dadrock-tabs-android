import { NextResponse } from 'next/server';
import { buildJimmyPaigeAnalysisPayload } from '@/lib/jimmyPaigeAnalysisPayload';
import {
  AiTabConditioningValidationError,
  buildAiTabConditioningContractV1,
  normalizeAiTabConditioningV1,
} from '@/lib/aiTabConditioningV1.mjs';
import { buildAiTabConditionedShadowProjectionV1 } from '@/lib/aiTabConditionedShadowProjectionV1.mjs';

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

    let conditioning;

    try {
      conditioning = normalizeAiTabConditioningV1(
        body?.conditioning,
        transcriptionType
      );
    } catch (error) {
      if (
        error instanceof AiTabConditioningValidationError
      ) {
        return NextResponse.json(
          {
            error: error.message,
            code: error.code,
          },
          { status: 400 }
        );
      }

      throw error;
    }

    // Preserve the existing analyzer as the default for Lead/Bass and as the
    // rollback path for Rhythm. V143 remains selected only through its own
    // environment variable, so adding conditioning cannot switch analyzers.
    const legacyAnalyzerUrl =
      process.env.ANALYZER_API_URL;

    const v143RhythmAnalyzerUrl =
      process.env.ANALYZER_API_URL_V143;

    const usingV143RhythmAnalyzer =
      transcriptionType === 'rhythm' &&
      Boolean(v143RhythmAnalyzerUrl);

    const analyzerUrl =
      usingV143RhythmAnalyzer
        ? v143RhythmAnalyzerUrl
        : legacyAnalyzerUrl;

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
          transcriptionType,
          hasSelectedAnalyzerUrl:
            Boolean(analyzerUrl),
          hasLegacyAnalyzerUrl:
            Boolean(legacyAnalyzerUrl),
          hasV143RhythmAnalyzerUrl:
            Boolean(v143RhythmAnalyzerUrl),
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
          conditioning,
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
        {
          transcriptionType,
          usingV143RhythmAnalyzer,
          analyzerData,
        }
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

    // V143 Rhythm must prove the complete anti-leakage contract before its
    // response can enter the structured product path. The payload builder below
    // independently enforces the same contract as a second fail-closed layer.
    const liveV143 = analyzerData?.liveV143;
    const v143RuntimeSafetyVerified =
      liveV143?.referenceFree === true &&
      liveV143?.professionalReferenceUsed === false &&
      liveV143?.referenceRuntimeInputUsed === false &&
      liveV143?.runtimeLabelsRequired === false;

    if (
      usingV143RhythmAnalyzer &&
      !v143RuntimeSafetyVerified
    ) {
      console.error(
        'V143 rhythm analyzer runtime safety check failed.'
      );

      return NextResponse.json(
        {
          error:
            'The V143 rhythm analyzer did not satisfy the reference-free runtime safety contract.',
        },
        { status: 502 }
      );
    }

    const structuredPayload =
      buildJimmyPaigeAnalysisPayload(
        analyzerData,
        {
          transcriptionType,
          usingV143RhythmAnalyzer,
        }
      );

    // The server-normalized conditioning contract is appended after analyzer
    // output normalization. The analyzer is therefore never authoritative for
    // request conditioning, reference authorization, or dual-context provenance.
    const conditioningContract =
      buildAiTabConditioningContractV1({
        conditioning,
        usingV143RhythmAnalyzer,
      });

    // Phase 2 is shadow-only: it reads copied normalized events plus the
    // server-normalized conditioning contract and emits parallel research
    // metadata. It never replaces generatedTab/events/renderEvents/measureGrid,
    // changes analysisEngine, selects an analyzer, or participates in PDF output.
    const conditioningShadowProjection =
      buildAiTabConditionedShadowProjectionV1({
        events: structuredPayload.events,
        conditioning,
      });

    return NextResponse.json({
      ...structuredPayload,
      rhythmCanaryActive:
        usingV143RhythmAnalyzer,
      conditioningContract,
      conditioningShadowProjection,
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
