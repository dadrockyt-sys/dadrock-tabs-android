# New Astra Work — CURRENT STATE

Updated: 2026-09-19 UTC
Active branch: `astra-work`
Canonical handoff: `docs/checkpoints/CURRENT_STATE.md`
Status: **MILESTONE 6C COMPLETE — HASHED CPU ENVIRONMENT INSTALLED; DEMUCS WEIGHT/RIGHTS STILL BLOCK EXECUTION; NO REAL-AUDIO QUALITY CLAIM**

## Product outcome

Jimmy PAIge powers `dadrocktabs.com/ai-tab`: upload audio, select bass / rhythm / lead guitar, receive accurate playable tab preview, optionally purchase the complete professional-quality PDF. The frontend is complete from the user's perspective. Backend musical quality is the priority.

Success requires requested-part separation, note/chord inference, onset/duration/technique accuracy, musical structure/rhythm, playable fingering and readable preview/full-PDF output. No single pitch percentage establishes the complete outcome.

## User decision and scope

On 2026-09-18 the user authorized archiving BOTH prior lines, starting New Astra Work, assembling their best qualities, and saving clean backend work after every major step for crash-resistant fresh-chat handoffs.

Active implementation and CPU synthetic verification may proceed in the new backend. No production change, paid/model-bearing execution, reclassification of historical results, or reopening of restricted datasets is implied. Previously exposed data cannot become an untouched final test by renaming the project.

## Archived baselines

- V143: `v143-contextual-prune-lobo` at `99e05eacbc3d8a38208ed41edadeee5b2f823c7b`.
- Songsterr Fresh: `songsterr-fresh-pipeline-v1` at `7be69898cf3eb7ae32cbe8963714895ad99c5853`.
- Exact original checkpoint snapshots and source blob IDs: `docs/checkpoints/archive/` and `docs/astra/ARCHIVE_MANIFEST.json`.
- Previous instructions to resume comparator recovery or RWC corpus hunting are archived task queues, not Astra's default next action.
- Preserve all old FAIL/PASS/provenance outcomes. V143 headline metrics remain unverified; current Fresh candidate real correctness remains unknown.

## What to retain

- Fresh: isolated deterministic musical structure, chord-shape assignment, contextual rhythm spelling, phrase-level fretboard optimization, product payload adapter and synthetic tests.
- V143: documented complete-song/PDF delivery experience, explicit traceability, and async ownership lessons (1800s result/control lifetime, 1200s orchestrator timeout, 600s margin). These are inherited design constraints to verify at integration, not a claim of an implemented Astra service.
- Existing frontend: upload/role request, generatedTab plus renderEvents/techniques/structure metadata, watermarked preview and unlock/full PDF.
- Neither legacy scorer, song-specific pruning rules nor unverifiable quality numbers will be imported as Astra acceptance criteria.

## Milestones

0. Establish durable checkpoint, archival source identities and repository instructions. COMPLETE: `8414a74fa18a542ecd6e99fca243a2403e38b29d`.
1. Copy the isolated deterministic backend to `astra_backend/`, retain original file hashes, run existing CPU synthetic suite, save the result. COMPLETE: `27c1bb6f80341244ce666f94e6b9da43a814baf4`; **104 passed, 0 failed**.
2. Specify the full-chain input/output and benchmark contracts: separate development/final evaluation, bass/lead/rhythm coverage, source-separation versus transcription versus rendering errors, completeness as well as precision, cost/latency budget and stop conditions. COMPLETE: `21f20cc6545155b7b7ccf9c18c2394ab7f183925`.
3. Build an offline adapter and representative synthetic end-to-end fixtures against that contract. COMPLETE: `f1fbb5594df709080b706d07d625579dbf65bf83`; **112 passed, 0 failed**.
4. Inventory lawful affordable real-audio candidates without executing them. COMPLETE: `3f16308e6aa9969a3e1c03f9bab91d7af6f6bf99`.
5. Encode candidate capabilities and blockers in an offline fail-closed preflight planner. COMPLETE in the commit containing this checkpoint; **120 passed, 0 failed**.
6. Freeze engine identities and gate execution. PART A COMPLETE: exact verifiable upstream tag/blob identities plus offline manifest validator; **128 passed, 0 failed**. PART B COMPLETE: direct official Demucs runtime selected, deterministic 57-package CPU lock frozen, unsafe ABI resolutions rejected; **131 passed, 0 failed**. PART C COMPLETE in the commit containing this checkpoint: exact hashed environment installed under Python 3.10.21, 57 installed distributions match the lock, compatibility check passed and packaged Basic Pitch model bytes were verified; **134 passed, 0 failed**. **NEXT ACTIVE TASK:** create a fail-closed local artifact-admission contract for the Demucs weight and record the exact external rights decision needed before any download/import/inference. Weight-specific terms remain unresolved and block execution/commercial use.

