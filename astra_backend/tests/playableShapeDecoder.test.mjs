import test from 'node:test';
import assert from 'node:assert/strict';

import { STANDARD_GUITAR_TUNING_MIDI } from '../index.mjs';
import { decodePlayableShape } from '../playableShapeDecoder.mjs';

function instrument(role) {
  return {
    role,
    tuningMidi: [...STANDARD_GUITAR_TUNING_MIDI],
    capoFret: 0,
  };
}

test('constrained decoder preserves every MIDI pitch and uses unique strings', () => {
  const result = decodePlayableShape([64, 59, 56], instrument('rhythm'));

  assert.equal(result.resolved, true);
  assert.equal(new Set(result.assignments.map((assignment) => assignment.lowToHighIndex)).size, 3);
  assert.deepEqual(result.assignments.map((assignment) => assignment.reconstructedMidi), [64, 59, 56]);
});

test('role-aware policy prefers an open string for rhythm but a fretted position for lead', () => {
  const rhythm = decodePlayableShape([64], instrument('rhythm'));
  const lead = decodePlayableShape([64], instrument('lead'));

  assert.equal(rhythm.assignments[0].fret, 0);
  assert.ok(lead.assignments[0].fret > 0);
});

test('impossible tight shape is rejected without dropping or changing source pitches', () => {
  const result = decodePlayableShape([64, 65], instrument('rhythm'), {
    policy: {
      maxFrettedSpan: 0,
      maxAdjacentFretDelta: 0,
    },
  });

  assert.equal(result.resolved, false);
  assert.equal(result.reason, 'NO_PLAYABLE_SHAPE_WITHIN_CONSTRAINTS');
  assert.deepEqual(result.sourceMidis, [64, 65]);
  assert.equal(result.assignments, null);
  assert.ok(result.rejectedCandidateCount > 0);
});

test('neighboring hand-position context can deterministically alter a local fingering choice', () => {
  const noContext = decodePlayableShape([64], instrument('lead'));
  const nearHighPosition = decodePlayableShape([64], instrument('lead'), {
    context: {
      previousCenterFret: 14,
    },
  });

  assert.notEqual(noContext.assignments[0].fret, nearHighPosition.assignments[0].fret);
  assert.ok(nearHighPosition.assignments[0].fret >= 9);
});

test('decoder tie-breaking is deterministic and raw shape diagnostics remain visible', () => {
  const first = decodePlayableShape([64, 59, 56], instrument('rhythm'));
  const second = decodePlayableShape([64, 59, 56], instrument('rhythm'));

  assert.deepEqual(first, second);
  assert.ok(Number.isFinite(first.diagnostics.frettedSpan));
  assert.ok(Number.isFinite(first.diagnostics.stringSpan));
  assert.ok(Number.isFinite(first.diagnostics.openStringCount));
  assert.ok(Number.isFinite(first.diagnostics.centerFret));
  assert.ok(Number.isFinite(first.diagnostics.maxAdjacentFretDelta));
  assert.ok(first.candidateCount > 0);
});
