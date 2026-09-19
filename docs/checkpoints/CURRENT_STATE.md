# New Astra Work — CURRENT STATE

Updated: 2026-09-19 UTC
Active branch: `astra-work`
Canonical handoff: `docs/checkpoints/CURRENT_STATE.md`
Status: **MILESTONE 7F COMPLETE — SEQUENTIAL CHUNK PROCESSOR IMPLEMENTED; TEXT-ONLY CLAP DESIGN FROZEN; OFFLINE STAGE INTEGRATION NEXT; 170 TESTS PASS**

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
6. Freeze engine identities and gate execution. PART A COMPLETE: exact verifiable upstream tag/blob identities plus offline manifest validator; **128 passed, 0 failed**. PART B COMPLETE: direct official Demucs runtime selected, deterministic 57-package CPU lock frozen, unsafe ABI resolutions rejected; **131 passed, 0 failed**. PART C COMPLETE: exact hashed environment installed under Python 3.10.21, 57 installed distributions match the lock, compatibility check passed and packaged Basic Pitch model bytes were verified; **134 passed, 0 failed**. PART D COMPLETE: exact Demucs artifact identity and external rights-decision requirements frozen in an offline admission gate; **140 passed, 0 failed**. 7A COMPLETE: no reviewed candidate currently combines bass+guitar capability, a plausible CPU path and a resolved commercial artifact-rights chain; **148 passed, 0 failed**.

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

## Milestone 6D evidence / handoff

- `astra_backend/demucsArtifactAdmission.mjs`: deterministic offline gate for the exact `htdemucs_6s` filename, official source URL and historical SHA-256. Any candidate/model/file/source/digest substitution throws.
- The gate cannot self-clear. Exact bytes still leave `DEMUCS_WEIGHT_RIGHTS_DECISION_NOT_FROZEN` until an owner-approved review record is committed and its digest is pinned in code.
- `docs/astra/DEMUCS_ARTIFACT_ADMISSION_V1.md`: defines the external record required for development evaluation and commercial paid-tab inference, including authoritative evidence, reviewer, date and restrictions.
- A software repository's MIT label is not automatically promoted into a weight-specific commercial-use conclusion. If that conclusion cannot be established, Astra will seek a model with explicit artifact terms or a separately licensed/trained replacement.
- Verification: `npm --prefix astra_backend test` -> **140 tests, 140 passed, 0 failed, 0 skipped/cancelled**.
- The new contract downloads nothing, reads no weight, imports no model, opens no audio and cannot authorize customer delivery.

## Branch-only verification runner

- `.github/workflows/astra-backend-tests.yml` runs only `npm --prefix astra_backend test` on `astra-work` / manual dispatch, records the exact test-output SHA-256, and has read-only repository permissions.
- It installs no model/runtime packages, downloads no model weights, opens no audio, invokes no paid service and performs no deployment or Production action.
- This runner exists because the active assistant execution container cannot resolve GitHub directly; GitHub Actions provides branch-attached reproducible Node verification without weakening any Astra model gate.

## Milestone 7A evidence / handoff

- `docs/astra/SEPARATION_ARTIFACT_RIGHTS_INVENTORY_V1.md`: no-download source/rights inventory with exact artifact identities where authoritative upstream digests were exposed.
- `astra_backend/separationCandidateRightsRegistry.mjs`: deterministic static fail-closed registry. It cannot download/import/invoke a model or open audio.
- Spleeter 5-stem has explicit MIT pretrained-model terms but no guitar stem. Open-Unmix `umxhq` also has bass + `other`, not guitar.
- StemSplit's `htdemucs_6s.onnx` and the reviewed guitar fine-tune expose bass + generic guitar, but both derive from `htdemucs_6s`; their downstream license labels do not clear Astra's unresolved base-weight rights chain.
- The guitar fine-tune explicitly combines overlapping guitar layers into one guitar stem; no candidate supplies independent lead/rhythm evidence.
- **Zero candidates are 7A inventory-qualified.** No execution/customer/production authorization is granted.
- Verification on implementation commit `46fe9f2fb9f90e167714d1222b40d60d92f299cc`: `npm --prefix astra_backend test` -> **148 tests, 148 passed, 0 failed, 0 skipped/cancelled** on Node `v24.20.0`; output SHA-256 `18e27897e9862144d5cec2776233a3a2f6edc670368ca34f0321e3a8b73fbaa1`.
- No weight was downloaded; no audio/model/installer/paid service/production route was invoked.

