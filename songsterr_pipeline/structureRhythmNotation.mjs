import {
  locateInStructureMap,
  normalizeStructureMap,
  runStructureMappedCore,
  snapTimestampToStructureMap,
} from './structureMap.mjs';

const EPSILON = 1e-9;

function finiteNumber(value, field) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`${field} must be finite.`);
  return parsed;
}

function resolveSourceEnd(event, index) {
  const start = Math.max(0, finiteNumber(event?.start, `events[${index}].start`));

  if (event?.end !== undefined && event?.end !== null) {
    const end = finiteNumber(event.end, `events[${index}].end`);
    if (end <= start) throw new Error(`events[${index}].end must be greater than start.`);
    return end;
  }

  if (event?.duration !== undefined && event?.duration !== null) {
    const duration = finiteNumber(event.duration, `events[${index}].duration`);
    if (duration <= 0) throw new Error(`events[${index}].duration must be positive.`);
    return start + duration;
  }

  return null;
}

function structureSlots(structureMap) {
  const slots = new Set([0, structureMap.durationSeconds]);
  for (const measure of structureMap.measures) {
    slots.add(measure.start);
    slots.add(measure.end);
    for (const beat of measure.beats) {
      slots.add(beat.start);
      slots.add(beat.end);
      for (const subdivision of beat.subdivisions) slots.add(subdivision);
    }
  }
  return [...slots].sort((a, b) => a - b);
}

function nextSlotAfter(seconds, structureMap) {
  return structureSlots(structureMap).find((slot) => slot > seconds + EPSILON) ?? null;
}

function projectEnd(sourceEnd, projectedStart, structureMap) {
  if (sourceEnd === null) {
    return {
      sourceEnd: null,
      projectedEnd: null,
      displacementSeconds: 0,
      moved: false,
      durationResolved: false,
    };
  }

  const snapped = snapTimestampToStructureMap(sourceEnd, structureMap);
  let projectedEnd = snapped.projectedStart;
  if (projectedEnd <= projectedStart + EPSILON) {
    projectedEnd = nextSlotAfter(projectedStart, structureMap);
    if (projectedEnd === null) projectedEnd = structureMap.durationSeconds;
  }

  if (projectedEnd <= projectedStart + EPSILON) {
    throw new Error('Resolved note duration collapsed at the end of structureMap.');
  }

  return {
    sourceEnd,
    projectedEnd,
    displacementSeconds: projectedEnd - sourceEnd,
    moved: Math.abs(projectedEnd - sourceEnd) > EPSILON,
    durationResolved: true,
  };
}

function beatBoundaries(structureMap) {
  const boundaries = new Set([0, structureMap.durationSeconds]);
  for (const measure of structureMap.measures) {
    boundaries.add(measure.start);
    boundaries.add(measure.end);
    for (const beat of measure.beats) {
      boundaries.add(beat.start);
      boundaries.add(beat.end);
    }
  }
  return [...boundaries].sort((a, b) => a - b);
}

function splitAtStructureBeatBoundaries(start, end, structureMap) {
  if (end <= start + EPSILON) return [{ start, end }];
  const cuts = beatBoundaries(structureMap).filter((boundary) => (
    boundary > start + EPSILON && boundary < end - EPSILON
  ));
  const points = [start, ...cuts, end];
  return points.slice(0, -1).map((segmentStart, index) => ({
    start: segmentStart,
    end: points[index + 1],
  }));
}

function buildNotationSegments(projectedStart, projectedEnd, structureMap) {
  return splitAtStructureBeatBoundaries(projectedStart, projectedEnd, structureMap)
    .map((segment, index, all) => {
      const position = locateInStructureMap(segment.start, structureMap);
      const measure = structureMap.measures.find((candidate) => candidate.measureNumber === position.measureNumber);
      const beat = measure?.beats.find((candidate) => candidate.beatNumber === position.beatNumber);
      const startsOnBeat = beat ? Math.abs(segment.start - beat.start) <= EPSILON : false;
      const durationSeconds = segment.end - segment.start;
      return {
        segmentIndex: index,
        start: segment.start,
        end: segment.end,
        durationSeconds,
        measureNumber: position.measureNumber,
        beatNumber: position.beatNumber,
        beatFraction: position.beatFraction,
        pickup: position.pickup,
        feel: position.feel,
        startsOnBeat,
        syncopatedStart: !startsOnBeat,
        tieFromPrevious: index > 0,
        tieToNext: index < all.length - 1,
      };
    });
}

function buildRestGaps(events) {
  const byCluster = new Map();
  for (const event of events) {
    if (event.projectedEnd === null) continue;
    const existing = byCluster.get(event.clusterId);
    if (!existing) {
      byCluster.set(event.clusterId, {
        clusterId: event.clusterId,
        start: event.projectedStart,
        end: event.projectedEnd,
      });
    } else {
      existing.start = Math.min(existing.start, event.projectedStart);
      existing.end = Math.max(existing.end, event.projectedEnd);
    }
  }

  const clusters = [...byCluster.values()].sort((a, b) => a.start - b.start || a.clusterId - b.clusterId);
  const rests = [];
  for (let index = 0; index < clusters.length - 1; index += 1) {
    const current = clusters[index];
    const next = clusters[index + 1];
    if (next.start > current.end + EPSILON) {
      rests.push({
        afterClusterId: current.clusterId,
        beforeClusterId: next.clusterId,
        start: current.end,
        end: next.start,
        durationSeconds: next.start - current.end,
        startPosition: locateInStructureMap(current.end, events[0].structureMap),
        endPosition: locateInStructureMap(next.start, events[0].structureMap),
      });
    }
  }
  return rests;
}

