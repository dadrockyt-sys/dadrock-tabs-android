import test from 'node:test';
import assert from 'node:assert/strict';

import { STANDARD_GUITAR_TUNING_MIDI } from '../index.mjs';
import { decodePlayableShape, enumeratePlayableShapes } from '../playableShapeDecoder.mjs';
import { optimizeFretboardPath } from '../fretboardPathOptimizer.mjs';

const leadInstrument = {
  role: 'lead',
  tuningMidi: [...STANDARD_GUITAR_TUNING_MIDI],
  capoFret: 0,
};

test('candidate enumeration returns multiple legal exact-MIDI states', () => {
  const enumeration = enumeratePlayableShapes([64], leadInstrument, { limit: 20 });

  assert.equal(enumeration.resolved, true);
  assert.ok(enumeration.candidates.length > 1);
  for (const candidate of enumeration.candidates) {
    assert.equal(candidate.assignments[0].reconstructedMidi, 64);
  }
});

test('global path reduces hand movement versus independent local decoding', () => {
  const onsetGroups = [
    { midis: [64] },
    { midis: [76] },
    { midis: [64] },
  ];

  const independentCenters = onsetGroups.map((group) => (
    decodePlayableShape(group.midis, leadInstrument).diagnostics.centerFret
  ));
  const independentMovement = Math.abs(independentCenters[1] - independentCenters[0])
    + Math.abs(independentCenters[2] - independentCenters[1]);

  const result = optimizeFretboardPath({
    onsetGroups,
    instrumentConfig: leadInstrument,
  });

  assert.equal(result.resolved, true);
  assert.ok(result.metrics.totalCenterFretMovement < independentMovement);
  assert.deepEqual(result.path.map((state) => state.sourceMidis), [[64], [76], [64]]);
});

test('every chosen chord state preserves exact pitches and unique strings', () => {
  const result = optimizeFretboardPath({
    onsetGroups: [
      { midis: [64, 59, 56] },
      { midis: [65, 60, 57] },
    ],
    instrumentConfig: {
      ...leadInstrument,
      role: 'rhythm',
    },
  });

  assert.equal(result.resolved, true);
  for (const state of result.path) {
    assert.deepEqual(state.assignments.map((assignment) => assignment.reconstructedMidi), state.sourceMidis);
    assert.equal(new Set(state.assignments.map((assignment) => assignment.lowToHighIndex)).size, state.assignments.length);
  }
});

test('unresolved onset aborts the phrase explicitly without dropping notes', () => {
  const result = optimizeFretboardPath({
    onsetGroups: [
      { midis: [64] },
      { midis: [64, 65] },
    ],
    instrumentConfig: {
      ...leadInstrument,
      role: 'rhythm',
    },
    policy: {
      maxFrettedSpan: 0,
      maxAdjacentFretDelta: 0,
    },
  });

  assert.equal(result.resolved, false);
  assert.equal(result.reason, 'UNRESOLVED_ONSET_SHAPE');
  assert.equal(result.unresolvedOnsetIndex, 1);
  assert.deepEqual(result.sourceMidis, [[64], [64, 65]]);
});

test('phrase path selection is deterministic and exposes raw movement diagnostics', () => {
  const input = {
    onsetGroups: [
      { midis: [64] },
      { midis: [76] },
      { midis: [67] },
    ],
    instrumentConfig: leadInstrument,
  };

  const first = optimizeFretboardPath(input);
  const second = optimizeFretboardPath(input);

  assert.deepEqual(first, second);
  assert.ok(Number.isFinite(first.metrics.totalCenterFretMovement));
  assert.ok(Number.isFinite(first.metrics.maxCenterFretMovement));
  assert.equal(first.metrics.unresolvedOnsetCount, 0);
});
