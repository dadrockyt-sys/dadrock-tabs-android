import {
  findPlayableShape,
  groupOnsetClusters,
  normalizeConditioning,
} from './index.mjs';

const EPSILON = 1e-9;
const DENOMINATORS = new Set([1, 2, 4, 8, 16, 32]);
const FEELS = new Set(['straight', 'triplet']);

function finiteNumber(value, field) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`${field} must be finite.`);
  return parsed;
}

function nonNegativeNumber(value, field) {
  const parsed = finiteNumber(value, field);
  if (parsed < 0) throw new Error(`${field} must be non-negative.`);
  return parsed;
}

function normalizeConfidence(value, field) {
  if (value === undefined || value === null) return null;
  const parsed = finiteNumber(value, field);
  if (parsed < 0 || parsed > 1) throw new Error(`${field} must be between 0 and 1.`);
  return parsed;
}

function normalizeProvenance(value, fallback = 'provided') {
  if (value === undefined || value === null) return { source: fallback };
  if (typeof value === 'string') return { source: value };
  if (typeof value !== 'object' || Array.isArray(value)) {
    throw new Error('provenance must be a string or object.');
  }
  return { ...value };
}

function normalizeTempoSegments(raw) {
  if (!Array.isArray(raw) || raw.length === 0) {
    throw new Error('tempoSegments must be a non-empty array.');
  }

  const segments = raw.map((segment, index) => {
    const start = nonNegativeNumber(segment?.start ?? 0, `tempoSegments[${index}].start`);
    const bpm = finiteNumber(segment?.bpm, `tempoSegments[${index}].bpm`);
    if (bpm < 20 || bpm > 400) throw new Error(`tempoSegments[${index}].bpm must be between 20 and 400.`);
    const end = segment?.end === undefined || segment?.end === null
      ? null
      : finiteNumber(segment.end, `tempoSegments[${index}].end`);
    if (end !== null && end <= start) throw new Error(`tempoSegments[${index}].end must be greater than start.`);
    return {
      start,
      end,
      bpm,
      confidence: normalizeConfidence(segment?.confidence, `tempoSegments[${index}].confidence`),
      provenance: normalizeProvenance(segment?.provenance, 'tempo-segment'),
    };
  }).sort((a, b) => a.start - b.start);

  for (let index = 1; index < segments.length; index += 1) {
    const previous = segments[index - 1];
    const current = segments[index];
    if (previous.end === null || current.start < previous.end - EPSILON) {
      throw new Error('tempoSegments must be ordered and non-overlapping.');
    }
  }
  return segments;
}

function normalizeMeterSegments(raw) {
  if (!Array.isArray(raw) || raw.length === 0) {
    throw new Error('meterSegments must be a non-empty array.');
  }

  const segments = raw.map((segment, index) => {
    const start = nonNegativeNumber(segment?.start ?? 0, `meterSegments[${index}].start`);
    const numerator = segment?.numerator;
    const denominator = segment?.denominator;
    if (!Number.isInteger(numerator) || numerator < 1 || numerator > 32) {
      throw new Error(`meterSegments[${index}].numerator must be an integer from 1 to 32.`);
    }
    if (!Number.isInteger(denominator) || !DENOMINATORS.has(denominator)) {
      throw new Error(`meterSegments[${index}].denominator is invalid.`);
    }
    const end = segment?.end === undefined || segment?.end === null
      ? null
      : finiteNumber(segment.end, `meterSegments[${index}].end`);
    if (end !== null && end <= start) throw new Error(`meterSegments[${index}].end must be greater than start.`);
    return {
      start,
      end,
      numerator,
      denominator,
      confidence: normalizeConfidence(segment?.confidence, `meterSegments[${index}].confidence`),
      provenance: normalizeProvenance(segment?.provenance, 'meter-segment'),
    };
  }).sort((a, b) => a.start - b.start);

  for (let index = 1; index < segments.length; index += 1) {
    const previous = segments[index - 1];
    const current = segments[index];
    if (previous.end === null || current.start < previous.end - EPSILON) {
      throw new Error('meterSegments must be ordered and non-overlapping.');
    }
  }
  return segments;
}

