const EPSILON = 1e-9;

function approxEqual(a, b, tolerance = 1e-7) {
  return Math.abs(a - b) <= tolerance;
}

function measureFor(structureMap, measureNumber) {
  const measure = structureMap.measures.find((candidate) => candidate.measureNumber === measureNumber);
  if (!measure) throw new Error(`Unknown measureNumber ${measureNumber}.`);
  return measure;
}

function beatForTimestamp(structureMap, seconds) {
  const measure = structureMap.measures.find((candidate, index) => (
    seconds + EPSILON >= candidate.start
    && (seconds < candidate.end - EPSILON || index === structureMap.measures.length - 1)
  )) ?? structureMap.measures.at(-1);
  const beat = measure.beats.find((candidate, index) => (
    seconds + EPSILON >= candidate.start
    && (seconds < candidate.end - EPSILON || index === measure.beats.length - 1)
  )) ?? measure.beats.at(-1);
  return { measure, beat };
}

function noteName(denominator) {
  const names = {
    1: 'whole',
    2: 'half',
    4: 'quarter',
    8: 'eighth',
    16: 'sixteenth',
    32: 'thirty-second',
    64: 'sixty-fourth',
  };
  return names[denominator] ?? `1/${denominator}`;
}

function standardCandidate(beatUnits, beatDenominator) {
  const candidates = [
    { beatUnits: 4, denominator: beatDenominator / 4 },
    { beatUnits: 2, denominator: beatDenominator / 2 },
    { beatUnits: 1, denominator: beatDenominator },
    { beatUnits: 0.5, denominator: beatDenominator * 2 },
    { beatUnits: 0.25, denominator: beatDenominator * 4 },
    { beatUnits: 0.125, denominator: beatDenominator * 8 },
  ].filter((candidate) => Number.isInteger(candidate.denominator) && candidate.denominator >= 1);

  return candidates.find((candidate) => approxEqual(beatUnits, candidate.beatUnits)) ?? null;
}

function dottedCandidate(beatUnits, beatDenominator) {
  const bases = [
    { beatUnits: 2, denominator: beatDenominator / 2 },
    { beatUnits: 1, denominator: beatDenominator },
    { beatUnits: 0.5, denominator: beatDenominator * 2 },
    { beatUnits: 0.25, denominator: beatDenominator * 4 },
  ].filter((candidate) => Number.isInteger(candidate.denominator) && candidate.denominator >= 1);

  return bases.find((candidate) => approxEqual(beatUnits, candidate.beatUnits * 1.5)) ?? null;
}

export function spellDuration({
  durationSeconds,
  beatDurationSeconds,
  beatDenominator,
  feel,
} = {}) {
  if (!(durationSeconds > 0) || !(beatDurationSeconds > 0)) {
    throw new Error('durationSeconds and beatDurationSeconds must be positive.');
  }
  const beatUnits = durationSeconds / beatDurationSeconds;

  if (feel === 'triplet') {
    const tripletUnits = beatUnits * 3;
    const rounded = Math.round(tripletUnits);
    if (rounded >= 1 && rounded <= 12 && approxEqual(tripletUnits, rounded)) {
      const subdivisionDenominator = beatDenominator * 2;
      return {
        resolved: true,
        kind: 'triplet',
        beatUnits,
        name: rounded === 1
          ? `${noteName(subdivisionDenominator)} triplet`
          : `${rounded} ${noteName(subdivisionDenominator)}-triplet units`,
        denominator: subdivisionDenominator,
        dots: 0,
        tuplet: { actual: 3, normal: 2, units: rounded },
      };
    }
  }

  const dotted = dottedCandidate(beatUnits, beatDenominator);
  if (dotted) {
    return {
      resolved: true,
      kind: 'dotted',
      beatUnits,
      name: `dotted ${noteName(dotted.denominator)}`,
      denominator: dotted.denominator,
      dots: 1,
      tuplet: null,
    };
  }

  const standard = standardCandidate(beatUnits, beatDenominator);
  if (standard) {
    return {
      resolved: true,
      kind: 'standard',
      beatUnits,
      name: noteName(standard.denominator),
      denominator: standard.denominator,
      dots: 0,
      tuplet: null,
    };
  }

  return {
    resolved: false,
    kind: 'unresolved',
    beatUnits,
    name: null,
    denominator: null,
    dots: 0,
    tuplet: null,
  };
}

function strongBeatNumbers(timeSignature) {
  const numerator = timeSignature.numerator;
  if (numerator === 4) return new Set([1, 3]);
  if (numerator === 2) return new Set([1]);
  if (numerator === 3) return new Set([1]);
  if (numerator === 6) return new Set([1, 4]);
  if (numerator === 9) return new Set([1, 4, 7]);
  if (numerator === 12) return new Set([1, 4, 7, 10]);
  return new Set([1]);
}

function boundaryIsStrong(structureMap, boundarySeconds) {
  const { measure, beat } = beatForTimestamp(structureMap, boundarySeconds + EPSILON * 10);
  if (Math.abs(boundarySeconds - measure.start) <= 1e-7) return true;
  return strongBeatNumbers(measure.timeSignature).has(beat.beatNumber);
}

function canMergeSegments(left, right, structureMap) {
  if (!approxEqual(left.end, right.start)) return false;
  if (left.measureNumber !== right.measureNumber) return false;
  if (left.syncopatedStart) return false;

  const { measure, beat } = beatForTimestamp(structureMap, left.start);
  if (!approxEqual(left.start, beat.start)) return false;
  if (boundaryIsStrong(structureMap, left.end)) return false;

  const totalDuration = right.end - left.start;
  const spelling = spellDuration({
    durationSeconds: totalDuration,
    beatDurationSeconds: beat.end - beat.start,
    beatDenominator: measure.timeSignature.denominator,
    feel: left.feel,
  });
  return spelling.resolved && spelling.kind === 'dotted';
}

