export const STANDARD_GUITAR_TUNING_MIDI = Object.freeze([40, 45, 50, 55, 59, 64]);
export const STANDARD_BASS_TUNING_MIDI = Object.freeze([28, 33, 38, 43]);

const ROLES = new Set(['lead', 'rhythm', 'bass']);
const FEELS = new Set(['auto', 'straight', 'triplet']);
const DENOMINATORS = new Set([1, 2, 4, 8, 16, 32]);
const MAX_FRET = 24;
const EPSILON = 1e-9;

function finiteNumber(value, field) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`${field} must be finite.`);
  return parsed;
}

function normalizeNullableNumber(value, field, minimum, maximum) {
  if (value === undefined || value === null) return null;
  const parsed = finiteNumber(value, field);
  if (parsed < minimum || parsed > maximum) {
    throw new Error(`${field} must be between ${minimum} and ${maximum}.`);
  }
  return parsed;
}

function defaultTuning(role) {
  return [...(role === 'bass' ? STANDARD_BASS_TUNING_MIDI : STANDARD_GUITAR_TUNING_MIDI)];
}

export function normalizeConditioning(raw = {}) {
  const structureSource = raw.structurePrior || {};
  const instrumentSource = raw.instrumentConfig || {};

  const role = instrumentSource.role;
  if (!ROLES.has(role)) throw new Error('instrumentConfig.role must be lead, rhythm, or bass.');

  const feel = structureSource.feel ?? 'auto';
  if (!FEELS.has(feel)) throw new Error('structurePrior.feel must be auto, straight, or triplet.');

  let timeSignature = null;
  if (structureSource.timeSignature !== undefined && structureSource.timeSignature !== null) {
    const numerator = structureSource.timeSignature.numerator;
    const denominator = structureSource.timeSignature.denominator;
    if (!Number.isInteger(numerator) || numerator < 1 || numerator > 32) {
      throw new Error('timeSignature.numerator must be an integer from 1 to 32.');
    }
    if (!Number.isInteger(denominator) || !DENOMINATORS.has(denominator)) {
      throw new Error('timeSignature.denominator is invalid.');
    }
    timeSignature = { numerator, denominator };
  }

  const capoFret = instrumentSource.capoFret ?? 0;
  if (!Number.isInteger(capoFret) || capoFret < 0 || capoFret > MAX_FRET) {
    throw new Error(`instrumentConfig.capoFret must be an integer from 0 to ${MAX_FRET}.`);
  }

  const tuningMidi = instrumentSource.tuningMidi === undefined || instrumentSource.tuningMidi === null
    ? defaultTuning(role)
    : [...instrumentSource.tuningMidi];

  const minStrings = 4;
  const maxStrings = role === 'bass' ? 6 : 8;
  if (tuningMidi.length < minStrings || tuningMidi.length > maxStrings) {
    throw new Error(`instrumentConfig.tuningMidi must contain ${minStrings}-${maxStrings} strings.`);
  }
  for (let index = 0; index < tuningMidi.length; index += 1) {
    const pitch = tuningMidi[index];
    if (!Number.isInteger(pitch) || pitch < 0 || pitch > 127) {
      throw new Error('Every tuning pitch must be an integer from 0 to 127.');
    }
    if (index > 0 && pitch <= tuningMidi[index - 1]) {
      throw new Error('tuningMidi must be strictly increasing from lowest to highest string.');
    }
  }

  return {
    version: 1,
    referenceBlind: true,
    structurePrior: {
      tempoBpm: normalizeNullableNumber(structureSource.tempoBpm, 'tempoBpm', 20, 400),
      timeSignature,
      pickupBeats: normalizeNullableNumber(structureSource.pickupBeats, 'pickupBeats', 0, 32),
      feel,
    },
    instrumentConfig: {
      role,
      tuningMidi,
      capoFret,
    },
  };
}

