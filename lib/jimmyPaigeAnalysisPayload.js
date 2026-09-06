import { buildV143AnalyzerQualityReport } from './v143AnalyzerQuality.js';
import { projectV143RenderEvents } from './v143RenderContract.js';

// Large practical Rhythm uploads can produce far more than the old 20k
// event ceiling. Keep a high defensive bound, but do not truncate ordinary
// full-length recordings at a song-sized limit.
const MAX_EVENTS = 100000;
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
  const raw =
    value && typeof value === 'object'
      ? value.type
      : value;
  const technique = cleanText(raw, 40).toLowerCase();
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
    fileSize: boundedInteger(value.fileSize, 1, 5 * 1024 * 1024 * 1024 * 1024, null),
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

  const liveV143 =
    analyzerData?.liveV143 &&
    typeof analyzerData.liveV143 === 'object' &&
    !Array.isArray(analyzerData.liveV143)
      ? analyzerData.liveV143
      : {};

  const referenceFree =
    liveV143.referenceFree === true;
  const professionalReferenceNotUsed =
    liveV143.professionalReferenceUsed === false;
  const referenceRuntimeInputNotUsed =
    liveV143.referenceRuntimeInputUsed === false;
  const runtimeLabelsNotRequired =
    liveV143.runtimeLabelsRequired === false;

  // Structured V143 Rhythm is allowed only when the analyzer explicitly proves
  // the complete runtime anti-leakage contract. A lone referenceFree=true flag
  // is insufficient: professional reference use, reference runtime inputs, or
  // runtime labels must all be explicitly absent before events can reach the
  // product renderer.
  const v143RuntimeSafetyVerified =
    referenceFree &&
    professionalReferenceNotUsed &&
    referenceRuntimeInputNotUsed &&
    runtimeLabelsNotRequired;

  if (
    usingV143RhythmAnalyzer &&
    !v143RuntimeSafetyVerified
  ) {
    throw new Error(
      'V143 rhythm analyzer failed the reference-free runtime safety contract.'
    );
  }

  const rawEvents =
    analyzerData?.events ??
    analyzerData?.noteEvents ??
    liveV143.events;

  const events = normalizeEvents(rawEvents);

  // This is the established DadRock V143 engraving contract. It only accepts
  // events that already carry authenticated musical placement (measure +
  // 16th-step) and playable string/fret data. We never infer those fields in
  // the browser or PDF layer. Unsafe V143 responses never receive renderEvents.
  const renderEvents = v143RuntimeSafetyVerified
    ? projectV143RenderEvents(rawEvents)
    : [];

  // The analyzer quality gate is observational and fail-closed: it reports
  // whether the real V143 response has enough authenticated evidence for a
  // structured professional render. It does not invent placement, mutate the
  // frozen analyzer output, or authorize production promotion.
  const analysisQuality = v143RuntimeSafetyVerified
    ? buildV143AnalyzerQualityReport({
        referenceFree,
        rawEvents,
        renderEvents,
      })
    : null;

  const structuredRenderEligible =
    v143RuntimeSafetyVerified &&
    analysisQuality?.passed === true &&
    renderEvents.length > 0;

  const measureGrid = sanitizeMeasureGrid(
    analyzerData?.measureGrid ??
    analyzerData?.notation?.measureGrid ??
    liveV143.measureGrid
  );

  const techniques = normalizeTechniques(
    analyzerData?.techniques
  );

  return {
    payloadContract: {
      name: 'jimmy-paige-structured-analysis',
      version: 3,
      referenceFree,
      professionalReferenceNotUsed,
      referenceRuntimeInputNotUsed,
      runtimeLabelsNotRequired,
      v143RuntimeSafetyVerified,
      transcriptionType: cleanText(transcriptionType, 20).toLowerCase(),
      boundedEventCount: events.length,
      renderEventCount: renderEvents.length,
      renderContractVersion:
        renderEvents.length > 0 ? 1 : null,
      structuredMeasureGridPresent: Boolean(measureGrid),
      analyzerQualityGatePassed:
        analysisQuality?.passed ?? null,
      structuredRenderEligible,
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
      structuredRenderEligible
        ? 'v143-reference-free-rhythm'
        : referenceFree
          ? 'v143-reference-free-rhythm-fallback'
          : 'legacy',
    analysisQuality,
    events,
    renderEvents,
    renderContractVersion:
      renderEvents.length > 0 ? 1 : null,
    measureGrid,
    audioMetadata: normalizeAudioMetadata(
      analyzerData?.audioMetadata
    ),
    normalizedAudio: normalizeAudioMetadata(
      analyzerData?.normalizedAudio
    ),
  };
}
