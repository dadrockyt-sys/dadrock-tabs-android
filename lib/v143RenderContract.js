const MAX_RENDER_EVENTS = 5000;

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

    const output = {
      eventIndex,
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

// Validate an event stream that has already been authenticated/projected by
// projectV143RenderEvents. Unlike a second projection, this preserves the
// original eventIndex values used by legato/connector relationships. This makes
// the structured event -> PDF path idempotent instead of compacting event IDs
// each time the renderer is called.
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

export function summarizeV143Techniques(events) {
  const types = new Set();
  for (const event of projectV143RenderEvents(events)) {
    for (const technique of event.techniques || []) types.add(technique);
  }
  return [...types].sort();
}

export { ALLOWED_TECHNIQUES, MAX_RENDER_EVENTS };