Do not assume training a new neural model from scratch is necessary or affordable. Compare component options against measured product failures before selecting the audio engine.

## Milestone 1 evidence / handoff

- `astra_backend/`: self-contained source/test snapshot. Runtime `.mjs` files and test files are byte-identical to the pinned Fresh source; README and package name are Astra-specific. Existing internal contract identifiers are intentionally preserved.
- `docs/astra/BACKEND_ADOPTION_MANIFEST.json`: original Git blob + SHA-256 for each copied file.
- `docs/astra/MILESTONE_1_VERIFICATION.json`: Node version, exact test command, counts and test-output digest.
- Verification: `npm --prefix astra_backend test` -> 104 tests, all passed; no skipped/cancelled tests. These are CPU synthetic/contract tests only.
- Both former branch checkpoints now contain explicit archive notices and point here. V143 notice commit `0710ce97c106e40eb8ad59975d6cffff5803d9a0`; Fresh notice commit `25e41dcac88f6067835c4d1d9e250c4d7e7542ac`.
- No archive branches or historical code were deleted; archive notices are documentation-only. Main/Production were not modified.
- No background training, model execution or automated save daemon is running. Milestone saves are performed by the working assistant; abrupt interruption can still lose uncommitted work.

## Milestone 2 evidence / handoff

- `docs/astra/FULL_CHAIN_CONTRACT_V1.md`: defines request, stage, event, structure, tablature, delivery, privacy and async boundaries around the actual `/ai-tab` product flow.
- `docs/astra/BENCHMARK_PLAN_V1.md`: separates reusable contract fixtures, development material and a future locked evaluation; requires bass/lead/rhythm coverage, raw precision and recall/completeness, stage-level error attribution, zero-new-spend operation and explicit stop conditions.
- `docs/astra/analyzer-request-v1.schema.json`: machine-readable request contract aligned with the existing upload/role boundary.
- `docs/astra/analyzer-result-v1.schema.json`: frontend-compatible result plus explicit `complete`, `partial`, `abstained` and `failed` states and a separate delivery decision.
- Schema JSON parsing: PASS. No external JSON Schema validator was installed, so meta-schema validation was not claimed.
- Backend regression verification after the documentation/schema changes: **104 passed, 0 failed**.
- The full-chain contract does not select an audio engine, dataset or quality threshold. Final customer-admission thresholds remain to be frozen before an authorized locked evaluation, after development evidence establishes defensible semantics and attainable performance.
- No real audio, model, network analyzer, payment path or production route was invoked.

## Milestone 3 evidence / handoff

- `astra_backend/analysisContractAdapter.mjs`: offline request normalization and result/delivery state machine. It has no network, process-spawn, model or archived-code dependency.
- The adapter preserves the frontend-compatible result fields while adding explicit input, extraction, events, structure and tablature stage states.
- Customer render events are emitted only when every stage is complete, the deterministic product payload is ready, structured rendering is compatible and a delivery-policy identity is supplied.
- Synthetic fixtures cover lead, rhythm and bass; complete, partial, abstained and failed results; absent requested role; unresolved rhythm fingering; triplet renderer incompatibility; input failure; and role-contract mismatch.
- Verification: `npm --prefix astra_backend test` -> **112 tests, 112 passed, 0 failed, 0 skipped/cancelled**.
- `docs/astra/MILESTONE_3_VERIFICATION.json` records the command, runtime and test-output digest.
- A synthetic delivery-policy identity exercises the complete state in tests. It grants no production/customer authority.
- No real audio, separator, event-inference model, network service, payment path or production route was invoked.

## Milestone 4 evidence / handoff

