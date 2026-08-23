const MAX_RENDER_EVENTS = 5000;
const SECTION_BLOCK_MEASURES = 4;

const ALLOWED_TECHNIQUES = new Set([
  'bend',
  'bend-release',
  'pre-bend',
  'sustain-tie',
  'let-ring',
  'palm-mute',
  'slide-up',
  'slide-down',
  'hammer-on',
  'pull-off',
  'vibrato',
  'dead-note',
  'muted-strum',
  'natural-harmonic',
  'pinch-harmonic',
  'tap',
  'trill',
]);

function finiteNumber(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) ? numeric : null;
}

function finiteInteger(value) {
  const numeric = finiteNumber(value);
  return numeric === null ? null : Math.round(numeric);
}

function optionalInteger(value) {
  if (value === null || value === undefined || value === '') return null;
  return finiteInteger(value);
}

function cleanTechniqueName(value) {
  const technique = String(value || '').trim().toLowerCase();
  return ALLOWED_TECHNIQUES.has(technique) ? technique : '';
}

export function getV143TechniqueTypes(event) {
  const techniques = [];
  const seen = new Set();

  const add = (value) => {
    const technique = cleanTechniqueName(value);
    if (!technique || seen.has(technique)) return;
    seen.add(technique);
    techniques.push(technique);
  };

  for (const item of event?.rhythmTechniques || []) {
    if (typeof item === 'string') add(item);
    else if (item && typeof item === 'object') add(item.type);
  }

  for (const item of event?.techniques || []) {
    if (typeof item === 'string') add(item);
    else if (item && typeof item === 'object') add(item.type);
  }

  return techniques.sort();
}

export function projectV143RenderEvents(rawEvents) {
  if (!Array.isArray(rawEvents)) return [];

  const projected = [];

  for (let eventIndex = 0; eventIndex < Math.min(rawEvents.length, MAX_RENDER_EVENTS); eventIndex += 1) {
    const event = rawEvents[eventIndex];
    if (!event || typeof event !== 'object') continue;

    const measure = finiteInteger(event.measure);
    const step = finiteInteger(event.step);
    const stringIndex = finiteInteger(event.stringIndex);
    const fret = finiteInteger(event.fret);
    const midi = finiteInteger(event.midi ?? event.dominantMidi);

    if (
      measure === null || measure < 1 ||
      step === null || step < 0 || step > 15 ||
      stringIndex === null || stringIndex < 0 || stringIndex > 5 ||
      fret === null || fret < 0 || fret > 36 ||
      midi === null
    ) {
      continue;
    }

    const sustain = event.rhythmSustain && typeof event.rhythmSustain === 'object'
      ? event.rhythmSustain
      : {};

    const durationSteps = Math.max(1, finiteInteger(
      sustain.durationSteps ?? event.durationSteps ?? 1
    ) || 1);
    const durationSeconds = finiteNumber(
      sustain.durationSeconds ?? event.durationSeconds
    );
    const existingEventIndex = optionalInteger(event.eventIndex);

    const output = {
      eventIndex:
        existingEventIndex !== null && existingEventIndex >= 0
          ? existingEventIndex
          : eventIndex,
      measure,
      step,
      stringIndex,
      fret,
      midi,
      durationSteps,
      techniques: getV143TechniqueTypes(event),
    };

    if (durationSeconds !== null && durationSeconds >= 0) {
      output.durationSeconds = durationSeconds;
    }

    const sustainTier = String(sustain.tier ?? event.sustainTier ?? '').trim().toLowerCase();
    if (['short', 'medium', 'long'].includes(sustainTier)) {
      output.sustainTier = sustainTier;
    }

    const bendSemitones = finiteNumber(event.bendSemitones);
    const bendTargetFret = optionalInteger(event.bendTargetFret);
    const bendTargetMidi = optionalInteger(event.bendTargetMidi);
    if (bendSemitones !== null && bendSemitones >= 0.35) {
      output.bendSemitones = bendSemitones;
      if (bendTargetFret !== null) output.bendTargetFret = bendTargetFret;
      if (bendTargetMidi !== null) output.bendTargetMidi = bendTargetMidi;
      output.bendRelease = event.bendRelease === true;
    }

    const legatoTargetEventIndex = optionalInteger(event.legatoTargetEventIndex);
    const legatoTargetFret = optionalInteger(event.legatoTargetFret);
    const legatoTargetMidi = optionalInteger(event.legatoTargetMidi);
    if (legatoTargetEventIndex !== null && legatoTargetEventIndex >= 0) {
      output.legatoTargetEventIndex = legatoTargetEventIndex;
      if (legatoTargetFret !== null) output.legatoTargetFret = legatoTargetFret;
      if (legatoTargetMidi !== null) output.legatoTargetMidi = legatoTargetMidi;
    }

    const continuationFrom = optionalInteger(event.legatoContinuationFromEventIndex);
    if (continuationFrom !== null && continuationFrom >= 0) {
      output.legatoContinuationFromEventIndex = continuationFrom;
    }

    const continuationType = cleanTechniqueName(event.legatoContinuationType);
    if (continuationType) output.legatoContinuationType = continuationType;

    projected.push(output);
  }

  return projected;
}

