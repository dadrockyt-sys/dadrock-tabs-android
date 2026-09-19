const EPSILON = 1e-9;

function stats(values) {
  if (values.length === 0) return { count: 0, meanAbs: 0, maxAbs: 0, min: null, max: null };
  const abs = values.map((value) => Math.abs(value));
  return {
    count: values.length,
    meanAbs: abs.reduce((sum, value) => sum + value, 0) / abs.length,
    maxAbs: Math.max(...abs),
    min: Math.min(...values),
    max: Math.max(...values),
  };
}

function structureDiagnostics(structureMap) {
  if (!structureMap) {
    return {
      present: false,
      complete: false,
      measureBoundaryConsistent: false,
      downbeatConsistent: false,
      tempoSegmentCount: 0,
      meterSegmentCount: 0,
      feelSegmentCount: 0,
      measureCount: 0,
      downbeatCount: 0,
      confidence: null,
    };
  }

  const measures = Array.isArray(structureMap.measures) ? structureMap.measures : [];
  const downbeats = Array.isArray(structureMap.downbeats) ? structureMap.downbeats : [];
  let measureBoundaryConsistent = measures.length > 0;
  for (let index = 0; index < measures.length; index += 1) {
    const measure = measures[index];
    if (!(Number.isFinite(measure.start) && Number.isFinite(measure.end) && measure.end > measure.start)) {
      measureBoundaryConsistent = false;
      break;
    }
    if (index === 0 && Math.abs(measure.start) > EPSILON) measureBoundaryConsistent = false;
    if (index > 0 && Math.abs(measure.start - measures[index - 1].end) > EPSILON) measureBoundaryConsistent = false;
  }
  if (measures.length > 0 && Number.isFinite(structureMap.durationSeconds)
    && Math.abs(measures.at(-1).end - structureMap.durationSeconds) > EPSILON) {
    measureBoundaryConsistent = false;
  }

  const fullMeasures = measures.filter((measure) => !measure.pickup);
  const downbeatConsistent = fullMeasures.every((measure) => downbeats.some((downbeat) => (
    downbeat.measureNumber === measure.measureNumber && Math.abs(downbeat.time - measure.start) <= EPSILON
  ))) && downbeats.length === fullMeasures.length;

  const complete = measureBoundaryConsistent
    && downbeatConsistent
    && Array.isArray(structureMap.tempoSegments) && structureMap.tempoSegments.length > 0
    && Array.isArray(structureMap.meterSegments) && structureMap.meterSegments.length > 0
    && Array.isArray(structureMap.feelSegments) && structureMap.feelSegments.length > 0;

  return {
    present: true,
    complete,
    measureBoundaryConsistent,
    downbeatConsistent,
    tempoSegmentCount: structureMap.tempoSegments?.length ?? 0,
    meterSegmentCount: structureMap.meterSegments?.length ?? 0,
    feelSegmentCount: structureMap.feelSegments?.length ?? 0,
    measureCount: measures.length,
    downbeatCount: downbeats.length,
    pickupDurationSeconds: structureMap.pickupDurationSeconds ?? 0,
    confidence: structureMap.confidence ?? null,
  };
}