- `docs/astra/AUDIO_ENGINE_INVENTORY_V1.md`: source-identity-pinned inventory of the current whole-mix Basic Pitch analyzer, six-stem CPU separator, historical register gate and historical structure estimate.
- Best bounded candidate for later authorized development comparison: `htdemucs_6s` bass/generic-guitar stem -> pinned Basic Pitch -> Astra. It is not selected for product use and has not been executed.
- Critical gap: no repository component cleanly separates lead from rhythm guitar. The historical “three-way separation” is fixed MIDI-register filtering and is rejected as role truth.
- Basic Pitch software is Apache-2.0; audio-separator and upstream Demucs software are MIT based on recorded upstream LICENSE blobs. Exact downloadable model-weight identity/terms still require review before real/commercial use.
- Current CPU separator allows 3300 seconds, outside Astra's intended 1200-second analyzer ceiling. Cost, memory, latency and downstream accuracy remain unmeasured.
- Main's Basic Pitch install is unpinned and uses identical upstream inference for all three role selections; role changes only post-inference fingering/tuning behavior.
- No real audio, separator, Basic Pitch inference, network analyzer, paid service or production route was invoked.

## Milestone 5 evidence / handoff

- `astra_backend/audioEngineRegistry.mjs`: deterministic static registry and per-role preflight plans for the whole-mix baseline, the `htdemucs_6s` development candidate and the rejected historical register gate.
- Bass may reference the candidate's direct bass stem. Lead and rhythm may reference only a generic guitar stem and always receive `LEAD_RHYTHM_DISTINCTION_UNAVAILABLE`; the planner never promotes that stem into lead/rhythm truth.
- Fixed MIDI-register filtering is explicitly rejected as role evidence. Caller-declared isolated inputs require provenance and do not self-authorize execution.
- Every current plan is `developmentExecutionReady: false` and `customerDeliveryEligible: false`. Plans also state that preflight opened no audio, invoked no model and performed no network access.
- Verification: `npm --prefix astra_backend test` -> **120 tests, 120 passed, 0 failed, 0 skipped/cancelled**.
- `docs/astra/MILESTONE_5_VERIFICATION.json` records the runtime, command and test-output digest.
- No audio/model dependency is imported by the registry. No real audio, model, network analyzer, paid service or production route was invoked.

## Milestone 6A evidence / handoff

- `docs/astra/ASTRA_ENGINE_EXECUTION_MANIFEST_V1.json`: development-only CPU candidate manifest. It pins `audio-separator` `v0.30.2`, official Demucs `v4.0.1`, `htdemucs_6s` config/weight identifiers and Basic Pitch `v0.4.0` plus its TFLite model Git blob.
- `docs/astra/ENGINE_IDENTITY_REVIEW_V1.md`: evidence and remaining blockers. Important correction: the archived Fresh manifest's `demucs==4.1.0` / `torch==2.14.0` package claims were not adopted because the official Meta Demucs repository exposes only `v4.0.0` and `v4.0.1` tags in the reviewed source.
- The archived Demucs weight SHA-256 is preserved as a historical observation, not relabeled as Astra verification.
- `astra_backend/engineExecutionManifest.mjs`: validates exact known identities, refuses package/model substitutions, keeps customer delivery false and reports missing install lock, model verification, rights, runtime and development-material authorization.
- Bass has no lead/rhythm blocker but is still not execution-ready. Lead and rhythm additionally receive `LEAD_RHYTHM_DISTINCTION_UNAVAILABLE`.
- Verification: `npm --prefix astra_backend test` -> **128 tests, 128 passed, 0 failed, 0 skipped/cancelled**.
- `docs/astra/MILESTONE_6A_VERIFICATION.json` records the runtime, command and test-output digest.
- No real audio was opened; no model, package installer, network analyzer, paid service or production route was invoked.

## Milestone 6B evidence / handoff

