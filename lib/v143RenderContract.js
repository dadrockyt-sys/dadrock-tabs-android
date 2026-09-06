// The former 5k cap could truncate a valid long Rhythm transcription.
// Retain a defensive resource bound while allowing large practical recordings.
const MAX_RENDER_EVENTS = 100000;
const SECTION_BLOCK_MEASURES = 4;
const SECTION_MIN_MEASURES = 8;
const SECTION_MAX_MEASURES = 16;
const SECTION_ONSET_CHANGE_THRESHOLD = 0.55;

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

function blockFeatures(events, firstMeasure) {
  const lastMeasure = firstMeasure + SECTION_BLOCK_MEASURES - 1;
  const blockEvents = events.filter(
    (event) => event.measure >= firstMeasure && event.measure <= lastMeasure
  );
  const onsets = new Set(
    blockEvents.map((event) => `${event.measure}:${event.step}`)
  );

  return {
    firstMeasure,
    lastMeasure,
    eventCount: blockEvents.length,
    onsetCount: onsets.size,
  };
}

function relativeChange(previous, current) {
  const low = Math.max(1, Math.min(Number(previous) || 0, Number(current) || 0));
  return Math.abs((Number(current) || 0) - (Number(previous) || 0)) / low;
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

function sectionObject(index, firstBlock, lastMeasure, blockCount, boundaryReason, boundaryStrength) {
  return {
    index,
    cluster: index,
    label: `SECTION ${sectionLetter(index)}`,
    startMeasure: firstBlock.firstMeasure,
    endMeasure: lastMeasure,
    blockCount,
    boundaryReason,
    boundaryStrength: Math.round(Number(boundaryStrength || 0) * 1000) / 1000,
    source: 'reference-free-render-event-change-points',
    referenceFree: true,
    professionalReferenceUsed: false,
    runtimeLabelsRequired: false,
  };
}

export function buildReferenceFreeRhythmSections(rawEvents) {
  const events = projectV143RenderEvents(rawEvents);
  if (!events.length) return [];

  const maximumMeasure = Math.max(...events.map((event) => event.measure));
  const blocks = [];
  for (let firstMeasure = 1; firstMeasure <= maximumMeasure; firstMeasure += SECTION_BLOCK_MEASURES) {
    blocks.push(blockFeatures(events, firstMeasure));
  }
  if (!blocks.length) return [];

  const sections = [];
  let sectionStartBlockIndex = 0;

  for (let blockIndex = 1; blockIndex < blocks.length; blockIndex += 1) {
    const current = blocks[blockIndex];
    const previous = blocks[blockIndex - 1];
    const sectionStart = blocks[sectionStartBlockIndex];
    const measuresSinceSectionStart = current.firstMeasure - sectionStart.firstMeasure;
    const onsetChange = relativeChange(previous.onsetCount, current.onsetCount);
    const minimumSpanReached = measuresSinceSectionStart >= SECTION_MIN_MEASURES;
    const maximumSpanReached = measuresSinceSectionStart >= SECTION_MAX_MEASURES;
    const significantChange =
      minimumSpanReached && onsetChange >= SECTION_ONSET_CHANGE_THRESHOLD;

    if (!maximumSpanReached && !significantChange) continue;

    sections.push(
      sectionObject(
        sections.length,
        sectionStart,
        current.firstMeasure - 1,
        blockIndex - sectionStartBlockIndex,
        significantChange ? 'onset-density-change' : 'maximum-phrase-span',
        onsetChange
      )
    );
    sectionStartBlockIndex = blockIndex;
  }

  const finalStart = blocks[sectionStartBlockIndex];
  sections.push(
    sectionObject(
      sections.length,
      finalStart,
      maximumMeasure,
      blocks.length - sectionStartBlockIndex,
      'song-tail',
      0
    )
  );

  const finalSection = sections[sections.length - 1];
  if (
    sections.length > 1 &&
    finalSection.endMeasure - finalSection.startMeasure + 1 < SECTION_MIN_MEASURES
  ) {
    const previous = sections[sections.length - 2];
    previous.endMeasure = finalSection.endMeasure;
    previous.blockCount += finalSection.blockCount;
    previous.tailMerged = true;
    sections.pop();
  }

  return sections.map((section, index) => ({
    ...section,
    index,
    cluster: index,
    label: `SECTION ${sectionLetter(index)}`,
  }));
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
  SECTION_MIN_MEASURES,
  SECTION_MAX_MEASURES,
  SECTION_ONSET_CHANGE_THRESHOLD,
};