function displacementStats(values) {
  if (values.length === 0) {
    return { count: 0, meanAbsSeconds: 0, maxAbsSeconds: 0 };
  }
  const abs = values.map((value) => Math.abs(value));
  return {
    count: values.length,
    meanAbsSeconds: abs.reduce((sum, value) => sum + value, 0) / abs.length,
    maxAbsSeconds: Math.max(...abs),
  };
}

export function buildStructureMappedEventSchema({
  events,
  structureMap,
  instrumentConfig,
  onsetToleranceSeconds = 0.01,
} = {}) {
  if (!Array.isArray(events)) throw new Error('events must be an array.');
  const map = normalizeStructureMap(structureMap);
  const core = runStructureMappedCore({
    events,
    structureMap: map,
    instrumentConfig,
    onsetToleranceSeconds,
  });

  const musicalEvents = core.events.map((coreEvent) => {
    const source = events[coreEvent.sourceEventIndex];
    const sourceEnd = resolveSourceEnd(source, coreEvent.sourceEventIndex);
    const endProjection = projectEnd(sourceEnd, coreEvent.projectedStart, map);
    const notationSegments = endProjection.projectedEnd === null
      ? []
      : buildNotationSegments(coreEvent.projectedStart, endProjection.projectedEnd, map);

    return {
      schemaVersion: 2,
      eventId: `event-${coreEvent.sourceEventIndex}`,
      sourceEventIndex: coreEvent.sourceEventIndex,
      clusterId: coreEvent.clusterId,
      midi: coreEvent.midi,
      sourceStart: coreEvent.sourceStart,
      sourceEnd,
      sourceDurationSeconds: sourceEnd === null ? null : sourceEnd - coreEvent.sourceStart,
      projectedStart: coreEvent.projectedStart,
      projectedEnd: endProjection.projectedEnd,
      projectedDurationSeconds: endProjection.projectedEnd === null
        ? null
        : endProjection.projectedEnd - coreEvent.projectedStart,
      onsetDisplacementSeconds: coreEvent.displacementSeconds,
      endDisplacementSeconds: endProjection.displacementSeconds,
      onsetMoved: Math.abs(coreEvent.displacementSeconds) > EPSILON,
      endMoved: endProjection.moved,
      durationResolved: endProjection.durationResolved,
      measureNumber: coreEvent.measureNumber,
      beatNumber: coreEvent.beatNumber,
      beatFraction: coreEvent.beatFraction,
      pickup: coreEvent.pickup,
      tempoBpm: coreEvent.tempoBpm,
      timeSignature: { ...coreEvent.timeSignature },
      feel: coreEvent.feel,
      instrument: { ...core.instrumentConfig, tuningMidi: [...core.instrumentConfig.tuningMidi] },
      fretboard: {
        stringNumberHighToLow: coreEvent.stringNumberHighToLow,
        lowToHighIndex: coreEvent.lowToHighIndex,
        fret: coreEvent.fret,
        reconstructedMidi: coreEvent.reconstructedMidi,
        shapeResolved: coreEvent.shapeResolved,
      },
      notation: {
        feel: coreEvent.feel,
        segments: notationSegments,
        tieSegmentCount: notationSegments.filter((segment) => segment.tieFromPrevious || segment.tieToNext).length,
        syncopatedStart: notationSegments[0]?.syncopatedStart ?? false,
      },
      provenance: {
        referenceBlind: true,
        structureMapVersion: map.version,
        structureMapSource: { ...map.provenance },
        legacyV143ScorerImported: false,
      },
      structureMap: map,
    };
  });

  const restGaps = musicalEvents.length === 0 ? [] : buildRestGaps(musicalEvents);
  const tiedEventCount = musicalEvents.filter((event) => event.notation.segments.length > 1).length;
  const notationSegmentCount = musicalEvents.reduce((sum, event) => sum + event.notation.segments.length, 0);
  const durationResolvedCount = musicalEvents.filter((event) => event.durationResolved).length;
  const syncopatedEventCount = musicalEvents.filter((event) => event.notation.syncopatedStart).length;

  const cleanEvents = musicalEvents.map(({ structureMap: _structureMap, ...event }) => event);

  return {
    pipeline: {
      name: 'songsterr-fresh-structure-mapped-event-schema',
      version: 1,
      eventSchemaVersion: 2,
      referenceBlind: true,
      legacyV143ScorerImported: false,
    },
    structureMap: map,
    instrumentConfig: core.instrumentConfig,
    events: cleanEvents,
    rests: restGaps,
    metrics: {
      sourceCount: events.length,
      outputEventCount: cleanEvents.length,
      countDelta: cleanEvents.length - events.length,
      exactMidiPreservedCount: cleanEvents.filter((event) => event.midi === events[event.sourceEventIndex].midi).length,
      durationResolvedCount,
      unresolvedDurationCount: cleanEvents.length - durationResolvedCount,
      notationSegmentCount,
      tiedEventCount,
      restGapCount: restGaps.length,
      syncopatedEventCount,
      onsetDisplacement: displacementStats(cleanEvents.map((event) => event.onsetDisplacementSeconds)),
      endDisplacement: displacementStats(
        cleanEvents.filter((event) => event.durationResolved).map((event) => event.endDisplacementSeconds),
      ),
    },
  };
}
