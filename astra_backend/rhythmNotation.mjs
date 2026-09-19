import {
  locateMusicalPosition,
  normalizeConditioning,
  resolveStructureGrid,
  runDeterministicCore,
  snapOnsetToGrid,
} from './index.mjs';

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

function nextBoundaryAfter(seconds, grid) {
  if (!grid.resolved) return null;

  if (seconds + EPSILON < grid.pickupSeconds) {
    const nextPickupBeat = (Math.floor((seconds + EPSILON) / grid.beatUnitSeconds) + 1) * grid.beatUnitSeconds;
    return Math.min(nextPickupBeat, grid.pickupSeconds);
  }

  const relative = Math.max(0, seconds - grid.pickupSeconds);
  const beatIndex = Math.floor((relative + EPSILON) / grid.beatUnitSeconds);
  return grid.pickupSeconds + (beatIndex + 1) * grid.beatUnitSeconds;
}

function splitAtBeatBoundaries(start, end, grid) {
  if (!grid.resolved || end <= start + EPSILON) {
    return [{ start, end }];
  }

  const segments = [];
  let cursor = start;
  let guard = 0;

  while (cursor < end - EPSILON) {
    guard += 1;
    if (guard > 10000) throw new Error('Rhythm segmentation exceeded safety limit.');

    const boundary = nextBoundaryAfter(cursor, grid);
    const segmentEnd = boundary === null ? end : Math.min(end, boundary);

    if (segmentEnd <= cursor + EPSILON) {
      return [{ start, end }];
    }

    segments.push({ start: cursor, end: segmentEnd });
    cursor = segmentEnd;
  }

  return segments;
}

function buildNotationSegments(projectedStart, projectedEnd, grid) {
  return splitAtBeatBoundaries(projectedStart, projectedEnd, grid).map((segment, index, all) => {
    const position = locateMusicalPosition(segment.start, grid);
    return {
      segmentIndex: index,
      start: segment.start,
      end: segment.end,
      durationSeconds: segment.end - segment.start,
      measureNumber: position.measureNumber,
      beatNumber: position.beatNumber,
      beatFraction: position.beatFraction,
      pickup: position.pickup,
      tieFromPrevious: index > 0,
      tieToNext: index < all.length - 1,
    };
  });
}

function projectEnd(sourceEnd, projectedStart, grid) {
  if (sourceEnd === null) {
    return {
      sourceEnd: null,
      projectedEnd: null,
      moved: false,
      durationResolved: false,
    };
  }

  if (!grid.resolved || grid.subdivisionSeconds === null) {
    return {
      sourceEnd,
      projectedEnd: Math.max(sourceEnd, projectedStart),
      moved: false,
      durationResolved: true,
    };
  }

  const snapped = snapOnsetToGrid(sourceEnd, grid);
  let projectedEnd = snapped.projectedStart;
  if (projectedEnd <= projectedStart + EPSILON) {
    projectedEnd = projectedStart + grid.subdivisionSeconds;
  }

  return {
    sourceEnd,
    projectedEnd,
    moved: Math.abs(projectedEnd - sourceEnd) > EPSILON,
    durationResolved: true,
  };
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
      });
    }
  }

  return rests;
}

export function buildMusicalEventSchema({ events, conditioning, onsetToleranceSeconds = 0.01 } = {}) {
  if (!Array.isArray(events)) throw new Error('events must be an array.');

  const normalizedConditioning = normalizeConditioning(conditioning);
  const grid = resolveStructureGrid(normalizedConditioning.structurePrior);
  const core = runDeterministicCore({ events, conditioning: normalizedConditioning, onsetToleranceSeconds });

  const musicalEvents = core.events.map((coreEvent) => {
    const source = events[coreEvent.sourceEventIndex];
    const sourceEnd = resolveSourceEnd(source, coreEvent.sourceEventIndex);
    const endProjection = projectEnd(sourceEnd, coreEvent.projectedStart, grid);
    const notationSegments = endProjection.projectedEnd === null
      ? []
      : buildNotationSegments(coreEvent.projectedStart, endProjection.projectedEnd, grid);

    return {
      schemaVersion: 1,
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
      onsetMoved: Math.abs(coreEvent.projectedStart - coreEvent.sourceStart) > EPSILON,
      endMoved: endProjection.moved,
      durationResolved: endProjection.durationResolved,
      measureNumber: coreEvent.measureNumber,
      beatNumber: coreEvent.beatNumber,
      beatFraction: coreEvent.beatFraction,
      pickup: coreEvent.pickup,
      instrument: {
        role: normalizedConditioning.instrumentConfig.role,
        tuningMidi: [...normalizedConditioning.instrumentConfig.tuningMidi],
        capoFret: normalizedConditioning.instrumentConfig.capoFret,
      },
      fretboard: {
        stringNumberHighToLow: coreEvent.stringNumberHighToLow,
        lowToHighIndex: coreEvent.lowToHighIndex,
        fret: coreEvent.fret,
        reconstructedMidi: coreEvent.reconstructedMidi,
        shapeResolved: coreEvent.shapeResolved,
      },
      notation: {
        feel: normalizedConditioning.structurePrior.feel,
        segments: notationSegments,
        tieSegmentCount: notationSegments.filter((segment) => segment.tieFromPrevious || segment.tieToNext).length,
      },
      provenance: {
        referenceBlind: true,
        legacyV143ScorerImported: false,
      },
    };
  });

  const restGaps = buildRestGaps(musicalEvents);
  const tiedEventCount = musicalEvents.filter((event) => event.notation.segments.length > 1).length;
  const notationSegmentCount = musicalEvents.reduce((sum, event) => sum + event.notation.segments.length, 0);
  const durationResolvedCount = musicalEvents.filter((event) => event.durationResolved).length;

  return {
    pipeline: {
      name: 'songsterr-fresh-musical-event-schema',
      version: 1,
      referenceBlind: true,
      legacyV143ScorerImported: false,
    },
    conditioning: normalizedConditioning,
    structureGrid: grid,
    events: musicalEvents,
    rests: restGaps,
    metrics: {
      sourceCount: events.length,
      outputEventCount: musicalEvents.length,
      countDelta: musicalEvents.length - events.length,
      exactMidiPreservedCount: musicalEvents.filter((event) => event.midi === events[event.sourceEventIndex].midi).length,
      durationResolvedCount,
      notationSegmentCount,
      tiedEventCount,
      restGapCount: restGaps.length,
    },
  };
}