export function resolveStructureGrid(structurePrior) {
  const { tempoBpm, timeSignature, pickupBeats, feel } = structurePrior;
  if (tempoBpm === null || timeSignature === null || pickupBeats === null) {
    return {
      resolved: false,
      reason: 'AUTO_STRUCTURE_UNRESOLVED',
      tempoBpm,
      timeSignature,
      pickupBeats,
      feel,
      beatUnitSeconds: null,
      measureSeconds: null,
      pickupSeconds: null,
      subdivisionsPerBeatUnit: null,
      subdivisionSeconds: null,
    };
  }

  const quarterSeconds = 60 / tempoBpm;
  const beatUnitSeconds = quarterSeconds * (4 / timeSignature.denominator);
  const measureSeconds = beatUnitSeconds * timeSignature.numerator;
  const pickupSeconds = beatUnitSeconds * pickupBeats;
  const subdivisionsPerBeatUnit = feel === 'straight' ? 4 : feel === 'triplet' ? 3 : null;
  const subdivisionSeconds = subdivisionsPerBeatUnit === null
    ? null
    : beatUnitSeconds / subdivisionsPerBeatUnit;

  return {
    resolved: true,
    reason: subdivisionsPerBeatUnit === null ? 'STRUCTURE_RESOLVED_FEEL_AUTO' : 'STRUCTURE_AND_FEEL_RESOLVED',
    tempoBpm,
    timeSignature: { ...timeSignature },
    pickupBeats,
    feel,
    beatUnitSeconds,
    measureSeconds,
    pickupSeconds,
    subdivisionsPerBeatUnit,
    subdivisionSeconds,
  };
}

export function locateMusicalPosition(seconds, grid) {
  const timestamp = Math.max(0, finiteNumber(seconds, 'seconds'));
  if (!grid.resolved) {
    return { measureNumber: null, beatNumber: null, beatFraction: null, pickup: null };
  }

  if (timestamp + EPSILON < grid.pickupSeconds) {
    const beatZero = Math.floor(timestamp / grid.beatUnitSeconds);
    const withinBeat = timestamp - beatZero * grid.beatUnitSeconds;
    return {
      measureNumber: 0,
      beatNumber: beatZero + 1,
      beatFraction: Math.max(0, Math.min(0.999999999, withinBeat / grid.beatUnitSeconds)),
      pickup: true,
    };
  }

  const relative = Math.max(0, timestamp - grid.pickupSeconds);
  const measureZero = Math.floor((relative + EPSILON) / grid.measureSeconds);
  const withinMeasure = relative - measureZero * grid.measureSeconds;
  const rawBeatZero = Math.floor((withinMeasure + EPSILON) / grid.beatUnitSeconds);
  const beatZero = Math.max(0, Math.min(grid.timeSignature.numerator - 1, rawBeatZero));
  const withinBeat = withinMeasure - beatZero * grid.beatUnitSeconds;

  return {
    measureNumber: measureZero + 1,
    beatNumber: beatZero + 1,
    beatFraction: Math.max(0, Math.min(0.999999999, withinBeat / grid.beatUnitSeconds)),
    pickup: false,
  };
}

export function snapOnsetToGrid(seconds, grid) {
  const sourceStart = Math.max(0, finiteNumber(seconds, 'seconds'));
  if (!grid.resolved || grid.subdivisionSeconds === null) {
    return {
      sourceStart,
      projectedStart: sourceStart,
      moved: false,
      gridSlot: null,
      position: locateMusicalPosition(sourceStart, grid),
    };
  }

  const base = sourceStart + EPSILON < grid.pickupSeconds ? 0 : grid.pickupSeconds;
  const relative = Math.max(0, sourceStart - base);
  const gridSlot = Math.round(relative / grid.subdivisionSeconds);
  const projectedStart = base + gridSlot * grid.subdivisionSeconds;

  return {
    sourceStart,
    projectedStart,
    moved: Math.abs(projectedStart - sourceStart) > EPSILON,
    gridSlot,
    position: locateMusicalPosition(projectedStart, grid),
  };
}

