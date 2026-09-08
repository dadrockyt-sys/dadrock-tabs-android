import { optimizeFretboardPath } from './fretboardPathOptimizer.mjs';

const EPSILON = 1e-9;

function cloneInvariantProjection(event) {
  return {
    eventId: event.eventId,
    sourceEventIndex: event.sourceEventIndex,
    clusterId: event.clusterId,
    midi: event.midi,
    sourceStart: event.sourceStart,
    sourceEnd: event.sourceEnd,
    projectedStart: event.projectedStart,
    projectedEnd: event.projectedEnd,
    measureNumber: event.measureNumber,
    beatNumber: event.beatNumber,
    beatFraction: event.beatFraction,
    pickup: event.pickup,
    tempoBpm: event.tempoBpm,
    timeSignature: event.timeSignature,
    feel: event.feel,
    notation: event.notation,
    provenance: event.provenance,
  };
}

function groupEvents(events) {
  const byCluster = new Map();
  events.forEach((event, eventIndex) => {
    const current = byCluster.get(event.clusterId);
    if (!current) {
      byCluster.set(event.clusterId, {
        onsetId: event.clusterId,
        time: event.projectedStart,
        midis: [event.midi],
        eventIndexes: [eventIndex],
      });
    } else {
      if (Math.abs(current.time - event.projectedStart) > EPSILON) {
        throw new Error(`cluster ${event.clusterId} contains inconsistent projectedStart values.`);
      }
      current.midis.push(event.midi);
      current.eventIndexes.push(eventIndex);
    }
  });
  return [...byCluster.values()].sort((a, b) => a.time - b.time || String(a.onsetId).localeCompare(String(b.onsetId)));
}

function centerFromFrets(frets) {
  const fretted = frets.filter((fret) => Number.isFinite(fret) && fret > 0);
  if (fretted.length === 0) return 0;
  return fretted.reduce((sum, fret) => sum + fret, 0) / fretted.length;
}

function originalMovement(events, groups) {
  const centers = groups.map((group) => centerFromFrets(
    group.eventIndexes.map((index) => events[index]?.fretboard?.fret),
  ));
  let total = 0;
  let max = 0;
  for (let index = 1; index < centers.length; index += 1) {
    const movement = Math.abs(centers[index] - centers[index - 1]);
    total += movement;
    max = Math.max(max, movement);
  }
  return { centers, total, max };
}

export function applyOptimizedFretboardPath(eventSchema, {
  policy = {},
  weights = {},
  maxCandidatesPerOnset = 24,
} = {}) {
  if (!eventSchema || !Array.isArray(eventSchema.events) || !eventSchema.instrumentConfig) {
    throw new Error('eventSchema must contain events and instrumentConfig.');
  }

  const beforeProjection = eventSchema.events.map(cloneInvariantProjection);
  const groups = groupEvents(eventSchema.events);
  const priorMovement = originalMovement(eventSchema.events, groups);
  const optimized = optimizeFretboardPath({
    onsetGroups: groups.map(({ onsetId, time, midis }) => ({ onsetId, time, midis })),
    instrumentConfig: eventSchema.instrumentConfig,
    policy,
    weights,
    maxCandidatesPerOnset,
  });

  if (!optimized.resolved) {
    return {
      ...eventSchema,
      fretboardPath: {
        ...optimized,
        applied: false,
        invariantProjectionPreserved: true,
        originalMovement: priorMovement,
      },
    };
  }

  const events = eventSchema.events.map((event) => ({
    ...event,
    fretboard: { ...(event.fretboard || {}) },
  }));

  optimized.path.forEach((state, pathIndex) => {
    const group = groups[pathIndex];
    if (state.assignments.length !== group.eventIndexes.length) {
      throw new Error('Path assignment count does not match cluster event count.');
    }

    state.assignments.forEach((assignment, assignmentIndex) => {
      const eventIndex = group.eventIndexes[assignmentIndex];
      const event = events[eventIndex];
      if (assignment.reconstructedMidi !== event.midi) {
        throw new Error('Fretboard path attempted to change MIDI identity.');
      }
      events[eventIndex] = {
        ...event,
        fretboard: {
          ...event.fretboard,
          stringNumberHighToLow: assignment.stringNumberHighToLow,
          lowToHighIndex: assignment.lowToHighIndex,
          fret: assignment.fret,
          reconstructedMidi: assignment.reconstructedMidi,
          shapeResolved: true,
          pathOptimized: true,
          pathOnsetIndex: pathIndex,
          pathCandidateCount: state.candidateCount,
        },
      };
    });
  });

  const afterProjection = events.map(cloneInvariantProjection);
  const invariantProjectionPreserved = JSON.stringify(beforeProjection) === JSON.stringify(afterProjection);
  if (!invariantProjectionPreserved) {
    throw new Error('Fretboard path integration changed a protected event invariant.');
  }

  return {
    ...eventSchema,
    pipeline: {
      ...(eventSchema.pipeline || {}),
      fretboardPathOptimizer: 'deterministic-v1',
    },
    events,
    fretboardPath: {
      ...optimized,
      applied: true,
      invariantProjectionPreserved,
      originalMovement: priorMovement,
      movementDelta: optimized.metrics.totalCenterFretMovement - priorMovement.total,
    },
  };
}