function normalizeFeelSegments(raw) {
  if (!Array.isArray(raw) || raw.length === 0) {
    throw new Error('feelSegments must be a non-empty array.');
  }

  const segments = raw.map((segment, index) => {
    const start = nonNegativeNumber(segment?.start ?? 0, `feelSegments[${index}].start`);
    const feel = segment?.feel;
    if (!FEELS.has(feel)) throw new Error(`feelSegments[${index}].feel must be straight or triplet.`);
    const end = segment?.end === undefined || segment?.end === null
      ? null
      : finiteNumber(segment.end, `feelSegments[${index}].end`);
    if (end !== null && end <= start) throw new Error(`feelSegments[${index}].end must be greater than start.`);
    return {
      start,
      end,
      feel,
      subdivisionsPerBeatUnit: feel === 'triplet' ? 3 : 4,
      confidence: normalizeConfidence(segment?.confidence, `feelSegments[${index}].confidence`),
      provenance: normalizeProvenance(segment?.provenance, 'feel-segment'),
    };
  }).sort((a, b) => a.start - b.start);

  for (let index = 1; index < segments.length; index += 1) {
    const previous = segments[index - 1];
    const current = segments[index];
    if (previous.end === null || current.start < previous.end - EPSILON) {
      throw new Error('feelSegments must be ordered and non-overlapping.');
    }
  }
  return segments;
}

function activeSegmentAt(segments, seconds, label) {
  const match = segments.find((segment) => (
    seconds + EPSILON >= segment.start
    && (segment.end === null || seconds < segment.end - EPSILON)
  ));
  if (!match) throw new Error(`No active ${label} segment at ${seconds}.`);
  return match;
}

function nextChangeAfter(seconds, segmentLists) {
  let next = null;
  for (const segments of segmentLists) {
    for (const segment of segments) {
      if (segment.start > seconds + EPSILON && (next === null || segment.start < next)) {
        next = segment.start;
      }
    }
  }
  return next;
}

function beatUnitSeconds(tempo, meter) {
  return (60 / tempo.bpm) * (4 / meter.denominator);
}

function buildBeat(beatNumber, start, end, feel) {
  const subdivisions = [];
  const count = feel.subdivisionsPerBeatUnit;
  const duration = end - start;
  for (let slot = 0; slot < count; slot += 1) {
    subdivisions.push(start + (duration * slot / count));
  }
  return {
    beatNumber,
    start,
    end,
    subdivisions,
  };
}

function buildMeasure({
  measureNumber,
  start,
  end,
  pickup,
  tempo,
  meter,
  feel,
}) {
  const unit = beatUnitSeconds(tempo, meter);
  const beats = [];
  let cursor = start;
  let beatNumber = 1;

  while (cursor < end - EPSILON) {
    const beatEnd = Math.min(end, cursor + unit);
    beats.push(buildBeat(beatNumber, cursor, beatEnd, feel));
    cursor = beatEnd;
    beatNumber += 1;
    if (beatNumber > 128) throw new Error('Beat materialization exceeded safety limit.');
  }

  return {
    measureNumber,
    start,
    end,
    durationSeconds: end - start,
    pickup,
    tempoBpm: tempo.bpm,
    timeSignature: { numerator: meter.numerator, denominator: meter.denominator },
    feel: feel.feel,
    subdivisionsPerBeatUnit: feel.subdivisionsPerBeatUnit,
    confidence: {
      tempo: tempo.confidence,
      meter: meter.confidence,
      feel: feel.confidence,
    },
    provenance: {
      tempo: { ...tempo.provenance },
      meter: { ...meter.provenance },
      feel: { ...feel.provenance },
    },
    beats,
  };
}

function validateSegmentCoverage(segments, durationSeconds, label) {
  if (segments[0].start > EPSILON) {
    throw new Error(`${label} must begin at 0.`);
  }
  for (let index = 0; index < segments.length - 1; index += 1) {
    const current = segments[index];
    const next = segments[index + 1];
    if (current.end === null || Math.abs(current.end - next.start) > EPSILON) {
      throw new Error(`${label} must cover time continuously without gaps.`);
    }
  }
  const last = segments.at(-1);
  if (last.end !== null && last.end < durationSeconds - EPSILON) {
    throw new Error(`${label} does not cover durationSeconds.`);
  }
}

