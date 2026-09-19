import test from 'node:test';
import assert from 'node:assert/strict';

import { STANDARD_GUITAR_TUNING_MIDI } from '../index.mjs';
import { applyContextualRhythmSpelling, spellDuration } from '../contextualRhythmSpelling.mjs';
import { buildStructureMap } from '../structureMap.mjs';
import { buildStructureMappedEventSchema } from '../structureRhythmNotation.mjs';

function instrument() {
  return {
    role: 'lead',
    tuningMidi: [...STANDARD_GUITAR_TUNING_MIDI],
    capoFret: 0,
  };
}

function map4x4({ durationSeconds = 4, feel = 'straight' } = {}) {
  return buildStructureMap({
    durationSeconds,
    tempoSegments: [{ start: 0, end: null, bpm: 120 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
    feelSegments: [{ start: 0, end: null, feel }],
  });
}

test('duration spelling recognizes standard, dotted, and triplet values in beat-relative units', () => {
  assert.equal(spellDuration({
    durationSeconds: 0.5,
    beatDurationSeconds: 0.5,
    beatDenominator: 4,
    feel: 'straight',
  }).name, 'quarter');

  assert.equal(spellDuration({
    durationSeconds: 0.75,
    beatDurationSeconds: 0.5,
    beatDenominator: 4,
    feel: 'straight',
  }).name, 'dotted quarter');

  const triplet = spellDuration({
    durationSeconds: 1 / 6,
    beatDurationSeconds: 0.5,
    beatDenominator: 4,
    feel: 'triplet',
  });
  assert.equal(triplet.kind, 'triplet');
  assert.equal(triplet.denominator, 8);
});

test('contextual spelling merges across a weak beat boundary when a dotted value is cleaner', () => {
  const schema = buildStructureMappedEventSchema({
    structureMap: map4x4(),
    instrumentConfig: instrument(),
    events: [{ start: 0, duration: 0.75, midi: 64 }],
  });
  const result = applyContextualRhythmSpelling(schema);
  const segments = result.events[0].notation.segments;

  assert.equal(segments.length, 1);
  assert.equal(segments[0].mergedAcrossWeakBeat, true);
  assert.equal(segments[0].spelling.kind, 'dotted');
  assert.equal(segments[0].spelling.name, 'dotted quarter');
  assert.equal(segments[0].tieToNext, false);
});

test('contextual spelling preserves a tie across the strong beat-3 boundary in 4/4', () => {
  const schema = buildStructureMappedEventSchema({
    structureMap: map4x4(),
    instrumentConfig: instrument(),
    events: [{ start: 0.5, duration: 0.75, midi: 64 }],
  });
  const result = applyContextualRhythmSpelling(schema);
  const segments = result.events[0].notation.segments;

  assert.equal(segments.length, 2);
  assert.equal(segments[0].end, 1.0);
  assert.equal(segments[0].tieToNext, true);
  assert.equal(segments[1].tieFromPrevious, true);
});

test('rest gaps are explicitly segmented and spelled without creating note events', () => {
  const schema = buildStructureMappedEventSchema({
    structureMap: map4x4(),
    instrumentConfig: instrument(),
    events: [
      { start: 0, duration: 0.25, midi: 64 },
      { start: 0.75, duration: 0.25, midi: 67 },
    ],
  });
  const result = applyContextualRhythmSpelling(schema);

  assert.equal(result.events.length, 2);
  assert.equal(result.rests.length, 1);
  assert.equal(result.rests[0].segments.length, 2);
  assert.deepEqual(result.rests[0].segments.map((segment) => segment.spelling.name), ['eighth', 'eighth']);
  assert.equal(result.rhythmSpelling.restSegmentCount, 2);
});

test('phrase-level feel diagnostics report a structure-map feel change without rewriting note identity', () => {
  const structureMap = buildStructureMap({
    durationSeconds: 4,
    tempoSegments: [{ start: 0, end: null, bpm: 120 }],
    meterSegments: [{ start: 0, end: null, numerator: 4, denominator: 4 }],
    feelSegments: [
      { start: 0, end: 2, feel: 'straight' },
      { start: 2, end: null, feel: 'triplet' },
    ],
  });
  const schema = buildStructureMappedEventSchema({
    structureMap,
    instrumentConfig: instrument(),
    events: [
      { start: 0.25, duration: 0.25, midi: 64 },
      { start: 2 + (1 / 6), duration: 1 / 6, midi: 67 },
    ],
  });
  const result = applyContextualRhythmSpelling(schema);

  assert.equal(result.rhythmSpelling.feel.consistent, false);
  assert.equal(result.rhythmSpelling.feel.changeCount, 1);
  assert.deepEqual(result.events.map((event) => event.eventId), ['event-0', 'event-1']);
  assert.deepEqual(result.events.map((event) => event.midi), [64, 67]);
});
