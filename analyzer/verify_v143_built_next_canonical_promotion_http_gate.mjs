import assert from 'node:assert/strict';
import http from 'node:http';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const baseUrl = String(
  process.env.V143_CANONICAL_HTTP_BASE_URL || 'http://127.0.0.1:4310'
).replace(/\/$/, '');

const analyzerHost = '127.0.0.1';
const analyzerPort = Number(
  process.env.V143_CANONICAL_HTTP_ANALYZER_PORT || 4311
);

const resultPath =
  process.env.V143_CANONICAL_HTTP_RESULT_PATH ||
  'debug/v143-contextual-prune/built-next-canonical-promotion-http-gate.json';

const expectedFeature = 'v143-branch-preview-canary';
const expectedRenderer = 'v143-structured-rhythm';
const analyzerToken = 'phase13-analyzer-token';
const blobToken = 'phase13-blob-token';
const inertAudioUrl = 'https://synthetic.invalid/v143-phase13-fixture.wav';

const rawEvents = [
  { start: 0.000, end: 0.080, stringIndex: 0, fret: 0, midi: 64 },
  { start: 0.375, end: 0.455, stringIndex: 1, fret: 1, midi: 60 },
  { start: 1.875, end: 1.955, stringIndex: 2, fret: 2, midi: 57 },
  { start: 2.000, end: 2.080, stringIndex: 3, fret: 2, midi: 52 },
  { start: 2.625, end: 2.705, stringIndex: 4, fret: 3, midi: 48 },
  { start: 3.875, end: 3.955, stringIndex: 5, fret: 5, midi: 45 },
  { start: 4.000, end: 4.080, stringIndex: 0, fret: 3, midi: 67 },
];

const oracle = [
  { eventIndex: 0, measure: 1, step: 0, stringIndex: 0, fret: 0, midi: 64 },
  { eventIndex: 1, measure: 1, step: 3, stringIndex: 1, fret: 1, midi: 60 },
  { eventIndex: 2, measure: 1, step: 15, stringIndex: 2, fret: 2, midi: 57 },
  { eventIndex: 3, measure: 2, step: 0, stringIndex: 3, fret: 2, midi: 52 },
  { eventIndex: 4, measure: 2, step: 5, stringIndex: 4, fret: 3, midi: 48 },
  { eventIndex: 5, measure: 2, step: 15, stringIndex: 5, fret: 5, midi: 45 },
  { eventIndex: 6, measure: 3, step: 0, stringIndex: 0, fret: 3, midi: 67 },
];

const generatedTab = [
  'e|--0---------------------------3--|',
  'B|------1---------------------------|',
  'G|--------------2-------------------|',
  'D|------------------2---------------|',
  'A|----------------------3-----------|',
  'E|------------------------------5---|',
].join('\n');

function field(value, confidence = 0.9, method = 'phase13-synthetic-known-truth-v1') {
  return { value, confidence, method };
}

function trustedObservation() {
  return {
    version: 1,
    provenance: {
      sourceKind: 'full-mixture',
      sourceIdentity: 'request-audio',
      referenceBlind: true,
      referenceRuntimeInputUsed: false,
    },
    diagnostics: {
      referenceBlind: true,
      carrierInputUsed: false,
      transcribedEventInputUsed: false,
      wavAdapter: {
        fullMixtureOnly: true,
        separatedCarrierUsed: false,
        transcribedEventInputUsed: false,
      },
    },
    tempoBpm: field(120, 0.92, 'phase13-synthetic-tempo-v1'),
    timeSignature: field(
      { numerator: 4, denominator: 4 },
      0.91,
      'phase13-synthetic-meter-v1'
    ),
    pickupBeats: field(0, 0.90, 'phase13-synthetic-pickup-v1'),
    feel: field('straight', 0.89, 'phase13-synthetic-feel-v1'),
  };
}

function analyzerResponseFixture() {
  return {
    generatedTab,
    events: rawEvents,
    liveV143: {
      referenceFree: true,
      professionalReferenceUsed: false,
      referenceRuntimeInputUsed: false,
      runtimeLabelsRequired: false,
    },
    tuning: 'Standard Tuning',
    tempo: 120,
    timeSignature: '4/4',
    keySignature: 'C major',
    confidence: 0.91,
    difficulty: 'Intermediate',
    techniques: [],
    mixtureObservation: trustedObservation(),
  };
}

function requestConditioning() {
  return {
    version: 1,
    structurePrior: {},
    instrumentConfig: {
      role: 'rhythm',
      tuningMidi: [40, 45, 50, 55, 59, 64],
      capoFret: 0,
    },
  };
}

function placementView(rows) {
  return rows.map((row) => ({
    eventIndex: row.eventIndex,
    measure: row.measure,
    step: row.step,
    stringIndex: row.stringIndex,
    fret: row.fret,
    midi: row.midi,
  }));
}