function normalizeEvents(events) {
  if (!Array.isArray(events)) throw new Error('events must be an array.');
  return events.map((event, sourceEventIndex) => {
    const start = Math.max(0, finiteNumber(event?.start, `events[${sourceEventIndex}].start`));
    const midi = event?.midi;
    if (!Number.isInteger(midi) || midi < 0 || midi > 127) {
      throw new Error(`events[${sourceEventIndex}].midi must be an integer from 0 to 127.`);
    }
    return {
      ...event,
      sourceEventIndex,
      start,
      midi,
    };
  });
}

export function groupOnsetClusters(events, toleranceSeconds = 0.01) {
  const tolerance = finiteNumber(toleranceSeconds, 'toleranceSeconds');
  if (tolerance < 0) throw new Error('toleranceSeconds must be non-negative.');

  const normalized = normalizeEvents(events).sort((left, right) => {
    if (left.start !== right.start) return left.start - right.start;
    return left.sourceEventIndex - right.sourceEventIndex;
  });

  const clusters = [];
  for (const event of normalized) {
    const current = clusters.at(-1);
    if (!current || Math.abs(event.start - current.anchorStart) > tolerance + EPSILON) {
      clusters.push({
        clusterId: clusters.length,
        anchorStart: event.start,
        events: [event],
      });
    } else {
      current.events.push(event);
    }
  }
  return clusters;
}

export function enumeratePlayablePositions(midi, instrumentConfig, maxFret = MAX_FRET) {
  if (!Number.isInteger(midi) || midi < 0 || midi > 127) return [];
  const tuning = instrumentConfig.tuningMidi;
  const capo = instrumentConfig.capoFret;
  const positions = [];

  for (let lowToHighIndex = 0; lowToHighIndex < tuning.length; lowToHighIndex += 1) {
    const physicalOpenMidi = tuning[lowToHighIndex];
    const soundingOpenMidi = physicalOpenMidi + capo;
    const fret = midi - soundingOpenMidi;
    if (Number.isInteger(fret) && fret >= 0 && fret <= maxFret) {
      positions.push({
        lowToHighIndex,
        stringNumberHighToLow: tuning.length - lowToHighIndex,
        fret,
        physicalOpenMidi,
        soundingOpenMidi,
        reconstructedMidi: soundingOpenMidi + fret,
      });
    }
  }
  return positions;
}

function targetFret(role) {
  if (role === 'rhythm') return 3;
  if (role === 'bass') return 5;
  return 7;
}

function shapeScore(assignments, role) {
  const frets = assignments.map((assignment) => assignment.fret);
  const strings = assignments.map((assignment) => assignment.lowToHighIndex);
  const fretSpan = Math.max(...frets) - Math.min(...frets);
  const stringSpan = Math.max(...strings) - Math.min(...strings);
  const target = targetFret(role);
  const targetPenalty = frets.reduce((sum, fret) => sum + Math.abs(fret - target), 0);
  const totalFret = frets.reduce((sum, fret) => sum + fret, 0);
  return fretSpan * 100 + stringSpan * 10 + targetPenalty + totalFret * 0.001;
}

function shapeTieKey(assignments) {
  return assignments
    .map((assignment) => `${String(assignment.stringNumberHighToLow).padStart(2, '0')}:${String(assignment.fret).padStart(2, '0')}`)
    .join('|');
}

