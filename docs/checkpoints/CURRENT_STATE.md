# New Astra Work — CURRENT STATE

Updated: 2026-09-19 UTC
Active branch: `astra-work`
Canonical handoff: `docs/checkpoints/CURRENT_STATE.md`
Status: **MILESTONE 4 COMPLETE — ZERO-NEW-SPEND ENGINE INVENTORY RECORDED; STATIC PREFLIGHT NEXT; NO REAL-AUDIO QUALITY CLAIM**

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
4. Select a lawful affordable real-audio development/evaluation plan, then execute only within the applicable authorization. PART A COMPLETE in the commit containing this checkpoint: static inventory and staged candidate recommendation. **NEXT ACTIVE TASK:** implement the offline candidate capability registry and preflight planner described in `docs/astra/AUDIO_ENGINE_INVENTORY_V1.md`; do not import/run Python models or use audio.

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

## Current evidence and limitations

- No Astra model has been trained, no real audio processed, and no customer-quality score exists.
- Frontend inspected on main at `bb992d901e78ab19645f8edc8e330d5a142ebd8e`; no live upload/payment/email test performed.
- No customer eligibility or delivery authorization is granted.
- Git preserves committed work; it cannot guarantee recovery of unsaved changes during an abrupt crash.

## Save / resume protocol

For every major milestone, save code, meaningful tests, provenance and this checkpoint in the same commit. Record verified results, blockers, active files, exact next action and parent/source commit IDs. Verify the commit exists on remote `astra-work`. Use the commit containing this checkpoint as its identity; do not create self-referential commit-hash edits.

At chat handoff: inspect branch/HEAD/status, read this file and AGENTS.md, then continue only the current milestone. If a tool or test fails, record it and the recovery step. Git history plus immutable snapshots is the durable record; chat memory is supplementary.

The active implementation surface is `astra_backend/`: add an offline static capability registry/preflight planner. It must express bass versus generic-guitar capability honestly, reject register-as-role claims and expose rights/runtime/evidence blockers. It must not import or execute audio/model dependencies.

## Copy-paste handoff

Continue Jimmy PAIge from `docs/checkpoints/CURRENT_STATE.md` on branch `astra-work` in `dadrockyt-sys/dadrock-tabs-android`. Read AGENTS.md first. Both V143/Gomyway and Songsterr Fresh are archived; do not resume their old task queues. Work on the active Astra milestone, preserve historical outcomes, and commit/push clean backend work plus this checkpoint after each major step. Do not modify main or Production.
