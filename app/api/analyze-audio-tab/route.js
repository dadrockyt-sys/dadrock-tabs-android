import { NextResponse } from 'next/server';
import { buildJimmyPaigeAnalysisPayload } from '@/lib/jimmyPaigeAnalysisPayload';
import {
  AiTabConditioningValidationError,
  buildAiTabConditioningContractV1,
  normalizeAiTabConditioningV1,
} from '@/lib/aiTabConditioningV1.mjs';
import { buildAiTabConditionedShadowProjectionV1 } from '@/lib/aiTabConditionedShadowProjectionV1.mjs';
import { buildAiTabMixtureStructureContextV1 } from '@/lib/aiTabMixtureStructureContextV1.mjs';
import { buildAiTabDualContextShadowFusionV1 } from '@/lib/aiTabDualContextShadowFusionV1.mjs';
import { buildAiTabMixtureStructureContextFromAnalyzerObservationV1 } from '@/lib/aiTabAnalyzerMixtureObservationAdmissionV1.mjs';
import { buildAiTabProductPlacementCandidateCanaryV1 } from '@/lib/aiTabProductPlacementCandidateCanaryV1.mjs';
import { buildAiTabProductPlacementPromotionV1 } from '@/lib/aiTabProductPlacementPromotionV1.mjs';

export const runtime = 'nodejs';
export const maxDuration = 150;

const ALLOWED_TRANSCRIPTION_TYPES = [
  'lead',
  'rhythm',
  'bass',
];

const ASYNC_OPERATIONS = new Set([
  'start',
  'status',
  'ack',
]);

function cleanText(value, maximumLength) {
  return String(value || '')
    .trim()
    .slice(0, maximumLength);
}

