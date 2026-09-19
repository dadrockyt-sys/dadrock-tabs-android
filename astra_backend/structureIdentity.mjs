const OFFSET_BASIS = 0x811c9dc5;
const FNV_PRIME = 0x01000193;

function finite(value, field) {
  const number = Number(value);
  if (!Number.isFinite(number)) throw new Error(`${field} must be finite.`);
  return number;
}

function canonicalNumber(value, field) {
  const number = finite(value, field);
  if (Object.is(number, -0)) return 0;
  return Number(number.toPrecision(15));
}

function canonicalSegment(segment, kind, index) {
  const base = {
    start: canonicalNumber(segment?.start, `${kind}[${index}].start`),
    end: segment?.end === null || segment?.end === undefined
      ? null
      : canonicalNumber(segment.end, `${kind}[${index}].end`),
  };
  if (kind === 'tempoSegments') return { ...base, bpm: canonicalNumber(segment?.bpm, `${kind}[${index}].bpm`) };
  if (kind === 'meterSegments') {
    return {
      ...base,
      numerator: Number(segment?.numerator),
      denominator: Number(segment?.denominator),
    };
  }
  return { ...base, feel: segment?.feel };
}

function canonicalStructure(structureMap) {
  if (!structureMap || typeof structureMap !== 'object') throw new Error('structureMap is required.');
  return {
    version: Number(structureMap.version),
    referenceBlind: structureMap.referenceBlind === true,
    durationSeconds: canonicalNumber(structureMap.durationSeconds, 'durationSeconds'),
    pickupDurationSeconds: canonicalNumber(structureMap.pickupDurationSeconds ?? 0, 'pickupDurationSeconds'),
    tempoSegments: (structureMap.tempoSegments ?? []).map((segment, index) => canonicalSegment(segment, 'tempoSegments', index)),
    meterSegments: (structureMap.meterSegments ?? []).map((segment, index) => canonicalSegment(segment, 'meterSegments', index)),
    feelSegments: (structureMap.feelSegments ?? []).map((segment, index) => canonicalSegment(segment, 'feelSegments', index)),
    measures: (structureMap.measures ?? []).map((measure, index) => ({
      measureNumber: Number(measure?.measureNumber),
      pickup: measure?.pickup === true,
      start: canonicalNumber(measure?.start, `measures[${index}].start`),
      end: canonicalNumber(measure?.end, `measures[${index}].end`),
      beatCount: Array.isArray(measure?.beats) ? measure.beats.length : 0,
    })),
  };
}

function fnv1a32(text) {
  let hash = OFFSET_BASIS;
  for (let index = 0; index < text.length; index += 1) {
    hash ^= text.charCodeAt(index);
    hash = Math.imul(hash, FNV_PRIME) >>> 0;
  }
  return hash.toString(16).padStart(8, '0');
}

export function buildStructureIdentity(structureMap) {
  const canonical = JSON.stringify(canonicalStructure(structureMap));
  return {
    contract: 'songsterr-fresh-frozen-structure-identity-v1',
    version: 1,
    signature: `fnv1a32:${fnv1a32(canonical)}`,
    canonicalLength: canonical.length,
  };
}
