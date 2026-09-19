import test from 'node:test';
import assert from 'node:assert/strict';

import { applyContextualRhythmSpelling } from '../contextualRhythmSpelling.mjs';

const EPSILON = 1e-9;
const LEFT_BOUNDARY = 1.0;
const RIGHT_BOUNDARY = 1.0 + 1e-14;
const SECOND_END = 1.5 + 1e-14;

function dustyStructureMap() {
  return {
    measures: [
      {
        measureNumber: 1,
        start: 0,
        end: RIGHT_BOUNDARY,
        timeSignature: { numerator: 4, denominator: 4 },
        feel: 'straight',
        beats: [
          { beatNumber: 1, start: 0, end: 0.5 },
          { beatNumber: 2, start: 0.5, end: LEFT_BOUNDARY },
        ],
      },
      {
        measureNumber: 2,
        start: RIGHT_BOUNDARY,
        end: 2.0 + 1e-14,
        timeSignature: { numerator: 4, denominator: 4 },
        feel: 'straight',
        beats: [
          { beatNumber: 1, start: RIGHT_BOUNDARY, end: SECOND_END },
          { beatNumber: 2, start: SECOND_END, end: 2.0 + 1e-14 },
        ],
      },
    ],
  };
}

function segment({ index, start, end, measureNumber, beatNumber }) {
  return {
    segmentIndex: index,
    start,
    end,
    durationSeconds: end - start,
    measureNumber,
    beatNumber,
    feel: 'straight',
    startsOnBeat: true,
    syncopatedStart: false,
    tieFromPrevious: index > 0,
    tieToNext: true,
  };
}

test('contextual rhythm spelling discards only sub-EPSILON floating-point boundary slices', () => {
  const structureMap = dustyStructureMap();
  const eventWithBoundaryDust = {
    eventId: 'event-7',
    sourceEventIndex: 7,
    midi: 64,
    sourceStart: 0.5,
    sourceEnd: SECOND_END,
    sourceDurationSeconds: SECOND_END - 0.5,
    notation: {
      segments: [
        segment({ index: 0, start: 0.5, end: LEFT_BOUNDARY, measureNumber: 1, beatNumber: 2 }),
        segment({ index: 1, start: LEFT_BOUNDARY, end: RIGHT_BOUNDARY, measureNumber: 1, beatNumber: 2 }),
        segment({ index: 2, start: RIGHT_BOUNDARY, end: SECOND_END, measureNumber: 2, beatNumber: 1 }),
      ],
    },
  };
  const eventEndingAtBoundaryDust = {
    eventId: 'event-8',
    sourceEventIndex: 8,
    midi: 67,
    sourceStart: 0.5,
    sourceEnd: RIGHT_BOUNDARY,
    sourceDurationSeconds: RIGHT_BOUNDARY - 0.5,
    notation: {
      segments: [
        segment({ index: 0, start: 0.5, end: LEFT_BOUNDARY, measureNumber: 1, beatNumber: 2 }),
        segment({ index: 1, start: LEFT_BOUNDARY, end: RIGHT_BOUNDARY, measureNumber: 1, beatNumber: 2 }),
      ],
    },
  };

  const result = applyContextualRhythmSpelling({
    pipeline: { name: 'boundary-epsilon-regression' },
    structureMap,
    events: [eventWithBoundaryDust, eventEndingAtBoundaryDust],
    rests: [{
      afterClusterId: 1,
      beforeClusterId: 2,
      start: 0.5,
      end: SECOND_END,
      durationSeconds: SECOND_END - 0.5,
    }],
  });

  assert.equal(result.rhythmSpelling.unresolvedEventSegmentCount, 0);
  assert.equal(result.rhythmSpelling.unresolvedRestSegmentCount, 0);

  assert.deepEqual(
    result.events.map(({ eventId, sourceEventIndex, midi, sourceStart, sourceEnd }) => ({
      eventId,
      sourceEventIndex,
      midi,
      sourceStart,
      sourceEnd,
    })),
    [
      { eventId: 'event-7', sourceEventIndex: 7, midi: 64, sourceStart: 0.5, sourceEnd: SECOND_END },
      { eventId: 'event-8', sourceEventIndex: 8, midi: 67, sourceStart: 0.5, sourceEnd: RIGHT_BOUNDARY },
    ],
  );

  const firstSegments = result.events[0].notation.segments;
  assert.equal(firstSegments.length, 2);
  assert.ok(firstSegments.every((row) => row.end - row.start > EPSILON));
  assert.deepEqual(firstSegments.map((row) => row.spelling.name), ['quarter', 'quarter']);
  assert.equal(firstSegments[0].tieFromPrevious, false);
  assert.equal(firstSegments[0].tieToNext, true);
  assert.equal(firstSegments[1].tieFromPrevious, true);
  assert.equal(firstSegments[1].tieToNext, false);

  const secondSegments = result.events[1].notation.segments;
  assert.equal(secondSegments.length, 1);
  assert.equal(secondSegments[0].tieFromPrevious, false);
  assert.equal(secondSegments[0].tieToNext, false);
  assert.equal(secondSegments[0].spelling.name, 'quarter');

  assert.equal(result.rests[0].segments.length, 2);
  assert.ok(result.rests[0].segments.every((row) => row.durationSeconds > EPSILON));
  assert.deepEqual(result.rests[0].segments.map((row) => row.spelling.name), ['quarter', 'quarter']);
});
