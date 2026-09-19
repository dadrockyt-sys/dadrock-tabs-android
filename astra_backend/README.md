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

## Sequential chunk processing

`processSampleChunks({ totalSamples, chunkOptions, read, process, write, signal })`
builds a sample plan and awaits each read/process/write in order. Callbacks receive
`{ chunk, signal }`; processor and writer also receive `samples`. Read and process
must return a dense finite-number Array, Float32Array or Float64Array of exactly
the input-window length. The writer receives only the cropped output and must
resolve `{ writtenSamples: chunk.output.end - chunk.output.start }` after the
whole range has been accepted. A success result has `status: 'complete'` and
confirmed `writtenSamples`/`writtenChunks` counts.

The adapter copies and validates buffers: processing may mutate its input without
changing the reader's source, and the writer owns a separate Float64Array. Callback
implementations must not mutate returned buffers after resolving or grow/retain
unbounded buffers if they need bounded memory. There is no whole-result allocation
or concurrency in the adapter; real model memory is a separate concern.

Configuration errors reject before callbacks run. Operational failures throw
`SampleChunkProcessingError` with the original `cause` and immutable `progress`:
status (`failed`/`cancelled`), stage, chunk index, confirmed prefix counts, and
`uncertainOutput`. A write error or invalid acknowledgement leaves its attempted
range uncertain because external partial side effects cannot be undone. Confirmed
counts exclude that range. Acknowledgements are a sink contract, not independent
verification of durable storage; retries/rollback/publication belong to the caller.

Cancellation is cooperative between awaited calls, with the AbortSignal passed
to every callback. A pending callback must settle before progress can be reported;
the adapter does not race an outstanding write or kill a hung processor. Cancellation
after a successful write records that acknowledgement but still returns no success.
No timeout, production I/O, inference, or delivery authorization is supplied here.

## Offline chunk analysis integration

`runAstraChunkedAnalysis({ request, chunks })` validates the existing analyzer
request before invoking `processSampleChunks(chunks)`. Operational outcomes appear
in `astra.stages.extraction.chunkProgress`, including confirmed counts and uncertain
write ranges. Configuration errors reject before callbacks. Original callback error
objects are not serialized into the result.

Complete sample processing maps to partial extraction with missing musical evidence;
cancellation maps to abstained extraction; failures map to failed extraction. The
existing overall status is abstained while role presence remains uncertain (or failed
on processing failure). Inspect chunkProgress.status for the mechanical outcome.
Input completion covers request and plan validation only, not decoding every sample.
Events, structure and tablature remain not-run. No pipeline payload or delivery policy
is accepted by this boundary, so generatedTab, events and renderEvents remain empty.
It neither opens the request audio URL nor invokes inference. Injected callbacks own
any external side effects and retain the processor's cooperative cancellation limits.

## Synthetic extraction handoff and CLAP metadata

`runAstraSyntheticExtraction({ request, chunks, evidence, downstream })` validates
synthetic-extraction-v1 evidence before reads: matching requestId/role/sampleCount,
a positive integer sampleRate (up to 384000), sampleIdentity, provenance source and
processor identities, and quality explicitly unresolved. Evidence is copied/frozen.
These are declarations, not proof that a sink contains those samples. Nonempty,
complete processing is required before the awaited downstream callback; failures or
cancellation skip it. The result keeps blocked `analysis`, `evidence` and diagnostic
`downstream` status separate. Callback return values are discarded. Downstream
errors/cancellation stay diagnostic and cannot authorize delivery. Cancellation is
cooperative; callback side effects cannot be rolled back.

`validateClapTextMetadata(entries)` checks an array of `{ key, shape, dtype }` against
203 expected text parameters and the reference persistent position_ids buffer.
Uniform optional module. prefixes are accepted; mixed prefixes, duplicates,
normalized collisions, extra/missing keys and wrong shapes/dtypes reject. The
reference profile requires float32 parameters and int64 position_ids. This is a
proposed strict profile, not observed checkpoint dtypes. Whole CLAP metadata must
first undergo a separately reviewed extraction; this validator accepts text only.
The backend-local `clapTextSchema.json` preserves namespace isolation;
tests exercise it against the documented source inventory. Passing cannot establish
tensor values, safe deserialization, actual checkpoint identity or execution readiness.

Remaining loader prerequisites: freeze tokenizer special-token/default behavior and
compatible runtime packages; inspect authorized checkpoint container/buffer/dtype
inventory with a safe loader; reject unknown pickle globals without fallback; verify
actual artifact hashes and numerical equivalence; measure peak memory and CPU time.
No such model work occurs in these synthetic helpers.

## Supplied events to diagnostic tablature

`runAstraSyntheticEventPipeline({ request, chunks, evidence, events, structureMap })`
connects complete synthetic chunks to the existing deterministic rhythm/fingering/tab
pipeline. Events require unique eventId, finite start and integer MIDI; optional end
or duration must be positive, consistent, and inside sampleCount/sampleRate. Onsets
must be before the clip end; note offsets may equal it. Missing end/duration remains
unresolved. Structure duration must match the clip (1e-9 seconds tolerance); tuning
and capo must be explicit. No resampling, inferred duration or invented notes occurs.

Inputs are copied before sample callbacks. Diagnostics preserve eventId via the
pipeline sourceEventIndex and expose events, rests, rhythm/fingering results and
text tab separately from the blocked analysis payload. Product-shell upstream
readiness is forced false; customerDeliveryEligible and deliveryReady remain false.
Failure/cancellation produces no diagnostics. Deterministic pipeline errors become
downstream failure, following the existing synthetic handoff contract.

Future sink verification must bind sampleIdentity to measured canonical sample bytes,
count, rate and completed writes; a caller-supplied label or receipt is insufficient.
Specify byte order/precision/channel layout, reject nonfinite samples, hash while
writing, and finalize only after every acknowledged write. Failed/uncertain ranges
must prevent publication; retries need sink-specific rollback/idempotency semantics.
For future CLAP extraction, validate artifact digest before safe deserialization,
allow only reviewed container forms and namespaces, reject unknown globals without
pickle fallback, reconcile actual tensor/buffer inventory, and record a derived
text-only artifact digest and parent identity. Metadata checks alone do not perform
these steps or authorize model execution.

## Not yet included

Astra audio separation, role-aware audio transcription, automatic musical-structure inference, a trained model, validated real-audio accuracy, HTTP job orchestration or production integration. Preserving supplied notes and passing synthetic tests is not a correctness claim about those notes.

## Verify

From this directory run `npm test` (Node built-in test runner, no third-party installation). Existing evidence/quality gates remain intact. Astra fixtures cover all roles and the complete/partial/abstained/failed result states. Test failures must be fixed or recorded; never reinterpret them as real-audio validation.

## Reuse boundary

The V143 contribution is documented operational and delivery experience, not its song-specific pruning or unknown metric formulas. Both old branches remain archived. New work changes this directory under the active Astra milestone, with tests and a checkpoint commit after every major step.