export function findPlayableShape(midis, instrumentConfig) {
  if (!Array.isArray(midis) || midis.length === 0) return null;
  if (midis.length > instrumentConfig.tuningMidi.length) return null;

  const positionSets = midis.map((midi) => enumeratePlayablePositions(midi, instrumentConfig));
  if (positionSets.some((positions) => positions.length === 0)) return null;

  const order = midis
    .map((midi, index) => ({ index, midi, optionCount: positionSets[index].length }))
    .sort((left, right) => left.optionCount - right.optionCount || right.midi - left.midi || left.index - right.index);

  let best = null;
  const assigned = new Array(midis.length).fill(null);
  const usedStrings = new Set();

  function visit(depth) {
    if (depth === order.length) {
      const candidate = assigned.map((assignment) => ({ ...assignment }));
      const score = shapeScore(candidate, instrumentConfig.role);
      const tieKey = shapeTieKey(candidate);
      if (!best || score < best.score - EPSILON || (Math.abs(score - best.score) <= EPSILON && tieKey < best.tieKey)) {
        best = { score, tieKey, assignments: candidate };
      }
      return;
    }

    const eventIndex = order[depth].index;
    for (const position of positionSets[eventIndex]) {
      if (usedStrings.has(position.lowToHighIndex)) continue;
      usedStrings.add(position.lowToHighIndex);
      assigned[eventIndex] = position;
      visit(depth + 1);
      assigned[eventIndex] = null;
      usedStrings.delete(position.lowToHighIndex);
    }
  }

  visit(0);
  return best;
}

export function runDeterministicCore({ events, conditioning, onsetToleranceSeconds = 0.01 } = {}) {
  const normalizedConditioning = normalizeConditioning(conditioning);
  const normalizedEvents = normalizeEvents(events);
  const grid = resolveStructureGrid(normalizedConditioning.structurePrior);
  const clusters = groupOnsetClusters(normalizedEvents, onsetToleranceSeconds);
  const outputEvents = [];

  for (const cluster of clusters) {
    const timing = snapOnsetToGrid(cluster.anchorStart, grid);
    const shape = findPlayableShape(
      cluster.events.map((event) => event.midi),
      normalizedConditioning.instrumentConfig,
    );

    cluster.events.forEach((event, clusterEventIndex) => {
      const position = shape?.assignments?.[clusterEventIndex] ?? null;
      outputEvents.push({
        sourceEventIndex: event.sourceEventIndex,
        clusterId: cluster.clusterId,
        sourceStart: event.start,
        projectedStart: timing.projectedStart,
        midi: event.midi,
        measureNumber: timing.position.measureNumber,
        beatNumber: timing.position.beatNumber,
        beatFraction: timing.position.beatFraction,
        pickup: timing.position.pickup,
        stringNumberHighToLow: position?.stringNumberHighToLow ?? null,
        lowToHighIndex: position?.lowToHighIndex ?? null,
        fret: position?.fret ?? null,
        reconstructedMidi: position?.reconstructedMidi ?? null,
        shapeResolved: Boolean(shape),
      });
    });
  }

  outputEvents.sort((left, right) => left.sourceEventIndex - right.sourceEventIndex);

  let exactMidiMatches = 0;
  let movedOnsetCount = 0;
  let playableAssignedCount = 0;
  let unassignedPlayableCount = 0;

  for (let index = 0; index < normalizedEvents.length; index += 1) {
    const source = normalizedEvents[index];
    const output = outputEvents[index];
    if (source.midi === output.midi) exactMidiMatches += 1;
    if (Math.abs(source.start - output.projectedStart) > EPSILON) movedOnsetCount += 1;
    if (output.reconstructedMidi === output.midi) playableAssignedCount += 1;
    else unassignedPlayableCount += 1;
  }

  return {
    pipeline: {
      name: 'songsterr-fresh-deterministic-core',
      version: 1,
      referenceBlind: true,
      legacyV143ScorerImported: false,
    },
    conditioning: normalizedConditioning,
    structureGrid: grid,
    clusters: clusters.map((cluster) => ({
      clusterId: cluster.clusterId,
      anchorStart: cluster.anchorStart,
      sourceEventIndexes: cluster.events.map((event) => event.sourceEventIndex),
    })),
    events: outputEvents,
    metrics: {
      sourceCount: normalizedEvents.length,
      outputCount: outputEvents.length,
      countDelta: outputEvents.length - normalizedEvents.length,
      exactMidiMatches,
      pitchPreservationRate: normalizedEvents.length === 0 ? 1 : exactMidiMatches / normalizedEvents.length,
      clusterCount: clusters.length,
      movedOnsetCount,
      playableAssignedCount,
      unassignedPlayableCount,
    },
  };
}
