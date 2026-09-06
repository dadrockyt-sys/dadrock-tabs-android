import { randomUUID } from 'node:crypto';
import { issueSignedToken, presignUrl, put } from '@vercel/blob';
import { createJimmyPaigeProfessionalPdf } from '@/lib/createJimmyPaigeProfessionalPdf';

const ARTIFACT_PREFIX = 'ai-tab/rhythm-pdf';
const ARTIFACT_ID_PATTERN = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const PREVIEW_URL_LIFETIME_MS = 6 * 60 * 60 * 1000;
const DOWNLOAD_URL_LIFETIME_MS = 60 * 60 * 1000;

function artifactPath(artifactId, name) {
  if (!ARTIFACT_ID_PATTERN.test(String(artifactId || ''))) {
    throw new Error('Invalid Rhythm PDF artifact reference.');
  }
  return `${ARTIFACT_PREFIX}/${artifactId}/${name}`;
}

async function createSignedGetUrl(pathname, lifetimeMs) {
  const validUntil = Date.now() + lifetimeMs;
  const token = await issueSignedToken({
    pathname,
    operations: ['get'],
    validUntil,
  });
  const { presignedUrl } = await presignUrl(token, {
    pathname,
    operation: 'get',
    validUntil,
    useCache: false,
  });
  if (!presignedUrl) {
    throw new Error('Unable to create a signed Rhythm PDF URL.');
  }
  return {
    url: presignedUrl,
    expiresAt: new Date(validUntil).toISOString(),
  };
}

function rendererInput({ completedPayload, song, artist, preview }) {
  return {
    song,
    artist,
    transcriptionType: 'rhythm',
    generatedTab: completedPayload.generatedTab,
    tuning: completedPayload.tuning || 'Standard Tuning',
    tempo: completedPayload.tempo || 120,
    timeSignature: completedPayload.timeSignature || '4/4',
    keySignature: completedPayload.keySignature || '',
    analysisEngine: completedPayload.analysisEngine || '',
    renderEvents: Array.isArray(completedPayload.renderEvents)
      ? completedPayload.renderEvents
      : [],
    measureGrid: completedPayload.measureGrid || null,
    confidence: completedPayload.confidence ?? null,
    difficulty: completedPayload.difficulty || null,
    techniques: Array.isArray(completedPayload.techniques)
      ? completedPayload.techniques
      : [],
    preview,
    previewSystems: 4,
  };
}

export async function createV143RhythmPdfArtifacts({
  completedPayload,
  song,
  artist,
}) {
  if (completedPayload?.analysisEngine !== 'v143-reference-free-rhythm') {
    throw new Error(
      'Rhythm PDF artifact delivery requires an authenticated structured V143 result.'
    );
  }

  const artifactId = randomUUID();
  const previewPath = artifactPath(artifactId, 'preview.pdf');
  const fullPath = artifactPath(artifactId, 'full.pdf');

  const [previewResult, fullResult] = await Promise.all([
    createJimmyPaigeProfessionalPdf(
      rendererInput({ completedPayload, song, artist, preview: true })
    ),
    createJimmyPaigeProfessionalPdf(
      rendererInput({ completedPayload, song, artist, preview: false })
    ),
  ]);

  await Promise.all([
    put(previewPath, Buffer.from(previewResult.pdfBytes), {
      access: 'private',
      addRandomSuffix: false,
      contentType: 'application/pdf',
    }),
    put(fullPath, Buffer.from(fullResult.pdfBytes), {
      access: 'private',
      addRandomSuffix: false,
      contentType: 'application/pdf',
    }),
  ]);

  const signedPreview = await createSignedGetUrl(
    previewPath,
    PREVIEW_URL_LIFETIME_MS
  );

  return {
    id: artifactId,
    previewUrl: signedPreview.url,
    previewExpiresAt: signedPreview.expiresAt,
    rendererMode:
      fullResult.rendererContract?.mode || 'v143-structured-rhythm',
  };
}

export async function createSignedV143RhythmPdfDownload(artifactId) {
  const fullPath = artifactPath(artifactId, 'full.pdf');
  const signedDownload = await createSignedGetUrl(
    fullPath,
    DOWNLOAD_URL_LIFETIME_MS
  );
  return {
    downloadUrl: signedDownload.url,
    expiresAt: signedDownload.expiresAt,
  };
}

export function isValidV143RhythmPdfArtifactId(value) {
  return ARTIFACT_ID_PATTERN.test(String(value || ''));
}
