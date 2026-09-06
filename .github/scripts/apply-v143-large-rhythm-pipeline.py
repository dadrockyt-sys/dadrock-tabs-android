from pathlib import Path


def replace_once(path, old, new):
    p = Path(path)
    text = p.read_text()
    count = text.count(old)
    if count != 1:
        raise SystemExit(
            f"{path}: expected exactly one match, found {count}: {old[:100]!r}"
        )
    p.write_text(text.replace(old, new, 1))


replace_once(
    "app/api/audio-upload/route.js",
    "          allowedContentTypes: ALLOWED_AUDIO_TYPES,\n          maximumSizeInBytes: 50 * 1024 * 1024,\n          addRandomSuffix: true,",
    "          // The browser uploads directly to Blob, so do not impose the old\n          // 50 MB application ceiling here. Vercel Blob/platform limits remain\n          // authoritative and are surfaced by the upload SDK.\n          allowedContentTypes: ALLOWED_AUDIO_TYPES,\n          addRandomSuffix: true,",
)

replace_once(
    "app/ai-tab/page.js",
    "            access: 'private',\n\n            handleUploadUrl:\n              '/api/audio-upload',",
    "            access: 'private',\n            multipart: true,\n\n            handleUploadUrl:\n              '/api/audio-upload',",
)

replace_once(
    "app/ai-tab/page.js",
    "          } = await sendAnalyzerRequest({\n            operation: 'status',\n            jobToken,\n            transcriptionType:\n              selectedType,\n          }));",
    "          } = await sendAnalyzerRequest({\n            operation: 'status',\n            jobToken,\n            transcriptionType:\n              selectedType,\n            delivery: 'pdf-artifacts',\n            song: songTitle.trim(),\n            artist: artistName.trim(),\n          }));",
)

replace_once(
    "app/ai-tab/page.js",
    "      setStatusMessage(\n        'Creating your watermarked tab preview...'\n      );\n\n      const response = await fetch(",
    "      setStatusMessage(\n        'Creating your watermarked tab preview...'\n      );\n\n      const artifactPreviewUrl =\n        analysisMetadata?.pdfArtifact?.previewUrl;\n\n      if (\n        selectedType === 'rhythm' &&\n        typeof artifactPreviewUrl === 'string' &&\n        artifactPreviewUrl.startsWith('https://')\n      ) {\n        clearPreviewPdfUrl();\n        setPreviewPdfUrl(artifactPreviewUrl);\n        return artifactPreviewUrl;\n      }\n\n      const response = await fetch(",
)

replace_once(
    "app/ai-tab/page.js",
    "              generatedTab,\n\n              tuning:",
    "              generatedTab,\n\n              pdfArtifactId:\n                analysisMetadata?.pdfArtifact?.id || null,\n\n              tuning:",
)

old_download = """        const contentType =
          response.headers.get(
            'content-type'
          ) || '';

        if (
          !contentType.includes(
            'application/pdf'
          )
        ) {
          const data = await response
            .json()
            .catch(() => ({}));

          throw new Error(
            data.error ||
              data.message ||
              'The server did not return a valid PDF file.'
          );
        }

        const pdfBlob =
          await response.blob();"""
new_download = """        const contentType =
          response.headers.get(
            'content-type'
          ) || '';

        let pdfResponse = response;

        if (contentType.includes('application/json')) {
          const data = await response
            .json()
            .catch(() => ({}));

          if (
            typeof data.downloadUrl !== 'string' ||
            !data.downloadUrl.startsWith('https://')
          ) {
            throw new Error(
              data.error ||
                data.message ||
                'The server did not return a valid PDF download.'
            );
          }

          pdfResponse = await fetch(data.downloadUrl, {
            cache: 'no-store',
          });

          if (!pdfResponse.ok) {
            throw new Error(
              'The signed PDF download could not be retrieved.'
            );
          }
        }

        const pdfContentType =
          pdfResponse.headers.get(
            'content-type'
          ) || '';

        if (
          !pdfContentType.includes(
            'application/pdf'
          )
        ) {
          throw new Error(
            'The server did not return a valid PDF file.'
          );
        }

        const pdfBlob =
          await pdfResponse.blob();"""
replace_once("app/ai-tab/page.js", old_download, new_download)