- `docs/astra/ENGINE_RUNTIME_LOCK_V1.md`: replaces the `audio-separator` wrapper candidate with the official `demucs==4.0.1` CLI. The wrapper did not depend on the official Demucs package and carried an unnecessary broad ONNX runtime surface.
- `astra_backend/engine/requirements.in`, `constraints.txt` and `requirements.lock`: Python 3.10, x86_64 manylinux 2.28, CPU-only graph with 57 packages and artifact hashes. Lock SHA-256: `a5614dbfad0be96aadc0d76297b6a59abe4e09c80bf2d6a484e53a14a58d38a7`.
- Critical pins: NumPy `1.26.4`, TFLite Runtime `2.14.0`, and matched Torch/Torchaudio `2.11.0+cpu`.
- Two consecutive resolutions were byte-identical. The first binary-only attempt failed because Demucs 4.0.1 has no usable target wheel; source build support is required. The first unconstrained graph was rejected because it paired Torch 2.14 with Torchaudio 2.11 and selected the known-risk NumPy 2.x/TFLite combination.
- `astra_backend/engineExecutionManifest.mjs` now verifies the complete hashed lock, refuses ABI drift, TensorFlow substitution and wrapper reintroduction, and reports installation as unverified.
- The official Demucs source connects `htdemucs_6s` to the exact Meta-hosted weight and verifies its checksum prefix. No separate weight-specific license statement was found in the reviewed source, so rights remain unresolved.
- Verification: `npm --prefix astra_backend test` -> **131 tests, 131 passed, 0 failed, 0 skipped/cancelled**.
- `docs/astra/MILESTONE_6B_VERIFICATION.json` records the commands, failures, lock identity and test-output digest.
- Dependency metadata was resolved over the network. No packages were installed, no model weight was downloaded, no audio was opened, no model was imported/executed, and no paid service or production route was invoked.

## Milestone 6C evidence / handoff

- `docs/astra/ENGINE_INSTALLATION_SMOKE_V1.md`: exact isolated-install commands and evidence boundary.
- The frozen lock installed successfully into a new temporary Python `3.10.21` environment with `uv pip sync --require-hashes --torch-backend cpu`; pinned Demucs 4.0.1 was built from its source distribution.
- `uv pip check`: PASS. All 57 installed distribution names and versions exactly match the complete frozen lock.
- `astra_backend/engine/installed-distributions.json`: canonical installed snapshot; SHA-256 `a286ef69bdc34636cf96bd6ee952c517c44ffebe22b73329f0390e6e987ab846`.
- The installed Basic Pitch TFLite artifact was verified without loading it: 204,448 bytes; Git blob SHA-1 `85a41befdd036e9b365a052b7c704c6810288b95`; SHA-256 `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`.
- `engineExecutionManifest.mjs` now refuses installed-package or Basic Pitch artifact substitution. The package-installation blocker is cleared; `DEMUCS_WEIGHT_NOT_VERIFIED_ON_ASTRA`, weight/model rights, runtime budget, development-audio authorization and lead/rhythm distinction remain explicit blockers.
- Verification: `npm --prefix astra_backend test` -> **134 tests, 134 passed, 0 failed, 0 skipped/cancelled**.
- No model runtime was imported, no Demucs weight was downloaded, no audio was opened, no inference was run, and no paid service or production route was invoked.

## Current evidence and limitations

- No Astra model has been trained, no real audio processed, and no customer-quality score exists.
- Frontend inspected on main at `bb992d901e78ab19645f8edc8e330d5a142ebd8e`; no live upload/payment/email test performed.
- No customer eligibility or delivery authorization is granted.
- Git preserves committed work; it cannot guarantee recovery of unsaved changes during an abrupt crash.

## Save / resume protocol

For every major milestone, save code, meaningful tests, provenance and this checkpoint in the same commit. Record verified results, blockers, active files, exact next action and parent/source commit IDs. Verify the commit exists on remote `astra-work`. Use the commit containing this checkpoint as its identity; do not create self-referential commit-hash edits.

At chat handoff: inspect branch/HEAD/status, read this file and AGENTS.md, then continue only the current milestone. If a tool or test fails, record it and the recovery step. Git history plus immutable snapshots is the durable record; chat memory is supplementary.

The active milestone is 6D. Build a deterministic, offline Demucs artifact-admission contract that accepts only the frozen `htdemucs_6s` filename and exact SHA-256, requires explicit rights clearance, and cannot download, import or execute the model. Record the precise external rights evidence/decision still required. Do not fetch the weight or process audio until that gate is satisfied.

## Copy-paste handoff

Continue Jimmy PAIge from `docs/checkpoints/CURRENT_STATE.md` on branch `astra-work` in `dadrockyt-sys/dadrock-tabs-android`. Read AGENTS.md first. Both V143/Gomyway and Songsterr Fresh are archived; do not resume their old task queues. Work on the active Astra milestone, preserve historical outcomes, and commit/push clean backend work plus this checkpoint after each major step. Do not modify main or Production.
