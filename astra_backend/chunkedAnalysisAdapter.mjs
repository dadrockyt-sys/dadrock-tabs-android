import { normalizeAstraAnalyzerRequest, buildAstraAnalyzerResult } from './analysisContractAdapter.mjs';
import { processSampleChunks, SampleChunkProcessingError } from './sampleChunkProcessor.mjs';

/** Offline extraction boundary. Sample completion does not supply musical evidence. */
export async function runAstraChunkedAnalysis({ request: rawRequest, chunks } = {}) {
  const request = normalizeAstraAnalyzerRequest(rawRequest);
  let progress;
  try {
    progress = await processSampleChunks(chunks);
  } catch (error) {
    if (!(error instanceof SampleChunkProcessingError)) throw error;
    progress = error.progress;
  }
  const completed = progress.status === 'complete';
  const cancelled = progress.status === 'cancelled';
  return buildAstraAnalyzerResult({
    request,
    stages: {
      input: { status: 'complete', blockers: [], validationScope: 'request-and-sample-plan' },
      extraction: {
        status: completed ? 'partial' : cancelled ? 'abstained' : 'failed',
        blockers: [completed ? 'EXTRACTION_MUSICAL_EVIDENCE_MISSING'
          : cancelled ? 'CHUNK_PROCESSING_CANCELLED' : 'CHUNK_PROCESSING_FAILED'],
        rolePresence: 'uncertain',
        chunkProgress: progress,
      },
      events: { status: 'not-run', blockers: ['VALIDATED_EXTRACTION_UNAVAILABLE'] },
      structure: { status: 'not-run', blockers: ['VALIDATED_EXTRACTION_UNAVAILABLE'] },
    },
    lineage: { separator: 'injected-sample-processor-unverified' },
  });
}
