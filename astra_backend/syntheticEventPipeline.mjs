import { normalizeAstraAnalyzerRequest } from './analysisContractAdapter.mjs';
import { validateSyntheticExtractionEvidence, runAstraSyntheticExtraction } from './syntheticExtractionHandoff.mjs';
import { normalizeStructureMap } from './structureMap.mjs';
import { runFreshDeterministicPipeline } from './deterministicPipeline.mjs';

function normalizeEvents(events, evidence) {
  if (!Array.isArray(events)) throw new TypeError('events must be an array.');
  const clipEnd = evidence.sampleCount / evidence.sampleRate;
  const seen = new Set();
  return events.map((event, index) => {
    const eventId = event?.eventId;
    if (typeof eventId !== 'string' || !eventId.trim() || eventId.length > 200 || seen.has(eventId)) {
      throw new TypeError('Each event requires a unique nonempty eventId.');
    }
    seen.add(eventId);
    const { start, midi } = event;
    if (!Number.isFinite(start) || start < 0 || start >= clipEnd) throw new RangeError(`Event ${index} onset outside clip.`);
    if (!Number.isInteger(midi) || midi < 0 || midi > 127) throw new TypeError(`Event ${index} MIDI is invalid.`);
    const hasEnd = event.end !== undefined && event.end !== null;
    const hasDuration = event.duration !== undefined && event.duration !== null;
    if (hasDuration && (!Number.isFinite(event.duration) || event.duration <= 0)) throw new RangeError('Invalid event duration.');
    if (hasEnd && (!Number.isFinite(event.end) || event.end <= start)) throw new RangeError('Invalid event end.');
    const end = hasEnd ? event.end : hasDuration ? start + event.duration : null;
    if (end !== null && (!Number.isFinite(end) || end <= start || end > clipEnd)) throw new RangeError('Event extends outside clip.');
    if (hasEnd && hasDuration && Math.abs(start + event.duration - end) > 1e-9) throw new RangeError('Conflicting event end and duration.');
    return Object.freeze({ eventId, start, midi, end,
      duration: end === null ? null : end - start });
  });
}

/** Supplied synthetic events become diagnostic tablature, never a delivery payload. */
export async function runAstraSyntheticEventPipeline({ request: rawRequest, chunks, evidence: rawEvidence, events, structureMap } = {}) {
  const request = normalizeAstraAnalyzerRequest(rawRequest);
  const evidence = validateSyntheticExtractionEvidence(rawEvidence, { request, totalSamples: chunks?.totalSamples });
  const supplied = normalizeEvents(events, evidence);
  const map = normalizeStructureMap(structuredClone(structureMap));
  if (Math.abs(map.durationSeconds - evidence.sampleCount / evidence.sampleRate) > 1e-9) {
    throw new RangeError('Structure duration must match the declared sample duration.');
  }
  const instrument = request.conditioning.instrumentConfig;
  if (instrument.tuningMidi === 'auto' || instrument.capoFret === 'auto') {
    throw new TypeError('Synthetic event diagnostics require explicit tuning and capo.');
  }
  let diagnostics = null;
  const result = await runAstraSyntheticExtraction({ request, chunks, evidence,
    downstream: () => {
      const pipeline = runFreshDeterministicPipeline({ events: supplied, structureMap: map,
        instrumentConfig: instrument,
        productShell: { upstreamEvidenceReady: false, upstreamEvidenceBlockers: ['SYNTHETIC_QUALITY_UNRESOLVED'] },
      });
      diagnostics = {
        kind: 'synthetic-event-diagnostics-v1', customerDeliveryEligible: false,
        sampleIdentity: evidence.sampleIdentity,
        events: pipeline.events.map(event => ({ ...event,
          eventId: supplied[event.sourceEventIndex].eventId,
          durationStatus: event.sourceEnd === null ? 'unresolved' : 'resolved',
        })),
        rests: pipeline.rests, metrics: pipeline.metrics,
        fretboardPath: pipeline.fretboardPath, rhythmSpelling: pipeline.rhythmSpelling,
        generatedTab: pipeline.productShell.generatedTab,
        payloadContract: pipeline.productShell.payloadContract,
      };
    },
  });
  return { ...result, diagnostics: result.downstream.status === 'complete' ? diagnostics : null };
}
