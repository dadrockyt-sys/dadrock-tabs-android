import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';
import path from 'node:path';

const baseUrl = String(
  process.env.V143_PREVIEW_SMOKE_BASE_URL || 'http://127.0.0.1:4310'
).replace(/\/$/, '');

const resultPath =
  process.env.V143_PREVIEW_SMOKE_RESULT_PATH ||
  'debug/v143-contextual-prune/next-preview-route-smoke.json';

const expectedFeature = 'v143-branch-preview-canary';
const smokeUserAgent =
  'Mozilla/5.0 (compatible; DadRock-V143-Preview-Smoke/1.0)';

function generatedTab() {
  return [
    'e|--3-----5-----7-----8--|',
    'B|-----------------------|',
    'G|-----------------------|',
    'D|-----------------------|',
    'A|-----------------------|',
    'E|-----------------------|',
  ].join('\n');
}

function validRenderEvents() {
  const frets = [3, 5, 7, 8, 5, 7, 8, 10, 7, 8, 10, 12];
  return frets.map((fret, index) => ({
    eventIndex: index,
    measure: Math.floor(index / 4) + 1,
    step: (index % 4) * 4,
    stringIndex: index % 3,
    fret,
    midi: 52 + index,
    rhythmTechniques:
      index === 2
        ? ['hammer-on']
        : index === 7
          ? ['slide-up']
          : [],
    rhythmSustain: {
      durationSteps: index % 3 === 0 ? 2 : 1,
      durationSeconds: index % 3 === 0 ? 0.5 : 0.25,
      tier: index % 3 === 0 ? 'medium' : 'short',
    },
  }));
}

function basePayload() {
  return {
    song: 'V143 Preview Route Smoke',
    artist: 'DadRock QA',
    transcriptionType: 'rhythm',
    generatedTab: generatedTab(),
    tuning: 'E Standard',
    tempo: 120,
    timeSignature: '4/4',
    keySignature: 'E minor',
    previewSystems: 2,
  };
}

async function postPreview(payload) {
  const response = await fetch(`${baseUrl}/api/generate-tab-preview`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'user-agent': smokeUserAgent,
    },
    body: JSON.stringify(payload),
  });

  const bytes = new Uint8Array(await response.arrayBuffer());
  return {
    response,
    bytes,
    contentType: response.headers.get('content-type') || '',
    feature: response.headers.get('x-jimmy-paige-pdf-feature') || '',
    renderer: response.headers.get('x-jimmy-paige-pdf-renderer') || '',
  };
}

function assertPdf(result, label) {
  assert.equal(result.response.status, 200, `${label} should return HTTP 200`);
  assert.match(
    result.contentType,
    /^application\/pdf/i,
    `${label} should return application/pdf`
  );
  assert.ok(result.bytes.length > 1000, `${label} PDF should be non-trivial`);
  assert.equal(
    new TextDecoder().decode(result.bytes.slice(0, 4)),
    '%PDF',
    `${label} response should start with %PDF`
  );
}

const evidence = {
  schemaVersion: 1,
  gate: 'v143-next-preview-route-smoke',
  branch: 'v143-contextual-prune-lobo',
  baseUrl,
  localNextPreviewSimulation: true,
  actualVercelPreviewDeployment: false,
  aiTabPageStatus: null,
  structured: {
    status: null,
    feature: null,
    renderer: null,
    pdfBytes: null,
    passed: false,
  },
  fallback: {
    status: null,
    feature: null,
    renderer: null,
    pdfBytes: null,
    passed: false,
  },
  validation400Passed: false,
  passed: false,
  vercelDeploymentAttempted: false,
  liveEndpointDeployedOrModified: false,
  productionModified: false,
  productionPromotionAuthorized: false,
  paidPurchaseAttempted: false,
  customerTokenRedeemed: false,
  customerEmailSent: false,
  error: null,
};