function spellSegment(segment, structureMap) {
  const { measure, beat } = beatForTimestamp(structureMap, segment.start);
  const spelling = spellDuration({
    durationSeconds: segment.end - segment.start,
    beatDurationSeconds: beat.end - beat.start,
    beatDenominator: measure.timeSignature.denominator,
    feel: segment.feel ?? measure.feel,
  });
  return {
    ...segment,
    spelling,
  };
}

function contextualizeEventSegments(event, structureMap) {
  const raw = event.notation.segments;
  if (raw.length <= 1) return raw.map((segment) => spellSegment(segment, structureMap));

  const merged = [];
  for (let index = 0; index < raw.length; index += 1) {
    const current = raw[index];
    const next = raw[index + 1];
    if (next && canMergeSegments(current, next, structureMap)) {
      const combined = {
        ...current,
        end: next.end,
        durationSeconds: next.end - current.start,
        tieFromPrevious: current.tieFromPrevious,
        tieToNext: next.tieToNext,
        mergedAcrossWeakBeat: true,
        mergedSourceSegmentIndexes: [current.segmentIndex, next.segmentIndex],
      };
      merged.push(spellSegment(combined, structureMap));
      index += 1;
    } else {
      merged.push(spellSegment({
        ...current,
        mergedAcrossWeakBeat: false,
        mergedSourceSegmentIndexes: [current.segmentIndex],
      }, structureMap));
    }
  }

  return merged.map((segment, index) => ({
    ...segment,
    segmentIndex: index,
    tieFromPrevious: index > 0,
    tieToNext: index < merged.length - 1,
  }));
}

function splitRangeAtBeatBoundaries(start, end, structureMap) {
  const boundaries = new Set([start, end]);
  for (const measure of structureMap.measures) {
    for (const beat of measure.beats) {
      if (beat.start > start + EPSILON && beat.start < end - EPSILON) boundaries.add(beat.start);
      if (beat.end > start + EPSILON && beat.end < end - EPSILON) boundaries.add(beat.end);
    }
  }
  const points = [...boundaries].sort((a, b) => a - b);
  return points.slice(0, -1).map((segmentStart, index) => ({
    start: segmentStart,
    end: points[index + 1],
  }));
}

function spellRestGap(rest, structureMap) {
  return {
    ...rest,
    segments: splitRangeAtBeatBoundaries(rest.start, rest.end, structureMap).map((segment, index) => {
      const { measure, beat } = beatForTimestamp(structureMap, segment.start);
      return {
        restSegmentIndex: index,
        start: segment.start,
        end: segment.end,
        durationSeconds: segment.end - segment.start,
        measureNumber: measure.measureNumber,
        beatNumber: beat.beatNumber,
        spelling: spellDuration({
          durationSeconds: segment.end - segment.start,
          beatDurationSeconds: beat.end - beat.start,
          beatDenominator: measure.timeSignature.denominator,
          feel: measure.feel,
        }),
      };
    }),
  };
}

function phraseFeelDiagnostics(structureMap) {
  const sequence = [];
  for (const measure of structureMap.measures) {
    if (sequence.length === 0 || sequence.at(-1).feel !== measure.feel) {
      sequence.push({
        measureNumber: measure.measureNumber,
        start: measure.start,
        feel: measure.feel,
      });
    }
  }
  return {
    segmentCount: sequence.length,
    changeCount: Math.max(0, sequence.length - 1),
    consistent: sequence.length <= 1,
    sequence,
  };
}

export function applyContextualRhythmSpelling(eventSchema) {
  if (!eventSchema?.structureMap || !Array.isArray(eventSchema?.events) || !Array.isArray(eventSchema?.rests)) {
    throw new Error('eventSchema must come from buildStructureMappedEventSchema.');
  }

  const structureMap = eventSchema.structureMap;
  const events = eventSchema.events.map((event) => {
    const segments = contextualizeEventSegments(event, structureMap);
    return {
      ...event,
      notation: {
        ...event.notation,
        segments,
        contextualSpellingApplied: true,
        contextualTieSegmentCount: segments.filter((segment) => segment.tieFromPrevious || segment.tieToNext).length,
        dottedSegmentCount: segments.filter((segment) => segment.spelling.kind === 'dotted').length,
        unresolvedSpellingSegmentCount: segments.filter((segment) => !segment.spelling.resolved).length,
      },
    };
  });

  const rests = eventSchema.rests.map((rest) => spellRestGap(rest, structureMap));
  const feel = phraseFeelDiagnostics(structureMap);

  return {
    ...eventSchema,
    pipeline: {
      ...eventSchema.pipeline,
      rhythmSpelling: 'contextual-v1',
    },
    events,
    rests,
    rhythmSpelling: {
      feel,
      dottedSegmentCount: events.reduce(
        (sum, event) => sum + event.notation.dottedSegmentCount,
        0,
      ),
      unresolvedEventSegmentCount: events.reduce(
        (sum, event) => sum + event.notation.unresolvedSpellingSegmentCount,
        0,
      ),
      restSegmentCount: rests.reduce((sum, rest) => sum + rest.segments.length, 0),
      unresolvedRestSegmentCount: rests.reduce(
        (sum, rest) => sum + rest.segments.filter((segment) => !segment.spelling.resolved).length,
        0,
      ),
    },
  };
}