async function buildCompletedProductPayload({
  analyzerData,
  transcriptionType,
  usingV143RhythmAnalyzer,
  conditioning,
}) {
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
    const error = new Error(
      'The V143 rhythm analyzer did not satisfy the reference-free runtime safety contract.'
    );
    error.code = 'V143_RUNTIME_SAFETY_FAILED';
    throw error;
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

  // Phase 2 remains the original raw-prior shadow diagnostic. It is retained
  // for lineage/inspection only and never participates in product rendering.
  const conditioningShadowProjection =
    buildAiTabConditionedShadowProjectionV1({
      events: structuredPayload.events,
      conditioning,
    });

  // Phase 8 preserves the exact Phase 3 null-observation context as the
  // canonical baseline. Only after that server-owned baseline succeeds may a
  // separately admitted analyzer full-mixture observation fill unresolved
  // research fields. Any observation-only failure returns this exact baseline.
  const baselineMixtureStructureContext =
    buildAiTabMixtureStructureContextV1({
      structurePrior: conditioning.structurePrior,
      mixtureObservation: null,
      mixtureSource: conditioningContract.provenance.mixtureSource,
    });

  const mixtureStructureContext =
    buildAiTabMixtureStructureContextFromAnalyzerObservationV1({
      baselineContext: baselineMixtureStructureContext,
      analyzerObservation: analyzerData?.mixtureObservation,
      structurePrior: conditioning.structurePrior,
      mixtureSource: conditioningContract.provenance.mixtureSource,
    });

  // Phase 4 completes the dual-context shadow topology. Global structure comes
  // only from the validated Phase 3/8 mixture context; role/tuning/capo come
  // only from Conditioning V1.
  const dualContextShadowProjection =
    buildAiTabDualContextShadowFusionV1({
      events: structuredPayload.events,
      conditioning,
      mixtureStructureContext,
    });

  // Phase 11 continues to observe the pre-promotion baseline so its historical
  // eligibility signal remains comparable. It exposes counts only, never rows.
  const productPlacementCandidateCanary =
    await buildAiTabProductPlacementCandidateCanaryV1({
      structuredPayload,
      dualContextShadowProjection,
    });

  // Phase 12 is the explicitly authorized Product/PDF placement boundary. It
  // may promote only the already-validated Phase 10 measure/step stream, only
  // when canonical analyzer placement is absent and the post-promotion V143
  // quality gate passes. Any promotion-only failure returns this exact baseline.
  const {
    promotedPayload,
    productPlacementPromotion,
  } = buildAiTabProductPlacementPromotionV1({
    structuredPayload,
    dualContextShadowProjection,
  });

  return {
    ...promotedPayload,
    rhythmCanaryActive:
      usingV143RhythmAnalyzer,
    conditioningContract,
    conditioningShadowProjection,
    mixtureStructureContext,
    dualContextShadowProjection,
    productPlacementCandidateCanary,
    productPlacementPromotion,
  };
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

    const requestedOperation = cleanText(
      body?.operation,
      20
    ).toLowerCase();

    const jobToken = cleanText(
      body?.jobToken,
      300
    );

    if (
      !transcriptionType ||
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
    // explicit rollback path for Rhythm. V143 remains selected only through its
    // own environment variable, so adding async control cannot switch analyzers.
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

    const operation =
      requestedOperation ||
      (usingV143RhythmAnalyzer
        ? 'start'
        : 'analyze');

    if (
      operation !== 'analyze' &&
      !ASYNC_OPERATIONS.has(operation)
    ) {
      return NextResponse.json(
        { error: 'Unsupported analyzer operation.' },
        { status: 400 }
      );
    }

    if (
      ASYNC_OPERATIONS.has(operation) &&
      !usingV143RhythmAnalyzer
    ) {
      return NextResponse.json(
        {
          error:
            'Async analysis is currently available only for Rhythm Guitar.',
        },
        { status: 400 }
      );
    }

    const needsAudioRequest =
      operation === 'start' ||
      operation === 'analyze';

    if (
      needsAudioRequest &&
      (
        !audioUrl ||
        !pathname ||
        !song ||
        !artist
      )
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
      (operation === 'status' || operation === 'ack') &&
      !jobToken
    ) {
      return NextResponse.json(
        { error: 'An async analysis job token is required.' },
        { status: 400 }
      );
    }

    if (
      !analyzerUrl ||
      !analyzerToken ||
      (needsAudioRequest && !blobToken)
    ) {
      console.error(
        'Analyzer configuration missing:',
        {
          transcriptionType,
          operation,
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

    const analyzerRequestBody =
      operation === 'status' ||
      operation === 'ack'
        ? {
            token: analyzerToken,
            operation,
            jobToken,
          }
        : {
            token: analyzerToken,
            operation,
            blobToken,
            audioUrl,
            pathname,
            song,
            artist,
            transcriptionType,
            conditioning,
          };

    const analyzerResponse = await fetch(
      analyzerUrl,
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify(
          analyzerRequestBody
        ),
        cache: 'no-store',
      }
    );

    const bridgeData =
      await analyzerResponse
        .json()
        .catch(() => ({}));

    if (!analyzerResponse.ok) {
      console.error(
        'Modal analyzer error:',
        {
          transcriptionType,
          operation,
          usingV143RhythmAnalyzer,
          bridgeStatus:
            analyzerResponse.status,
        }
      );

      return NextResponse.json(
        {
          error:
            bridgeData?.detail ||
            bridgeData?.error ||
            'The audio could not be analyzed.',
        },
        {
          status:
            analyzerResponse.status,
        }
      );
    }

    if (operation === 'start') {
      if (
        bridgeData?.status !== 'processing' ||
        !bridgeData?.jobToken
      ) {
        return NextResponse.json(
          {
            error:
              'The async analyzer did not return a valid job token.',
          },
          { status: 502 }
        );
      }

      return NextResponse.json(
        {
          rhythmCanaryActive: true,
          analysisJob: {
            status: 'processing',
            token: bridgeData.jobToken,
            pollAfterMs:
              Number(bridgeData.pollAfterMs) ||
              3000,
            expiresInSeconds:
              Number(bridgeData.expiresInSeconds) ||
              900,
          },
        },
        { status: 202 }
      );
    }

    if (operation === 'ack') {
      return NextResponse.json({
        analysisJob: {
          status: 'acknowledged',
          resultCleared:
            bridgeData?.resultCleared === true,
        },
      });
    }

    let analyzerData = bridgeData;

    if (operation === 'status') {
      if (bridgeData?.status === 'processing') {
        return NextResponse.json(
          {
            rhythmCanaryActive: true,
            analysisJob: {
              status: 'processing',
              token: jobToken,
              pollAfterMs:
                Number(bridgeData.pollAfterMs) ||
                3000,
              expiresInSeconds:
                Number(bridgeData.expiresInSeconds) ||
                900,
            },
          },
          { status: 202 }
        );
      }

      if (bridgeData?.status === 'failed') {
        return NextResponse.json(
          {
            error:
              bridgeData?.error ||
              'The analyzer could not complete the request.',
          },
          { status: 502 }
        );
      }

      if (
        bridgeData?.status !== 'completed' ||
        !bridgeData?.result ||
        typeof bridgeData.result !== 'object'
      ) {
        return NextResponse.json(
          {
            error:
              'The async analyzer returned an invalid completion response.',
          },
          { status: 502 }
        );
      }

      analyzerData = bridgeData.result;
    }

    const completedPayload =
      await buildCompletedProductPayload({
        analyzerData,
        transcriptionType,
        usingV143RhythmAnalyzer,
        conditioning,
      });

    return NextResponse.json(
      operation === 'status'
        ? {
            ...completedPayload,
            analysisJob: {
              status: 'completed',
              token: jobToken,
            },
          }
        : completedPayload
    );
  } catch (error) {
    console.error(
      'Analyze audio tab route error:',
      error
    );

    const status =
      error?.code ===
      'V143_RUNTIME_SAFETY_FAILED'
        ? 502
        : 500;

    return NextResponse.json(
      {
        error:
          error instanceof Error
            ? error.message
            : 'Unable to analyze the audio.',
      },
      { status }
    );
  }
}