const evidence = {
  schemaVersion: 1,
  gate: 'v143-built-next-canonical-promotion-http-gate',
  branch: 'v143-contextual-prune-lobo',
  baseUrl,
  analyzerStubUrl: `http://${analyzerHost}:${analyzerPort}/analyze`,
  localNextPreviewSimulation: true,
  actualVercelPreviewDeployment: false,
  referenceBlind: true,
  externalAudioAssetsUsed: false,
  inertAudioUrlFetched: false,
  guitarSetRead: false,
  splitMySongRead: false,
  goatRestrictedBytesRead: false,
  referenceScoreCalls: 0,
  modalInvoked: false,
  modalDeployed: false,
  gpuUsed: false,
  cudaUsed: false,
  analyzerStubRequestCount: 0,
  analyzerStubContractPassed: false,
  analysisStatus: null,
  rhythmCanaryActive: false,
  promotionReason: null,
  baselineRenderEventCount: null,
  canonicalRenderEventCount: null,
  exactKnownTruthMatches: 0,
  canonicalGeneratedTabUnchanged: false,
  canonicalEventCount: null,
  previewStatus: null,
  previewFeature: null,
  previewRenderer: null,
  previewPdfBytes: null,
  invalidAnalysis400Passed: false,
  passed: false,
  vercelDeploymentAttempted: false,
  liveEndpointDeployedOrModified: false,
  mainModified: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  error: null,
};

async function persistEvidence() {
  const absolute = path.resolve(resultPath);
  await mkdir(path.dirname(absolute), { recursive: true });
  await writeFile(absolute, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
}

function readJsonBody(request) {
  return new Promise((resolve, reject) => {
    let text = '';
    request.setEncoding('utf8');
    request.on('data', (chunk) => {
      text += chunk;
      if (text.length > 1_000_000) {
        reject(new Error('Analyzer stub request body too large'));
        request.destroy();
      }
    });
    request.on('end', () => {
      try {
        resolve(JSON.parse(text || '{}'));
      } catch (error) {
        reject(error);
      }
    });
    request.on('error', reject);
  });
}

let stubFailure = null;
const analyzerServer = http.createServer(async (request, response) => {
  try {
    if (request.method !== 'POST' || request.url !== '/analyze') {
      response.writeHead(404, { 'content-type': 'application/json' });
      response.end(JSON.stringify({ error: 'not found' }));
      return;
    }

    const body = await readJsonBody(request);
    evidence.analyzerStubRequestCount += 1;

    assert.equal(body.token, analyzerToken, 'analyzer token should be forwarded');
    assert.equal(body.blobToken, blobToken, 'blob token should be forwarded');
    assert.equal(body.audioUrl, inertAudioUrl, 'inert audio URL metadata should be preserved');
    assert.equal(body.transcriptionType, 'rhythm');
    assert.equal(body.conditioning?.version, 1);
    assert.equal(body.conditioning?.instrumentConfig?.role, 'rhythm');
    assert.deepEqual(
      body.conditioning?.instrumentConfig?.tuningMidi,
      [40, 45, 50, 55, 59, 64]
    );
    assert.equal(body.conditioning?.instrumentConfig?.capoFret, 0);

    evidence.analyzerStubContractPassed = true;

    response.writeHead(200, { 'content-type': 'application/json' });
    response.end(JSON.stringify(analyzerResponseFixture()));
  } catch (error) {
    stubFailure = error;
    response.writeHead(500, { 'content-type': 'application/json' });
    response.end(
      JSON.stringify({
        error: error instanceof Error ? error.message : String(error),
      })
    );
  }
});

async function listenAnalyzerStub() {
  await new Promise((resolve, reject) => {
    const onError = (error) => {
      analyzerServer.off('listening', onListening);
      reject(error);
    };
    const onListening = () => {
      analyzerServer.off('error', onError);
      resolve();
    };
    analyzerServer.once('error', onError);
    analyzerServer.once('listening', onListening);
    analyzerServer.listen(analyzerPort, analyzerHost);
  });
}

async function closeAnalyzerStub() {
  if (!analyzerServer.listening) return;
  await new Promise((resolve) => analyzerServer.close(() => resolve()));
}

async function postJson(url, body) {
  return fetch(url, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'user-agent': 'Mozilla/5.0 (compatible; DadRock-V143-Canonical-HTTP-Gate/1.0)',
    },
    body: JSON.stringify(body),
  });
}