async function persistEvidence() {
  const absolute = path.resolve(resultPath);
  await mkdir(path.dirname(absolute), { recursive: true });
  await writeFile(absolute, `${JSON.stringify(evidence, null, 2)}\n`, 'utf8');
}

try {
  const pageResponse = await fetch(`${baseUrl}/ai-tab`, {
    redirect: 'manual',
    headers: {
      'user-agent': smokeUserAgent,
    },
  });
  evidence.aiTabPageStatus = pageResponse.status;
  assert.equal(pageResponse.status, 200, '/ai-tab should load from the built server');

  const structured = await postPreview({
    ...basePayload(),
    analysisEngine: 'v143-reference-free-rhythm',
    renderEvents: validRenderEvents(),
    measureGrid: null,
    confidence: 0.91,
    difficulty: 'intermediate',
    techniques: ['hammer-on', 'slide-up'],
  });

  evidence.structured.status = structured.response.status;
  evidence.structured.feature = structured.feature;
  evidence.structured.renderer = structured.renderer;
  evidence.structured.pdfBytes = structured.bytes.length;

  assertPdf(structured, 'structured V143 Preview request');
  assert.equal(
    structured.feature,
    expectedFeature,
    'Preview branch feature should auto-enable from VERCEL_ENV/VERCEL_GIT_COMMIT_REF'
  );
  assert.equal(
    structured.renderer,
    'v143-structured-rhythm',
    'valid V143 structured events should route to the structured rhythm renderer'
  );
  evidence.structured.passed = true;

  const fallback = await postPreview({
    ...basePayload(),
    analysisEngine: 'v143-reference-free-rhythm-fallback',
    renderEvents: [
      {
        eventIndex: 0,
        measure: 1,
        step: 0,
        stringIndex: 0,
        fret: 3,
        midi: 55,
      },
    ],
    measureGrid: null,
  });

  evidence.fallback.status = fallback.response.status;
  evidence.fallback.feature = fallback.feature;
  evidence.fallback.renderer = fallback.renderer;
  evidence.fallback.pdfBytes = fallback.bytes.length;

  assertPdf(fallback, 'fallback Preview request');
  assert.equal(
    fallback.feature,
    expectedFeature,
    'professional renderer feature should remain enabled for safe fallback'
  );
  assert.equal(
    fallback.renderer,
    'polished-safe-fallback',
    'fallback-labeled/invalid structured data must stay on polished safe fallback'
  );
  evidence.fallback.passed = true;

  const invalidResponse = await fetch(`${baseUrl}/api/generate-tab-preview`, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      'user-agent': smokeUserAgent,
    },
    body: JSON.stringify({
      song: 'Missing Tab Smoke',
      artist: 'DadRock QA',
      transcriptionType: 'rhythm',
    }),
  });
  assert.equal(invalidResponse.status, 400, 'missing generated tab should return 400');
  evidence.validation400Passed = true;

  evidence.passed = true;
  await persistEvidence();

  console.log('=== V143 BUILT NEXT PREVIEW ROUTE SMOKE PASSED ===');
  console.log(`aiTabPageStatus: ${evidence.aiTabPageStatus}`);
  console.log(`structuredFeature: ${evidence.structured.feature}`);
  console.log(`structuredRenderer: ${evidence.structured.renderer}`);
  console.log(`structuredPdfBytes: ${evidence.structured.pdfBytes}`);
  console.log(`fallbackRenderer: ${evidence.fallback.renderer}`);
  console.log(`fallbackPdfBytes: ${evidence.fallback.pdfBytes}`);
  console.log('actualVercelPreviewDeployment: false');
  console.log('productionModified: false');
} catch (error) {
  evidence.error = error instanceof Error ? error.message : String(error);
  await persistEvidence();
  console.error('V143 BUILT NEXT PREVIEW ROUTE SMOKE FAILED');
  console.error(evidence.error);
  process.exitCode = 1;
}
