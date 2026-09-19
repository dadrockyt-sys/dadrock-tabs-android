import { evaluateFreshPipeline } from './freshEvaluator.mjs';

const EPSILON = 1e-7;
const MEASURES_PER_ROW = 6;
const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

function clamp(value, minimum, maximum) {
  return Math.min(maximum, Math.max(minimum, value));
}

function noteName(midi) {
  return NOTE_NAMES[((Number(midi) % 12) + 12) % 12] ?? '?';
}

function tuningLabel(instrumentConfig) {
  return instrumentConfig.tuningMidi.map(noteName).join(' ');
}

function uniqueStrings(values) {
  return [...new Set(
    values
      .filter(Boolean)
      .map((value) => String(value).trim().toLowerCase())
      .filter(Boolean),
  )].sort();
}

function techniqueTypes(event) {
  const values = [];
  const add = (value) => {
    if (typeof value === 'string') values.push(value);
    else if (value && typeof value === 'object' && typeof value.type === 'string') values.push(value.type);
  };
  add(event?.technique);
  for (const item of event?.techniques ?? []) add(item);
  for (const item of event?.notation?.techniques ?? []) add(item);
  return uniqueStrings(values);
}

function measureByNumber(structureMap, number) {
  return structureMap.measures.find((measure) => measure.measureNumber === number) ?? null;
}

function rendererStringIndex(event, stringCount) {
  if (Number.isInteger(event?.fretboard?.stringNumberHighToLow)) {
    return event.fretboard.stringNumberHighToLow - 1;
  }
  if (Number.isInteger(event?.fretboard?.lowToHighIndex)) {
    return stringCount - 1 - event.fretboard.lowToHighIndex;
  }
  return null;
}

function measureSixteenthCount(measure) {
  const denominator = measure?.timeSignature?.denominator;
  const numerator = measure?.timeSignature?.numerator;
  if (!Number.isInteger(denominator) || !Number.isInteger(numerator) || denominator <= 0) return null;
  if (16 % denominator !== 0) return null;
  return numerator * (16 / denominator);
}

function eventLegacyStep(event, measure) {
  const stepsPerBeat = 16 / measure.timeSignature.denominator;
  if (!Number.isInteger(stepsPerBeat)) return null;
  const raw = (event.beatNumber - 1) * stepsPerBeat + event.beatFraction * stepsPerBeat;
  const rounded = Math.round(raw);
  if (Math.abs(raw - rounded) > EPSILON) return null;
  if (rounded < 0 || rounded > 15) return null;
  return rounded;
}

function segmentDurationSteps(segment, structureMap) {
  const measure = measureByNumber(structureMap, segment.measureNumber);
  if (!measure || measure.pickup) return null;
  const totalSteps = measureSixteenthCount(measure);
  if (totalSteps === null || totalSteps > 16) return null;
  const stepSeconds = (measure.end - measure.start) / totalSteps;
  const raw = (segment.end - segment.start) / stepSeconds;
  const rounded = Math.round(raw);
  return Math.abs(raw - rounded) <= EPSILON && rounded >= 0 ? rounded : null;
}

function durationSteps(event, structureMap) {
  const segments = event?.notation?.segments ?? [];
  if (!segments.length) return 1;
  let total = 0;
  for (const segment of segments) {
    const steps = segmentDurationSteps(segment, structureMap);
    if (steps === null) return null;
    total += steps;
  }
  return Math.max(1, total);
}

function projectionCompatibility(result) {
  const structureMap = result.structureMap;
  if (!structureMap) return { compatible: false, reason: 'STRUCTURE_MAP_MISSING' };
  if (structureMap.measures.some((measure) => measure.pickup)) {
    return { compatible: false, reason: 'LEGACY_RENDER_PICKUP_UNSUPPORTED' };
  }

  for (const measure of structureMap.measures) {
    const count = measureSixteenthCount(measure);
    if (count === null || count > 16) {
      return { compatible: false, reason: 'LEGACY_RENDER_METER_UNSUPPORTED' };
    }
  }

  const stringCount = result.instrumentConfig?.tuningMidi?.length ?? 0;
  for (const event of result.events ?? []) {
    const measure = measureByNumber(structureMap, event.measureNumber);
    if (!measure) return { compatible: false, reason: 'EVENT_MEASURE_MISSING' };
    if (eventLegacyStep(event, measure) === null) {
      return { compatible: false, reason: 'LEGACY_RENDER_SUBDIVISION_UNSUPPORTED' };
    }
    const stringIndex = rendererStringIndex(event, stringCount);
    if (!Number.isInteger(stringIndex)
      || stringIndex < 0
      || stringIndex >= stringCount
      || !Number.isInteger(event?.fretboard?.fret)) {
      return { compatible: false, reason: 'LEGACY_RENDER_FRETBOARD_INCOMPLETE' };
    }
    if (durationSteps(event, structureMap) === null) {
      return { compatible: false, reason: 'LEGACY_RENDER_DURATION_UNSUPPORTED' };
    }
  }

  return { compatible: true, reason: null };
}