function eventDiagnostics(result, sourceEvents) {
  const events = Array.isArray(result?.events) ? result.events : [];
  const expectedSourceCount = Array.isArray(sourceEvents) ? sourceEvents.length : null;
  const sourceIndexes = events.map((event) => event.sourceEventIndex);
  const uniqueSourceIndexes = new Set(sourceIndexes);
  const duplicateSourceIdentityCount = sourceIndexes.length - uniqueSourceIndexes.size;
  const missingSourceIdentityCount = expectedSourceCount === null
    ? null
    : Array.from({ length: expectedSourceCount }, (_, index) => index).filter((index) => !uniqueSourceIndexes.has(index)).length;

  let exactMidiPreservedCount = null;
  let exactMidiPreservationRate = null;
  if (Array.isArray(sourceEvents)) {
    exactMidiPreservedCount = events.filter((event) => sourceEvents[event.sourceEventIndex]?.midi === event.midi).length;
    exactMidiPreservationRate = sourceEvents.length === 0 ? 1 : exactMidiPreservedCount / sourceEvents.length;
  }

  const onsetDisplacements = events
    .filter((event) => Number.isFinite(event.sourceStart) && Number.isFinite(event.projectedStart))
    .map((event) => event.projectedStart - event.sourceStart);
  const endDisplacements = events
    .filter((event) => Number.isFinite(event.sourceEnd) && Number.isFinite(event.projectedEnd))
    .map((event) => event.projectedEnd - event.sourceEnd);

  const clusters = new Map();
  for (const event of events) {
    const cluster = clusters.get(event.clusterId) ?? [];
    cluster.push(event);
    clusters.set(event.clusterId, cluster);
  }
  const inconsistentClusterTimingCount = [...clusters.values()].filter((cluster) => {
    if (cluster.length <= 1) return false;
    const anchor = cluster[0].projectedStart;
    return cluster.some((event) => Math.abs(event.projectedStart - anchor) > EPSILON);
  }).length;

  return {
    expectedSourceCount,
    outputCount: events.length,
    countDelta: expectedSourceCount === null ? null : events.length - expectedSourceCount,
    uniqueSourceIdentityCount: uniqueSourceIndexes.size,
    duplicateSourceIdentityCount,
    missingSourceIdentityCount,
    exactMidiPreservedCount,
    exactMidiPreservationRate,
    clusterCount: clusters.size,
    inconsistentClusterTimingCount,
    onsetDisplacementSeconds: stats(onsetDisplacements),
    endDisplacementSeconds: stats(endDisplacements),
  };
}

function rhythmDiagnostics(result) {
  const events = Array.isArray(result?.events) ? result.events : [];
  const rests = Array.isArray(result?.rests) ? result.rests : [];
  const durationResolvedCount = events.filter((event) => event.durationResolved === true || Number.isFinite(event.projectedEnd)).length;
  const unresolvedDurationCount = events.length - durationResolvedCount;
  const notationSegmentCount = events.reduce((sum, event) => sum + (event.notation?.segments?.length ?? 0), 0);
  const tiedEventCount = events.filter((event) => (event.notation?.segments?.length ?? 0) > 1).length;
  const notationIncompleteCount = events.filter((event) => (
    (event.durationResolved === true || Number.isFinite(event.projectedEnd)) && (event.notation?.segments?.length ?? 0) === 0
  )).length;
  const unresolvedRhythmSpellingCount = events.reduce((sum, event) => (
    sum + (event.notation?.unresolvedSpellingSegmentCount ?? 0)
  ), 0) + (result?.rhythmSpelling?.unresolvedRestSegmentCount ?? 0);

  return {
    durationResolvedCount,
    unresolvedDurationCount,
    notationSegmentCount,
    tiedEventCount,
    restGapCount: rests.length,
    notationIncompleteCount,
    unresolvedRhythmSpellingCount,
    restSegmentCount: result?.rhythmSpelling?.restSegmentCount ?? null,
    feelDiagnostics: result?.rhythmSpelling?.feel ?? null,
  };
}

function playabilityDiagnostics(result) {
  const events = Array.isArray(result?.events) ? result.events : [];
  let playableAssignedCount = 0;
  let unplayableAssignedCount = 0;
  const clusters = new Map();

  for (const event of events) {
    const fretboard = event.fretboard ?? {};
    const playable = Number.isInteger(fretboard.lowToHighIndex)
      && Number.isInteger(fretboard.fret)
      && fretboard.fret >= 0
      && fretboard.reconstructedMidi === event.midi;
    if (playable) playableAssignedCount += 1;
    else unplayableAssignedCount += 1;

    const cluster = clusters.get(event.clusterId) ?? [];
    cluster.push(event);
    clusters.set(event.clusterId, cluster);
  }

  let uniqueStringChordViolationCount = 0;
  const clusterShapeDiagnostics = [];
  for (const [clusterId, cluster] of clusters) {
    const assigned = cluster.filter((event) => Number.isInteger(event.fretboard?.lowToHighIndex));
    if (assigned.length > 1 && new Set(assigned.map((event) => event.fretboard.lowToHighIndex)).size !== assigned.length) {
      uniqueStringChordViolationCount += 1;
    }
    const frets = assigned.map((event) => event.fretboard.fret);
    const fretted = frets.filter((fret) => fret > 0);
    const strings = assigned.map((event) => event.fretboard.lowToHighIndex);
    clusterShapeDiagnostics.push({
      clusterId,
      eventCount: cluster.length,
      assignedCount: assigned.length,
      frettedSpan: fretted.length <= 1 ? 0 : Math.max(...fretted) - Math.min(...fretted),
      stringSpan: strings.length <= 1 ? 0 : Math.max(...strings) - Math.min(...strings),
      centerFret: fretted.length === 0 ? 0 : fretted.reduce((sum, fret) => sum + fret, 0) / fretted.length,
      openStringCount: frets.filter((fret) => fret === 0).length,
    });
  }

  const path = result?.fretboardPath;
  return {
    playableAssignedCount,
    unplayableAssignedCount,
    uniqueStringChordViolationCount,
    clusterShapeDiagnostics,
    pathResolved: path?.resolved ?? null,
    pathApplied: path?.applied ?? null,
    totalCenterFretMovement: path?.metrics?.totalCenterFretMovement ?? null,
    maxCenterFretMovement: path?.metrics?.maxCenterFretMovement ?? null,
    stringSetChangeCount: path?.metrics?.stringSetChangeCount ?? null,
    pathCandidateCounts: path?.metrics?.candidateCounts ?? null,
    pathUnresolvedOnsetCount: path?.metrics?.unresolvedOnsetCount ?? path?.diagnostics?.unresolvedOnsetCount ?? null,
  };
}

