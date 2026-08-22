const MAX_EVENTS = 20000;
const MAX_TECHNIQUES = 40;
const MAX_AUDIO_METADATA_KEYS = 16;

function cleanText(value, maximumLength = 160) {
  return String(value ?? '')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, maximumLength);
}

function finiteNumber(value, fallback = null) {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function boundedInteger(value, minimum, maximum, fallback = null) {
  const parsed = Number(value);
  if (!Number.isInteger(parsed)) return fallback;
  return Math.min(maximum, Math.max(minimum, parsed));
}

function normalizeTechnique(value) {
  const technique = cleanText(value, 40).toLowerCase();
  return technique || null;
}

function normalizeEvent(event, index) {
  if (!event || typeof event !== 'object') return null;

  const start = finiteNumber(
    event.start ?? event.startTime ?? event.onsetTime,
    null
  );
  const end = finiteNumber(
    event.end ?? event.endTime ?? event.offsetTime,
    start
  );
  const stringIndex = boundedInteger(
    event.stringIndex,
    0,
    5,
    null
  );
  const fret = boundedInteger(
    event.fret,
    0,
    36,
    null
  );

  if (
    start === null ||
    start < 0 ||
    stringIndex === null ||
    fret === null
  ) {
    return null;
  }

  const safeEnd =
    end === null || end < start
      ? start
      : end;

  return {
    eventIndex: index,
    start,
    end: safeEnd,
    duration: Math.max(
      0,
      finiteNumber(event.duration, safeEnd - start)
    ),
    midi: boundedInteger(event.midi, 0, 127, null),
    amplitude: finiteNumber(event.amplitude, null),
    stringIndex,
    fret,
    technique: normalizeTechnique(event.technique),
    bendSemitones: Math.max(
      0,
      finiteNumber(event.bendSemitones, 0)
    ),
    source: cleanText(event.source, 80) || null,
    confidence: finiteNumber(event.confidence, null),
  };
}

function normalizeEvents(value) {
  if (!Array.isArray(value)) return [];

  const rows = [];
  for (let index = 0; index < value.length && rows.length < MAX_EVENTS; index += 1) {
    const normalized = normalizeEvent(value[index], index);
    if (normalized) rows.push(normalized);
  }

  rows.sort((a, b) => {
    if (a.start !== b.start) return a.start - b.start;
    if (a.stringIndex !== b.stringIndex) return a.stringIndex - b.stringIndex;
    if (a.fret !== b.fret) return a.fret - b.fret;
    return a.eventIndex - b.eventIndex;
  });

  return rows;
}

function normalizeTechniques(value) {
  if (!Array.isArray(value)) return [];

  return [
    ...new Set(
      value
        .map(normalizeTechnique)
        .filter(Boolean)
    ),
  ].slice(0, MAX_TECHNIQUES);
}

function normalizeAudioMetadata(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return null;
  }

  const allowed = {
    durationSeconds: finiteNumber(value.durationSeconds, null),
    sampleRate: boundedInteger(value.sampleRate, 1, 768000, null),
    channels: boundedInteger(value.channels, 1, 32, null),
    channelLayout: cleanText(value.channelLayout, 80) || null,
    codec: cleanText(value.codec, 80) || null,
    bitrate: boundedInteger(value.bitrate, 1, 100000000, null),
    formatName: cleanText(value.formatName, 120) || null,
    fileSize: boundedInteger(value.fileSize, 1, 1024 * 1024 * 1024, null),
  };

  return Object.fromEntries(
    Object.entries(allowed)
      .filter(([, fieldValue]) => fieldValue !== null)
      .slice(0, MAX_AUDIO_METADATA_KEYS)
  );
}

function sanitizeMeasureGrid(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return null;
  }

  // A measure grid is already a derived, read-only renderer projection. Keep it
  // intact here so its internal provenance fields/digests survive transport;
  // the professional PDF contract performs the fail-closed semantic validation
  // immediately before rendering.
  return value;
}

export function buildJimmyPaigeAnalysisPayload(
  analyzerData = {},
  {
    transcriptionType = '',
    usingV143RhythmAnalyzer = false,
  } = {}
) {
  const generatedTab = String(
    analyzerData?.generatedTab || ''
  ).replace(/\r\n/g, '\n').trim().slice(0, 30000);

  if (!generatedTab) {
    throw new Error('Analyzer returned no tablature.');
  }

  if (
    usingV143RhythmAnalyzer &&
    analyzerData?.liveV143?.referenceFree !== true
  ) {
    throw new Error(
      'V143 rhythm analyzer did not identify itself as reference-free.'
    );
  }

  const events = normalizeEvents(
    analyzerData?.events ??
    analyzerData?.noteEvents ??
    analyzerData?.liveV143?.events
  );

  const measureGrid = sanitizeMeasureGrid(
    analyzerData?.measureGrid ??
    analyzerData?.notation?.measureGrid ??
    analyzerData?.liveV143?.measureGrid
  );

  const techniques = normalizeTechniques(
    analyzerData?.techniques
  );

  return {
    payloadContract: {
      name: 'jimmy-paige-structured-analysis',
      version: 1,
      referenceFree:
        analyzerData?.liveV143?.referenceFree === true,
      transcriptionType: cleanText(transcriptionType, 20).toLowerCase(),
      boundedEventCount: events.length,
      structuredMeasureGridPresent: Boolean(measureGrid),
      productionPromotionAuthorized: false,
    },
    generatedTab,
    tuning: cleanText(analyzerData?.tuning, 80) || null,
    tempo: finiteNumber(analyzerData?.tempo, null),
    timeSignature: cleanText(analyzerData?.timeSignature, 20) || null,
    keySignature: cleanText(analyzerData?.keySignature, 40) || null,
    difficulty: cleanText(analyzerData?.difficulty, 80) || null,
    techniques,
    confidence: finiteNumber(analyzerData?.confidence, null),
    noteCount: boundedInteger(
      analyzerData?.noteCount,
      0,
      MAX_EVENTS,
      events.length
    ),
    analysisEngine:
      analyzerData?.liveV143?.referenceFree === true
        ? 'v143-reference-free-rhythm'
        : 'legacy',
    events,
    measureGrid,
    audioMetadata: normalizeAudioMetadata(
      analyzerData?.audioMetadata
    ),
    normalizedAudio: normalizeAudioMetadata(
      analyzerData?.normalizedAudio
    ),
  };
}
