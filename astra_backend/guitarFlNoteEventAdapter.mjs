const EXPECTED_CHECKPOINT_SHA256 = '50d93dba89bdd3401849bc735614478e83d9f46d21fa3f71d8aca5acc0a52028';

function require(condition, message) {
  if (!condition) throw new Error(message);
}

function finite(value, field) {
  const parsed = Number(value);
  if (!Number.isFinite(parsed)) throw new Error(`${field} must be finite.`);
  return parsed;
}

function integerMidi(value, field) {
  const midi = Number(value);
  if (!Number.isInteger(midi) || midi < 0 || midi > 127) {
    throw new Error(`${field} must be an integer from 0 to 127.`);
  }
  return midi;
}

function normalizeEvent(event, index) {
  const start = finite(event?.start, `events[${index}].start`);
  require(start >= 0, `events[${index}].start must be non-negative.`);

  const midi = integerMidi(event?.pitch ?? event?.midi, `events[${index}].pitch`);

  const hasEnd = event?.end !== undefined && event?.end !== null;
  const end = hasEnd ? finite(event.end, `events[${index}].end`) : null;
  if (end !== null) require(end > start, `events[${index}].end must be greater than start.`);

  const sourceEventIndex = event?.eventId === undefined || event?.eventId === null
    ? index
    : Number(event.eventId);
  require(Number.isInteger(sourceEventIndex) && sourceEventIndex >= 0,
    `events[${index}].eventId must be a non-negative integer when present.`);

  const normalized = {
    midi,
    start,
    sourceEventIndex,
    provenance: {
      source: 'guitar-fl-frozen-note-events-v1',
      checkpointSha256: EXPECTED_CHECKPOINT_SHA256,
      referenceBlind: true,
      roleAuthority: false,
      confidenceSynthesized: false,
    },
  };

  if (end !== null) {
    normalized.end = end;
    normalized.duration = end - start;
  }

  return normalized;
}

export function adaptFrozenGuitarFlEvents(payload = {}) {
  require(payload?.schema === 'astra-fresh-front-end-candidate-v1',
    'payload schema must be astra-fresh-front-end-candidate-v1.');
  require(payload?.frontEnd === 'xavriley_guitar_fl',
    'payload frontEnd must be xavriley_guitar_fl.');
  require(payload?.referenceRead === false, 'payload must declare referenceRead: false.');
  require(payload?.predictionMutation === false, 'payload must declare predictionMutation: false.');
  require(payload?.thresholdSearch === false, 'payload must declare thresholdSearch: false.');
  require(payload?.optimizerSteps === 0, 'payload must declare optimizerSteps: 0.');
  require(payload?.identity?.checkpointSha256 === EXPECTED_CHECKPOINT_SHA256,
    'payload checkpoint SHA-256 does not match frozen guitar-fl identity.');
  require(Array.isArray(payload?.events), 'payload.events must be an array.');
  require(payload?.eventCount === payload.events.length, 'payload eventCount must equal events.length.');

  const normalized = payload.events.map(normalizeEvent);

  for (let i = 1; i < normalized.length; i += 1) {
    const prev = normalized[i - 1];
    const curr = normalized[i];
    require(
      curr.start > prev.start
        || (curr.start === prev.start && curr.midi >= prev.midi),
      'payload events must be deterministically sorted by onset then MIDI.',
    );
  }

  return {
    adapterContract: {
      name: 'astra-guitar-fl-generic-note-event-adapter',
      version: 1,
      referenceBlind: true,
      modelInvoked: false,
      networkAccess: false,
      roleAuthority: false,
      confidenceSynthesized: false,
      stringFretSynthesized: false,
      duplicateSimultaneousPitchesDeduplicated: false,
    },
    frontEnd: {
      id: 'xavriley_guitar_fl',
      checkpointSha256: EXPECTED_CHECKPOINT_SHA256,
    },
    source: {
      trackStem: payload.trackStem ?? null,
      sourceAudioSha256: payload.sourceAudioSha256 ?? null,
      eventCount: payload.eventCount,
    },
    events: normalized,
  };
}

export const GUITAR_FL_EXPECTED_CHECKPOINT_SHA256 = EXPECTED_CHECKPOINT_SHA256;