replace_once(
    "lib/jimmyPaigeAnalysisPayload.js",
    "const MAX_EVENTS = 20000;",
    "// Large practical Rhythm uploads can produce far more than the old 20k\n// event ceiling. Keep a high defensive bound, but do not truncate ordinary\n// full-length recordings at a song-sized limit.\nconst MAX_EVENTS = 100000;",
)
replace_once(
    "lib/jimmyPaigeAnalysisPayload.js",
    "    fileSize: boundedInteger(value.fileSize, 1, 1024 * 1024 * 1024, null),",
    "    fileSize: boundedInteger(value.fileSize, 1, 5 * 1024 * 1024 * 1024 * 1024, null),",
)
replace_once(
    "lib/v143RenderContract.js",
    "const MAX_RENDER_EVENTS = 5000;",
    "// The former 5k cap could truncate a valid long Rhythm transcription.\n// Retain a defensive resource bound while allowing large practical recordings.\nconst MAX_RENDER_EVENTS = 100000;",
)

helper = r"""import { randomUUID } from 'node:crypto';
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
"""
Path("lib/v143RhythmPdfArtifacts.js").write_text(helper)

replace_once(
    "app/api/analyze-audio-tab/route.js",
    "import { buildAiTabProductPlacementPromotionV1 } from '@/lib/aiTabProductPlacementPromotionV1.mjs';",
    "import { buildAiTabProductPlacementPromotionV1 } from '@/lib/aiTabProductPlacementPromotionV1.mjs';\nimport { createV143RhythmPdfArtifacts } from '@/lib/v143RhythmPdfArtifacts';",
)
replace_once(
    "app/api/analyze-audio-tab/route.js",
    "    const jobToken = cleanText(\n      body?.jobToken,\n      300\n    );",
    "    const jobToken = cleanText(\n      body?.jobToken,\n      300\n    );\n\n    const delivery = cleanText(\n      body?.delivery,\n      40\n    ).toLowerCase();",
)

old_return = """    return NextResponse.json(
      operation === 'status'
        ? {
            ...completedPayload,
            analysisJob: {
              status: 'completed',
              token: jobToken,
            },
          }
        : completedPayload
    );"""
new_return = """    if (
      operation === 'status' &&
      usingV143RhythmAnalyzer &&
      delivery === 'pdf-artifacts'
    ) {
      if (!song || !artist) {
        return NextResponse.json(
          { error: 'Song and artist are required for Rhythm PDF artifact delivery.' },
          { status: 400 }
        );
      }

      const pdfArtifact =
        await createV143RhythmPdfArtifacts({
          completedPayload,
          song,
          artist,
        });

      // Keep the browser response compact. The full structured result was used
      // above to render both PDFs and remains only in the existing transient
      // analyzer result until the browser ACKs this same job token.
      return NextResponse.json({
        generatedTab: completedPayload.generatedTab,
        tuning: completedPayload.tuning,
        tempo: completedPayload.tempo,
        timeSignature: completedPayload.timeSignature,
        keySignature: completedPayload.keySignature,
        difficulty: completedPayload.difficulty,
        techniques: completedPayload.techniques,
        confidence: completedPayload.confidence,
        noteCount: completedPayload.noteCount,
        analysisEngine: completedPayload.analysisEngine,
        analysisQuality: completedPayload.analysisQuality,
        audioMetadata: completedPayload.audioMetadata,
        payloadContract: completedPayload.payloadContract,
        pdfArtifact,
        analysisJob: {
          status: 'completed',
          token: jobToken,
        },
      });
    }

    return NextResponse.json(
      operation === 'status'
        ? {
            ...completedPayload,
            analysisJob: {
              status: 'completed',
              token: jobToken,
            },
          }
        : completedPayload
    );"""
replace_once("app/api/analyze-audio-tab/route.js", old_return, new_return)

replace_once(
    "app/api/generate-tab-pdf/route.js",
    "import { NextResponse } from 'next/server';",
    "import { NextResponse } from 'next/server';\nimport {\n  createSignedV143RhythmPdfDownload,\n  isValidV143RhythmPdfArtifactId,\n} from '@/lib/v143RhythmPdfArtifacts';",
)
replace_once(
    "app/api/generate-tab-pdf/route.js",
    "    const generatedTab = cleanTabText(body?.generatedTab);",
    "    const generatedTab = cleanTabText(body?.generatedTab);\n    const pdfArtifactId = cleanText(body?.pdfArtifactId, 80);",
)

