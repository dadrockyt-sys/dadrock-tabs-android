import assert from 'node:assert/strict';

import { buildJimmyPaigeAnalysisPayload } from '../lib/jimmyPaigeAnalysisPayload.js';

function safeLiveV143(overrides = {}) {
  return {
    referenceFree: true,
    professionalReferenceUsed: false,
    referenceRuntimeInputUsed: false,
    runtimeLabelsRequired: false,
    ...overrides,
  };
}

function validEvent(index) {
  return {
    start: index * 0.25,
    end: index * 0.25 + 0.2,
    measure: Math.floor(index / 4) + 1,
    step: (index * 4) % 16,
    stringIndex: index % 6,
    fret: 3 + index,
    midi: 52 + index,
    rhythmTechniques:
      index % 2 === 0
        ? ['palm-mute']
        : ['let-ring'],
    rhythmSustain: {
      durationSteps: index % 3 === 0 ? 2 : 1,
      durationSeconds: index % 3 === 0 ? 0.5 : 0.25,
      tier: index % 3 === 0 ? 'medium' : 'short',
    },
  };
}

const passingEvents = Array.from(
  { length: 8 },
  (_, index) => validEvent(index)
);

const passingPayload = buildJimmyPaigeAnalysisPayload(
  {
    generatedTab: 'e|--3--5--7--8--|',
    liveV143: safeLiveV143(),
    events: passingEvents,
    tuning: 'E A D G B E',
    tempo: 120,
    timeSignature: '4/4',
  },
  {
    transcriptionType: 'rhythm',
    usingV143RhythmAnalyzer: true,
  }
);

assert.equal(
  passingPayload.analysisQuality?.passed,
  true,
  'valid V143 fixture should pass analyzer quality gate'
);
assert.equal(
  passingPayload.payloadContract?.structuredRenderEligible,
  true,
  'valid V143 fixture should be structured-render eligible'
);
assert.equal(
  passingPayload.analysisEngine,
  'v143-reference-free-rhythm',
  'passing V143 fixture should expose structured engine identity'
);
assert.equal(
  passingPayload.renderEvents.length,
  8,
  'all valid fixture events should survive projection'
);
assert.equal(
  passingPayload.payloadContract?.productionPromotionAuthorized,
  false,
  'payload must never authorize production promotion'
);
assert.equal(
  passingPayload.analysisQuality?.productionPromotionAuthorized,
  false,
  'quality report must never authorize production promotion'
);

const failingEvents = Array.from(
  { length: 8 },
  (_, index) => ({
    ...validEvent(index),
    measure: index === 0 ? 1 : undefined,
    step: index === 0 ? 0 : undefined,
  })
);

const failingPayload = buildJimmyPaigeAnalysisPayload(
  {
    generatedTab: 'e|--3-----------|',
    liveV143: safeLiveV143(),
    events: failingEvents,
  },
  {
    transcriptionType: 'rhythm',
    usingV143RhythmAnalyzer: true,
  }
);

assert.equal(
  failingPayload.analysisQuality?.passed,
  false,
  'sparse musical placement must fail analyzer quality gate'
);
assert.equal(
  failingPayload.payloadContract?.structuredRenderEligible,
  false,
  'failed V143 quality must not be structured-render eligible'
);
assert.equal(
  failingPayload.analysisEngine,
  'v143-reference-free-rhythm-fallback',
  'failed V143 quality must be labeled fallback-only'
);
assert.ok(
  failingPayload.analysisQuality?.failures.includes(
    'render-event-survival-below-threshold'
  ),
  'failed fixture should report render-event survival failure'
);
assert.ok(
  failingPayload.analysisQuality?.failures.includes(
    'measure-step-coverage-below-threshold'
  ),
  'failed fixture should report measure/step coverage failure'
);
assert.ok(
  failingPayload.generatedTab.length > 0,
  'fallback-only V143 response should preserve generated tab text'
);

const legacyPayload = buildJimmyPaigeAnalysisPayload(
  {
    generatedTab: 'e|--0--2--3--|',
    events: [],
  },
  {
    transcriptionType: 'lead',
    usingV143RhythmAnalyzer: false,
  }
);

assert.equal(
  legacyPayload.analysisEngine,
  'legacy',
  'legacy Lead/Bass path must remain legacy'
);
assert.equal(
  legacyPayload.analysisQuality,
  null,
  'legacy path must not be subjected to V143 quality gate'
);

assert.throws(
  () =>
    buildJimmyPaigeAnalysisPayload(
      {
        generatedTab: 'e|--0--|',
        liveV143: safeLiveV143({
          referenceFree: false,
        }),
        events: passingEvents,
      },
      {
        transcriptionType: 'rhythm',
        usingV143RhythmAnalyzer: true,
      }
    ),
  /failed the reference-free runtime safety contract/i,
  'V143 anti-leakage identity mismatch must remain fail-closed'
);

console.log('=== V143 ANALYZER QUALITY GATE VERIFIED ===');
console.log(`passingRenderEvents: ${passingPayload.renderEvents.length}`);
console.log(
  `passingSurvivalPercent: ${passingPayload.analysisQuality.metrics.renderEventSurvivalPercent}`
);
console.log(
  `failingRenderEvents: ${failingPayload.renderEvents.length}`
);
console.log(
  `failingReasons: ${failingPayload.analysisQuality.failures.join(',')}`
);
console.log(`legacyEngine: ${legacyPayload.analysisEngine}`);
console.log('productionPromotionAuthorized: false');
