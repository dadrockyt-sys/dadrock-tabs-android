import test from 'node:test';
import assert from 'node:assert/strict';

import { STANDARD_GUITAR_TUNING_MIDI } from '../index.mjs';
import { buildMusicalEventSchema } from '../rhythmNotation.mjs';

function conditioning(overrides = {}) {
  return {
    structurePrior: {
      tempoBpm: 120,
      timeSignature: { numerator: 4, denominator: 4 },
      pickupBeats: 0,
      feel: 'straight',
      ...(overrides.structurePrior || {}),
    },
    instrumentConfig: {
      role: 'lead',
      tuningMidi: [...STANDARD_GUITAR_TUNING_MIDI],
      capoFret: 0,
      ...(overrides.instrumentConfig || {}),
    },
  };
}

test('musical event schema preserves one source identity and exact MIDI per detected note', () => {
  const result = buildMusicalEventSchema({
    conditioning: conditioning(),
    events: [
      { start: 0.125, duration: 0.25, midi: 64 },
      { start: 0.625, end: 0.875, midi: 67 },
    ],
  });

  assert.equal(result.pipeline.referenceBlind, true);
  assert.equal(result.pipeline.legacyV143ScorerImported, false);
  assert.equal(result.metrics.sourceCount, 2);
  assert.equal(result.metrics.outputEventCount, 2);
  assert.equal(result.metrics.countDelta, 0);
  assert.equal(result.metrics.exactMidiPreservedCount, 2);
  assert.deepEqual(result.events.map((event) => event.eventId), ['event-0', 'event-1']);
  assert.deepEqual(result.events.map((event) => event.midi), [64, 67]);
});

test('note crossing a beat boundary is represented by tied notation segments without duplicating the event', () => {
  const result = buildMusicalEventSchema({
    conditioning: conditioning(),
    events: [{ start: 0.375, duration: 0.25, midi: 64 }],
  });

  const event = result.events[0];
  assert.equal(result.events.length, 1);
  assert.equal(event.notation.segments.length, 2);
  assert.equal(event.notation.segments[0].start, 0.375);
  assert.equal(event.notation.segments[0].end, 0.5);
  assert.equal(event.notation.segments[0].tieFromPrevious, false);
  assert.equal(event.notation.segments[0].tieToNext, true);
  assert.equal(event.notation.segments[1].start, 0.5);
  assert.equal(event.notation.segments[1].end, 0.625);
  assert.equal(event.notation.segments[1].tieFromPrevious, true);
  assert.equal(event.notation.segments[1].tieToNext, false);
  assert.equal(result.metrics.tiedEventCount, 1);
});

test('note crossing a measure boundary keeps one event and moves the second tied segment into the next measure', () => {
  const result = buildMusicalEventSchema({
    conditioning: conditioning(),
    events: [{ start: 1.875, duration: 0.25, midi: 59 }],
  });

  const segments = result.events[0].notation.segments;
  assert.equal(segments.length, 2);
  assert.equal(segments[0].measureNumber, 1);
  assert.equal(segments[0].beatNumber, 4);
  assert.equal(segments[0].end, 2.0);
  assert.equal(segments[1].measureNumber, 2);
  assert.equal(segments[1].beatNumber, 1);
  assert.equal(segments[1].start, 2.0);
  assert.equal(result.metrics.countDelta, 0);
});

test('silent gap between duration-resolved clusters becomes a rest diagnostic, not a fake note event', () => {
  const result = buildMusicalEventSchema({
    conditioning: conditioning(),
    events: [
      { start: 0.0, duration: 0.25, midi: 64 },
      { start: 0.75, duration: 0.25, midi: 67 },
    ],
  });

  assert.equal(result.events.length, 2);
  assert.equal(result.rests.length, 1);
  assert.equal(result.rests[0].start, 0.25);
  assert.equal(result.rests[0].end, 0.75);
  assert.equal(result.rests[0].durationSeconds, 0.5);
  assert.equal(result.metrics.restGapCount, 1);
});

test('triplet feel uses three subdivisions per beat while preserving MIDI identity', () => {
  const result = buildMusicalEventSchema({
    conditioning: conditioning({ structurePrior: { feel: 'triplet' } }),
    events: [{ start: 0.17, end: 0.51, midi: 62 }],
  });

  assert.equal(result.structureGrid.subdivisionsPerBeatUnit, 3);
  assert.ok(Math.abs(result.events[0].projectedStart - (1 / 6)) < 1e-9);
  assert.ok(Math.abs(result.events[0].projectedEnd - 0.5) < 1e-9);
  assert.equal(result.events[0].midi, 62);
  assert.equal(result.metrics.countDelta, 0);
});

test('missing duration stays explicitly unresolved instead of inventing a note length', () => {
  const result = buildMusicalEventSchema({
    conditioning: conditioning(),
    events: [{ start: 0.25, midi: 64 }],
  });

  const event = result.events[0];
  assert.equal(event.durationResolved, false);
  assert.equal(event.sourceEnd, null);
  assert.equal(event.projectedEnd, null);
  assert.deepEqual(event.notation.segments, []);
  assert.equal(result.metrics.durationResolvedCount, 0);
  assert.equal(result.metrics.countDelta, 0);
});