export function buildStructureMap({
  durationSeconds,
  pickupDurationSeconds = 0,
  tempoSegments,
  meterSegments,
  feelSegments,
  confidence = {},
  provenance = {},
} = {}) {
  const duration = finiteNumber(durationSeconds, 'durationSeconds');
  if (duration <= 0) throw new Error('durationSeconds must be positive.');

  const pickupDuration = nonNegativeNumber(pickupDurationSeconds, 'pickupDurationSeconds');
  if (pickupDuration >= duration - EPSILON) {
    throw new Error('pickupDurationSeconds must be shorter than durationSeconds.');
  }

  const tempos = normalizeTempoSegments(tempoSegments);
  const meters = normalizeMeterSegments(meterSegments);
  const feels = normalizeFeelSegments(feelSegments);
  validateSegmentCoverage(tempos, duration, 'tempoSegments');
  validateSegmentCoverage(meters, duration, 'meterSegments');
  validateSegmentCoverage(feels, duration, 'feelSegments');

  const measures = [];
  const downbeats = [];
  let cursor = 0;

  if (pickupDuration > EPSILON) {
    const tempo = activeSegmentAt(tempos, 0, 'tempo');
    const meter = activeSegmentAt(meters, 0, 'meter');
    const feel = activeSegmentAt(feels, 0, 'feel');
    measures.push(buildMeasure({
      measureNumber: 0,
      start: 0,
      end: pickupDuration,
      pickup: true,
      tempo,
      meter,
      feel,
    }));
    cursor = pickupDuration;
  }

  let measureNumber = 1;
  let guard = 0;
  while (cursor < duration - EPSILON) {
    guard += 1;
    if (guard > 10000) throw new Error('Measure materialization exceeded safety limit.');

    const tempo = activeSegmentAt(tempos, cursor, 'tempo');
    const meter = activeSegmentAt(meters, cursor, 'meter');
    const feel = activeSegmentAt(feels, cursor, 'feel');
    const naturalEnd = cursor + beatUnitSeconds(tempo, meter) * meter.numerator;
    const nextChange = nextChangeAfter(cursor, [tempos, meters, feels]);

    if (nextChange !== null && nextChange < naturalEnd - EPSILON) {
      throw new Error(`STRUCTURE_CHANGE_MUST_ALIGN_TO_MEASURE_BOUNDARY at ${nextChange}.`);
    }

    const end = Math.min(duration, naturalEnd);
    const measure = buildMeasure({
      measureNumber,
      start: cursor,
      end,
      pickup: false,
      tempo,
      meter,
      feel,
    });
    measures.push(measure);
    downbeats.push({
      time: cursor,
      measureNumber,
      confidence: normalizeConfidence(confidence?.downbeats, 'confidence.downbeats'),
      provenance: normalizeProvenance(provenance?.downbeats, 'materialized-downbeat'),
    });
    cursor = end;
    measureNumber += 1;
  }

  return normalizeStructureMap({
    version: 1,
    referenceBlind: true,
    durationSeconds: duration,
    pickupDurationSeconds: pickupDuration,
    tempoSegments: tempos,
    meterSegments: meters,
    feelSegments: feels,
    downbeats,
    measures,
    confidence: {
      overall: normalizeConfidence(confidence?.overall, 'confidence.overall'),
      tempo: normalizeConfidence(confidence?.tempo, 'confidence.tempo'),
      meter: normalizeConfidence(confidence?.meter, 'confidence.meter'),
      downbeats: normalizeConfidence(confidence?.downbeats, 'confidence.downbeats'),
      measures: normalizeConfidence(confidence?.measures, 'confidence.measures'),
      feel: normalizeConfidence(confidence?.feel, 'confidence.feel'),
    },
    provenance: normalizeProvenance(provenance, 'structure-map-builder'),
  });
}