function failure(code, details = {}) {
  return { code, ...details };
}

export function evaluateFreshPipeline(result, { sourceEvents = null } = {}) {
  const structure = structureDiagnostics(result?.structureMap);
  const events = eventDiagnostics(result, sourceEvents);
  const rhythm = rhythmDiagnostics(result);
  const playability = playabilityDiagnostics(result);
  const failures = [];

  if (!structure.present) failures.push(failure('STRUCTURE_MAP_MISSING'));
  else {
    if (!structure.measureBoundaryConsistent) failures.push(failure('MEASURE_BOUNDARY_INCONSISTENT'));
    if (!structure.downbeatConsistent) failures.push(failure('DOWNBEAT_INCONSISTENT'));
    if (!structure.complete) failures.push(failure('STRUCTURE_MAP_INCOMPLETE'));
  }

  if (events.countDelta !== null && events.countDelta !== 0) failures.push(failure('EVENT_COUNT_DRIFT', { countDelta: events.countDelta }));
  if (events.exactMidiPreservationRate !== null && events.exactMidiPreservationRate !== 1) failures.push(failure('MIDI_IDENTITY_MISMATCH', { rate: events.exactMidiPreservationRate }));
  if (events.duplicateSourceIdentityCount > 0 || (events.missingSourceIdentityCount ?? 0) > 0) {
    failures.push(failure('SOURCE_IDENTITY_DRIFT', {
      duplicateCount: events.duplicateSourceIdentityCount,
      missingCount: events.missingSourceIdentityCount,
    }));
  }
  if (events.inconsistentClusterTimingCount > 0) failures.push(failure('INCONSISTENT_CLUSTER_TIMING', { count: events.inconsistentClusterTimingCount }));
  if (rhythm.unresolvedDurationCount > 0) failures.push(failure('UNRESOLVED_DURATION', { count: rhythm.unresolvedDurationCount }));
  if (rhythm.notationIncompleteCount > 0) failures.push(failure('NOTATION_INCOMPLETE', { count: rhythm.notationIncompleteCount }));
  if (rhythm.unresolvedRhythmSpellingCount > 0) failures.push(failure('UNRESOLVED_RHYTHM_SPELLING', { count: rhythm.unresolvedRhythmSpellingCount }));
  if (playability.unplayableAssignedCount > 0) failures.push(failure('UNPLAYABLE_ASSIGNMENT', { count: playability.unplayableAssignedCount }));
  if (playability.uniqueStringChordViolationCount > 0) failures.push(failure('UNIQUE_STRING_CHORD_VIOLATION', { count: playability.uniqueStringChordViolationCount }));
  if (playability.pathResolved === false) failures.push(failure('FRETBOARD_PATH_UNRESOLVED', { unresolvedOnsetCount: playability.pathUnresolvedOnsetCount }));

  return {
    evaluator: {
      name: 'songsterr-fresh-raw-evaluator',
      version: 1,
      compositeScoreDefined: false,
      compositeScore: null,
      legacyV143ScorerImported: false,
    },
    structure,
    events,
    rhythm,
    playability,
    failures,
    passedRawIntegrityChecks: failures.length === 0,
  };
}