## Milestone 7B evidence / handoff

- `docs/astra/INDEPENDENT_SEPARATOR_REVIEW_V1.md`: no-download Banquet review pinned to source revision `79ed5bb75e5c3a40cd319d9d990cee913fc65c26` and Zenodo record `13694558`.
- `astra_backend/independentSeparationCandidateReview.mjs`: static fail-closed review for Banquet. It records explicit bass/guitar target classes, CPU control, checkpoint metadata and unresolved rights/query blockers; it cannot download/import/invoke a model or open audio.
- Banquet is independent of the frozen Demucs weight and is technically promising for bass plus generic guitar. Its BYOQ inference supports CPU via `use_cuda=false` but requires a separate ten-second query clip. The reviewed `PasstFiLMConditionedBandit` query encoder derives conditioning from query audio; no label-only product path was identified in the canonical source inspected.
- Source code is MIT. The exact Zenodo checkpoint license/commercial rights were not established by the evidence available to this review, so model use remains blocked. MoisesDB training/data commercial-rights lineage is also not yet cleared.
- Lead/rhythm remains blocked; instrument-class targets do not establish musical role.
- Initial implementation verification at `4b531ede14c1dcc28c41011c0a2aca32ff5cc024`: **154/154**; output SHA-256 `c12bc6f6a25ba94c1e58cfb7e8bf8e11cbf68b425e346618606d21f518f325f9`.
- Final provenance-frozen implementation verification at `ad5634f942b39fe0f3eb98f720ff6cee802da528`: **154 tests, 154 passed, 0 failed, 0 skipped/cancelled** on Node `v24.20.0`; output SHA-256 `f59c0438acb245c35a31cf3177638f2c4d2ca4381f0703f169afa9aa9c293360`.
- No checkpoint was downloaded; no model/audio/installer/paid service/production route was invoked.

## Current evidence and limitations

- No Astra model has been trained, no real audio processed, and no customer-quality score exists.
- Frontend inspected on main at `bb992d901e78ab19645f8edc8e330d5a142ebd8e`; no live upload/payment/email test performed.
- No customer eligibility or delivery authorization is granted.
- Git preserves committed work; it cannot guarantee recovery of unsaved changes during an abrupt crash.

## Save / resume protocol

For every major milestone, save code, meaningful tests, provenance and this checkpoint in the same commit. Record verified results, blockers, active files, exact next action and parent/source commit IDs. Verify the commit exists on remote `astra-work`. Use the commit containing this checkpoint as its identity; do not create self-referential commit-hash edits.

At chat handoff: inspect branch/HEAD/status, read this file and AGENTS.md, then continue only the current milestone. If a tool or test fails, record it and the recovery step. Git history plus immutable snapshots is the durable record; chat memory is supplementary.

## Milestone 7C evidence / handoff

- Parent/source branch commit: `115b668fc625d8468a5c7b408f277b6de3b87602`. Local HEAD and origin/astra-work were brought to this verified remote identity before work. The older divergent local milestone-6D commit was preserved as `astra-work-local-preserved-f3693e25`; it was not merged or discarded. The remote has progressed beyond the historical 128-test handoff.
- `docs/astra/BANQUET_RIGHTS_QUERY_REVIEW_V1.md`: authoritative Zenodo retrieval attempts failed/time out; no new license/record revision could be established. This is unavailable evidence, not proof of prohibited use. The checkpoint rights remain unresolved.
- Canonical Banquet model source confirms an audio-derived 768-dimensional PaSST-to-FiLM boundary. A cached embedding adapter is technically conceivable, but no upstream label-only/precomputed-vector input or authorized query source was established. The actual model uses `Passt`, not `PasstWrapper`; its OpenMIC PaSST dependency also needs exact artifact/rights review before execution.
- Banquet's 7C admission success conditions were NOT met. Existing code gates remain unchanged and blocked. No new documentation-mirroring tests were added.
- Independent search continued to SAM-Audio, pinned to `bb4c6999d2677c7402360e426afc01ddfad6dce0`. Its README documents text prompting, and its SAM License expressly covers trained weights. It is a research lead only: gated checkpoint access, exact artifact/dependency rights and CPU/memory/latency feasibility remain unreviewed.
- Verification: `npm --prefix astra_backend test` -> **154 tests, 154 passed, 0 failed, 0 skipped/cancelled**. Runtime, output digest, retrieval failures and no-execution boundaries are in `docs/astra/MILESTONE_7C_VERIFICATION.json`.
- No model weight, query recording or audio was downloaded/opened; no inference, package installation, paid service, main change or production deployment occurred.