export function normalizeStructureMap(raw = {}) {
  if (raw?.version !== 1) throw new Error('structureMap.version must be 1.');
  const durationSeconds = finiteNumber(raw?.durationSeconds, 'structureMap.durationSeconds');
  if (durationSeconds <= 0) throw new Error('structureMap.durationSeconds must be positive.');
  const pickupDurationSeconds = nonNegativeNumber(raw?.pickupDurationSeconds ?? 0, 'structureMap.pickupDurationSeconds');

  if (!Array.isArray(raw?.measures) || raw.measures.length === 0) {
    throw new Error('structureMap.measures must be a non-empty array.');
  }

  let previousEnd = 0;
  const measures = raw.measures.map((measure, index) => {
    const start = finiteNumber(measure?.start, `structureMap.measures[${index}].start`);
    const end = finiteNumber(measure?.end, `structureMap.measures[${index}].end`);
    if (end <= start) throw new Error(`structureMap.measures[${index}].end must be greater than start.`);
    if (index > 0 && Math.abs(start - previousEnd) > EPSILON) {
      throw new Error('structureMap.measures must be contiguous and ordered.');
    }
    previousEnd = end;

    if (!Array.isArray(measure?.beats) || measure.beats.length === 0) {
      throw new Error(`structureMap.measures[${index}].beats must be non-empty.`);
    }

    const beats = measure.beats.map((beat, beatIndex) => {
      const beatStart = finiteNumber(beat?.start, `structureMap.measures[${index}].beats[${beatIndex}].start`);
      const beatEnd = finiteNumber(beat?.end, `structureMap.measures[${index}].beats[${beatIndex}].end`);
      if (beatEnd <= beatStart) throw new Error('structureMap beat end must be greater than start.');
      const subdivisions = [...(beat?.subdivisions || [])].map((value, slotIndex) => (
        finiteNumber(value, `structureMap.measures[${index}].beats[${beatIndex}].subdivisions[${slotIndex}]`)
      ));
      if (subdivisions.length === 0) throw new Error('structureMap beats must contain subdivision positions.');
      for (let slot = 1; slot < subdivisions.length; slot += 1) {
        if (subdivisions[slot] <= subdivisions[slot - 1] + EPSILON) {
          throw new Error('structureMap beat subdivisions must be strictly increasing.');
        }
      }
      if (subdivisions[0] < beatStart - EPSILON || subdivisions.at(-1) >= beatEnd - EPSILON) {
        throw new Error('structureMap beat subdivisions must fall inside the beat.');
      }
      return {
        beatNumber: beat.beatNumber,
        start: beatStart,
        end: beatEnd,
        subdivisions,
      };
    });

    return {
      ...measure,
      start,
      end,
      durationSeconds: end - start,
      timeSignature: { ...measure.timeSignature },
      confidence: { ...(measure.confidence || {}) },
      provenance: { ...(measure.provenance || {}) },
      beats,
    };
  });

  if (Math.abs(measures.at(-1).end - durationSeconds) > EPSILON) {
    throw new Error('structureMap measures must end at durationSeconds.');
  }

  return {
    version: 1,
    referenceBlind: raw.referenceBlind !== false,
    durationSeconds,
    pickupDurationSeconds,
    tempoSegments: raw.tempoSegments.map((segment) => ({ ...segment, provenance: { ...segment.provenance } })),
    meterSegments: raw.meterSegments.map((segment) => ({ ...segment, provenance: { ...segment.provenance } })),
    feelSegments: raw.feelSegments.map((segment) => ({ ...segment, provenance: { ...segment.provenance } })),
    downbeats: (raw.downbeats || []).map((downbeat) => ({ ...downbeat, provenance: { ...(downbeat.provenance || {}) } })),
    measures,
    confidence: { ...(raw.confidence || {}) },
    provenance: { ...(raw.provenance || {}) },
  };
}

export function locateInStructureMap(seconds, structureMap) {
  const map = normalizeStructureMap(structureMap);
  const timestamp = Math.min(map.durationSeconds, Math.max(0, finiteNumber(seconds, 'seconds')));
  const measure = map.measures.find((candidate, index) => (
    timestamp + EPSILON >= candidate.start
    && (timestamp < candidate.end - EPSILON || index === map.measures.length - 1)
  )) ?? map.measures.at(-1);

  const beat = measure.beats.find((candidate, index) => (
    timestamp + EPSILON >= candidate.start
    && (timestamp < candidate.end - EPSILON || index === measure.beats.length - 1)
  )) ?? measure.beats.at(-1);

  const beatFraction = Math.max(0, Math.min(0.999999999, (timestamp - beat.start) / (beat.end - beat.start)));
  return {
    measureNumber: measure.measureNumber,
    beatNumber: beat.beatNumber,
    beatFraction,
    pickup: Boolean(measure.pickup),
    tempoBpm: measure.tempoBpm,
    timeSignature: { ...measure.timeSignature },
    feel: measure.feel,
  };
}