try {
  await listenAnalyzerStub();

  const analysisResponse = await postJson(`${baseUrl}/api/analyze-audio-tab`, {
    audioUrl: inertAudioUrl,
    pathname: 'v143-phase13-fixture.wav',
    song: 'V143 Phase 13 Canonical HTTP Gate',
    artist: 'DadRock QA',
    transcriptionType: 'rhythm',
    conditioning: requestConditioning(),
  });

  evidence.analysisStatus = analysisResponse.status;
  const analysis = await analysisResponse.json();

  if (stubFailure) throw stubFailure;

  assert.equal(analysisResponse.status, 200, 'analysis HTTP route should return 200');
  assert.equal(evidence.analyzerStubRequestCount, 1, 'analyzer stub should receive exactly one request');
  assert.equal(evidence.analyzerStubContractPassed, true);
  assert.equal(analysis.rhythmCanaryActive, true);
  evidence.rhythmCanaryActive = analysis.rhythmCanaryActive === true;

  assert.equal(analysis.productPlacementPromotion?.promoted, true);
  assert.equal(
    analysis.productPlacementPromotion?.reason,
    'PROMOTED_PLACEMENT_ONLY'
  );
  assert.equal(
    analysis.productPlacementPromotion?.baselineRenderEventCount,
    0
  );
  assert.equal(
    analysis.productPlacementPromotion?.canonicalRenderEventCount,
    7
  );

  evidence.promotionReason = analysis.productPlacementPromotion?.reason || null;
  evidence.baselineRenderEventCount =
    analysis.productPlacementPromotion?.baselineRenderEventCount ?? null;
  evidence.canonicalRenderEventCount =
    analysis.productPlacementPromotion?.canonicalRenderEventCount ?? null;

  assert.equal(Array.isArray(analysis.renderEvents), true);
  assert.equal(analysis.renderEvents.length, 7);
  assert.deepEqual(placementView(analysis.renderEvents), oracle);
  evidence.exactKnownTruthMatches = 7;

  assert.equal(analysis.generatedTab, generatedTab);
  evidence.canonicalGeneratedTabUnchanged = true;

  assert.equal(Array.isArray(analysis.events), true);
  assert.equal(analysis.events.length, 7);
  evidence.canonicalEventCount = analysis.events.length;

  assert.equal(analysis.conditioningContract?.provenance?.referenceBlind, true);
  assert.equal(
    analysis.dualContextShadowProjection?.fusionContract?.referenceBlind,
    true
  );
  assert.equal(
    analysis.dualContextShadowProjection?.fusionContract?.referenceScoreAuthorized,
    false
  );

  const previewResponse = await postJson(`${baseUrl}/api/generate-tab-preview`, {
    song: 'V143 Phase 13 Canonical HTTP Gate',
    artist: 'DadRock QA',
    transcriptionType: 'rhythm',
    generatedTab: analysis.generatedTab,
    tuning: analysis.tuning,
    tempo: analysis.tempo,
    timeSignature: analysis.timeSignature,
    keySignature: analysis.keySignature,
    previewSystems: 4,
    renderEvents: analysis.renderEvents,
    measureGrid: analysis.measureGrid,
    analysisEngine: analysis.analysisEngine,
    confidence: analysis.confidence,
    difficulty: analysis.difficulty,
    techniques: analysis.techniques,
  });

  evidence.previewStatus = previewResponse.status;
  evidence.previewFeature =
    previewResponse.headers.get('x-jimmy-paige-pdf-feature') || '';
  evidence.previewRenderer =
    previewResponse.headers.get('x-jimmy-paige-pdf-renderer') || '';

  const previewBytes = new Uint8Array(await previewResponse.arrayBuffer());
  evidence.previewPdfBytes = previewBytes.length;

  assert.equal(previewResponse.status, 200, 'preview route should return HTTP 200');
  assert.match(
    previewResponse.headers.get('content-type') || '',
    /^application\/pdf/i
  );
  assert.ok(previewBytes.length > 1000, 'structured preview PDF should be non-trivial');
  assert.equal(new TextDecoder().decode(previewBytes.slice(0, 4)), '%PDF');
  assert.equal(evidence.previewFeature, expectedFeature);
  assert.equal(evidence.previewRenderer, expectedRenderer);

  const invalidAnalysis = await postJson(`${baseUrl}/api/analyze-audio-tab`, {
    song: 'Missing required fields',
  });
  assert.equal(invalidAnalysis.status, 400);
  evidence.invalidAnalysis400Passed = true;

  assert.equal(evidence.analyzerStubRequestCount, 1, 'invalid request must fail before analyzer invocation');

  evidence.passed = true;
  await persistEvidence();

  console.log('=== V143 BUILT NEXT CANONICAL PROMOTION HTTP GATE PASSED ===');
  console.log(`analysisStatus: ${evidence.analysisStatus}`);
  console.log(`promotionReason: ${evidence.promotionReason}`);
  console.log(`canonicalRenderEventCount: ${evidence.canonicalRenderEventCount}`);
  console.log(`exactKnownTruthMatches: ${evidence.exactKnownTruthMatches}/7`);
  console.log(`previewFeature: ${evidence.previewFeature}`);
  console.log(`previewRenderer: ${evidence.previewRenderer}`);
  console.log(`previewPdfBytes: ${evidence.previewPdfBytes}`);
  console.log('actualVercelPreviewDeployment: false');
  console.log('productionModified: false');
} catch (error) {
  evidence.error = error instanceof Error ? error.message : String(error);
  await persistEvidence();
  console.error('V143 BUILT NEXT CANONICAL PROMOTION HTTP GATE FAILED');
  console.error(evidence.error);
  process.exitCode = 1;
} finally {
  await closeAnalyzerStub();
}
