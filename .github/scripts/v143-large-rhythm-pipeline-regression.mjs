import fs from 'node:fs';

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