marker = """    const professionalPdfFeature =
      getJimmyPaigeProfessionalPdfFeatureState();"""
artifact_branch = """    if (
      transcriptionType === 'rhythm' &&
      pdfArtifactId
    ) {
      if (!isValidV143RhythmPdfArtifactId(pdfArtifactId)) {
        return NextResponse.json(
          { error: 'Invalid Rhythm PDF artifact reference.' },
          { status: 400 }
        );
      }

      const { downloadUrl, expiresAt } =
        await createSignedV143RhythmPdfDownload(pdfArtifactId);
      const fileName = createSafeFileName({
        song,
        artist,
        transcriptionType,
      });

      const emailResult = await resend.emails.send({
        from:
          process.env.RESEND_FROM_EMAIL ||
          'DadRock Tabs <onboarding@resend.dev>',
        to: customerEmail,
        subject: `${song} — ${transcriptionType} tab PDF`,
        html: `
          <h2>Your DadRock Tabs PDF is ready</h2>
          <p><strong>${song}</strong> by ${artist}</p>
          <p><a href="${downloadUrl}">Download your finished ${transcriptionType} tab PDF</a></p>
          <p>This private download link expires at ${expiresAt}.</p>
          <p>Thank you for supporting DadRock Tabs.</p>
        `,
      });

      if (emailResult.error) {
        console.error('Resend email error:', emailResult.error);
      }

      return NextResponse.json({
        downloadUrl,
        expiresAt,
        fileName,
      });
    }

    const professionalPdfFeature =
      getJimmyPaigeProfessionalPdfFeatureState();"""
replace_once("app/api/generate-tab-pdf/route.js", marker, artifact_branch)

regression = r"""import fs from 'node:fs';

function read(path) {
  return fs.readFileSync(path, 'utf8');
}
function assert(condition, message) {
  if (!condition) throw new Error(message);
}

const page = read('app/ai-tab/page.js');
const upload = read('app/api/audio-upload/route.js');
const analyze = read('app/api/analyze-audio-tab/route.js');
const pdf = read('app/api/generate-tab-pdf/route.js');
const payload = read('lib/jimmyPaigeAnalysisPayload.js');
const render = read('lib/v143RenderContract.js');
const artifacts = read('lib/v143RhythmPdfArtifacts.js');

assert(page.includes("multipart: true"), 'audio upload must use multipart');
assert(!upload.includes('50 * 1024 * 1024'), 'old 50 MB upload cap must be removed');
assert(page.includes("delivery: 'pdf-artifacts'"), 'Rhythm status must request compact PDF artifacts');
assert(page.includes('analysisMetadata?.pdfArtifact?.previewUrl'), 'preview must consume signed artifact URL');
assert(page.includes('analysisMetadata?.pdfArtifact?.id || null'), 'download must send artifact id');
assert(page.includes('pdfResponse = await fetch(data.downloadUrl'), 'full PDF must download directly from signed Blob URL');
assert(analyze.includes('createV143RhythmPdfArtifacts'), 'status must render PDF artifacts server-side');
assert(analyze.includes("delivery === 'pdf-artifacts'"), 'artifact delivery gate missing');
assert(analyze.includes('pdfArtifact,'), 'compact completed response must include artifact reference');
assert(pdf.includes('createSignedV143RhythmPdfDownload'), 'unlock route must sign existing full PDF artifact');
assert(pdf.includes('isValidV143RhythmPdfArtifactId'), 'artifact id must be validated');
assert(artifacts.includes("access: 'private'"), 'PDF artifacts must remain private');
assert(artifacts.includes("operations: ['get']"), 'signed PDF access must be GET-only');
assert(artifacts.includes('createJimmyPaigeProfessionalPdf'), 'artifact generation must use deterministic PDF renderer');
assert(!artifacts.includes('ANALYZER_API'), 'PDF artifact helper must never call analyzer');
assert(payload.includes('const MAX_EVENTS = 100000;'), 'structured payload long-file cap not raised');
assert(render.includes('const MAX_RENDER_EVENTS = 100000;'), 'render-event long-file cap not raised');
console.log('V143 large Rhythm upload -> compact artifact -> PDF regression: GREEN');
"""
Path(".github/scripts/v143-large-rhythm-pipeline-regression.mjs").write_text(regression)
