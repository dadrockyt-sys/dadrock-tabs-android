import { normalizeAstraAnalyzerRequest } from './analysisContractAdapter.mjs';
import { runAstraChunkedAnalysis } from './chunkedAnalysisAdapter.mjs';

function identity(value, field) {
  if (typeof value !== 'string' || !value.trim() || value.length > 200) {
    throw new TypeError(`${field} must be a nonempty identity up to 200 characters.`);
  }
  return value.trim();
}

/** Validates synthetic declarations, not audio content or musical truth. */
export function validateSyntheticExtractionEvidence(raw, { request, totalSamples } = {}) {
  if (!raw || raw.kind !== 'synthetic-extraction-v1' || raw.quality !== 'unresolved') {
    throw new TypeError('Synthetic extraction requires explicit unresolved quality.');
  }
  if (raw.requestId !== request.requestId || raw.role !== request.transcriptionType) {
    throw new TypeError('Extraction request/role mismatch.');
  }
  if (!Number.isSafeInteger(raw.sampleCount) || raw.sampleCount <= 0 || raw.sampleCount !== totalSamples) {
    throw new TypeError('Extraction sample count must match a nonempty chunk plan.');
  }
  if (!Number.isSafeInteger(raw.sampleRate) || raw.sampleRate <= 0 || raw.sampleRate > 384000) {
    throw new TypeError('Extraction sample rate must be an integer from 1 to 384000.');
  }
  return Object.freeze({
    kind: raw.kind, quality: 'unresolved', requestId: raw.requestId, role: raw.role,
    sampleCount: raw.sampleCount, sampleRate: raw.sampleRate,
    sampleIdentity: identity(raw.sampleIdentity, 'sampleIdentity'),
    provenance: Object.freeze({
      source: identity(raw.provenance?.source, 'provenance.source'),
      processor: identity(raw.provenance?.processor, 'provenance.processor'),
    }),
  });
}

/** Downstream synthetic diagnostics stay separate from the blocked analyzer payload. */
export async function runAstraSyntheticExtraction({ request: rawRequest, chunks, evidence: rawEvidence, downstream } = {}) {
  const request = normalizeAstraAnalyzerRequest(rawRequest);
  const evidence = validateSyntheticExtractionEvidence(rawEvidence, { request, totalSamples: chunks?.totalSamples });
  if (typeof downstream !== 'function') throw new TypeError('downstream must be a function.');
  const analysis = await runAstraChunkedAnalysis({ request, chunks });
  const progress = analysis.astra.stages.extraction.chunkProgress;
  let outcome = { status: 'not-run', reason: 'CHUNKS_INCOMPLETE' };
  if (progress.status === 'complete' && !chunks.signal?.aborted) {
    try {
      // Callback results deliberately cannot become analyzer payload or evidence.
      await downstream({ evidence, progress, signal: chunks.signal });
      outcome = chunks.signal?.aborted
        ? { status: 'cancelled', reason: 'SYNTHETIC_DOWNSTREAM_CANCELLED' }
        : { status: 'complete', reason: 'SYNTHETIC_DIAGNOSTICS_ONLY' };
    } catch {
      outcome = { status: chunks.signal?.aborted ? 'cancelled' : 'failed', reason: 'SYNTHETIC_DOWNSTREAM_FAILED' };
    }
  }
  return { analysis, evidence, downstream: Object.freeze(outcome) };
}