export function validateV143RenderEvents(renderEvents) {
  if (!Array.isArray(renderEvents) || renderEvents.length === 0) return [];
  if (renderEvents.length > MAX_RENDER_EVENTS) return [];

  const normalized = projectV143RenderEvents(renderEvents);
  if (normalized.length !== renderEvents.length) return [];

  for (let index = 0; index < renderEvents.length; index += 1) {
    const sourceEventIndex = finiteInteger(renderEvents[index]?.eventIndex);
    if (sourceEventIndex === null || sourceEventIndex < 0) return [];
    normalized[index].eventIndex = sourceEventIndex;
  }

  return normalized;
}

function jaccard(setA, setB) {
  if (setA.size === 0 && setB.size === 0) return 1;
  if (setA.size === 0 || setB.size === 0) return 0;
  let intersection = 0;
  for (const value of setA) {
    if (setB.has(value)) intersection += 1;
  }
  return intersection / (setA.size + setB.size - intersection);
}

function blockFeatures(events, firstMeasure) {
  const lastMeasure = firstMeasure + SECTION_BLOCK_MEASURES - 1;
  const blockEvents = events.filter(
    (event) => event.measure >= firstMeasure && event.measure <= lastMeasure
  );
  const onsets = new Map();
  for (const event of blockEvents) {
    const key = `${event.measure}:${event.step}`;
    onsets.set(key, (onsets.get(key) || 0) + 1);
  }

  const rhythm = new Set();
  const pitch = new Set();
  for (const event of blockEvents) {
    const offset = event.measure - firstMeasure;
    const onsetSize = Math.min(6, onsets.get(`${event.measure}:${event.step}`) || 1);
    rhythm.add(`${offset}:${event.step}:${onsetSize}`);
    pitch.add(`${offset}:${event.step}:${((event.midi % 12) + 12) % 12}`);
  }

  return {
    firstMeasure,
    lastMeasure,
    eventCount: blockEvents.length,
    onsetCount: onsets.size,
    rhythm,
    pitch,
  };
}

function blockSimilarity(a, b) {
  const rhythmSimilarity = jaccard(a.rhythm, b.rhythm);
  const pitchSimilarity = jaccard(a.pitch, b.pitch);
  const high = Math.max(a.eventCount, b.eventCount, 1);
  const low = Math.min(a.eventCount, b.eventCount);
  const densitySimilarity = low / high;
  return (
    rhythmSimilarity * 0.55 +
    pitchSimilarity * 0.3 +
    densitySimilarity * 0.15
  );
}

function sectionLetter(index) {
  let value = index + 1;
  let label = '';
  while (value > 0) {
    value -= 1;
    label = String.fromCharCode(65 + (value % 26)) + label;
    value = Math.floor(value / 26);
  }
  return label;
}

