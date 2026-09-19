import { applyContextualRhythmSpelling } from './contextualRhythmSpelling.mjs';
import { buildProductShellPayload } from './productShellAdapter.mjs';
import { applyOptimizedFretboardPath } from './structureFretboardPath.mjs';
import { buildStructureMappedEventSchema } from './structureRhythmNotation.mjs';

function cloneSourceIdentity(events) {
  return events.map((event, sourceEventIndex) => ({
    sourceEventIndex,
    midi: event?.midi,
    start: event?.start,
    end: event?.end ?? null,
    duration: event?.duration ?? null,
  }));
}

export function runFreshDeterministicPipeline({
  events,
  structureMap,
  instrumentConfig,
  onsetToleranceSeconds = 0.01,
  fretboardPathOptions = {},
  productShell = {},
} = {}) {
  if (!Array.isArray(events)) throw new Error('events must be an array.');
  if (!structureMap) throw new Error('structureMap is required.');
  if (!instrumentConfig) throw new Error('instrumentConfig is required.');

  const sourceIdentity = cloneSourceIdentity(events);

  const eventSchema = buildStructureMappedEventSchema({
    events,
    structureMap,
    instrumentConfig,
    onsetToleranceSeconds,
  });

  const rhythmSpelled = applyContextualRhythmSpelling(eventSchema);
  const fretboardResolved = applyOptimizedFretboardPath(
    rhythmSpelled,
    fretboardPathOptions,
  );

  const payload = buildProductShellPayload({
    result: fretboardResolved,
    sourceEvents: events,
    ...productShell,
  });

  const finalIdentity = fretboardResolved.events.map((event) => ({
    sourceEventIndex: event.sourceEventIndex,
    midi: event.midi,
    start: event.sourceStart,
    end: event.sourceEnd,
    duration: event.sourceDurationSeconds,
  }));

  return {
    pipeline: {
      name: 'songsterr-fresh-deterministic-pipeline',
      version: 1,
      referenceBlind: true,
      legacyV143ScorerImported: false,
      modelOrAudioAnalyzerInvoked: false,
    },
    sourceIdentity,
    finalIdentity,
    structureMap: fretboardResolved.structureMap,
    instrumentConfig: fretboardResolved.instrumentConfig,
    events: fretboardResolved.events,
    rests: fretboardResolved.rests,
    rhythmSpelling: fretboardResolved.rhythmSpelling ?? null,
    fretboardPath: fretboardResolved.fretboardPath ?? null,
    metrics: fretboardResolved.metrics ?? null,
    freshDiagnostics: payload.freshDiagnostics,
    productShell: payload,
  };
}