## Milestone 7D evidence / handoff

- Parent: `8d0a38e55ab7e239cd6118845641b7285a49c49c`; local HEAD, origin/astra-work and the remote matched before work.
- `docs/astra/SAM_AUDIO_RESOURCE_REVIEW_V1.md` records source identities, mandatory/config-dependent components, resource evidence and exact access failures.
- Standard SAM-Audio small is **deferred under the existing 4096-MB CPU target**: the public checkpoint listing is 5.1 GB; the loader additionally initializes T5, vision and configured auxiliary models. Disk size is not measured RAM, but no plausible standard-loader fit was established. No claim that every optimized implementation is impossible.
- Small-model config/checkpoint detail pages returned 401; no gate was bypassed, access requested or terms accepted. The public model card has a CPU fallback example, but no measured small-model CPU result. Published A100 latency cannot establish Astra CPU latency.
- Bounded independent search identified AudioSep's real text-query/CPU path. Pinned GitHub revision `944583f18b84589dc965de3ad77525c945334252`; official Space artifact revision `5638854dccfaea5c5fa4f634c00fe74fbb119244`; two published SHA-256 identities are recorded. Combined artifacts are 3,617,315,079 bytes, not a peak-RAM measurement.
- The artifact-hosting Space declares MIT at the pinned revision. This is meaningful publisher evidence, but CLAP upstream artifact rights and complete initialization memory remain unreviewed. AudioSep is not execution-ready or customer-eligible.
- Static inspection found AudioSep's chunk path returns all-zero output for inputs <=160,000 samples (five seconds at 32 kHz), and a README/function-name mismatch. No model was run. These are concrete integration risks for the next work, not Astra quality measurements.
- `npm --prefix astra_backend test`: **154 passed, 0 failed, 0 skipped/cancelled**. `docs/astra/MILESTONE_7D_VERIFICATION.json` records runtime and output digest. Runtime gates unchanged; documentation-only milestone.
- No weights, real audio, protected reference data, model runtime, package installer, paid service, main or Production action. Git command-line writes lack authentication in this workspace; milestone saving uses the connected GitHub API, with exact local/remote tree comparison and ref verification.

## Milestone 7E evidence / handoff

- Parent: `bbeaa9964b130cd7bb26025c2711728a830a778d`; local, origin and remote matched before implementation.
- `astra_backend/sampleChunkPlan.mjs`, exported via `index.mjs`, implements immutable lazy sample-index chunk planning with explicit input/output/context/crop intervals. Handles short clips, exact boundaries and tails without omissions or duplicate output ownership; no model or file access.
- Six meaningful tests in `tests/sampleChunkPlan.test.mjs` include synthetic sample-ID reconstruction, 2,280 length/context combinations, 32-kHz boundary cases, invalid options/overflow, lazy huge plans, repeatability and mutation isolation. Public export tested. README documents alignment and edge limitations.
- `docs/astra/AUDIOSEP_CLAP_REVIEW_V1.md` establishes the upstream CLAP publisher link: official LAION README names the exact file; published SHA-256 and byte size match AudioSep's Space copy; the upstream model repository declares CC0. Immutable artifact commit `4226474e38defca6fc9272a7848bb7b0355ccd7a` and license commit `d57333f4fd55123da1ee2e89c3e46fa7cebad415` recorded. Do not restart this resolved publisher-link search or pretend all rights evidence is absent.
- AudioSep remains resource-unverified: full CLAP audio/text construction, separate RoBERTa initialization, CPU checkpoint copies and non-strict separator loading need an exact adapter. Text-only CLAP could reduce footprint but has not been implemented or validated. Disk bytes are not resident/peak memory.
- `npm --prefix astra_backend test`: **160 passed, 0 failed, 0 skipped/cancelled**. `docs/astra/MILESTONE_7E_VERIFICATION.json` records runtime and output digest.
- No models/weights/audio/installer/paid service/main/Production actions. CPU synthetic tests only. Existing engine readiness/customer gates remain unchanged.

