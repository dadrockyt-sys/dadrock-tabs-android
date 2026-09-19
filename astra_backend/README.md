# Jimmy PAIge — Astra backend

Active branch: `astra-work`. Canonical progress: `../docs/checkpoints/CURRENT_STATE.md`.

This is an independently editable, self-contained copy of the Fresh deterministic core and its CPU synthetic tests, pinned from commit `7be69898cf3eb7ae32cbe8963714895ad99c5853`. It does not import the archived directory, V143 code, neural models, network clients or production routes. Original module labels and contract versions intentionally remain unchanged so adoption does not silently alter payload semantics.

## Included

Musical structure mapping; simultaneous playable shapes; rhythm spelling including rests/ties; phrase-level fretboard paths; product payload adaptation; note-evidence diagnostics and conservative delivery gates. The offline `analysisContractAdapter.mjs` implements the Astra V1 request/result state machine without audio inference or network access. The static `audioEngineRegistry.mjs` records candidate capabilities and blockers. `engineExecutionManifest.mjs` verifies the candidate's known upstream identities, hashed direct-Demucs CPU dependency lock, exact installed-distribution snapshot and packaged Basic Pitch TFLite artifact. `demucsArtifactAdmission.mjs` freezes the one allowed weight identity and cannot clear until an external rights decision is committed. These modules refuse substitutions and customer authorization; they do not open audio, load models or perform network access. `separationCandidateRightsRegistry.mjs` records the no-download 7A rights/capability screen and keeps downstream conversions/fine-tunes blocked when upstream weight rights remain unresolved. Source identities for the adopted Fresh snapshot: `../docs/astra/BACKEND_ADOPTION_MANIFEST.json`.

## Sample chunk planning

`createSampleChunkPlan(totalSamples, { coreSamples, leftContextSamples = 0, rightContextSamples = 0 })`
is an independent, lazy, repeatable iterable of sample slices. Counts must be safe integers;
the core must be positive. Empty input yields no chunks. All intervals are half-open:
`input` and `output` use global sample coordinates, while `crop` indexes a sample-aligned
processed input window. `leftContext` and `rightContext` mark context in global coordinates.
Context is clipped at file edges, without implicit padding. Each output sample has exactly
one owner; input context may overlap. The plan is immutable and allocates one descriptor
at a time, not the entire clip. It neither loads audio nor invokes or admits a model.

```js
const plan = createSampleChunkPlan(sampleCount, {
  coreSamples: 96000, leftContextSamples: 32000, rightContextSamples: 32000,
});
for (const { input, crop, output } of plan) {
  // Read input.start:input.end; process that window using a separately admitted adapter.
  // Keep crop.start:crop.end and write it to output.start:output.end.
}
```

Integration must verify output length/alignment, model stride, edge-padding needs and seam
quality. Coverage tests do not prove musical accuracy or that an actual model preserves samples.

## Not yet included

Astra audio separation, role-aware audio transcription, automatic musical-structure inference, a trained model, validated real-audio accuracy, HTTP job orchestration or production integration. Preserving supplied notes and passing synthetic tests is not a correctness claim about those notes.

## Verify

From this directory run `npm test` (Node built-in test runner, no third-party installation). Existing evidence/quality gates remain intact. Astra fixtures cover all roles and the complete/partial/abstained/failed result states. Test failures must be fixed or recorded; never reinterpret them as real-audio validation.

## Reuse boundary

The V143 contribution is documented operational and delivery experience, not its song-specific pruning or unknown metric formulas. Both old branches remain archived. New work changes this directory under the active Astra milestone, with tests and a checkpoint commit after every major step.
