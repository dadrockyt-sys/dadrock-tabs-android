import test from 'node:test';
import assert from 'node:assert/strict';

import {
  encodeGuitarTechsStringFrame,
  getGuitarTechsLabelContract,
  validateGuitarTechsStringTrackMap,
} from '../guitarTechsLabelContract.mjs';

const standardTuning = [40, 45, 50, 55, 59, 64];

test('label contract preserves pinned TabCNN fret and silence semantics', () => {
  const contract = getGuitarTechsLabelContract();
  assert.equal(contract.numStrings, 6);
  assert.equal(contract.maxFret, 19);
  assert.equal(contract.classesPerString, 21);
  assert.equal(contract.totalLogits, 126);
  assert.equal(contract.silenceTablatureState, -1);
  assert.equal(contract.silenceSoftmaxClass, 20);
});

test('missing tuning abstains instead of assuming standard tuning', () => {
  const result = encodeGuitarTechsStringFrame({
    stringIndex: 0,
    activeMidiPitches: [40],
  });
  assert.deepEqual(result, { state: 'abstained', reason: 'TUNING_UNVERIFIED' });
});

test('explicit tuning maps pitch to fret while silence maps to class 20', () => {
  const openE = encodeGuitarTechsStringFrame({
    stringIndex: 0,
    activeMidiPitches: [40],
    tuningMidi: standardTuning,
  });
  assert.equal(openE.fret, 0);
  assert.equal(openE.softmaxClass, 0);

  const fret12 = encodeGuitarTechsStringFrame({
    stringIndex: 0,
    activeMidiPitches: [52],
    tuningMidi: standardTuning,
  });
  assert.equal(fret12.fret, 12);
  assert.equal(fret12.softmaxClass, 12);

  const silence = encodeGuitarTechsStringFrame({
    stringIndex: 0,
    activeMidiPitches: [],
    tuningMidi: standardTuning,
  });
  assert.equal(silence.tablatureState, -1);
  assert.equal(silence.softmaxClass, 20);
});

test('out-of-range pitch and same-string polyphony never clip or force a label', () => {
  assert.equal(
    encodeGuitarTechsStringFrame({
      stringIndex: 0,
      activeMidiPitches: [60],
      tuningMidi: standardTuning,
    }).reason,
    'FRET_OUT_OF_RANGE',
  );
  assert.equal(
    encodeGuitarTechsStringFrame({
      stringIndex: 0,
      activeMidiPitches: [40, 43],
      tuningMidi: standardTuning,
    }).reason,
    'SAME_STRING_POLYPHONY_UNREPRESENTABLE',
  );
});

test('six-track physical string mapping must be a one-to-one permutation', () => {
  assert.equal(validateGuitarTechsStringTrackMap([0, 1, 2, 3, 4, 5]), true);
  assert.equal(validateGuitarTechsStringTrackMap([5, 4, 3, 2, 1, 0]), true);
  assert.equal(validateGuitarTechsStringTrackMap([0, 1, 2, 3, 4, 4]), false);
  assert.equal(validateGuitarTechsStringTrackMap([0, 1, 2]), false);
});
