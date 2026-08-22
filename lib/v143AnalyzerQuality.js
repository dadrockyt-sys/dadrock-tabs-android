import { MAX_RENDER_EVENTS } from './v143RenderContract.js';

const QUALITY_GATE_VERSION = 1;

const QUALITY_THRESHOLDS = Object.freeze({
  minimumRenderEvents: 4,
  minimumRenderSurvivalPercent: 70,
  minimumPlayableStringFretPercent: 70,
  minimumMusicalPlacementPercent: 70,
  minimumPitchValidityPercent: 70,
});

function finiteInteger(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) && Number.isInteger(numeric)
    ? numeric
    : null;
}

function percentage(numerator, denominator) {
  if (!denominator) return 0;
  return Math.round((numerator / denominator) * 1000) / 10;
}

function hasPlayableStringFret(event) {
  const stringIndex = finiteInteger(event?.stringIndex);
  const fret = finiteInteger(event?.fret);

  return (
    stringIndex !== null &&
    stringIndex >= 0 &&
    stringIndex <= 5 &&
    fret !== null &&
    fret >= 0 &&
    fret <= 36
  );
}

function hasMusicalPlacement(event) {
  const measure = finiteInteger(event?.measure);
  const step = finiteInteger(event?.step);

  return (
    measure !== null &&
    measure >= 1 &&
    step !== null &&
    step >= 0 &&
    step <= 15
  );
}

function hasPitch(event) {
  const midi = finiteInteger(
    event?.midi ?? event?.dominantMidi
  );

  return (
    midi !== null &&
    midi >= 0 &&
    midi <= 127
  );
}

function uniqueSortedNumbers(values) {
  return [...new Set(values)]
    .filter((value) => Number.isFinite(value))
    .sort((a, b) => a - b);
}

export function buildV143AnalyzerQualityReport({
  referenceFree = false,
  rawEvents = [],
  renderEvents = [],
} = {}) {
  const sourceEvents = Array.isArray(rawEvents)
    ? rawEvents
    : [];

  const projectedEvents = Array.isArray(renderEvents)
    ? renderEvents
    : [];

  const consideredEvents = sourceEvents.slice(
    0,
    MAX_RENDER_EVENTS
  );

  const rawEventCount = sourceEvents.length;
  const consideredRawEventCount =
    consideredEvents.length;
  const validRenderEventCount =
    projectedEvents.length;

  const playableStringFretCount =
    consideredEvents.filter(
      hasPlayableStringFret
    ).length;

  const musicalPlacementCount =
    consideredEvents.filter(
      hasMusicalPlacement
    ).length;

  const pitchValidityCount =
    consideredEvents.filter(hasPitch).length;

  const renderEventSurvivalPercent =
    percentage(
      validRenderEventCount,
      consideredRawEventCount
    );

  const playableStringFretPercent =
    percentage(
      playableStringFretCount,
      consideredRawEventCount
    );

  const musicalPlacementPercent =
    percentage(
      musicalPlacementCount,
      consideredRawEventCount
    );

  const pitchValidityPercent =
    percentage(
      pitchValidityCount,
      consideredRawEventCount
    );

  const measures = uniqueSortedNumbers(
    projectedEvents.map(
      (event) => Number(event?.measure)
    )
  );

  const steps = uniqueSortedNumbers(
    projectedEvents.map(
      (event) => Number(event?.step)
    )
  ).filter(
    (step) => step >= 0 && step <= 15
  );

  const techniqueTypes = [
    ...new Set(
      projectedEvents.flatMap((event) =>
        Array.isArray(event?.techniques)
          ? event.techniques
              .map((value) =>
                String(value || '')
                  .trim()
                  .toLowerCase()
              )
              .filter(Boolean)
          : []
      )
    ),
  ].sort();

  const techniqueEventCount =
    projectedEvents.filter(
      (event) =>
        Array.isArray(event?.techniques) &&
        event.techniques.length > 0
    ).length;

  const sustainEventCount =
    projectedEvents.filter((event) => {
      const durationSteps =
        finiteInteger(event?.durationSteps);
      const sustainTier = String(
        event?.sustainTier || ''
      )
        .trim()
        .toLowerCase();

      return (
        (durationSteps !== null &&
          durationSteps > 1) ||
        ['short', 'medium', 'long'].includes(
          sustainTier
        )
      );
    }).length;

  const failures = [];

  if (referenceFree !== true) {
    failures.push(
      'reference-free-identity-missing'
    );
  }

  if (consideredRawEventCount === 0) {
    failures.push('no-raw-events');
  }

  if (
    validRenderEventCount <
    QUALITY_THRESHOLDS.minimumRenderEvents
  ) {
    failures.push(
      'insufficient-valid-render-events'
    );
  }

  if (
    renderEventSurvivalPercent <
    QUALITY_THRESHOLDS.minimumRenderSurvivalPercent
  ) {
    failures.push(
      'render-event-survival-below-threshold'
    );
  }

  if (
    playableStringFretPercent <
    QUALITY_THRESHOLDS.minimumPlayableStringFretPercent
  ) {
    failures.push(
      'playable-string-fret-coverage-below-threshold'
    );
  }

  if (
    musicalPlacementPercent <
    QUALITY_THRESHOLDS.minimumMusicalPlacementPercent
  ) {
    failures.push(
      'measure-step-coverage-below-threshold'
    );
  }

  if (
    pitchValidityPercent <
    QUALITY_THRESHOLDS.minimumPitchValidityPercent
  ) {
    failures.push(
      'pitch-coverage-below-threshold'
    );
  }

  if (measures.length === 0) {
    failures.push('no-valid-measure-coverage');
  }

  return {
    contract: {
      name: 'v143-analyzer-output-quality',
      version: QUALITY_GATE_VERSION,
    },
    passed: failures.length === 0,
    failures,
    thresholds: {
      ...QUALITY_THRESHOLDS,
    },
    metrics: {
      referenceFreeIdentity:
        referenceFree === true,
      rawEventCount,
      consideredRawEventCount,
      validRenderEventCount,
      renderEventSurvivalPercent,
      playableStringFretCount,
      playableStringFretPercent,
      musicalPlacementCount,
      musicalPlacementPercent,
      pitchValidityCount,
      pitchValidityPercent,
      measureRange:
        measures.length > 0
          ? {
              first: measures[0],
              last:
                measures[measures.length - 1],
              uniqueMeasureCount:
                measures.length,
            }
          : null,
      stepCoverage: {
        uniqueSteps: steps,
        uniqueStepCount: steps.length,
        sixteenthGridCoveragePercent:
          percentage(steps.length, 16),
      },
      techniqueCoverage: {
        eventCount: techniqueEventCount,
        eventPercent: percentage(
          techniqueEventCount,
          validRenderEventCount
        ),
        types: techniqueTypes,
      },
      sustainCoverage: {
        eventCount: sustainEventCount,
        eventPercent: percentage(
          sustainEventCount,
          validRenderEventCount
        ),
      },
    },
    productionPromotionAuthorized: false,
  };
}

export {
  QUALITY_GATE_VERSION,
  QUALITY_THRESHOLDS,
};