function buildRenderEvents(result) {
  const stringCount = result.instrumentConfig.tuningMidi.length;
  return result.events.map((event, index) => {
    const measure = measureByNumber(result.structureMap, event.measureNumber);
    return {
      eventIndex: Number.isInteger(event.sourceEventIndex) ? event.sourceEventIndex : index,
      measure: event.measureNumber,
      step: eventLegacyStep(event, measure),
      stringIndex: rendererStringIndex(event, stringCount),
      fret: event.fretboard.fret,
      midi: event.midi,
      durationSteps: durationSteps(event, result.structureMap),
      techniques: techniqueTypes(event),
      ...(Number.isFinite(event.projectedDurationSeconds)
        ? { durationSeconds: event.projectedDurationSeconds }
        : {}),
      source: 'songsterr-fresh-pipeline-v1',
    };
  });
}

function buildMeasureGrid(result) {
  const rows = new Map();
  const measures = result.structureMap.measures.filter((measure) => !measure.pickup);
  for (const measure of measures) {
    const rowNumber = Math.floor((measure.measureNumber - 1) / MEASURES_PER_ROW) + 1;
    if (!rows.has(rowNumber)) rows.set(rowNumber, { rowNumber, notes: [], fragments: [] });
  }

  const stringCount = result.instrumentConfig.tuningMidi.length;
  result.events.forEach((event, index) => {
    const measure = measureByNumber(result.structureMap, event.measureNumber);
    const rowNumber = Math.floor((event.measureNumber - 1) / MEASURES_PER_ROW) + 1;
    const measureSlot = (event.measureNumber - 1) % MEASURES_PER_ROW;
    const within = clamp(
      (event.projectedStart - measure.start) / (measure.end - measure.start),
      0,
      0.999999999,
    );
    const rowRatio = (measureSlot + within) / MEASURES_PER_ROW;
    rows.get(rowNumber).notes.push({
      eventIndex: Number.isInteger(event.sourceEventIndex) ? event.sourceEventIndex : index,
      measure: event.measureNumber,
      rowRatio,
      stringIndex: rendererStringIndex(event, stringCount),
      fret: event.fretboard.fret,
      midi: event.midi,
      measureGridReadOnly: true,
      musicallyFiltered: true,
      source: 'songsterr-fresh-pipeline-v1',
    });
  });

  return {
    passed: true,
    measureGridVersion: 7,
    measureGridType: 'songsterr-fresh-read-only-projection',
    measuresPerRow: MEASURES_PER_ROW,
    rows: [...rows.values()].sort((a, b) => a.rowNumber - b.rowNumber),
    markers: [],
    referenceFree: true,
    legacyV143ScorerImported: false,
  };
}

function slotsForMeasure(measure) {
  const slots = new Set();
  for (const beat of measure.beats ?? []) {
    for (const slot of beat.subdivisions ?? []) slots.add(slot);
  }
  return [...slots].sort((a, b) => a - b);
}

function positionalLabels(role, stringCount) {
  if (role === 'bass') return ['G', 'D', 'A', 'E'].slice(0, stringCount);
  return ['e', 'B', 'G', 'D', 'A', 'E'].slice(0, stringCount);
}