export function snapTimestampToStructureMap(seconds, structureMap) {
  const map = normalizeStructureMap(structureMap);
  const sourceStart = Math.min(map.durationSeconds, Math.max(0, finiteNumber(seconds, 'seconds')));
  const candidates = [];

  for (const measure of map.measures) {
    for (const beat of measure.beats) {
      for (const subdivision of beat.subdivisions) candidates.push(subdivision);
    }
  }
  candidates.push(map.durationSeconds);

  let projectedStart = candidates[0];
  let bestDistance = Math.abs(sourceStart - projectedStart);
  for (const candidate of candidates.slice(1)) {
    const distance = Math.abs(sourceStart - candidate);
    if (distance < bestDistance - EPSILON || (Math.abs(distance - bestDistance) <= EPSILON && candidate < projectedStart)) {
      projectedStart = candidate;
      bestDistance = distance;
    }
  }

  return {
    sourceStart,
    projectedStart,
    displacementSeconds: projectedStart - sourceStart,
    moved: bestDistance > EPSILON,
    position: locateInStructureMap(projectedStart, map),
  };
}

export function runStructureMappedCore({
  events,
  structureMap,
  instrumentConfig,
  onsetToleranceSeconds = 0.01,
} = {}) {
  if (!Array.isArray(events)) throw new Error('events must be an array.');
  const map = normalizeStructureMap(structureMap);
  const normalizedInstrument = normalizeConditioning({
    structurePrior: {},
    instrumentConfig,
  }).instrumentConfig;
  const clusters = groupOnsetClusters(events, onsetToleranceSeconds);
  const outputEvents = [];

  for (const cluster of clusters) {
    const timing = snapTimestampToStructureMap(cluster.anchorStart, map);
    const shape = findPlayableShape(
      cluster.events.map((event) => event.midi),
      normalizedInstrument,
    );

    cluster.events.forEach((event, clusterEventIndex) => {
      const position = shape?.assignments?.[clusterEventIndex] ?? null;
      outputEvents.push({
        sourceEventIndex: event.sourceEventIndex,
        clusterId: cluster.clusterId,
        sourceStart: event.start,
        projectedStart: timing.projectedStart,
        displacementSeconds: timing.projectedStart - event.start,
        midi: event.midi,
        measureNumber: timing.position.measureNumber,
        beatNumber: timing.position.beatNumber,
        beatFraction: timing.position.beatFraction,
        pickup: timing.position.pickup,
        tempoBpm: timing.position.tempoBpm,
        timeSignature: timing.position.timeSignature,
        feel: timing.position.feel,
        stringNumberHighToLow: position?.stringNumberHighToLow ?? null,
        lowToHighIndex: position?.lowToHighIndex ?? null,
        fret: position?.fret ?? null,
        reconstructedMidi: position?.reconstructedMidi ?? null,
        shapeResolved: Boolean(shape),
      });
    });
  }

  outputEvents.sort((a, b) => a.sourceEventIndex - b.sourceEventIndex);
  const exactMidiPreservedCount = outputEvents.filter((event, index) => event.midi === events[index].midi).length;

  return {
    pipeline: {
      name: 'songsterr-fresh-structure-mapped-core',
      version: 1,
      referenceBlind: true,
      legacyV143ScorerImported: false,
    },
    structureMap: map,
    instrumentConfig: normalizedInstrument,
    clusters: clusters.map((cluster) => ({
      clusterId: cluster.clusterId,
      anchorStart: cluster.anchorStart,
      sourceEventIndexes: cluster.events.map((event) => event.sourceEventIndex),
    })),
    events: outputEvents,
    metrics: {
      sourceCount: events.length,
      outputCount: outputEvents.length,
      countDelta: outputEvents.length - events.length,
      exactMidiPreservedCount,
      pitchPreservationRate: events.length === 0 ? 1 : exactMidiPreservedCount / events.length,
      movedOnsetCount: outputEvents.filter((event) => Math.abs(event.displacementSeconds) > EPSILON).length,
      maxAbsOnsetDisplacementSeconds: outputEvents.reduce(
        (max, event) => Math.max(max, Math.abs(event.displacementSeconds)),
        0,
      ),
      playableAssignedCount: outputEvents.filter((event) => event.reconstructedMidi === event.midi).length,
      unresolvedPlayableCount: outputEvents.filter((event) => event.reconstructedMidi !== event.midi).length,
    },
  };
}