## Milestone 7F evidence / handoff

- Parent: `bdf2636bec5650b9312865693b416629dd166314`; local, origin and remote matched before implementation.
- `astra_backend/sampleChunkProcessor.mjs`, exported through `index.mjs`, adds sequential injected read/process/write callbacks around the sample planner. It validates exact lengths and finite numeric samples, copies callback buffers, crops context and awaits each write acknowledgement before advancing.
- Failures and cooperative cancellation expose confirmed sample/chunk counts and any uncertain write range. A partial/failed write cannot report completion. Cancellation waits for in-flight callbacks; this is not a timeout or process-kill mechanism. Callbacks remain responsible for truthful acknowledgements and external I/O.
- Ten new synthetic tests cover reconstruction including short/exact/tail cases, asynchronous ordering, malformed outputs, callback failures, partial writes, cancellation, buffer ownership/detachment and configuration validation. README documents the callback contract.
- `docs/astra/CLAP_TEXT_ONLY_LOADING_DESIGN_V1.md` freezes the pinned source text path: RoBERTa pooler output, fine-tuned projection and normalization; strict text-key selection; local tokenizer/config requirements; no HTSAT or redundant pretrained text initialization. Actual checkpoint keys/shapes, tokenizer artifact hashes, package pins, equivalence and peak memory remain unverified. This is a design, not an implemented model loader.
- `npm --prefix astra_backend test`: **170 passed, 0 failed, 0 skipped/cancelled**. Runtime/output digest and execution boundaries are recorded in `docs/astra/MILESTONE_7F_VERIFICATION.json`.
- Public source/config metadata only; no weights, model imports/inference, real audio, installers, paid services, main or Production changes. Existing readiness/customer gates and 4096 MB / 1200 seconds / zero-new-spend constraints remain unchanged.

## Exact next step — Milestone 7G

1. Read the sequential processor contract in `astra_backend/README.md`, `sampleChunkProcessor.mjs`, the existing offline analysis-stage adapter and `docs/astra/CLAP_TEXT_ONLY_LOADING_DESIGN_V1.md`. Preserve archived outcomes and existing engine/customer gates.
2. Connect chunk complete/failed/cancelled outcomes to the existing offline analysis-stage contract using injected synthetic callbacks. Preserve confirmed and uncertain progress; partial, failed or cancelled output must never enter render/delivery paths. Complete sample processing alone cannot establish musical quality or customer eligibility.
3. Add meaningful synthetic integration tests for complete processing, mid-stream failure, uncertain writes and cancellation through the analysis boundary. No real audio, model runtime, package installation or weight downloads.
4. Continue the text-only design prerequisites with public metadata: freeze local tokenizer/config identities and a source-derived exact text-key inventory. Explicitly distinguish source expectations from uninspected checkpoint tensors; do not infer memory fit or embedding equivalence.
5. Run the full backend suite; update verification and this checkpoint with actual results and remaining blockers. Commit code/tests/docs together on astra-work, verify remote tree/ref and leave the local branch clean. Use the connected GitHub API if CLI writes lack credentials. No main/Production action.

**7G outcome:** tested offline analysis integration with fail-closed partial-output handling and more precise loader prerequisites; no model execution or real-audio quality claim.

## Copy-paste handoff

Continue Jimmy PAIge from `docs/checkpoints/CURRENT_STATE.md` on branch `astra-work` in `dadrockyt-sys/dadrock-tabs-android`. Read AGENTS.md first. Both V143/Gomyway and Songsterr Fresh are archived; do not resume their old task queues. Work on the active Astra milestone, preserve historical outcomes, and commit/push clean backend work plus this checkpoint after each major step. Do not modify main or Production.