function buildGeneratedTab(result) {
  const measures = result.structureMap?.measures ?? [];
  const events = result.events ?? [];
  const stringCount = result.instrumentConfig.tuningMidi.length;
  const labels = positionalLabels(result.instrumentConfig.role, stringCount);
  const systems = [];

  for (let start = 0; start < measures.length; start += MEASURES_PER_ROW) {
    const group = measures.slice(start, start + MEASURES_PER_ROW);
    const lines = Array.from({ length: stringCount }, (_, row) => `${labels[row] ?? 'E'}|`);

    for (const measure of group) {
      const slots = slotsForMeasure(measure);
      const width = Math.max(1, slots.length);
      const cells = Array.from(
        { length: stringCount },
        () => Array.from({ length: width }, () => '---'),
      );
      const measureEvents = events.filter((event) => event.measureNumber === measure.measureNumber);

      for (const event of measureEvents) {
        const stringIndex = rendererStringIndex(event, stringCount);
        if (!Number.isInteger(stringIndex) || stringIndex < 0 || stringIndex >= stringCount) continue;
        let slotIndex = 0;
        let best = Infinity;
        for (let index = 0; index < slots.length; index += 1) {
          const distance = Math.abs(slots[index] - event.projectedStart);
          if (distance < best) {
            best = distance;
            slotIndex = index;
          }
        }
        const fret = Number.isInteger(event?.fretboard?.fret) ? String(event.fretboard.fret) : '?';
        cells[stringIndex][slotIndex] = fret.padEnd(3, '-').slice(0, 3);
      }

      for (let row = 0; row < stringCount; row += 1) {
        lines[row] += `${cells[row].join('')}|`;
      }
    }

    systems.push(`RIFF ${systems.length + 1}\n${lines.join('\n')}`);
  }

  return systems.join('\n\n').trim();
}

export function buildProductShellPayload({
  result,
  sourceEvents = null,
  keySignature = null,
  difficulty = null,
  techniques = [],
  confidence = null,
  upstreamEvidenceReady = true,
  upstreamEvidenceBlockers = [],
} = {}) {
  if (!result?.structureMap || !Array.isArray(result?.events) || !result?.instrumentConfig) {
    throw new Error('result must contain structureMap, events, and instrumentConfig.');
  }
  if (typeof upstreamEvidenceReady !== 'boolean') {
    throw new Error('upstreamEvidenceReady must be boolean.');
  }
  if (!Array.isArray(upstreamEvidenceBlockers)) {
    throw new Error('upstreamEvidenceBlockers must be an array.');
  }

  const normalizedUpstreamBlockers = [...new Set(
    upstreamEvidenceBlockers.map((value) => String(value).trim()).filter(Boolean),
  )];
  if (upstreamEvidenceReady && normalizedUpstreamBlockers.length > 0) {
    throw new Error('upstreamEvidenceReady cannot be true when upstreamEvidenceBlockers are present.');
  }

  const evaluation = evaluateFreshPipeline(result, { sourceEvents });
  const compatibility = projectionCompatibility(result);
  const generatedTab = buildGeneratedTab(result);
  const rawResultReady = evaluation.passedRawIntegrityChecks && Boolean(generatedTab);
  const deliveryReady = upstreamEvidenceReady && rawResultReady;
  const structuredRenderEligible = deliveryReady && compatibility.compatible;
  const allTechniques = uniqueStrings([
    ...(techniques ?? []),
    ...result.events.flatMap(techniqueTypes),
  ]);
  const firstTempo = result.structureMap.tempoSegments?.[0]?.bpm ?? null;
  const firstMeter = result.structureMap.meterSegments?.[0] ?? null;

  return {
    payloadContract: {
      name: 'songsterr-fresh-product-shell',
      version: 1,
      referenceBlind: true,
      legacyV143ScorerImported: false,
      upstreamEvidenceReady,
      upstreamEvidenceBlockers: normalizedUpstreamBlockers,
      rawResultReady,
      structuredRenderEligible,
      legacyProjectionCompatible: compatibility.compatible,
      legacyProjectionReason: compatibility.reason,
      deliveryReady,
    },
    generatedTab,
    transcriptionType: result.instrumentConfig.role,
    tuning: tuningLabel(result.instrumentConfig),
    tempo: firstTempo,
    timeSignature: firstMeter ? `${firstMeter.numerator}/${firstMeter.denominator}` : null,
    keySignature: keySignature ? String(keySignature) : null,
    difficulty: difficulty ? String(difficulty) : null,
    techniques: allTechniques,
    confidence: Number.isFinite(Number(confidence))
      ? Number(confidence)
      : (result.structureMap.confidence?.overall ?? null),
    analysisEngine: 'songsterr-fresh-pipeline-v1',
    events: result.events,
    renderEvents: structuredRenderEligible ? buildRenderEvents(result) : [],
    renderContractVersion: structuredRenderEligible ? 1 : null,
    measureGrid: structuredRenderEligible ? buildMeasureGrid(result) : null,
    structureMap: result.structureMap,
    freshDiagnostics: evaluation,
  };
}