export function buildReferenceFreeRhythmSections(rawEvents) {
  const events = projectV143RenderEvents(rawEvents);
  if (!events.length) return [];

  const maximumMeasure = Math.max(...events.map((event) => event.measure));
  const blocks = [];
  for (let firstMeasure = 1; firstMeasure <= maximumMeasure; firstMeasure += SECTION_BLOCK_MEASURES) {
    blocks.push(blockFeatures(events, firstMeasure));
  }

  const clusters = [];
  const assignments = [];
  for (const block of blocks) {
    let bestCluster = -1;
    let bestSimilarity = -1;
    for (let index = 0; index < clusters.length; index += 1) {
      const similarity = blockSimilarity(block, clusters[index]);
      if (similarity > bestSimilarity) {
        bestSimilarity = similarity;
        bestCluster = index;
      }
    }

    if (bestCluster < 0 || bestSimilarity < 0.6) {
      bestCluster = clusters.length;
      clusters.push(block);
    }
    assignments.push(bestCluster);
  }

  const sections = [];
  for (let index = 0; index < blocks.length; index += 1) {
    const cluster = assignments[index];
    const block = blocks[index];
    const previous = sections[sections.length - 1];
    if (previous && previous.cluster === cluster) {
      previous.endMeasure = Math.min(maximumMeasure, block.lastMeasure);
      previous.blockCount += 1;
      continue;
    }

    sections.push({
      index: sections.length,
      cluster,
      label: `SECTION ${sectionLetter(cluster)}`,
      startMeasure: block.firstMeasure,
      endMeasure: Math.min(maximumMeasure, block.lastMeasure),
      blockCount: 1,
      source: 'reference-free-render-event-self-similarity',
      referenceFree: true,
      professionalReferenceUsed: false,
      runtimeLabelsRequired: false,
    });
  }

  return sections;
}

export function summarizeV143RhythmPresentation(rawEvents) {
  const events = projectV143RenderEvents(rawEvents);
  const uniqueMeasures = new Set();
  const uniqueOnsets = new Set();
  const techniqueTypes = new Set();
  const notesPerMeasure = new Map();
  const notesPerOnset = new Map();

  for (const event of events) {
    uniqueMeasures.add(event.measure);
    const onsetKey = `${event.measure}:${event.step}`;
    uniqueOnsets.add(onsetKey);
    notesPerMeasure.set(event.measure, (notesPerMeasure.get(event.measure) || 0) + 1);
    notesPerOnset.set(onsetKey, (notesPerOnset.get(onsetKey) || 0) + 1);
    for (const technique of event.techniques || []) techniqueTypes.add(technique);
  }

  const measureCounts = [...notesPerMeasure.values()];
  const onsetCounts = [...notesPerOnset.values()];
  const sections = buildReferenceFreeRhythmSections(events);

  return {
    eventCount: events.length,
    uniqueMeasureCount: uniqueMeasures.size,
    uniqueOnsetCount: uniqueOnsets.size,
    averageNotesPerMeasure:
      uniqueMeasures.size > 0 ? events.length / uniqueMeasures.size : 0,
    minimumNotesPerPopulatedMeasure:
      measureCounts.length ? Math.min(...measureCounts) : 0,
    maximumNotesPerPopulatedMeasure:
      measureCounts.length ? Math.max(...measureCounts) : 0,
    maximumChordSize:
      onsetCounts.length ? Math.max(...onsetCounts) : 0,
    multiNoteOnsetCount: onsetCounts.filter((count) => count > 1).length,
    techniqueEventCount: events.filter((event) => event.techniques?.length).length,
    techniqueTypes: [...techniqueTypes].sort(),
    sectionCount: sections.length,
    sections,
    oneNotePerMeasureCollapseDetected:
      uniqueMeasures.size >= 8 && events.length <= uniqueMeasures.size + 1,
    referenceFree: true,
    professionalReferenceUsed: false,
    runtimeLabelsRequired: false,
  };
}

export function summarizeV143Techniques(events) {
  const types = new Set();
  for (const event of projectV143RenderEvents(events)) {
    for (const technique of event.techniques || []) types.add(technique);
  }
  return [...types].sort();
}

export {
  ALLOWED_TECHNIQUES,
  MAX_RENDER_EVENTS,
  SECTION_BLOCK_MEASURES,
};
