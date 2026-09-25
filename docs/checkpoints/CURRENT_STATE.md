# New Astra Work — CURRENT STATE

Updated: 2026-09-21 UTC
Active branch: `astra-work`
Canonical handoff: `docs/checkpoints/CURRENT_STATE.md`
Status: **GUITAR-TECHS V1 FAILURE FROZEN; V2 200-FRAME DESIGN + CPU BUDGET + IMPLEMENTATION VERIFIED; V2 P1/P2 REAL TRAINING AUTHORIZED; P3 SEALED**

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

## Milestone 7G evidence / handoff

- Parent: `90df21ab43255e11d5b1fa01e2d9cea217c84b0f`; local, origin and remote matched before implementation.
- `astra_backend/chunkedAnalysisAdapter.mjs` exports `runAstraChunkedAnalysis`: validates requests before callbacks, connects processor outcomes to the analyzer extraction stage and preserves confirmed/uncertain progress. Cancellation maps to abstention; failures map to failed. Complete samples remain partial extraction with uncertain role. Events/structure/tablature do not run; no tab, render events or delivery eligibility is emitted.
- Six new synthetic integration tests cover successful reconstruction without delivery, read/process failures, uncertain sink receipts and JSON preservation, cancellation, empty input and preflight rejection. Full suite: **176 passed, 0 failed, 0 skipped/cancelled**. Initial fixtures used incorrect chunk-option names; corrected to the existing planner contract, then targeted and full suites passed.
- `docs/astra/CLAP_TOKENIZER_FILES_V1.json` freezes SHA-256, Git blob identities and sizes of config/tokenizer config/vocabulary/merges at an immutable public revision. Non-weight bytes were fetched and hashed; all four blob hashes match tree metadata.
- `docs/astra/CLAP_TEXT_KEY_INVENTORY_V1.json` enumerates 203 source-derived parameter names/shapes and reference buffer behavior. Transformers 4.30.2 is a source reference, not an approved runtime pin. Actual checkpoint tensors/buffers, tokenizer execution, dependency lock, numerical equivalence and resource fit remain unverified.
- Web-tool metadata/source retrieval failed; direct public HTTPS retrieval succeeded. An exploratory offline filename glob had no matches; the existing analysisContractAdapter was used. Details and output digest are in `MILESTONE_7G_VERIFICATION.json`.
- No weights, model imports/inference, real audio, package installations, paid services, main or Production changes. 4096 MB / 1200 seconds / zero-new-spend and existing readiness gates remain intact.

## Milestone 7H evidence / handoff

- Parent: `72fed47b22e180e07de26b1409940fc60425beac`; local, origin and remote matched at start.
- `syntheticExtractionHandoff.mjs` validates request/role/sample count/rate/identity/provenance and explicit unresolved quality. Immutable synthetic declarations are passed downstream only after all chunk writes complete. Failure/cancellation skips downstream; downstream errors stay explicit diagnostics. Callback return values never populate the analyzer or delivery payload. Identity is declared, not independently verified against sink bytes.
- `clapTextMetadata.mjs` checks 203 source-derived parameter keys plus reference position_ids metadata. Missing/extra keys, bad shapes/dtypes, mixed prefixes and normalized duplicates fail. Backend-local inventory preserves runtime namespace isolation. Float32 parameters/int64 buffer are a reference acceptance profile, not observed checkpoint dtypes. No tensor contents are validated.
- Seven new tests cover synthetic downstream sequencing, evidence mutation isolation, preflight errors, failed/cancelled chunks, downstream failures, and metadata corruption/prefix cases. Full suite: **183 passed, 0 failed, 0 skipped/cancelled**.
- Initial full suite caught the metadata module importing the documentation inventory outside the backend namespace. Fixed by adding a backend-local reference inventory; the boundary guard was preserved and full suite rerun. Verification records the output digest.
- README records remaining tokenizer defaults, runtime pins, safe deserialization, artifact/buffer verification, equivalence and resource prerequisites. No weights, models, real audio, package installation, paid services, main or Production actions. Existing engine/customer gates and 4096 MB / 1200 seconds / zero-new-spend unchanged.

## Milestone 7I evidence / handoff

- Parent: `ae16b315fa733673b2e1440451de02e3e4978739`; local, origin and remote matched at start.
- `syntheticEventPipeline.mjs` connects supplied synthetic events/structure to the existing deterministic rhythm, fingering and tab pipeline after complete chunks. Diagnostic text/events remain separate from the blocked analyzer payload; product-shell upstream readiness is forced false.
- Validates unique event IDs, numeric MIDI/onsets, positive durations/offsets, consistent end+duration, clip bounds from sample count/rate, matching structure duration and explicit tuning/capo before reads. Missing duration stays unresolved; source event IDs survive pipeline indexing. Inputs are snapshotted before callbacks.
- Six new tests cover all three roles, identity/timing preservation, missing duration and empty events, invalid/out-of-range data, exact tail offsets, conflicting durations, structure mismatch, failed/cancelled chunks and mutation isolation. Full suite: **189 passed, 0 failed, 0 skipped/cancelled**. Output digest in `MILESTONE_7I_VERIFICATION.json`.
- README clarifies future canonical sink byte/count/rate verification, incomplete-write handling and safe checkpoint extraction. No measured sink digest, weights, models, real audio, installs, paid services, main or Production actions. Existing readiness/customer gates and resource constraints unchanged.

## Real-audio evaluation steering / intake

The user explicitly requested real-audio evaluation, then identified Gomyway midterm and professional 113 on main/public for this purpose. This supersedes the next synthetic-only sink task. Authorization to use these named materials for development evaluation is recorded; historical exposure and archived outcomes remain intact. Do not ask for an audio upload again.

`docs/astra/GOMYWAY_REAL_AUDIO_INTAKE_V1.json` pins the audio and candidate reference identities at main commit bb992d901e78ab19645f8edc8e330d5a142ebd8e. Both downloaded bytes match Git blob identities. The 210.674649-second stereo 44100-Hz AAC midterm recording fully decoded with ffmpeg (exit 0). Professionalexample.jpg was visually inspected and shows the song's guitar tablature, and the user subsequently confirmed it as the 113-measure rhythm scorer. No transcription/model execution or accuracy score occurred. Prior /tmp/astra-engine-smoke-W0bAmw/venv runtime is absent. No runtime gates, main or Production changed.

## First real-audio baseline / reference recovery

- User clarified Professionalexample.jpg is the professional 113-measure rhythm reference; bass and lead references also exist in the archived pipelines and are scoring-only. Do not ask this identity question again.
- Both archived branches have identical reference receipt blobs. `GOMYWAY_113_REFERENCE_RECOVERY_V1.json` records identities, 17 bass pages, 22 lead pages, uncertainty annotations and unavailable private screenshot bytes. Library content and exact-filename searches found no matches. Git receipts explicitly exclude private screenshot bytes/normalized note labels from the public repository.
- Rhythm scoring sources recovered by identity: intro fixture blob `0ca4791471dc7834465fe746af8df185672d9c62`, approved measures 17–113 blob `5d7aac488eedd35ff144dbf1590c24d32fa0cf66`. Header/schema inspection incidentally exposed part of measure 17; this remains exposed development material, never blind holdout evidence.
- Restored exact Python 3.10.21 / 57-package locked CPU environment at `/tmp/astra-real-evaluation-venv`; snapshot matches and pip check pass. Verified Basic Pitch packaged TFLite SHA256 before loading.
- Predeclared first-30-second whole-mix Basic Pitch baseline in `GOMYWAY_BASELINE_PREREG_V1.json`. Runner reads audio/model only, no references. Fixed MIDI40–88, onset .5, frame .3, minimum duration127.7ms; no post-output tuning.
- Successful real inference: **87 events, 12.6276 seconds, peak RSS395408 KiB (~386 MiB)**. Full candidate events saved in `docs/astra/evaluations/GOMYWAY_FIRST30_BASIC_PITCH_V1.json`; provenance/hash/recovery details in `GOMYWAY_BASELINE_RESULT_V1.json`. This measures a short whole-mix TFLite baseline, not AudioSep separation, full-song fit, role accuracy or customer readiness.
- Initial attempt found prior /tmp audio absent; source was restored from pinned commit and hash verified. Runner now rejects missing input before model loading. Intended TFLite backend succeeded despite optional-backend/deprecation warnings. Full backend suite **189/189 passed**. No paid service, Demucs/AudioSep separation, main or Production action.

## Bass / lead PDF recovery update

User supplied the new public PDF locations. Exact main commit `6121b79769cba891952fb1c1624b0bac76c6dac7` contains `public/Gomywaybassreference.pdf` (corrected from supplied referenc3 spelling) and `public/Gomywayleadreference.pdf`. Both were downloaded and matched to published Git blob identities. Bass: 6 pages; lead: 7 pages. Details/hashes in `GOMYWAY_REFERENCE_PDF_INTAKE_V1.json`.

All-page overviews and full opening/ending pages were visually inspected. These are image-only PDFs with no extractable text layer. Visible coverage reaches 113, including collapsed rests (bass opening six measures, lead opening four; lead ending three measures from 111). Meter changes at 104/105 must not be flattened into uniform 4/4. This is a coverage review, not completed note-level normalization or proof of byte equivalence to old screenshots. Existing uncertainty annotations remain applicable. No predictions changed, no new model run or score. The missing-reference-file blocker is now cleared: do not ask the user to reattach the old screenshots.

## Scorer and provisional fixed-grid comparison

User requests lower overhead: batch focused reads/checks, concise updates, no unnecessary model/full-suite reruns. Chat quota/model settings are not controlled by repository code.

- `astra_backend/evaluation/score_note_onsets.py` performs exact-MIDI one-to-one onset matching, maximizing count then minimizing total absolute error per pitch. Validates identities/pitches/onsets and uses a half-open scoring window. Seven focused unittest cases passed (duplicates, greedy-loss case, minimum error, pitch/window boundaries, empty input, invalid values, order invariance).
- `score_rhythm_fixture.py` replays the comparison from an external reference file and validates its Git blob. No normalized reference notes added to public Git. Replay output is byte-identical to the saved aggregate result.
- Old global/local alignment scripts use prediction-match maximization; they were inspected but not run or accepted as independent alignment. Their blobs are 28619a9af7a357d5637d494cfec39d44abf79bd6 and 2456cc17ca1065124e11697df63966307d0429e0.
- `GOMYWAY_RHYTHM_SCORING_SPEC_V1.json` declares a single provisional grid: 129 BPM, assumed measure-1 offset 0, measures1–16 window [0,29.767441860465116), exact fretted MIDI (no bend adjustment), 50-ms onset tolerance. No offset search or retuning.
- `GOMYWAY_RHYTHM_PROVISIONAL_SCORE_V1.json`: 87 predictions, 104 rhythm-fixture targets, 5 matched, 82 unmatched predictions, 99 unmatched targets, matched mean absolute onset error27.8ms. Conditional P5.75% / R4.81% / F1 5.24%. These are NOT overall model accuracy: independent alignment and fresh label validation are absent; unmatched whole-mix events may belong to other instruments. Do not report 5.24% as validated transcription accuracy.
- Predictions remain hash 6ee8495a7fa54e7c9a76079792a53908724dbe6adb5e517f761b47b1dec21659. No inference rerun, settings change, new packages, main/Production change. Existing 189-test backend result retained; only seven relevant scorer tests and exact replay run this step.

## Independent audio pulse evidence — 2026-09-20

- The exact baseline waveform SHA256 remains 60ed11dcdea26a3773d1867671001e30d11e28e0bc9429cdb94a6575c87792cb. Librosa 0.11.0 was run on that audio alone (hop128, sample rate22050), with no prediction/reference matching. It returned overall tempo127.6042 BPM and the first33 beat timestamps, which are preserved in `GOMYWAY_AUDIO_TIMING_EVIDENCE_V1.json`.
- First RMS>0.01 window begins0.05805s; first detected onset0.110295s; first detected pulse0.121905s. None is automatically measure1/downbeat ground truth.
- A descriptive regression of 24 detected pulses in the declared early [.5,12) second window gives126.6463 BPM, residual RMS6.64ms. Its period differs from129 BPM by about0.519s over60 intervals. This is concrete audio-derived evidence against relying on the old fixed129 grid; it is not a verified full-song tempo map or proof of exact quarter-note/downbeat interpretation.
- `inspect_audio_timing.py` contains the audio-only extraction procedure for future reproducibility. The initial exploratory extraction succeeded. A later attempt to run the saved script encountered exit127: the temporary Python environment had disappeared after an environment update. Prior successful observations were preserved and regression recomputed with stdlib; no redundant installation/model run was performed. Saved script has not yet completed an end-to-end rerun.
- Archived midterm source manifest blob83d57a9c4b6b70c800e4076e1394fefba3318bde confirms exact source audio hash but provides no independently verified measure-start anchor. Historical champion scores do not belong to Astra. No new accuracy score, model change or promotion.
- Honor user's usage preference: short updates, batched focused work, no unnecessary repeated full-suite/model runs. Restore a needed runtime in a stable workspace cache rather than /tmp where feasible; verify locked identities after restoration. Do not claim control over GPT quota settings.

## Direct professional-image audit — 2026-09-20

- Recovered exact source audio/image into `/workspace/scratch/3a241f38aa8b/astra-eval-cache` with frozen SHA256 checks, avoiding another model/runtime installation. Decoded opening16s with installed ffmpeg for inspection. Workspace cache is reusable while present, not guaranteed durable; Git source identities remain authoritative.
- Original-resolution rhythm image review found concrete discrepancies in the historical two-bar fixture: an omitted visible open-string event, apparent string-line mismatch for a low open-string event, and two visible ending double-stop attacks where the fixture encodes one. Rhythmic stems and bend/release transitions require fresh audit. `GOMYWAY_INTRO_REFERENCE_AUDIT_V1.json` records the source identities and findings without publishing normalized labels.
- Therefore the historical104-target/5-match result must not be rehabilitated solely by tempo/offset correction. Keep it historical and conditional; the fixture is not qualified for validated scoring. No predictions or scores were regenerated.
- An exploratory short-time Fourier peak inspection of the opening audio produced multiple peaks per frame; those peaks are not reliable note identities or a verified first-measure anchor. No spectral peak was promoted to scoring ground truth. Source first16s decode succeeded; no model was run.

## Reviewed scoring integration

`astra_backend/evaluation/score_reviewed_bundle.py` now connects hashed predictions, private labels and an independent piecewise timing map to the tested onset scorer. It validates exact audio/professional source identities, reviewed label state, empty unresolved-items list, reviewed coverage, scoped role set and timing continuity/coverage. Rests/tie/bend continuations cannot create attacks; combined-role identical coincident pitches merge once. Validation failure writes no report; existing reports cannot be overwritten. Outputs omit private reference IDs, preserve input/spec hashes and keep customer delivery false/role accuracy null.

`docs/astra/REVIEWED_SCORING_BUNDLE_V1.md` documents the CLI and full contract, including the limitation that review assertions/hashes cannot independently prove musical truth or prospective freezing. `GOMYWAY_SCORING_BUNDLE_STATUS_V1.json` binds current source/prediction identities but leaves label/alignment hashes null, explicitly blocked. No reviewer approvals or scoring targets invented.

Focused evaluation suite: **15 tests passed** (7 existing onset tests, 8 new integration tests covering tampering, scope/source identity, unresolved evidence, gaps, non-attacks, coincident roles, CLI failure/no output and piecewise timing). No model/full-backend rerun or installation. Previous189-test backend result remains historical, not a new run. No actual replacement Gomyway score, archived changes, main or Production changes.

## Audio-only alignment review aid — 2026-09-20

- Added `build_alignment_review.py` and `alignment_review.html`: exact WAV/evidence hash and rate checks, embedded audio/waveform, 33 diagnostic pulse markers, slower playback, seek/capture controls and explicit quarter-note anchors. No predictions or reference labels loaded. Anchor exports are always draft with unresolved review items; scorer admission remains blocked.
- Recovered first30 WAV from the existing pinned source via ffmpeg; SHA256 matches the frozen baseline exactly. Generated the private `Gomyway-Audio-Review.html` without another model run or package install. This is a review aid, not completed alignment or fresh normalized labels.
- 19 focused Python tests pass (15 scoring + 4 builder). Actual JavaScript syntax/export logic checks pass, including invalid anchor rejection. Browser end-to-end attempt failed before navigation: Playwright Chromium executable absent; agent-browser CLI also absent. Playback, layout and browser download still need a real browser check. No browser download was attempted.
- Contract/reproduction and limitations: `docs/astra/AUDIO_ALIGNMENT_REVIEW_V1.md`. Continue by using the review page to identify independent musical anchors and auditing the first two measures directly. Do not spend another turn rediscovering broad tempo or rebuilding this helper. Preserve draft status until musical evidence is actually verified.

## Fresh visual reference draft — 2026-09-20

- Individually inspected measures1-16 using enlarged crops of the exact2160×3840 professional image. Enlargement was for inspection only; no image generation or inferred extra detail. The second screenshot begins with13-14 (unobscured duplicate of the first screenshot's player-covered bottom row), then15-16. Do not count screenshot starts as new measure ranges.
- Saved private `Gomyway-Reference-Draft-M1-16.json`, SHA256 `482e18ec5d06087912bc4f172db7f2ea9a4d85d93e9b4db06a23223eb29f72ca`. Contains source bounds per measure, fresh string/fret observations, provisional quarter-note positions,136 candidate pitched entries and16 continuation entries. This is draft notation evidence, not136 approved scoring targets. No sounding MIDI or audio alignment has been assigned.
- All16 measures remain draft: confirm tuning/capo, full-bend attack/continuation semantics, slurred open-note onset policy, and rhythmic subdivisions. First-measure audio anchor remains unverified. No candidate score/prediction changes, model run or new test-suite run. JSON/unique IDs/position bounds/source hash checked. Prior test results retained.
- Public receipt `GOMYWAY_FRESH_REFERENCE_DRAFT_V1.json` records the artifact hash and aggregate findings without publishing the note table. Retrieve the private filename and verify its hash if the workspace copy disappears. Continue reviewing this draft; do not recreate the old incomplete template or restart initial image recovery.

## User confirmations and scoring review fix — 2026-09-20

- User explicitly confirmed standard guitar tuning E A D G B E with no capo, and that the first audible guitar riff begins at measure1 of the professional reference. Treat both as resolved identity facts; do not ask again. No exact onset timestamp was supplied, so measure1 time remains unverified.
- Updated the same private `Gomyway-Reference-Draft-M1-16.json` to revision2, SHA256 `021a225cf1daa518689b0c55b86f9cfba71463a4e1d78d2525da80207db0b8fe` (supersedes482e18ec…). Added120 candidate sounding MIDI values using confirmed tuning;16 bend-attack pitches remain null, with separate fretted MIDI recorded. All labels remain draft and have no approved audio alignment.
- Clarified onset policy: a distinct hammer-on/pull-off note counts as an onset despite no new pick stroke; continuous bend/tie motion alone does not add a target. This settles the metric definition, not all source-event timing or bend interpretation.
- Fixed a concrete scoring admission gap: alignment reviewStatus complete no longer passes with unresolvedItems present, missing or malformed. It now requires explicit empty unresolvedItems, just like label review.21 focused Python tests pass, including contradictory alignment review declarations and synthetic legato/bend behavior. No model rerun, new accuracy score, main or Production change.

## Bounded opening-attack evidence — 2026-09-20

- `inspect_opening_attack.py` completed on the exact frozen WAV, analyzing only its first second with existing NumPy2.3.5. Saved10 explicit energy-threshold/persistence observations and17 short-window harmonic observations in `GOMYWAY_OPENING_ATTACK_EVIDENCE_V1.json`. No predictions/labels read, inference, installation or broad tempo rediscovery. Core diagnostic runtime approximately0.023s (excludes Python startup).
- Depending on threshold, first signal rise is0.06984–0.10177s. This describes signal activity, NOT a verified onset confidence interval or exact measure1 anchor. The earlier low transient and later stronger energy rise must not be collapsed into an invented timestamp.
- Harmonic subsets broadly agree around242Hz at0.24–0.28s and about219–223Hz by0.36–0.40s, supporting a changing pitch later in the gesture. They disagree around the early attack. This restricted180–280.75Hz harmonic diagnostic cannot establish the actual attack note; overlapping subsets are not independent estimators. No strongest peak was promoted to musical truth.
- Private draft revision3 SHA256 `7b720cad92b5b3d6e414f88923094e4f4997bca7668bfddcce4b3bb58287f004` now fills the16 bend-start candidates using the printed fret at the beginning of the upward bend curve. All136 pitch candidates are present, but the16 bend starts remain explicitly NOT audio-verified and all labels remain draft. Replaces revision2, not a new reference identity.
- Validated real diagnostic JSON,10 energy rows/17 harmonic rows,136 populated pitch candidates and all152 entries retaining draft status. No new unit-suite run;21-test result remains previous milestone evidence. No score, main or Production change.
- Do not repeat these spectral/threshold diagnostics expecting them to settle mixed-audio ambiguity. Next useful evidence is direct musical listening/annotation of the attack and subsequent anchors (the existing review page), plus rhythm-source review. User already confirmed standard tuning/no capo and opening measure1; do not re-ask those facts. A populated candidate must not be relabeled reviewed without new evidence.

## Source rhythm and opening pre-bend correction — 2026-09-20

- Re-inspected source crops for all16 measures, including unobscured13-14 in panel2. Explicitly read beams, flags, augmentation dots and the unnumbered tied stem. Stored source-symbol spans and source note-onset/tie classifications in private draft. All16 measures cover four quarter notes exactly by rational arithmetic;136 rhythmic positions span64 quarters. Simultaneous chord notes count as one rhythmic position. This completes the source rhythm reading, not acoustic timing/duration verification.
- User replied **Bent first** to the question whether the opening note is picked normally then bent or pre-bent before picking. Interpret as opening pre-bend; the source full marking supplies nominal two-semitone amount. Corrected that opening candidate rather than leaving the unbent-fret assumption. Confirmation applies to opening note only; do not silently apply it to the15 later bends. Do not ask again about opening pre-bend, standard tuning/no capo or starting measure1.
- Same private draft now revision5, SHA256 `a131cee0bfb20ec574b4f14c49395a62cf89abccea7e20a300153e05d5ee04d9`. Revision4 (`b669007b…`) completed rhythm reading; revision5 incorporated the user's mid-task correction. All152 entries remain draft;136 pitch candidates retained. Remaining15 bend starts and exact audio timestamps remain unresolved.
- Browser verification attempted with a55-second-bounded Playwright headless Chromium download. CDN request timed out after30s; outer command terminated the retry at55s (exit124). Browser remains unavailable; no playback/listening verification was performed. Do not repeat downloads in this environment without changed connectivity. The existing review page remains available for a listener; this is a tool availability blocker, not a reason to infer timestamp truth.
- Validated private JSON, all-measure rational coverage,136 pitch candidates and draft status. No new unit-suite/model run or real score; previous21-test result remains historical. Receipt updated without publishing note labels. No main/Production change.

## Audio-only pulse timing prior — 2026-09-20

- Added `astra_backend/evaluation/build_pulse_timing_prior.py`: a standard-library, fail-closed transform of the preserved audio-only pulse evidence. It refuses evidence that read predictions/reference labels, validates pulse ordering and frame resolution, uses median/MAD plus a minimum three-frame tolerance to flag irregular intervals, and fits only contiguous stable pulse runs. It never selects a downbeat, creates scoring-map approval or makes customer delivery eligible.
- Frozen public diagnostic receipt `docs/astra/GOMYWAY_PULSE_TIMING_PRIOR_V1.json` from the exact timing-evidence blob (`51d829f467e020c935dfa426422f8c65747c7222`; SHA256 `cf9d2811fe911394fc8cd6396551071e191f9bc733b8c41cb23e73f5936acca4`). The 33 pulses have median interval `0.47600907029478456s` (126.0480 BPM). Three intervals are flagged: pulse0→1 (0.5050340s) and the short/long pair around 14.286s (0.3773243s / 0.5456689s).
- The long stable run pulse1→29 fits `0.4736641980273226s` per pulse = **126.6720 BPM**, RMS residual **6.31ms**, max residual **16.21ms**. This independently agrees with the earlier .5–12s regression at 126.6463 BPM, but remains only tracker phase/rate evidence.
- Opening observations stay separate: RMS activity 0.05805s, detected onset 0.110295s and first observed pulse 0.121905s. The first pulse interval itself is flagged, so none of these may be silently promoted to measure1/downbeat. The report emits an empty candidateDownbeats list, measureOneStartVerified false and tempoMapVerified false.
- Added six focused tests for regular/glitched pulse trains, prediction/label contamination, invalid pulses, frame-quantization tolerance and exclusive CLI output. Local focused verification against the current scorer/bundle code: **23 tests passed** (7 onset scorer + 10 reviewed-bundle + 6 pulse-prior). The existing four alignment-builder tests and 189-test Node backend result were not rerun locally in this step.
- Updated the branch-only CI workflow to run the 27 standard-library Python evaluation tests plus the existing browser-script syntax check after the complete Node backend suite. It installs no audio/model packages and runs no inference. This save itself decoded no audio and reran no model/predictions.

## Repeated-opening bend review and private revision 6 — 2026-09-20

- Recovered the exact private revision5 label draft from Library and the exact embedded 30-second review WAV (SHA256 `60ed11dcdea26a3773d1867671001e30d11e28e0bc9429cdb94a6575c87792cb`). No candidate predictions were read.
- Added `astra_backend/evaluation/inspect_repeated_openings.py`, an audio-only NumPy diagnostic driven by the already-frozen 1.8946567921s four-pulse measure-period prior. It finds a bounded opening attack, sequentially matches the repeated opening within ±0.10s, and compares short-time harmonic contours/clusters. It remains diagnostic-only and cannot approve timing, labels, scoring or delivery.
- Real repeated-opening evidence: measures2–16 stacked ridge is low→high→low (222.061→247.632→220.715Hz). 13/15 later measures pass the direct contour rule; all15/15 are spectrally closer to the later-opening cluster than to the user-confirmed pre-bent measure1. This corroborates the already-completed source reading: measures2–16 attack at the printed/fretted pitch then bend upward/release; measure1 remains pre-bent.
- Corrected reproducibility before save: removed wall-clock runtime from the diagnostic output. Deterministic diagnostic SHA256 is `775e1a9264fed4237bdb6f11b72a0f568254ddb6b57037cdae65d685105d0c06`. Three focused synthetic NumPy tests pass (cluster/contour, hash fail-closed, timing-prior fail-closed).
- Private `Gomyway-Reference-Draft-M1-16-r6.json` is now durably stored outside public Git, SHA256 `5f040af4d7daa2eb6b74445bfe46e72f5847e2410ec21d3f01d603630edcd977`. It contains 136 reviewed sounding-at-attack pitches:120 ordinary source-fret/tuning readings,1 user-confirmed opening pre-bend and15 later bend-start reviews. Its top-level state remains draft only because absolute audio timing is unresolved.
- Public `GOMYWAY_PITCH_REVIEW_RECEIPT_V1.json` exposes hashes/counts only; normalized note targets remain private. No model rerun, separator, candidate change, new score, main or Production change.

## Bounded reviewed score — measures 1–15 — 2026-09-20

- Closed the timing blocker without extrapolation by scoring only measures1–15. Sixteen independently observed repeated-opening attacks bound all15 measure segments from beat0 to beat60: audio window [0.09868480725623582, 28.299319727891156). Measure16 is deliberately excluded because its closing boundary is not independently observed.
- Private reviewed labels are stored outside public Git as `GOMYWAY_REVIEWED_LABELS_M1_15.json`, SHA256 `a696af9dcbc6f69eeec11600aa21d19fcb44a386a231e4041730a74e2f517e15`:126 attacks +15 tie continuations, reviewStatus complete, coverage reviewed, exact rhythm-source identity and revision6 pitch policy. Private alignment `GOMYWAY_ALIGNMENT_M1_15.json` SHA256 `31947a9c73b025e565a048d69da54ffb94464f6ea5acf73f526c89d823c063ae` contains15 contiguous observed measure segments and no prediction-derived anchor.
- The original frozen first30 Basic Pitch candidate remains unchanged at SHA256 `6ee8495a7fa54e7c9a76079792a53908724dbe6adb5e517f761b47b1dec21659`. Public `GOMYWAY_FIRST30_SCORING_PROJECTION_V1.json` is an exact start+MIDI projection because those are the only candidate fields consumed by the onset scorer; projection SHA256 `1f3298efa446b36e7679a0eb3753d1aa03675732cbfd119a236c7c3b78bd13d7`. No inference was rerun.
- Reviewed development score over the bounded window: **83 predictions,126 targets,26 TP,57 FP,100 FN; precision31.33%, recall20.63%, F1 24.88%, matched onset MAE22.99ms**. Public aggregate: `docs/astra/GOMYWAY_REVIEWED_M1_15_SCORE_V1.json`. This is whole-mix Basic Pitch versus rhythm labels, NOT requested-role separation accuracy or customer accuracy.
- One-to-one onset-only diagnostic upper bound (ignoring MIDI) is46/126 targets: precision55.42%, recall36.51%, F144.02%, MAE18.18ms. Exact pitch therefore accounts for substantial additional loss, but onset/event coverage is already poor before pitch identity is considered.
- Concrete failure signature: all15 reviewed MIDI50 targets and all14 reviewed MIDI57 targets have zero exact matches in this window. The candidate mostly detects MIDI40/52 material. This shows source/event inference is the dominant current failure; renderer/fingering tuning cannot repair the missing acoustic evidence.
- Private spec/result were also saved to Library. `GOMYWAY_SCORING_BUNDLE_STATUS_V1.json` is updated from blocked to reviewed-bounded-score-complete-m1-15. Customer delivery remains false; roleAccuracy remains null; no main/Production change.

## Guitar-isolation oracle salience diagnostic — 2026-09-20

- Recovered the existing user-provided guitar-only development asset from Library. Its two stored copies are byte-identical M4A SHA256 `6601b8d01cbbbe6b6e70d9ec0ca3c15d17873c78e62ae4acdc258c96f168e3c9`; duration217.060136s. Decoded first30 mono PCM16/22050 WAV SHA256 `e294d78c8c0f853861ab5bb1effed2dd54799bfb308ef48e036c144dfaec71d6`.
- The isolated file is a different derived/mastered asset, so source timestamps were NOT reused directly. Audio-only chroma-DTW correspondences over measure starts2–15 fit `isolated = 0.5229997584 + 1.0107587634 * source` with RMS residual7.32ms and max15.28ms. Its first clear guitar attack at0.621134s agrees with the affine prediction0.622746s.
- Added `astra_backend/evaluation/compare_isolation_salience.py` and three focused NumPy tests (positive-gain synthetic, hash mismatch fail-closed, draft-label fail-closed): **3 passed** locally. The diagnostic reads private reviewed labels only to ask whether the known target pitch is acoustically more exposed; it never reads candidate predictions.
- Across126 reviewed M1–15 attacks, the guitar-only oracle improves harmonic contrast on104 targets; median gain **+2.73dB**. The classes with zero exact matches in the whole-mix score improve materially: MIDI50 median **+4.09dB** (14/15 positive) and MIDI57 **+2.41dB** (9/14 positive). MIDI62 and67 each gain about+4.3dB on all14 targets.
- Public aggregate: `docs/astra/GOMYWAY_ISOLATION_SALIENCE_V1.json`. This is NOT transcription accuracy and does not imply an approved separator can reproduce the oracle. It is concrete evidence that source isolation is a high-value next component rather than a renderer/fingering problem.
- The exact locked Basic Pitch/TFLite runtime is absent from the active container. No unpinned replacement was installed and no isolated-audio model inference was claimed. Existing model/runtime identity gates remain intact.

## Oracle transcription preregistration and clock projection — 2026-09-20

- Froze `docs/astra/GOMYWAY_ORACLE_TRANSCRIPTION_PREREGISTRATION_V1.json` **before any oracle Basic Pitch predictions exist**, SHA256 `cf78dff6ea5935dfcd3698b3b29e2a55f3772f249bb4d526e5b6cb3ffd0b2c03`. It pins the guitar-only first30 WAV `e294d78c8c0f853861ab5bb1effed2dd54799bfb308ef48e036c144dfaec71d6`, source M4A `6601b8d01cbbbe6b6e70d9ec0ca3c15d17873c78e62ae4acdc258c96f168e3c9`, canonical source audio `60ed11dcdea26a3773d1867671001e30d11e28e0bc9429cdb94a6575c87792cb`, reviewed-label/alignment hashes, fixed 50ms tolerance and the already-independent affine time relation.
- The inference contract is now immutable: Python `3.10.21`, requirements lock SHA256 `a5614dbfad0be96aadc0d76297b6a59abe4e09c80bf2d6a484e53a14a58d38a7`, Basic Pitch `0.4.0`, model SHA256 `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`, runner Git blob `95950c50e00777ba3c0398b917f95dcece70065c`, and the exact first30 thresholds/settings already used by the whole-mix baseline. Alignment/tolerance/MIDI mutation after seeing oracle predictions is forbidden.
- Added `astra_backend/evaluation/project_oracle_predictions.py`. It accepts only the preregistered Basic Pitch result identity, validates runtime/model/settings and oracle audio identity, maps `sourceSeconds=(isolatedSeconds-offset)/scale`, preserves MIDI unchanged, rejects role/delivery/accuracy claims, drops rather than clips events whose projected onset is before source time zero, and emits a canonical-source-clock prediction document suitable for the existing scorer.
- Six focused standard-library tests pass locally: exact inverse-clock mapping/MIDI preservation, pre-zero exclusion, oracle identity/role fail-closed behavior, frozen runtime/model/settings/transform/tolerance, invalid event/order rejection and exclusive CLI output. The branch CI suite now includes these tests; no model dependency is needed to verify projection semantics.
- Runtime restoration was checked before save. No cached Basic Pitch, TFLite model/runtime or Python3.10 environment exists under the active persistent cache/workspace paths. Earlier `uv` restoration attempts could not obtain the required runtime/packages because package-download DNS/network access failed; no unpinned substitute was installed. No oracle model inference or new score is claimed.
- The reviewed M1–15 bundle, revision6 labels, timing map, 87-event whole-mix candidate and 24.88% bounded baseline remain unchanged. No main/Production change.

## Frozen runtime export attempt — 2026-09-20

- Added a branch-only GitHub Actions runtime exporter. It receives **no audio, labels, predictions or credentials**. Its sole job is to reproduce the previously verified Python3.10.21 + 57-package hashed environment from `astra_backend/engine/requirements.lock`, compare installed name/version metadata byte-for-byte in meaning with `installed-distributions.json`, verify the packaged Basic Pitch model SHA256 and archive the resulting Python prefix as a workflow artifact.
- The workflow is triggered only when its own file changes on `astra-work`. It has read-only repository permissions and performs no deployment, production action, Demucs weight download, audio access or model inference.
- This is an execution-recovery step for the private oracle test. Success would let the exact runtime be transferred back to the active workspace without placing private development audio in GitHub. Failure must be recorded as a blocker rather than weakening the preregistered runtime identity.

## Frozen runtime export first-attempt result — 2026-09-20

- GitHub Actions supplied exact Python3.10.21 and `uv==0.10.0`. `uv pip sync --require-hashes --torch-backend cpu` resolved57 packages, built pinned Demucs4.0.1, installed Basic Pitch0.4.0/TFLite2.14.0/Torch+Torchaudio2.11.0+cpu and `uv pip check` passed.
- Identity verification found **zero missing frozen distributions**. The only extra distribution was `pip==26.2.1`, pre-seeded by `actions/setup-python`; it is not present in the historical uv-created 57-package snapshot. The archive step therefore correctly failed closed and no runtime artifact was emitted.
- The retry removes only that runner-seeded pip distribution *after* hash-locked sync/check, using external `uv`, then repeats the exact 57-distribution + Basic Pitch model-byte verification. No locked package version, preregistered inference setting or model identity changes.

## Oracle guitar transcription score — 2026-09-20

- Exact frozen runtime recovery succeeded through the private GitHub Actions artifact: runtime ZIP SHA256 `47a6ad49740721d83b1589c897c48efd0c4d0ddbc8e0c0919dc38feaab6c9def`, embedded Python3.10.21 runtime tar SHA256 `8113897ae9412d921c5011570577d5a6ef00fb73ec59a1a57c8769880d914edb`. The transferred runtime re-verified Basic Pitch0.4.0 and model SHA256 `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`.
- Ran the preregistered runner blob `95950c50e00777ba3c0398b917f95dcece70065c` exactly once on oracle WAV `e294d78c8c0f853861ab5bb1effed2dd54799bfb308ef48e036c144dfaec71d6`. Frozen native result SHA256 `0e107ea954ab34b7701a31bd9ca0cccac1f01283528d070d5a5c6b15f2c42e68`:156 events,18.6281s model wall time,372304KiB peak RSS.
- Real output exposed one validation-only bug before scoring: Basic Pitch event rows are unordered. Removed the projector's incorrect ordering requirement; events remain in native order and no MIDI/timing/scoring parameter changed. The corrected projector retains all six fail-closed tests plus explicit unordered-input acceptance.
- Source-clock projection SHA256 `d305a86f543900a7ed6984b8c020b1cc13b99d8c0fcbcff0d2bad8e17c4690ce` maps all156 events through the preregistered affine relation; zero events were dropped. Private spec SHA256 `9acc13ee888d939ea0a1a120a84289806f8a7e0a4b7ccfd7538943bb1ee4e572`; private score SHA256 `36ae31bc186d9aeb9154d0c674110fa91e9d840833d78cd0a6441ee6a848dfc3`. All are stored durably outside public Git.
- Reviewed M1–15 oracle score: **151 in-window predictions,126 targets,40 TP,111 FP,86 FN; precision26.49%, recall31.75%, F128.88%, onset MAE21.78ms**. Whole-mix baseline was26 TP/57 FP/100 FN; precision31.33%, recall20.63%, F124.88%. Isolation therefore adds14 exact TPs and reduces FNs by14, but also exposes many more extra notes.
- Onset-only diagnostic improves from46→70 matched targets: recall36.51%→55.56% and F144.02%→50.54%, with essentially unchanged matched onset MAE (~18.2ms). This is strong evidence that isolation improves acoustic event visibility even though pitch identity remains weak.
- The two prior zero-match classes remain zero exact matches after isolation. MIDI50/D3 has **11/15 targets with an onset-aligned MIDI62/D4 prediction** within50ms: a systematic +12-semitone octave error. MIDI57/A3 bend-start has only **1/14 targets with any prediction at all within50ms**; the bend attack is mostly absent, not merely octave-shifted.
- Public aggregate is `docs/astra/GOMYWAY_ORACLE_REVIEWED_M1_15_SCORE_V1.json`. This development oracle is not a production separator and generic guitar does not establish rhythm/lead role truth. Customer delivery remains false; main/Production unchanged.

## Raw Basic Pitch activation diagnostic — 2026-09-20

- Captured the exact Basic Pitch0.4.0 raw model outputs on the frozen guitar-only oracle using Python3.10.21/model SHA256 `3db297d54af8e01c6e5618245c956b1d71b6a2b978cb2dedb527173186552676`. Capture was reference-blind. Private tensor archive `GOMYWAY_ORACLE_BASIC_PITCH_RAW_ACTIVATIONS_V1.npz` SHA256 `0cd4d4365763d249bef32236bee188b038b11275852d620995a6029fe7d9d2a6`; metadata SHA256 `01440b6ed664a28992e2b9a6fc56a7fb111bc5f6f16753f93c60fb47e2f65012`. Both are durably stored in Library, not public Git.
- Shapes are note2580x88, onset2580x88 and contour2580x264. The standard MIDI-note bins are MIDI21–108 and contour resolution is3 bins/semitone.
- Post-capture reviewed diagnostics separate the two failures. For the15 reviewed D3/MIDI50 targets, the neural activation itself favors D4/MIDI62: median target onset max ~0.3205 vs octave-up ~0.7715; median target frame max ~0.1186 vs octave-up ~0.5624. D3 frame evidence never reaches the standard0.3 note threshold, so merely lowering postprocessing thresholds is not a credible octave fix.
- For the14 reviewed A3/MIDI57 bend-start attacks, the onset head often fires while the sustained-note head remains weak: median onset max ~0.4190, frame max ~0.1442. Raw contour median moves from ~57.7 MIDI around46–69ms through ~58.0/58.3/59.0 to ~59.3 by161–230ms. The model retains attacked upward-glide evidence that the standard note decoder discards.
- Public aggregate receipt: `docs/astra/GOMYWAY_RAW_ACTIVATION_DIAGNOSTIC_V1.json`. Raw tensors/private labels are not published. Customer delivery remains false.

## Reference-blind contextual octave repair — 2026-09-20

- Added `astra_backend/evaluation/repair_contextual_octaves.py`. It does not read reference labels, audio or raw tensors. It only considers singleton onset groups and may move one event down exactly12 semitones when both immediate neighboring onset groups support that lower voice within a0.75s horizon and local voice-leading cost improves by at least8 semitones. Chord groups, timestamps and event count are immutable.
- Seven synthetic tests pass locally: supported octave repair, chord preservation, two-sided-evidence requirement, context-horizon guard, count/timing immutability, input/delivery immutability and invalid-event rejection. Branch CI now includes the suite.
- On the frozen source-clock oracle projection, the rule proposes exactly7 repairs. Private repaired projection SHA256 `bf7b5ed4f03614095b4ef7fa494335b110d7a009e2c559215a8b46c28a079763`, private score spec SHA256 `c7f91a492e2ea473635bcf0f4e80dab1e0426d0cbe580b6e887768244c9a400b`, score SHA256 `7a947236019e9eb366f0fcd471a3f494ea80b656cadc68ad68037cf4b37b2a8f`; all are durably stored outside public Git.
- Reviewed M1–15 score improves from40 TP/111 FP/86 FN to **45 TP/106 FP/81 FN; precision29.80%, recall35.71%, F1 32.49%**, with the same151 in-window predictions and onset MAE21.38ms. Five previously missed targets become exact matches and **zero previously matched targets are lost**.
- Recovery audit: four D3/MIDI50 targets are corrected (0/15 ->4/15 exact matches) plus one G3/MIDI55 target. MIDI57 bend-start remains0/14. This confirms local octave ambiguity and attacked-bend omission are separable backend failures.
- Public aggregate: `docs/astra/GOMYWAY_CONTEXTUAL_OCTAVE_SCORE_V1.json`. This rule was evaluated on development material and requires prospective cross-song validation before product use; it is not a fixed-register gate and does not establish rhythm/lead role truth.

## Raw bend-start detector + octave-supported refinement — 2026-09-20

- Added `astra_backend/evaluation/extract_raw_bend_starts.py`, a reference-blind technique candidate extractor over the frozen Basic Pitch raw onset/contour tensors. It uses Basic Pitch's own 0.5 onset and 0.3 frame-salience thresholds, requires an early contour within 1 semitone of the candidate and a 1–3-semitone rise over roughly 35–240ms, suppresses only an already-decoded same-pitch onset, and locally deduplicates neighboring raw bins. No rhythm labels, target MIDI values, measure numbers or score are read.
- Private V1 bend output SHA256 `201534080ea02a21ac5104dc7b771a96f05eecb75b344c74186008268802d71b`:57 candidates. Seven synthetic detector tests pass locally.
- Added `astra_backend/evaluation/refine_bend_octave_support.py`. V2 may move an upper-octave bend candidate down exactly12 semitones only when the lower octave independently has >=0.3 onset support within one model frame and independently satisfies the same contour-rise semantics. Six synthetic refinement tests pass locally.
- Private V2 output SHA256 `3a463dd3ae737135827b4f33730969436e91305c0a5f37362ac71ef6489ae4b1`:49 candidates after11 octave-supported changes/deduplication. Against rhythm bend starts alone, V2 improves exact recovery from4/14 to6/14 and timing-only remains8/14, but48 in-window candidates leave precision too low for direct note insertion.
- Public aggregate `docs/astra/GOMYWAY_BEND_CANDIDATE_EVAL_V1.json` records the deliberate **do-not-merge** decision. Candidate output, code snapshot and detailed evaluation are durably stored in Library. This negative/partial result redirected work toward role separation instead of threshold tuning.

## Lead reference recovery + dual-role benchmark correction — 2026-09-20

- Recovered the professional lead reference from `main/public/Gomywayleadreference.pdf` through a branch-only read-only artifact export. Local PDF SHA256 `a11a2c04fdda73e667df16df99aedf9ae0a3ed7af85f62f3c1773b7784a97f56`. Render-first visual review shows a four-bar multimeasure rest in measures1–4 and the repeated lead riff in measures5–16.
- Normalized only bounded measures1–15 privately. Lead label SHA256 `f9751f364864ddb3b161a870d8ab26ac7b338ffe4c04db08a24ace4d381e23fb`:77 attacked lead targets in measures5–15; measures1–4 are source-verified silence. Times use the already-frozen independent M1–15 alignment; no prediction was used to derive them. Private dual-role benchmark SHA256 `adaf89eca6b87096120009b550a2b6e598e2fd91ba6f39525ae60e4895a8da56`.
- There are **zero same-MIDI cross-role target collisions within the frozen50ms tolerance**, so one-to-one joint scoring can attribute exact matches to rhythm versus lead without double-counting a prediction.
- Frozen generic-guitar oracle:151 in-window predictions against203 combined rhythm+lead targets -> **75 TP / 76 FP / 128 FN; precision49.67%, recall36.95%, F1 42.37%**. Of the75 joint matches,40 are rhythm and35 are lead. Separate diagnostic recall: rhythm31.75%, lead45.45%.
- Critical correction: the contextual octave transform changes the role allocation to45 rhythm +30 lead matches but leaves the **joint result exactly unchanged at75 TP / 76 FP / 128 FN, F1 42.37%**. The apparent five-note rhythm improvement was a five-note loss from the lead role, not a net transcription gain.
- Therefore octave-high detections on this generic guitar oracle cannot be called Basic Pitch octave mistakes solely from rhythm scoring. Many are valid lead-guitar events. `docs/astra/GOMYWAY_CONTEXTUAL_OCTAVE_SCORE_V1.json` now carries this correction, and `docs/astra/GOMYWAY_DUAL_ROLE_GUITAR_BENCHMARK_V1.json` is the authoritative aggregate.
- Added `astra_backend/evaluation/score_role_aware_note_onsets.py`: one shared prediction inventory is matched jointly across role target sets, so one prediction cannot score twice. It fails closed on same-MIDI cross-role target collisions. Five synthetic tests pass locally, including explicit role-transfer-with-unchanged-joint-score behavior; branch CI now includes them.
- This supersedes the prior interpretation that contextual octave repair established a transcription-accuracy breakthrough. The transform remains useful research evidence about local role ambiguity, but is **not** a product correction rule.
- No main/Production change. Private normalized lead labels remain outside public Git.

## Stereo spatial role-evidence breakthrough — 2026-09-20

- The existing user-provided isolated guitar source is true stereo. A first30 PCM decode has SHA256 `b5e18d67397463c5de1bdb0644cc50ba4ac90c9357936c77e81bb563fbefe2c6`; left/right mono channel hashes are `2bb45aabaa9d09ed8a8a044480d9d2fc4398b0c10dfb5abcfd2ba9d53b262f65` and `e98ba1290c53010f65537fac232170ea4715cbdb25393bf4667e8a0ef2034fae`. L/R waveform correlation is only **0.05325**, demonstrating materially distinct channel content before any model inference.
- Froze private stereo-channel preregistration before channel inference, SHA256 `dce9a009789cb96bb40c0495cb91456f6852ff7abd9fae4cba9635dcf8ef2a09`. It pins the exact Python3.10.21 / Basic Pitch0.4.0 / model / runner / threshold identities and requires both channels to use the already-frozen isolated→source affine clock. It predeclares a full2x2 channel-by-role evaluation and forbids post-score threshold/audio swapping.
- Ran exact locked Basic Pitch once per channel. Left native SHA256 `d701c904c263e6402e7cced7b8206bf51bb81864dcf8bea5314ed806f5e28f6a`:166 events,2.027s model wall,261088KiB peak RSS. Right SHA256 `28ab54e0caacf98765daba3befb0c01efdbad19df9cf45b596efe07167207dd2`:128 events,1.997s model wall,260532KiB peak RSS. No runtime/model/settings substitutions.
- Channel-role matrix is strongly asymmetric: left→rhythm scores45 TP versus left→lead17 TP; right→lead42 TP versus right→rhythm16 TP. The opposite role mapping is therefore poor. Raw L→rhythm + R→lead gives87 correct-role TPs before cross-channel duplicate cleanup.
- Added `astra_backend/evaluation/stereo_role_evidence.py`. It is reference-blind and uses **relative** channel evidence only: low inter-channel correlation, onset-group chordality and relative median pitch. It has no fixed MIDI cutoff. It abstains if channels are too correlated or chordality/register evidence does not agree. Eight synthetic tests pass locally and branch CI now includes them.
- On the real predictions, the frozen classifier completes with **left→rhythm, right→lead**: left chord-like rate11.90% / median MIDI52; right0.92% / median MIDI63; chordality ratio12.98x and relative median gap11 semitones. Private role-evidence report SHA256 `544398724e736243e469180e38df851cafcadbb70ac3f0998564a23306fd2bf3`.
- Cross-channel same-MIDI/time duplicates are removed only when one channel has higher model amplitude; exact amplitude ties remain duplicated to avoid role bias. In the bounded M1–15 score this produces rhythm139 predictions /43 TP /96 FP /83 FN (F132.45%) and lead106 /41 TP /65 FP /36 FN (F144.81%). Aggregate **84 TP /161 FP /119 FN; precision34.29%, recall41.38%, F137.50%**.
- A conservative mode keeps the original mono inventory and uses stereo only as role evidence. In-window it assigns57 events to rhythm and55 to lead, while abstaining on11 ambiguous and28 unmatched events. Aggregate assigned precision is **49.11%**, recall27.09%, F134.92%; lead precision is52.73%. This gives a useful fail-closed option while the high-recall stereo streams remain development-only.
- Public aggregate: `docs/astra/GOMYWAY_STEREO_ROLE_EVIDENCE_V1.json`. Private preregistration, native outputs, source-clock projections, role evidence and detailed score are durably stored in Library.
- Architectural consequence: **do not fold stereo to mono before role analysis**. Stereo spatial evidence should be attempted first and may cheaply resolve rhythm/lead roles; mono/high-correlation inputs must fall back to a general separator/role-inference path. Customer delivery remains false and main/Production are unchanged.

## Structure-grid precision filter — 2026-09-20

- Added `astra_backend/evaluation/filter_structure_grid.py`, a reference-blind fail-closed filter over the independently reviewed M1–15 timing map. It materializes the frozen straight-sixteenth grid and only rejects predictions farther than the existing inclusive 50ms scorer tolerance from every valid subdivision. It never changes MIDI/timing or adds events.
- Fixed the only local test issue before save: binary floating-point can represent a mathematical 50ms boundary microscopically above `0.05`, so the inclusive comparison uses a fixed `1e-9s` numerical epsilon without changing the musical tolerance. **7/7 focused tests pass** and branch CI includes them.
- Applied after reference-blind stereo role mapping + cross-channel duplicate resolution: predictions fall245→231 while **all84 correct-role TPs remain**. FP falls161→147; aggregate precision34.29%→36.36%; recall stays41.38%; F137.50%→38.71%. Rhythm F133.33%; lead F146.59%.
- Public aggregate: `docs/astra/GOMYWAY_STEREO_STRUCTURE_GRID_SCORE_V1.json`. Private filtered prediction hashes: rhythm `265bd933c01bc6ab2e17a87e3e851b1381fcbf40ffa4a4744a8e6158cbc2b073`, lead `694e7002c7d208459c153534bc3368d9fe67081d62027f99fc8fd096f6375a90`; score `c4a011dc3b27f88dc455fad10107ddad8e5051e1fb0942415571d7ba1de5447b`.

## Recurring-phrase confidence partition — 2026-09-20

- Added `astra_backend/evaluation/repeated_phrase_confidence.py`. A note event is recurring-core only when the same MIDI at the same within-measure structure slot appears in at least **3 distinct measures**. The confidence mode activates only if at least60% of the stream's reviewed-window events meet that recurrence condition; otherwise it abstains. One-off events are retained as `uncertain`, never silently deleted.
- Corrected the contract before scoring so out-of-window events are not required to carry reviewed-window grid metadata. **7/7 focused tests pass** and CI includes them.
- Prediction-only evidence activates strongly: rhythm recurring support67.42% across16 recurring keys; lead83.84% across14 keys.
- After frozen scoring, recurring core has172 predictions / **79 TP / 93 FP / 124 FN; precision45.93%, recall38.92%, F142.13%**. Rhythm precision44.94%; lead precision46.99%. The59-event uncertain bucket contains only5 TP and54 FP, supporting calibrated abstention instead of destructive pruning.
- Public aggregate: `docs/astra/GOMYWAY_STEREO_RECURRING_CONFIDENCE_V1.json`. Private partition hashes: rhythm `bfcc0544e6461eb189636ee89fe3446e313107cc9b70330b0d021cbc24e65cb7`, lead `ef5f95f08badd87689d9b5e4d7ec66533bd6840ea2c73f7427bc1f6e0147589d`, score `b83588c13b6bbd492cf543bb5fe125447356d98238a0c8dbacd4e487a4163ebe`.

## Role-resolved glide-continuity bend recovery — 2026-09-20

- Restored the exact frozen Python3.10.21 / Basic Pitch0.4.0 runtime and regenerated L/R first30 PCM solely to capture raw channel tensors. Frozen right-channel note events reproduced exactly; left reproduced all166 note pitches/times with only three <=1e-5 amplitude differences at the30s boundary outside the reviewed window. Left raw tensor SHA256 `41660cff543dd6f23bd2679eae911df050afb8329d98176ade4ee3a256969b4f`; right `cc0f57764feca8c43519be3e2a69ecc447806b5623d6921abef52f895f152cc4`.
- Running the already-frozen attacked-bend detector separately by stereo role still left too many slur/neighbor-transition candidates. Added `astra_backend/evaluation/refine_bend_glide_continuity.py`: reference-blind physical-continuity evidence requires at least8 active contour frames,4 distinct contour bins, no >1-semitone frame jump and >=90% nondecreasing contour movement across35–240ms. Active contour floor is0.15. No target MIDI, measure number or reference label enters the rule.
- **5/5 focused synthetic tests pass** and CI includes them. Frozen V3 output hashes: left `dea072a9db104a070cc2ab9b0d3e36fa04256973e6b1eed0c9ed2846e606eabe`; right `131541574a0a97784b2dbbef92e21afd52f4d0cbd5232073598d75e2b373f01c`.
- Left/rhythm V3 shrinks42 V2 candidates to8 total /7 in the reviewed window while retaining **5/14 exact reviewed attacked-bend starts**. Diagnostic exact precision becomes71.43%, recall35.71%, F147.62%; timing-only precision85.71%, recall42.86%, F157.14%.
- Applying the **already frozen** recurring-confidence rule to V3 retains6 role-supported recurring bend candidates and abstains on the lone nonrecurring +1-semitone candidate. Private bend partition SHA256 `71acd3f198adc3072a9256de59dbb0515205a003bbfe6e38e450e30eeecaa3a7`.
- Merging only those recurring stereo-rhythm bends into the recurring rhythm core restores the five TPs that recurrence-only confidence had withheld for just one additional FP. Rhythm becomes95 predictions /45 TP /50 FP /81 FN; precision47.37%, recall35.71%, F140.72%. Lead recurring core remains83 /39 TP /44 FP /38 FN; F148.75%.
- **Best balanced development state so far:**178 predictions against203 rhythm+lead targets -> **84 TP / 94 FP / 119 FN; precision47.19%, recall41.38%, F144.09%**. Relative to raw stereo role streams, TP is preserved at84 while FP drops161→94. Relative to recurring core without bend recovery, TP rises79→84 for only one added FP.
- Public aggregate: `docs/astra/GOMYWAY_STEREO_CORE_PLUS_BENDS_V1.json`. Private rhythm merged prediction SHA256 `4f2f06dd19c4c5bd1a40bb6b5b7d1e6b1dcd4e57c17d64081e80d4d321102659`; private combined score SHA256 `4a652749f3ac873ea57fbebc243fb655b1515fc8abe0659f6da62ffd4adc3481`.
- The current Library uploader returned `container_session_expired` when asked to persist the newest structure/repetition/bend private outputs. The exact hashes, deterministic code, frozen source artifacts and public aggregate receipts are committed; do **not** claim those newest private files are Library-persisted until an upload succeeds. Older source predictions/labels/alignment remain durably in Library.
- Customer delivery remains false; this is exposed development material. No main/Production change.

## Remaining-error attribution + raw-onset bottleneck — 2026-09-21

- Froze a post-score diagnostic of the previous84TP/94FP/119FN high-confidence stereo core. Private attribution SHA256 `def27b6cb5da8359a21023408b8a19ed368372521fa1a1cd1cea210753d537ed`; public aggregate `docs/astra/GOMYWAY_STEREO_CORE_ERROR_ATTRIBUTION_V1.json`.
- Of119 FNs: **5** are exact decoded events held in the uncertainty bucket, **14** are exact events in the opposite spatial channel, **47** have decoded onset evidence near the target but wrong pitch, and **53** have no final decoded onset in either channel. Rhythm FN technique flags include9 remaining reviewed attacked-bend starts and12 legato-slur attacks.
- Of94 FPs: **71** have no reviewed target nearby,16 are wrong-pitch events near a reviewed target, and7 exactly match an opposite-role target. This confirms both spurious-event and pitch/role leakage remain material.
- Raw tensor follow-up on the53 apparently missing decoded onsets found **32/53 already exceed Basic Pitch's unchanged0.5 neural onset threshold at the correct target pitch**, another13 lie in0.3–0.5, and only8 are below0.3. Private raw-onset diagnostic SHA256 `73b498f4d99e307439dadbc391be7aad81b57f79c2bdfe422395e8a5974d0faf`.
- Interpretation: Basic Pitch's final note decoder/frame-sustain requirements discard substantial usable attack evidence. The next recovery experiment therefore used structure to supply pitch identity and the unchanged neural onset threshold to supply independent acoustic attack evidence, rather than globally lowering thresholds.

## Recurring raw-onset gap recovery — 2026-09-21

- Added `astra_backend/evaluation/recover_recurring_raw_onsets.py`. It can propose a missing event only for a role/MIDI/within-measure key already observed in at least3 distinct measures by the frozen recurring-confidence layer. It fills **internal gaps only** between first/last observed support; it never extrapolates leading/trailing measures and never invents a new pitch.
- For a gap, an existing decoded same-MIDI event is preferred. Otherwise the correct stereo role channel must contain a local raw onset peak at the same MIDI within50ms of the independently frozen structure slot and the peak must meet Basic Pitch's unchanged **0.5 onset threshold**. The recovered event retains its acoustic onset rather than snapping to the grid.
- **6/6 synthetic tests pass locally** and the branch CI suite includes them. Proposal generation was completed and hashed before reviewed labels were scored.
- Frozen proposal hashes: rhythm `7670e2fc8d0b3656238d88e3914ff6766bef835427e2e306997ef6f1774fe28d` with44 proposals; lead `8c2d7c7658c68042a0cc7c673d4cc58d8638d88d08cd09edaea9aabc4adf6c9e` with21. After scoring,26 rhythm +8 lead proposals are exact TPs: **34/65 recovered events are correct**.
- New role scores: rhythm139 predictions / **71 TP /68 FP /55 FN; precision51.08%, recall56.35%, F153.58%**. Lead104 / **47 TP /57 FP /30 FN; precision45.19%, recall61.04%, F151.93%**.
- **New best aggregate development state:**243 predictions /203 targets -> **118 TP /125 FP /85 FN; precision48.56%, recall58.13%, F152.91%**. Relative to the prior high-confidence core, TP rises84→118 and FN falls119→85 while precision also rises47.19%→48.56%.
- Private score SHA256 `3f67b633419c01f06d02c1c9c2b1c2de4dfca4506f387fda7eaf8d72a7d706a5`; public aggregate `docs/astra/GOMYWAY_RECURRING_RAW_ONSET_RECOVERY_V1.json`. This is the first role-aware development configuration above50% F1.
- No global onset/frame threshold was lowered. This remains exposed development material and customer delivery remains false.

## Branch CI dependency correction — 2026-09-21

- The lightweight branch CI initially failed only when importing the new NumPy-based glide unit test; the preceding68 focused tests passed. The workflow now installs pinned `numpy==1.26.4 --no-deps` solely for activation-array unit tests before the focused suite.
- This changes the old statement that the focused CI installs no runtime package: it now installs exactly one already-frozen numerical test dependency. It still installs no Basic Pitch, TFLite, Torch, separator/model weights, opens no audio, runs no inference and performs no Production action.

## Post-52.91% rejected development experiments — 2026-09-21

- Tested an additional Basic Pitch frame-support gate on the frozen recurring raw-onset recoveries using the unchanged 0.3 frame threshold across the existing minimum-note window. It removed six recoveries but lost three TPs; aggregate F1 fell from52.91% to52.27%. Rejected.
- Tested a 0.3–0.5 onset supplement that required the same pitch to also meet the unchanged0.3 frame threshold. Frozen proposals added27 events but only3 became TPs; aggregate F1 fell to51.27%. Rejected. The winning recovery remains the unchanged0.5 onset path.
- Tested spatial own-channel dominance on recovered events. Precision rose slightly but four TPs were lost and aggregate F1 fell to52.78%. Rejected.
- Tested a majority-density recurrence gate. It over-pruned legitimate rhythm recoveries and reduced aggregate F1 to49.05%. Rejected.
- Tested simple and polyphonic recurring-slot pitch-substitution rules. Both abstained with **zero real substitutions**, showing the residual wrong-pitch class is not a simple one-extra/one-missing recurring-slot mismatch. No score change.
- Tested hidden chord-tone completion from cross-measure raw onset/frame consensus plus Astra playable-shape ranking. The frozen stress test proposed126 additions but recovered only3 TPs and collapsed F1 to42.98%. Rejected decisively.
- Astra's existing playable-shape diagnostic found **0 physically impossible onset groups** in the recovered role streams. Remaining FPs are plausible guitar events, not obviously impossible fretboard geometry.
- Conclusion: stop song-specific metric chasing on Gomyway. The52.91% baseline is the current development winner. The remaining bottleneck requires a stronger/general event-pitch model or broader cross-song evidence, not additional threshold tuning on this exposed song.

## Role-evidence integration into Astra — 2026-09-21

- Extended `astra_backend/noteEvidenceAdapter.mjs` with optional explicit evidence-state provenance while preserving legacy behavior. Supported states: `promoted-core`, `promoted-technique`, `recovered-recurring-onset`, `ambiguous`, `unassigned`, and `rejected`.
- Evidence states must agree with the existing classification contract: promoted states require `unambiguous`; `ambiguous` requires ambiguous classification; `unassigned` requires no-candidate; rejected requires rejected. Legacy inputs without a state remain valid and are reported as `unspecified`.
- Added `astra_backend/roleEvidenceIntegrationAdapter.mjs`. It converts explicit role-evidence streams into the existing structure-conditioned note-evidence contract, preserves structure identity/slot checks, and always returns `customerDeliveryEligible:false`.
- The adapter **fails closed** if role evidence has abstained but any promoted stream is supplied (`ABSTAINED_ROLE_EVIDENCE_CANNOT_PROMOTE`). Ambiguous/unassigned evidence can still be preserved for diagnostics.
- Added synthetic tests covering core/technique/recovery provenance, unresolved evidence preservation, abstention, duplicate IDs, lead/rhythm guitar mapping, bass mapping and determinism. The adapter also passes through `noteEvidenceEvaluator`; unresolved polyphony/pitch/duration evidence remains rejected for complete-tab acceptance, and role abstention surfaces as `ROLE_RELEVANCE_UNRESOLVED`.
- Extended `noteEvidenceDiagnostics.mjs` to report evidence-state counts descriptively. No composite score or hidden acceptance metric was added.
- Architecture note: `docs/astra/ROLE_EVIDENCE_INTEGRATION_V1.md`.
- Integration commits through `ab7d87248e03b63ab75ad3b8d0ef72a06bf61597`. Final branch verification: **215/215 Node tests passed**, **78/78 focused Python evaluation tests passed**, and the browser export script syntax/immutability checks passed. Node test-output SHA256 `5ba6eeb62fa6f861bf0be02d3cb21171e234d0c5865ad97384a73d728a66c390`; focused evaluation output SHA256 `0bba37d84c05ace9e0ec08b078456438ad94642f51c80e89a108fe56f13528e0`.
- This integration changes no Gomyway metric. The authoritative exposed-development best remains **118 TP /125 FP /85 FN; precision48.56%, recall58.13%, F152.91%**.
- No main/Production change and no customer-delivery authority granted.

## Deterministic pipeline + frontend analysis integration — 2026-09-21

- Added `astra_backend/roleEvidencePipelineAdapter.mjs`. It composes role evidence -> `noteEvidenceAdapter` -> `noteEvidenceEvaluator` -> `noteEventExposure` -> deterministic tab pipeline. The deterministic tab engine runs **only** when the existing evidence evaluator accepts the evidence and complete-tab-eligible events exist.
- The wrapper preserves source evidence IDs/states in a separate `eventEvidence` mapping while leaving the deterministic tablature engine itself unchanged. Ambiguous/unassigned evidence cannot enter deterministic events. Role abstention cannot promote anything. The wrapper always reports `customerDeliveryEligible:false`.
- Added synthetic coverage proving a fully resolved role stream reaches deterministic tablature with `promoted-core`, `promoted-technique`, and `recovered-recurring-onset` provenance intact; ambiguous, unassigned and abstained evidence stop before tablature; role mismatch fails before execution; output is deterministic.
- Added `astra_backend/roleEvidenceAnalysisAdapter.mjs` to bridge the role-evidence pipeline into the existing frontend-shaped Astra analyzer result. A resolved synthetic tab can produce generated text/events, but the bridge intentionally supplies **no delivery policy**, so overall status remains partial and `renderEvents` stay empty/customer delivery false.
- Frontend-shaped synthetic fixtures verify: complete role evidence -> partial-but-informative analyzer result with policy blocker; ambiguous evidence -> no deterministic/frontend events; role abstention -> overall `abstained` with no invented tab; request/pipeline role mismatch -> fail closed.
- Final integration verification on commit `ab7d87248e03b63ab75ad3b8d0ef72a06bf61597`: **215 Node tests passed, 0 failed; 78 focused evaluation tests passed, 0 failed; browser export checks passed**.
- This closes the current architecture milestone: the successful stereo/structure/repetition/technique/recovery evidence can now flow through Astra's real contracts without bypassing acceptance or delivery gates. No main/Production change.

## Second-song inventory + stronger note-inference pivot — 2026-09-21

- Added `docs/astra/SECOND_SONG_DEVELOPMENT_INVENTORY_V1.md`. Current repository/Library inventory does **not** contain an adequate second song with both audio and independent note-level onset+MIDI truth.
- `public/Stairway to Heaven AI test.m4a` exists, but the archived `analyzer/fixtures/stairway_intro_reference.json` has an empty `notes` array and only phrase/chord-position truth. It is useful later for fingering/path regression, **not** for note-event precision/recall or validating the52.91% Gomyway recovery rules.
- Therefore the52.91% Gomyway result remains exposed development evidence only. No additional Gomyway threshold/rule tuning is authorized for broader quality claims.
- Added `astra_backend/noteInferenceCandidateRegistry.mjs`, tests, and `docs/astra/NOTE_INFERENCE_CANDIDATE_INVENTORY_V1.md`.
- Primary next guitar note-inference candidate: **DAFx-24 GuitarProFX-augmented TabCNN**. Pinned source repository `robust-guitar-tabs/code` at revision `f50309ad06dc734ddae5e3a0eda756fca221e2e7`.
- Official published checkpoint metadata identified at Zenodo record `11406378`: file `best_TabCNN_tablature_trancription_model`,3,345,122 bytes, published MD5 `ce168b2cd426f81a2a78499214e40605`, record license metadata CC-BY-4.0. Astra has **not** downloaded the checkpoint and has not computed its own SHA-256.
- Secondary candidate: **MR-MT3**, source `gudgud96/MR-MT3` revision `826ea84a933f93cd707d11e91af711f1d19c8d79`, MIT code. Candidate checkpoint identity is frozen in the registry, but no bytes were downloaded or executed.
- Added `docs/astra/TABCNN_GUITARPROFX_SOURCE_REVIEW_V1.md`. Exact source preprocessing semantics are now pinned:22,050 Hz mono input; RMS normalization;512-sample hop;192-bin CQT;24 bins/octave; C1 minimum; gamma0; amplitude-to-dB with ref=max then `/80 + 1`;9-frame TabCNN context;19-fret guitar profile; grouped-softmax fret/none classification per string.
- The official inference source has a CPU path when `gpu_id < 0`, but Astra has not measured latency or memory.
- Critical reproducibility blocker: the source dependency declarations are lower-bounded rather than exact, and the VQT source itself warns that librosa conventions changed. Exact runtime versions and numerical preprocessing reproduction must be frozen before model execution.
- TabCNN is **generic guitar** note/tablature inference. It does not establish lead-versus-rhythm identity; Astra's existing role-evidence/abstention layer remains authoritative for that distinction.
- No main/Production change and no customer-delivery authority granted.

## TabCNN fail-closed development preflight implemented — 2026-09-21

- Added `astra_backend/tabcnnPreflight.mjs` at commit `2488da44b399a49c4760d345fe1b810f0c3ab144` and focused tests at `87b8e90857dbdc7962765723cd5c8c72aef0e639`.
- The preflight is **static and no-action**: it invokes no model, downloads no artifact, opens no audio, performs no network access, mutates no Production state, and never grants customer delivery.
- It pins the reviewed TabCNN source revision/blobs and exact preprocessing identity:22,050 Hz mono/RMS input,512-sample hop,192 CQT bins,24 bins/octave, C1 fmin, gamma0, dB/ref=max with `/80 + 1`,9-frame context and19-fret guitar profile.
- It can only return `developmentExecutionReady:true` when every blocker is explicitly cleared: official Zenodo identity matches, official-source download occurred, published MD5 matches, Astra SHA-256 exists, exact dependency lock/hash exists, exact package versions are frozen, preprocessing numerical-reproduction receipt exists, CPU smoke receipt exists, wall time <=1200s, peak memory <=4096MB, checkpoint-license review is complete, training-data commercial-rights review is complete, and development use is authorized.
- Synthetic tests prove: empty evidence fails closed; all synthetic receipts can clear **development execution only**; source/preprocessing drift blocks; MD5 alone is insufficient without official-source download + Astra SHA-256; CPU budget overruns block; missing preprocessing receipt blocks; rights checks are independently required; expected identity reads are deterministic/defensive.
- Current branch HEAD at checkpoint save: `87b8e90857dbdc7962765723cd5c8c72aef0e639`.
- **No TabCNN checkpoint has been downloaded or executed.** Customer delivery remains false.

## TabCNN official artifact identity frozen — 2026-09-21

- Verified the preflight gate commit `87b8e90857dbdc7962765723cd5c8c72aef0e639`: GitHub Actions run `35556466333` completed successfully.
- Added a dedicated branch-only identity workflow, `.github/workflows/tabcnn-artifact-identity.yml`. It downloads only the exact official Zenodo checkpoint, computes size/MD5/SHA-256, performs no import/inference/audio access, deletes the temporary bytes, has read-only repository permissions, and does not persist the model artifact.
- Official Zenodo record `11406378` identifies file `best_TabCNN_tablature_trancription_model`; published MD5 `ce168b2cd426f81a2a78499214e40605`. The official record also states that the best-performing GuitarProFX TabCNN weights are provided.
- First identity acquisition run `35558742279` succeeded from the official Zenodo URL: **3,345,122 bytes**, MD5 **`ce168b2cd426f81a2a78499214e40605`**, Astra SHA-256 **`1470a308896629352a811082843eb708cbc2f1aa3092757340055ef76a53ed0c`**. The temporary checkpoint was deleted and not committed/uploaded as an artifact.
- `docs/astra/TABCNN_ARTIFACT_RECEIPT_V1.json` freezes that evidence. Raw receipt SHA-256: **`611a34fb6c087e99ba0fbb552407b1facd9729c995886e3cf7c9fc92ff491283`**.
- Commit `9425ed25ccc3cac0349f4580a3f633bd90702a2b` pins the exact Astra SHA-256 in `tabcnnPreflight.mjs`, hardens the identity workflow to require it on future downloads, and adds a substitution regression test. A syntactically valid but different SHA-256 now fails closed with `OFFICIAL_ARTIFACT_SHA256_UNVERIFIED`.
- Verification on commit `9425ed25ccc3cac0349f4580a3f633bd90702a2b`: artifact identity run `35558828514` **PASS**; Astra backend run `35558828537` **232/232 Node tests passed**, **78/78 focused Python tests passed**. Node output SHA-256 **`79786a97dc6a4101707d946c80d8ca1877ea4cafdf4065f3d1a869e7c29f2e83`**; focused evaluation output SHA-256 **`ca44d6ec178213c755ca2b7f5ea3bfb7d11821587dcca4ad435d71254e3fe2a1`**.
- This clears only official checkpoint byte identity. **TabCNN has not been imported or executed.** Development execution remains blocked on exact inference runtime, numerical preprocessing reproduction, CPU smoke/budget evidence, checkpoint/training-data rights review and explicit development authorization. Customer delivery remains false.

## TabCNN runtime, preprocessing and legacy compatibility frozen — 2026-09-21

- The minimal Linux CPU runtime is now frozen under Python **3.10.15** with exact package versions in `astra_backend/tabcnn_runtime/requirements.lock.txt`.
- Dependency lock SHA-256: **`0e711709b063a705ad11570f6b7ef4dfe5bcc2d433d98707a1a74897dbb25bc0`**.
- Binary/wheel identity manifest SHA-256: **`0796acee36cea76e9784e602da190223a14a89907381882b401986763c371567`**.
- Frozen core runtime: NumPy **1.21.6**, SciPy **1.8.1**, librosa **0.9.1**, PyTorch **1.11.0+cpu**, Numba **0.55.2**, llvmlite **0.38.1**. The lock also freezes every resolved transitive package.
- `docs/astra/TABCNN_PREPROCESSING_RECEIPT_V1.json` freezes the deterministic synthetic-audio reproduction contract. Astra independently mirrors the pinned upstream 22,050 Hz/RMS -> 192-bin CQT/24 bins per octave -> dB `/80 + 1` -> 9-frame window path.
- A second GitHub runner exposed a least-significant-bit FFT/CQT byte difference while Astra and the pinned upstream implementation still matched **exactly within that run**. The gate was corrected: raw CQT/window byte hashes are diagnostic only; portable acceptance now requires frozen source/runtime identities, exact waveform identity, exact shapes/dtypes/ranges, and same-run Astra-vs-upstream max absolute difference <= **1e-7**.
- Runtime workflow `35560657208` passed the corrected portable preprocessing gate.
- Static checkpoint inspection proved the verified official artifact is a Torch ZIP with a **protocol-2 pickle**. The pickle references exactly three `amt_tools` classes: `amt_tools.models.tabcnn.TabCNN`, `amt_tools.models.common.SoftmaxGroups`, and `amt_tools.tools.instrument.GuitarProfile`.
- `docs/astra/TABCNN_STATIC_CHECKPOINT_INSPECTION_V1.json` freezes the static archive/pickle receipt, SHA-256 **`72ecf7e106bc69ce7ef4aa66888cb544535615ad3a9c8a6246bb09a460da3971`**.
- The frozen runtime can import those exact three class paths from the exact pinned upstream blobs **without opening or unpickling the checkpoint**.
- `docs/astra/TABCNN_LEGACY_IMPORT_SURFACE_V1.json` freezes that import-surface receipt, SHA-256 **`b9d795cd0ddfb7e070cba24e57e62a7c8d3723c2dad0b853f69c8efc36662805`**.
- Final verification on commit `f9dd12df9ac68fb1fa7532569c50363837550d5f`: Astra backend run `35560826986` **237/237 Node tests passed** and **78/78 focused Python tests passed**; Node output SHA-256 **`8d69c1345da22c0ccc037b53f30e74d6780e571d2fc7fbf0facaf96acdca3190`**; focused evaluation output SHA-256 **`1b05d9396e990414cfeadd891c37d1ce399527be450faa519ae353de4cc63f5d`**. Runtime preflight run `35560827097` **PASS**.
- **No checkpoint deserialization, model forward pass, Gomyway evaluation or customer execution occurred.**

## TabCNN rights/provenance review — execution remains blocked

- Added `docs/astra/TABCNN_RIGHTS_PROVENANCE_REVIEW_V1.md`.
- The released robust-guitar-tabs code is CC0 and the Zenodo checkpoint record publishes the checkpoint under CC-BY-4.0 metadata.
- The DAFx-24 training lineage nevertheless includes **DadaGP-derived GuitarPro performances** plus GuitarSet/EGFxSet-related material.
- DadaGP's own repository says dataset access is requested **for research purposes**. Its MIT repository license applies to the software and does not establish a commercial license for the separate score corpus.
- Public GuitarSet metadata is inconsistent enough that Astra does not choose a permissive interpretation by convenience; third-party mirrors report CC-BY-4.0 while OpenAIRE/DataCite indexing reports CC-BY-NC for the Zenodo record lineage.
- Therefore `trainingDataCommercialRightsCleared` is a separate fail-closed preflight requirement. A completed review does **not** mean the lineage is commercially cleared.
- Candidate blocker is now explicit: `TRAINING_DATA_COMMERCIAL_RIGHTS_UNRESOLVED`. Checkpoint deserialization remains unauthorized.
- Customer delivery remains false.

## Rights-clean Guitar-TECHS candidate registered — 2026-09-21

- Commit `3fac5cad04c44e08c2fbdb3282111804b4457e1d` registers `astra_guitartechs_tabcnn_v1` as the primary next guitar note-inference candidate.
- Architecture family is TabCNN-compatible six-string fret-state output, but initialization is **random only**. The blocked GuitarProFX checkpoint may not be deserialized, used for initialization, distillation or hidden teacher labels.
- Guitar-TECHS is treated as generic-guitar evidence only; Astra role evidence remains authoritative for lead-versus-rhythm identity. Bass remains out of scope for this candidate.
- Performer-disjoint design is fixed: P1 train -> P2 validate and P2 train -> P1 validate; only after development choices freeze may a final model fit P1+P2. P3 is a sealed final source-disjoint generalization gate.
- All capture channels from the same underlying performance must remain in the same split. Random clip/channel splitting is forbidden.
- Verification on `3fac5cad04c44e08c2fbdb3282111804b4457e1d`: **243/243 Node tests passed**, **78/78 focused Python tests passed**. Node output SHA-256 `279667d9a4198e4dddbd4f3504ee72a8a4d1de61a755a8d7d8664c1ee178be5d`; focused evaluation output SHA-256 `59bbead0bd8d34a61e0a846eb0957262479f96aa5e909b2980a7f08366e0926a`.

## Guitar-TECHS published identity + split contract frozen — 2026-09-21

- Added metadata-only workflow `.github/workflows/guitar-techs-metadata-identity.yml` at `8c5822dd4f7d3b94d72214db967d23fb7469c310`. Workflow run `35561191581` passed.
- The workflow made **HEAD requests only** to the nine official Zenodo archives. No training audio/MIDI archive body was downloaded or opened.
- Official project-owned website identity is pinned to repository `guitar-techs/guitar-techs.github.io`, commit `19a2954f789bfd192b2b4732788ceb000c1dd687`, `index.html` blob `64627b4fb227cd0e29cff05926f02fe0e12b5f26`. That exact blob states that all data is licensed under **CC BY 4.0**.
- `docs/astra/GUITARTECHS_DATASET_MANIFEST_V1.json` freezes record `https://zenodo.org/records/14963133`, version `v1`, exact published archive byte counts and published MD5s for all nine archives. Total published bytes: **4,133,550,356**. Manifest SHA-256: **`a3445d799c4a0b17a0078dac0c9387a0e676111367a5f07d608fd55bd8118e52`**.
- Exact archives:
  - P1 chords 981,741,162 bytes / MD5 `be9ef8bbdceb1912d565254e607a6d94`
  - P1 scales 453,349,723 / `9c0b98e8fb42a522df727ea8bf545e4f`
  - P1 single notes 108,626,613 / `ca0c4674dde3805574685a313f7c39eb`
  - P1 techniques 326,280,863 / `18634a41a6db5a8de10d07eb3122a872`
  - P2 chords 1,150,819,056 / `eb6f74dd19162237189281688ad7ad2e`
  - P2 scales 471,254,783 / `96664853872f51e5f8aa4447313b7cf5`
  - P2 single notes 116,133,457 / `40fbf03d8b04bb2cf42df20f36dc2254`
  - P2 techniques 395,839,610 / `f4189251ce50be25f06a173b2c2bba00`
  - sealed P3 music 129,505,089 / `071ba80aecf00f4a31fbd167b3f22198`
- `docs/astra/GUITARTECHS_SPLIT_RECEIPT_V1.json` freezes the non-random performer-disjoint split and sealed P3 rule. Receipt SHA-256: **`d116556c13d250af28900bb1d73d2c0ccd3130246db8bdd2d6d387ac87be799a`**.
- Added `guitarTechsDatasetIdentity.mjs` with fail-closed substitution tests. Record/version/license/archive/split drift is rejected.
- Important distinction: published size+MD5 identity is frozen, but **Astra SHA-256s are not yet acquired** because media bodies have not been downloaded. Blocker is now `DATASET_ASTRA_SHA256_NOT_FROZEN`, not the older vague published-identity blocker.
- Extracted performance grouping is also not yet verified because archives have not been opened. P3 remains sealed.
- Verification on `e29ec07e6e773cdc6d29d9736a007c0d6feea1fe`: **247/247 Node tests passed**, **78/78 focused Python tests passed**. Node output SHA-256 **`cc2e92438bd1716ddbde76a1663ab7be5bdb126754e65ce90ed5ee336916b555`**; focused evaluation output SHA-256 **`4790f8cba9f8c973c899b5774c5942ec961ffb6d3542cf21df8dd09a98d9218d`**.
- No model was trained or executed; no main/Production/customer-delivery authority changed.

## Guitar-TECHS label, alignment and bounded training contract frozen — 2026-09-21

- Commit `989d438459f43b4217e8500f430eb05017fbe2f0` adds `docs/astra/GUITARTECHS_LABEL_ALIGNMENT_TRAINING_CONTRACT_V1.json` and companion review markdown.
- Contract receipt SHA-256: **`09436268922e0d24332b7e3234225d54a0f28e58e23b55ea71227eeab1b1e81f`**.
- Pinned TabCNN semantics were checked directly from source revision `f50309ad06dc734ddae5e3a0eda756fca221e2e7`:
  - six independent string groups;
  - frets **0–19** are softmax classes **0–19**;
  - tablature silence state is **-1**, mapped by `SoftmaxGroups.get_loss()` to final class **20**;
  - **21 classes/string, 126 logits total**.
- Added `guitarTechsLabelContract.mjs`. It refuses to infer frets without an explicit verified six-track string map and tuning. Standard EADGBE is **not** assumed from the upstream source model. Missing tuning, out-of-range frets and same-string polyphony abstain/mask rather than clip or relabel as silence.
- V1 primary training content is limited to content with stable fret truth once filenames/layout are verified: chords, scales, ordinary single notes and palm mute. Vibrato, pinch harmonics, natural harmonics and bendings remain auxiliary/held-out until their actual MIDI/pitch-bend semantics are inspected.
- Alignment policy is frozen without media access:
  - P1/P2 development material only; P3 cannot influence alignment;
  - search lag **-100..+100 ms** at 1 ms steps;
  - minimum 30 MIDI onset groups;
  - require >=80% matched within 20 ms after correction;
  - median absolute residual <=10 ms;
  - five deterministic strata/bootstrap estimates with lag MAD <=5 ms;
  - never apply >100 ms correction;
  - otherwise exclude the recording group and abstain.
- Initial training contract follows the pinned research training path where appropriate: random initialization, Adadelta, learning rate **1.0**, batch **32**, maximum **2,500 iterations/fold**, 50 validation checkpoints. Astra seed is **20260921**.
- Training runtime identity reuses the already frozen Python 3.10.15 / PyTorch 1.11.0+cpu lock and wheel manifest. Paid compute and real training remain unauthorized.
- Development metrics schema is frozen: onset+string+fret precision/recall/F1, note-event completeness, frame string+fret accuracy, abstention, per-content-class results and cross-performer consistency. Frame accuracy alone is explicitly insufficient.
- Numeric development acceptance thresholds remain intentionally unfrozen until P1/P2 baselines exist. P3 opening remains unauthorized.
- Verification: GitHub Actions run `35561654060` **PASS**; **256/256 Node tests passed**, **78/78 focused Python tests passed**. Node output SHA-256 **`1994796f76cf776d2331e983b94a15e1e1f650079ef192e2d8ecd4866e8a401b`**; focused evaluation output SHA-256 **`4bcd91c580b06cf0e87e63eac172d0db2fbbea0a317852327ef1070020f578af`**.
- No Guitar-TECHS archive body was downloaded/opened and no model was trained or executed on real data.

## Guitar-TECHS synthetic training-path smoke passed — 2026-09-21

- Commit `f1110dcc9f6b0184b831a5574b9cc215ae853fd6` added a deterministic CPU backward/optimizer smoke using the exact frozen Python 3.10.15 / PyTorch 1.11.0+cpu runtime and exact pinned TabCNN source blobs.
- The smoke used **random initialization only**. It loaded no published GuitarProFX checkpoint and opened no Guitar-TECHS media.
- GitHub Actions run `35561780492` **PASS**:
  - seed `20260921`;
  - batch 32;
  - one 192 x 9 synthetic feature window per sample;
  - six strings x 21 classes = **126 logits**;
  - Adadelta learning rate 1.0;
  - loss **18.26586151123047**;
  - finite gradient norm **1.2271532566034684** across 10 gradient tensors;
  - model state changed from SHA-256 `cb8b060ea57c9b5c16d64bfba1cc3479f4a8cad1263062fcc0736f10f6f19529` to `e67706628b4f24a38879c5ee483a73cb67f24d1762d3cd6d6fe9abbca431976d`;
  - repeated in-process runs were deterministic;
  - observed wall time **0.194629882 s**;
  - peak RSS **357.9375 MB**, below the 2,048 MB smoke budget.
- Frozen receipt: `docs/astra/GUITARTECHS_SYNTHETIC_TRAINING_SMOKE_V1.json`, SHA-256 **`ffb9c4178fe28683e2020083df96678a74e9a66413bb26d52aa5c01d07e49b9d`**.
- Candidate `astra_guitartechs_tabcnn_v1` now records `syntheticTrainingSmokePassed:true`; blocker `SYNTHETIC_TRAINING_SMOKE_PENDING` is removed.
- This does **not** authorize real dataset download, real training, P3 access, main/Production change or customer delivery.

## Guitar-TECHS P1/P2 development acquisition gate frozen — 2026-09-21

- Added `docs/astra/GUITARTECHS_DEVELOPMENT_ACQUISITION_CONTRACT_V1.json`, SHA-256 **`0d8ceae4938cc79b658498a74021a132358683a60f48d09358fcbe935a7bc02c`**.
- Added `astra_backend/guitarTechsDevelopmentAcquisition.mjs` and focused tests.
- The gate is deliberately **no-action**: it downloads, opens and extracts no media; trains no model; opens no P3 data; grants no customer delivery.
- Only the exact eight P1/P2 archives from the frozen Guitar-TECHS manifest are eligible for an acquisition plan. Staged exact subsets are supported so the ~4.004 GB development corpus can be acquired deliberately rather than as an uncontrolled all-or-nothing action.
- Every requested archive must match exact file name, performer/category, published byte count and MD5.
- Acquisition planning requires both `developmentMediaAcquisitionAuthorized:true` and exact authorization scope `guitar-techs-p1-p2-development-media-v1`.
- `P3_music.zip` is categorically rejected with `GUITAR_TECHS_P3_SEALED` even if an authorization flag is supplied.
- Duplicate, unknown and substituted archive identities fail closed.
- After a future authorized download, Astra SHA-256 must be computed **before extraction**; extracted grouping/string-map/tuning receipts remain mandatory before alignment or training.
- Candidate registry now records the acquisition contract as frozen but `developmentMediaAcquisitionAuthorized:false`; blocker `DEVELOPMENT_MEDIA_ACQUISITION_NOT_AUTHORIZED` is explicit.
- No Guitar-TECHS media body was downloaded or opened in this milestone.
- Verification on commit `cd220e3a49af20fdd90f372b905643a531290e24`: GitHub Actions run `35562034522` **PASS**; **265/265 Node tests passed**, **78/78 focused Python tests passed**. Node output SHA-256 **`bd464b272d4967afa9c8a212274aca799ea32eaec66d77a22680e521f4a83631`**; focused evaluation output SHA-256 **`c3e9b24273bfcb1986f324625128c41357acace18e840f74fa7d9f0446e3b313`**.
- Receipt bookkeeping corrected before handoff: SHA-256 **`0d8ceae4938cc79b658498a74021a132358683a60f48d09358fcbe935a7bc02c`** is the digest of the exact committed JSON bytes; the earlier pre-serialization draft digest is not authoritative.

## Guitar-TECHS P1/P2 byte identity acquisition complete — 2026-09-21

- User authorization scope remained `guitar-techs-p1-p2-development-media-v1`; P3 and real training remained unauthorized.
- Authorization commit: `104aaea644dfb25aec7f5ace1d5b3efe00c48896`.
- Branch-only identity workflow run `35562765028`: **PASS**, all eight P1/P2 matrix jobs completed successfully.
- Every archive matched its frozen published file name, byte count and MD5 before Astra SHA-256 was computed. Each archive was then deleted without extraction.
- Frozen combined receipt: `docs/astra/GUITARTECHS_DEVELOPMENT_ARCHIVE_IDENTITY_V1.json`; receipt SHA-256 **`b6a4a577d7a447f4073dba85e6f3a4de7236544a6ed79df20b7f25d49c8602ac`**.
- Astra SHA-256 identities:
  - P1 chords: `de4aa76ef4b86ce981496161b741dc39bd22dec5250da351e5e68a44da249326`
  - P1 scales: `79d7e9d148820867a9095697c9521e40a4b11c198384edfce1951de7219b3509`
  - P1 single notes: `130592ae5555476ea8e4070c0f3421794ef8b5e252dfa780745d07eedd0eb4a4`
  - P1 techniques: `1e4b80a464182d345e129f3e1158b6c05690c60b5f9be4bde3fb26f23263236e`
  - P2 chords: `9d4a46261cc840d6a66412ad0ebffcfba1fbce579bec0205127190b7bd7a4bce`
  - P2 scales: `d5efc7134764bd8124a712fd301d020d143a6e589eb8e1f2e0ddcbf94524ff17`
  - P2 single notes: `d6b54e40d22113d6c0a663165cb2af63735897a35bb45fc6d0ed49c944b548d9`
  - P2 techniques: `05fc065c010add9e5348095d7198fdc45b967c657e3e12ef8afdb74808371816`
- `guitarTechsDatasetIdentity.mjs` now validates the exact eight Astra SHA-256 values plus the exact receipt digest; a caller-provided boolean can no longer clear the SHA gate.
- Candidate registry now records acquisition authorization and identity completion. `DEVELOPMENT_MEDIA_ACQUISITION_NOT_AUTHORIZED` and `DATASET_ASTRA_SHA256_NOT_FROZEN` are cleared; media is not persisted and `TRAINING_MEDIA_NOT_ACQUIRED` remains until inventory-only extraction reacquires the verified P1/P2 bytes.
- `P3_music.zip` was not downloaded, opened, inspected or hashed by Astra. Real training did not run. Main/Production/customer-delivery behavior did not change.

## Exact next step — authorized inventory-only extraction

1. Reacquire only the same frozen eight P1/P2 archives under the existing authorization.
2. For every archive, re-verify published bytes + MD5 + the now-frozen Astra SHA-256 **before extraction**.
3. Extract for inventory only and freeze receipts for underlying-performance grouping, correlated capture-view grouping, exact six-string MIDI/track mapping, tuning evidence, and technique MIDI/pitch-bend semantics.
4. Keep `P3_music.zip` sealed and untouched.
5. Run the already-frozen alignment checks only after the extraction receipts exist.
6. Do **not** begin real model training without a separate explicit training authorization.
7. Keep `main`, Production and customer-delivery behavior unchanged.

## NEXT ACTION TO RESUME — explicit

**Proceed with inventory-only extraction of the verified P1/P2 development archives under the existing authorization; do not ask for acquisition authorization again.**

Re-verify every archive against the frozen byte count, MD5 and Astra SHA-256 before extracting it. P3 remains sealed and real training remains unauthorized.

## Guitar-TECHS inventory extraction probe started — 2026-09-21

- Identity-freeze commit `c3dbef4e7ed2d290ccea227f63a669272ac84fcf` passed GitHub Actions run `35563216204`: **265/265 Node tests passed**, **78/78 focused Python tests passed**. Node output SHA-256 `b1f11b2c75898296977f723accf0902784acfe439b882890496d4e67da10a033`; focused evaluation output SHA-256 `7648c12a60f894501b1d143be007ca9a186d9a0c5c0151a802c5d62786141306`.
- Inventory extraction is already authorized for P1/P2. To avoid guessing archive semantics, the first extraction step is a bounded probe of the smallest verified archive, `P1_singlenotes.zip`.
- The probe must re-verify exact bytes, published MD5 and frozen Astra SHA-256 `130592ae5555476ea8e4070c0f3421794ef8b5e252dfa780745d07eedd0eb4a4` before extraction.
- It may inspect directory/file layout, text metadata, WAV headers and MIDI structural metadata only. It performs no alignment, feature generation, model import or training.
- `P3_music.zip` remains sealed and is not referenced as a downloadable input.

## Guitar-TECHS inventory probe result — 2026-09-21

- Probe workflow run `35563338841` completed successfully on `P1_singlenotes.zip`. Frozen byte/MD5/SHA identities passed before extraction; the extracted media was deleted after inspection.
- Clean visible contents: 1 MIDI file, 2 WAV audio captures, 2 MP3 video captures. Resource forks/`.DS_Store` are ignored as packaging noise.
- Underlying performance key is consistently `allsinglenotes`; capture views are `directinput`, `micamp`, `ego`, and `exo`.
- The MIDI is format 1 / PPQ 960 with one conductor track plus six named string tracks: high-to-low `e`, `B`, `G`, `D`, `A`, `E`.
- P1 single-note track minima are 64, 59, 55, 50, 45, 40 respectively, providing direct dataset tuning evidence consistent with E2-A2-D3-G3-B3-E4; this is observed evidence, not an assumed default.
- No pitch-bend events occur in the P1 ordinary-single-note MIDI.
- Direct-input WAV: mono, 48 kHz, 24-bit, 552.0 s. Mic/amp WAV: mono, 48 kHz, 16-bit, approximately 552.00035 s. The shared performance stem supports grouping these as correlated capture views of one performance.
- No alignment, audio feature extraction, model import or training was performed. P3 was not opened.
- Added reusable `astra_backend/guitartechs_inventory/inspect_extracted.py` and branch-only full P1/P2 inventory workflow. The full matrix re-verifies bytes + MD5 + frozen Astra SHA-256 before each archive is extracted.

## P2 chords receipt recovery — 2026-09-21

- Full P1/P2 inventory workflow run `35563511409` completed the P2 chords inventory job successfully, but GitHub's per-job log backing blob returned `BlobNotFound` when the assistant attempted to collect that receipt.
- This is an evidence-retrieval failure, not an inventory-job failure.
- A one-archive recovery workflow re-runs only the already-authorized, already-hash-frozen `P2_chords.zip`, re-verifies bytes + MD5 + Astra SHA-256 before extraction, writes the inventory receipt to a small short-lived Actions artifact, deletes extracted media, and performs no alignment or training.
- P3 remains sealed.

## Guitar-TECHS P1/P2 inventory evidence frozen — 2026-09-21

- Full authorized inventory run `35563511409` completed **all eight** P1/P2 jobs successfully. Every archive was re-verified against frozen byte count, published MD5 and Astra SHA-256 before extraction; extracted media was deleted after inventory.
- P2-chords receipt recovery run `35563847021` also completed successfully after the original job-log backing blob was unavailable. Recovery artifact `10623565422` digest: `sha256:7e7cf64058903eed463f4e066b0896d0241022d0fae0f8d371e577618bb813f1`.
- Frozen combined receipt: `docs/astra/GUITARTECHS_DEVELOPMENT_INVENTORY_EVIDENCE_V1.json`; SHA-256 **`4d21d578a275587abe18d9f5382074fa9c33bd2f0698c5d10b340788de306bcd`**. Companion review: `docs/astra/GUITARTECHS_DEVELOPMENT_INVENTORY_REVIEW_V1.md`.
- Inventory covers **92 underlying performance groups**, 460 visible files and the four correlated capture families `directinput`, `micamp`, `ego`, `exo`. Every performance group has one MIDI file; all inspected MIDIs are format 1 / PPQ 960.
- String labels are explicit MIDI track names `e/B/G/D/A/E`. Single-note, scale and technique files use fixed indices 1–6, but chord files can omit unplayed strings and shift later track indices. **Chord string identity is now frozen as track-name-based, never positional.**
- P1 tuning is directly evidenced by single-note minima `64,59,55,50,45,40` -> E2-A2-D3-G3-B3-E4.
- P2 single-note minima are `64,59,55,51,45,40`; the D-string open MIDI 50 is not directly observed, and the reviewed official dataset page does not state tuning. Astra therefore keeps **`P2_D_STRING_TUNING_NOT_FULLY_VERIFIED`** as a fail-closed blocker instead of assuming D3.
- Technique semantics review found zero MIDI pitch-bend events in both performers' named technique MIDIs, including Bendings/Vibrato, while P2 scale MIDIs and two P2 chord MIDIs do contain pitch-bend events. Pitch-bend-controller presence is therefore **not** a trustworthy technique label. V1 primary note/fret content remains chords, scales, ordinary single notes and PalmMute; Bendings/Harmonics/PinchHarmonics/Vibrato remain auxiliary/held out.
- Added `astra_backend/guitarTechsInventoryEvidence.mjs` with fail-closed receipt/run/group/string-map/P3/alignment/training checks and focused tests.
- Candidate registry now clears `EXTRACTED_PERFORMANCE_GROUPING_NOT_VERIFIED` and the vague `TUNING_METADATA_NOT_FROZEN`; it records the inventory receipt and keeps the precise P2 D-string tuning blocker.
- No alignment, model import, real training, P3 access, main/Production change or customer-delivery authorization occurred.
- Verification on commit `23f92111f83595212aa92254c8e441321c1128cc`: GitHub Actions run `35565044068` **PASS**; **270/270 Node tests passed**, **78/78 focused Python tests passed**. Node output SHA-256 `f2b013d26a4949059eccc87bb65c8e3fe1b7dc11566111147fdea1c7eb324dab`; focused evaluation output SHA-256 `67253464b610a8b2f4120a193010b27dd34defc64aff76cb941a5d96442b0c6e`.

## P2 six-string tuning evidence frozen — 2026-09-21

- The P2 `allsinglenotes` inventory itself resolves the prior D-string gap without P3 or model inference.
- P1 establishes the shared six-track schema: each `e/B/G/D/A/E` track contains 23 consecutive chromatic positions spanning 22 semitones, with opens `64/59/55/50/45/40`.
- P2 matches P1 exactly on five strings and again has 23 consecutive positions. The P2 D track alone has 22 consecutive pitches `51..72`: relative to the same D-string sweep, **only MIDI 50 is missing**.
- Treating MIDI 51 as an alternate D# open would require the corresponding 22-fret endpoint MIDI 73, which is also absent and conflicts with the explicit `D` track identity and shared AllNotes schema.
- P2 tuning is therefore frozen as low-to-high `40,45,50,55,59,64` = **E2 A2 D3 G3 B3 E4**. The receipt explicitly distinguishes the structurally verified D3 open from a directly observed P2 MIDI-50 event.
- Frozen receipt: `docs/astra/GUITARTECHS_P2_TUNING_EVIDENCE_V1.json`; SHA-256 **`5474eaccdf651c637dc7b3b2145098fe050714b77542b843742ac2f645702715`**. Added `astra_backend/guitarTechsTuningEvidence.mjs` and fail-closed substitution tests.
- Candidate registry now clears `P2_D_STRING_TUNING_NOT_FULLY_VERIFIED` while retaining alignment, metric-threshold, training, P3, role-evidence and customer-delivery blockers.
- No alignment, model import, training, P3 access or Production/customer action occurred.

## Exact next step — run frozen P1/P2 alignment checks

1. Reacquire only the frozen P1/P2 development archives needed for the alignment run under the existing development-media authorization; re-verify bytes + MD5 + Astra SHA-256 before extraction.
2. Run only the frozen alignment policy: lag -100..+100 ms at 1 ms steps, minimum 30 MIDI onset groups, >=80% within 20 ms after correction, median absolute residual <=10 ms, five deterministic strata/bootstrap lag estimates with MAD <=5 ms, and never apply >100 ms correction.
3. Exclude/abstain any recording group that fails the frozen alignment gate; do not tune thresholds after results.
4. Freeze alignment receipts before any feature generation or model training.
5. **Do not begin real model training without separate explicit training authorization.**
6. Keep P3 sealed and keep `main`, Production and customer-delivery behavior unchanged.


## Frozen P1/P2 alignment implementation launched — 2026-09-21

- Added `docs/astra/GUITARTECHS_ALIGNMENT_IMPLEMENTATION_V1.json`, SHA-256 **`b33dd0fd220fcef4a459cc47277f48cf90c0acd320e523c3afcea5fc52a8a26f`**, before observing any real alignment result.
- Frozen script: `astra_backend/guitartechs_alignment/align_development.py`, SHA-256 **`b084da0900acf9bd4ec61386a4a928350af0e138c9ed36ef3fbafb15539bc330`**.
- The implementation preserves the already-frozen gate: lag -100..+100 ms at 1 ms steps; minimum 30 MIDI onset groups; >=80% matched within 20 ms; median absolute residual <=10 ms; five deterministic onset-index strata with lag MAD <=5 ms; maximum applied correction 100 ms; failures abstain.
- Audio evidence is now exactly specified: ffmpeg decode to mono 8 kHz signed-16 PCM; 20 ms frame / 2 ms hop log-RMS positive-flux envelope; [0.25, 0.5, 0.25] smoothing; frame-end timestamps; median positive-flux peak-strength threshold. Exact ffmpeg version is recorded per result receipt.
- Synthetic tests recover both positive and negative known lags and verify the abstention guards before any real-media job can run.
- Branch-only workflow `.github/workflows/guitar-techs-development-alignment.yml` is restricted to the same eight P1/P2 archive allowlist, re-verifies byte count + MD5 + Astra SHA-256 before extraction, uploads JSON receipts only, and deletes media after each job.
- P3 is not an input. The workflow performs no TabCNN feature generation, model import or training. Real training remains unauthorized.
- Corrected run `35565695012` passed the frozen script identity and all synthetic lag tests. All eight media jobs then failed at runner prerequisite before download because `ubuntu-24.04` did not have ffmpeg installed; **every download/extraction/alignment step was skipped**. The workflow now installs ffmpeg explicitly and records its exact version in result receipts.
- First media-reaching run `35565808226` verified and aligned P1 single-notes far enough to print a coarse summary (**3/4 capture paths complete, 1 abstained**), but an orchestration mismatch left the script writing `/tmp/P1_singlenotes.alignment.json` while upload expected `/tmp/alignment-receipt.json`. Cleanup correctly deleted media and the unuploaded detailed receipt, so that coarse result is **diagnostic only and not frozen evidence**. The output path is now corrected exactly; a clean rerun is required.
- First branch verification attempt on commit `b57f3dc68c09101990e70100a296465a27cd4c88` failed **before any alignment media job started** because the committed script bytes had SHA-256 `b084da0900acf9bd4ec61386a4a928350af0e138c9ed36ef3fbafb15539bc330` while the preregistration still contained the pre-formatting digest `ff7b1dd6799efeeca5d0239269a5e6431ad595a6320ce536ef5bba20d937b547`. The synthetic gate prevented media access. Commit correcting the frozen script identity kept the algorithm bytes unchanged. A subsequent regression check found the implementation-JSON receipt itself had actual committed SHA-256 `b33dd0fd220fcef4a459cc47277f48cf90c0acd320e523c3afcea5fc52a8a26f` rather than the pre-serialization digest `0061b05a8e72982bf75d64554bcd003febbcdd9d7bf7b0377d826ea6e21f205e`; that bookkeeping digest is corrected without changing the implementation JSON bytes.


## Guitar-TECHS P1/P2 alignment evidence frozen — 2026-09-21

- Clean authoritative alignment workflow run `35565975272` completed successfully on source commit `f6c0d17d367b1a264529ffce66a0a6d919bfd147`; all eight P1/P2 matrix jobs and the synthetic pre-media gate succeeded.
- The run used the preregistered alignment implementation unchanged: script SHA-256 `b084da0900acf9bd4ec61386a4a928350af0e138c9ed36ef3fbafb15539bc330`; implementation receipt SHA-256 `b33dd0fd220fcef4a459cc47277f48cf90c0acd320e523c3afcea5fc52a8a26f`.
- Across **92 performances / 368 capture paths**, **275 passed** and **93 abstained**.
- V1 primary content (chords, scales, single notes, PalmMute): **256 / 336 capture paths accepted**, **80 abstained and excluded**. P1 contributes 136 accepted / 32 abstained; P2 contributes 120 accepted / 48 abstained.
- Primary-view acceptance: P1 directinput 41/42, micamp 41/42, ego 33/42, exo 21/42; P2 directinput 39/42, micamp 37/42, ego 19/42, exo 25/42.
- Primary abstention causes were exactly the frozen gates: 62 `MAXIMUM_BOOTSTRAP_LAG_MAD_EXCEEDED` occurrences and 47 `MAXIMUM_MEDIAN_ABSOLUTE_RESIDUAL_EXCEEDED` occurrences. No primary capture failed minimum matched fraction or the 30-onset minimum.
- No threshold was changed after observing results. Failed recording-session + capture-path pairs remain excluded exactly as the contract required.
- Frozen combined receipt: `docs/astra/GUITARTECHS_DEVELOPMENT_ALIGNMENT_EVIDENCE_V1.json`; SHA-256 **`8e65fda2a74f5f5af77ab62be3538715d9ec2c0dcd783de5837a56c5dd42b1ae`**. Review: `docs/astra/GUITARTECHS_DEVELOPMENT_ALIGNMENT_REVIEW_V1.md`.
- The receipt pins all eight Actions artifact digests, all eight detailed receipt SHA-256 values, runtime versions, the exact 80-path abstention list, accepted-set digest `f520f5ffe3daf44da9bad1d145adaa1c9ff0bb662141b027f85b8c7bc827eabc` and abstained-set digest `b4221bdc8236eb5f7c3a1cc5dca0f0d5d931d6acff7a56210525f08c0d26c812`.
- Candidate registry now records `alignmentCorrectionVerified:true` **only for the exact accepted primary subset** and removes `ALIGNMENT_CORRECTION_NOT_VERIFIED`.
- Added `astra_backend/guitarTechsAlignmentEvidence.mjs` and fail-closed receipt/run/implementation/count/set/P3/training substitution tests.
- No TabCNN feature generation, model import, real training, P3 access, main/Production mutation or customer delivery occurred.

## Exact next step — freeze development acceptance thresholds before real training

1. Freeze numeric P1/P2 development acceptance thresholds for the already-required metrics **before** any real model training.
2. Thresholds must evaluate both performer-disjoint folds and include onset string/fret precision, recall, F1, note-event completeness, frame string/fret accuracy, abstention rate, per-content-class results and cross-performer consistency.
3. Define failure/abstention behavior without using P3 and without looking at any trained Guitar-TECHS model result.
4. Keep the exact 256-path alignment allowlist mandatory for any later feature generation/training job.
5. **Do not begin real model training without separate explicit training authorization.**
6. Keep P3 sealed and keep `main`, Production and customer-delivery behavior unchanged.


## Guitar-TECHS development metric thresholds frozen — 2026-09-21

- Alignment-evidence commit `fff9beaacdbbe44a3bb42a1437decc83768489a6` passed GitHub Actions run `35566840139`.
- Before any real Astra Guitar-TECHS model training, numeric development acceptance thresholds and exact metric semantics are now preregistered in `docs/astra/GUITARTECHS_DEVELOPMENT_METRIC_THRESHOLDS_V1.json`; SHA-256 **`fba6c921f17ec2ba3bace55b50823ea33bbf7828b61c0705da78b48ac8cfbe15`**.
- External sanity anchor only: Pedroza et al., ICASSP 2025 Table III reports the Guitar-TECHS-augmented model at tablature P 0.809±0.018, R 0.699±0.048, F1 0.747±0.031, TDR 0.905±0.015. Astra explicitly does **not** claim those published frame/tablature metrics or folds are equivalent to its stricter exact onset+string+fret evaluation.
- Evaluation is restricted to the frozen 256-path alignment-accepted primary set and both performer-disjoint folds. Accepted views are averaged within each underlying performance before macro-averaging performances to prevent correlated-view weighting.
- Event match is one-to-one exact physical string + fret with onset tolerance 50 ms; note-event completeness is duration-overlap based; frame accuracy is exact string/fret accuracy on active-union frames only, excluding silence-only true negatives.
- Each fold must meet: precision >=0.75, recall >=0.60, onset string/fret F1 >=0.67, note-event completeness >=0.60, active-union frame accuracy >=0.70, abstention <=0.10, and each primary content class F1 >=0.55.
- Across folds: macro onset F1 >=0.70, macro completeness >=0.65, F1 gap <=0.10 and frame-accuracy gap <=0.10.
- Missing, non-finite or empty required metrics fail closed. Post-result threshold retuning is forbidden.
- Added `astra_backend/guitarTechsDevelopmentMetricThresholds.mjs` with fail-closed two-fold evaluation and focused tests.
- Candidate registry now records `developmentMetricThresholdsFrozen:true` and removes `DEVELOPMENT_METRIC_THRESHOLDS_NOT_FROZEN`.
- This milestone ran **no real training**, opened no P3 material, authorized no paid compute and changed neither main nor Production.
- Verification on commit `a37b55c6bcf2138bbeadfad21df1ffec9044e8a1`: GitHub Actions run `35567110651` **PASS**; **287/287 Node tests passed**, **78/78 focused Python tests passed**. Node output SHA-256 `3f4cb79e6b228998c38b88a84677b6b6ab4a61b9a60b01f04709616c0b73bce9`; focused evaluation output SHA-256 `aa34637b546e98ae5c20c7802f1f9f23d8ba8db68ef2e4553e5fe031e7ed6c7c`.

## Next authorization gate — real P1/P2 model training

All pre-training evidence gates that can be completed without a real training run are now frozen: archive identity, grouping, string mapping, tuning, alignment allowlist, deterministic runtime/smoke, development metric definitions and acceptance thresholds.

Real training remains separately unauthorized. A future authorization must be explicit for bounded P1/P2 training only; P3 stays sealed until a trained candidate passes both development folds under the frozen thresholds. Production/customer delivery remains unauthorized regardless.


## P1/P2 real training authorized — 2026-09-21

- User explicitly authorized the next bounded real-training gate.
- Frozen authorization scope: `guitar-techs-p1-p2-real-training-v1`.
- Receipt: `docs/astra/GUITARTECHS_REAL_TRAINING_AUTHORIZATION_V1.json`; SHA-256 **`175de606db2276dd745d697e1e996e6c533a7ad6542d258ed66e2a8bbb6ea0d0`**.
- Authorized: random-initialized Astra TabCNN training on P1/P2 only, both performer-disjoint folds, max 2,500 iterations/fold, batch 32, Adadelta lr 1.0, seed 20260921, 50 validation checkpoints/fold, exact frozen 256-path alignment allowlist and frozen development thresholds.
- Not authorized: P3 access, published GuitarProFX checkpoint loading, paid compute, main/Production mutation or customer delivery.
- Candidate registry now clears `TRAINING_NOT_AUTHORIZED`; `MODEL_NOT_TRAINED`, P3 and customer-delivery gates remain.
- Next action is implementation/preflight freeze, followed by the branch-only CPU training workflow if preflight passes.


## Bounded real-training implementation launched — 2026-09-21

- Repository visibility verified public before launch; standard GitHub-hosted CPU runners are used and paid compute remains forbidden.
- Training script frozen at Git blob `d4a3dd99c4a2c3cda16c10bde1a5dc63f6380254`.
- Exact 256-path alignment correction map frozen at Git blob `9090d465422ebf5d4fdf170693fe0936934f3073`.
- Implementation receipt Git blob: `159d6b60ed25582181efd1d036bf86b47bbd5563`.
- Checkpoint selection is preregistered on 10 deterministic performance-balanced validation captures (4 chords, 4 scales, 1 single-notes, 1 PalmMute; view priority directinput -> micamp -> ego -> exo). The selected checkpoint is then evaluated once on the full opposite-performer frozen accepted population.
- Training remains capped at 2,500 iterations/fold, batch 32, Adadelta lr 1.0, seed 20260921, random initialization only, 50 checkpoint-selection evaluations.
- The workflow must pass authorization/source identity checks and a synthetic self-test before any media access.
- P3 is absent from workflow inputs; raw P1/P2 media is sequentially verified, prepared, and deleted. Output artifacts are development-only fold model + receipt retained 7 days.
- Main, Production and customer delivery remain unchanged and unauthorized.


## Real-training preflight correction — 2026-09-21

- Launch run `35568412209` failed in the **training-core self-test before media access**. Both fold jobs were skipped; no P1/P2 archive was downloaded or opened.
- Failure was a mask-axis bookkeeping error in the evaluator self-test path: prediction arrays are frame-major while the frozen label mask is string-major.
- Corrected training script Git blob: `d4a3dd99c4a2c3cda16c10bde1a5dc63f6380254`.
- Updated implementation receipt Git blob: `159d6b60ed25582181efd1d036bf86b47bbd5563`.
- No thresholds, training limits, sampling rules, model architecture, dataset allowlist or authorization scope changed.


## Real-training media-fetch retry hardening — 2026-09-21

- Corrected preflight run `35568621144` passed authorization identity checks, exact runtime installation and the training-core self-test.
- Both performer-disjoint fold jobs then failed **before dataset preparation completed and before any optimizer step** because Zenodo returned repeated HTTP 504 responses on the first development archive.
- No model was trained, no checkpoint was selected, no P3 data was touched and customer delivery remained disabled.
- Retry hardening changes orchestration only:
  - fold jobs are serialized (`max-parallel: 1`) to avoid two simultaneous ~4 GB corpus fetches;
  - each archive first tries Zenodo's record API content endpoint, then the published file endpoint;
  - bounded retry/backoff and partial-file cleanup are explicit;
  - all frozen byte count, MD5 and Astra SHA-256 verification remains mandatory before extraction.
- Training limits, seed, random initialization, 256-path allowlist, alignment corrections, metric thresholds and checkpoint-selection policy are unchanged.


## Bounded P1/P2 real training active — 2026-09-21

- User authorization is active under scope `guitar-techs-p1-p2-real-training-v1`; P3, paid compute, main/Production mutation and customer delivery remain forbidden.
- First corrected media-reaching run `35568621144` passed preflight but both folds stopped before any optimizer step because Zenodo returned repeated HTTP 504 responses on the first archive.
- Fetch orchestration was hardened without changing the frozen training/evaluation contract: folds serialized, Zenodo API-content endpoint added as primary with published-file fallback, bounded retry/backoff and partial-file cleanup retained.
- Exact launch commit: `ec4860d9da2eef2952bf47bb7beb904b215562c4`.
- Active GitHub Actions run: **`35569391647`**.
- Preflight job `106237628363`: **PASS**, including authorization/source identity checks, exact frozen runtime install and training-core self-test.
- Fold 1 job `106237810511` (`P1 -> P2`) successfully crossed the earlier Zenodo failure point and is currently in **Prepare exact frozen 256-path P1/P2 development set**.
- Fold 2 job `106237810493` (`P2 -> P1`) remains queued by the intentional `max-parallel: 1` serialization.
- At this checkpoint there have been **zero real optimizer steps in this launch yet**; model training begins only after the 256-path prepared manifest is complete.
- Frozen limits remain unchanged: random initialization, 2,500 iterations/fold, batch 32, Adadelta lr 1.0, seed 20260921, 50 checkpoint evaluations/fold, exact 256-path alignment allowlist, frozen metric thresholds.
- P3 is absent from workflow inputs.

## NEXT ACTION TO RESUME — active training run

Inspect Actions run `35569391647` first. Do not launch a duplicate while it is active. If fold 1 completes, collect its development-only model/result artifact and exact metrics; then allow serialized fold 2 to complete. Evaluate both folds only against the already-frozen threshold receipt. Do not tune thresholds after seeing results. Do not open P3 unless a later checkpoint explicitly establishes that both development folds passed and separately authorizes the sealed final gate.


## Guitar-TECHS bounded P1/P2 real training result frozen — 2026-09-21

- Authoritative GitHub Actions run `35569391647` completed preflight plus both serialized performer-disjoint training folds successfully at the workflow level.
- Each fold used random initialization, exact frozen 256-path allowlist, 2,500 iterations, batch 32, Adadelta lr 1.0, seed 20260921 and 50 checkpoint evaluations. No published checkpoint was loaded, no paid compute was used and P3 remained unopened.
- P1->P2 selected iteration 1400. Full validation: P **0.2019**, R **0.3270**, F1 **0.2379**, completeness **0.2325**, frame accuracy **0.2445**, abstention **0.0**. All four content-class F1 values are below 0.55.
- P2->P1 selected iteration 2300. Full validation: P **0.1487**, R **0.3062**, F1 **0.1894**, completeness **0.1759**, frame accuracy **0.2357**, abstention **0.0**. All four content-class F1 values are below 0.55.
- Aggregate macro F1 **0.2136** vs frozen >=0.70; macro completeness **0.2042** vs >=0.65.
- Cross-performer consistency itself passes: F1 gap **0.0485** <=0.10 and frame-accuracy gap **0.0088** <=0.10. This is a consistently weak candidate, not a single-performer anomaly.
- P1->P2 artifact `10630257769`, artifact digest `sha256:564f30d82e3e5d7ac6b21b3a7ded3ceddff6d2fe457d877d1e92666997f7b2b6`, result SHA-256 `024e5d2d3612732e85f2c0b812f223e602fcdf6e69f82ca8d5a2d0d0e89090f0`, model SHA-256 `8dc70d94741e0b472e93481f498efafb7627445896594752b217e000f2832a83`.
- P2->P1 artifact `10635588120`, artifact digest `sha256:036189322b4eb5f5ca2f7eac6a82c8a3471cfd814355087f8d6452bb62306734`, result SHA-256 `c6dcc9e557c7e030f523410e705c35e4e7fea3c994e490487c7755e3e2793950`, model SHA-256 `d480cadf66fc0d98608c719252c34bdab4c3120252167e8786502b4332264841`.
- Frozen aggregate receipt: `docs/astra/GUITARTECHS_REAL_TRAINING_DEVELOPMENT_RESULT_V1.json`; SHA-256 **`3edfcf97766bef89ea56429a7385107d99868dc948d867251bcc5f9066a18112`**.
- Candidate registry now records `modelTrained:true`, `developmentEvaluationPassed:false`, `realTrainingAuthorizationConsumed:true`, and blocker `DEVELOPMENT_THRESHOLDS_NOT_MET`. `MODEL_NOT_TRAINED` and `TRAINING_MEDIA_NOT_ACQUIRED` are cleared.
- **Do not retune the frozen acceptance thresholds to rescue this result. Do not open P3. Do not promote either failed fold model.**

## Exact next step — P1/P2-only failure diagnosis

1. Diagnose preprocessing/label/model-learning failure using only frozen P1/P2 development evidence and synthetic/unit tests.
2. Check label occupancy and silence-class balance, fret-range masking, per-string class distributions, CQT/frame-to-label temporal convention, training batch sampling balance, and whether the pinned TabCNN tensor/output semantics match the loss/evaluator exactly.
3. Prefer static analyses and tiny synthetic/fixture experiments first; do not launch another full real training run under the consumed V1 authorization.
4. Any changed training design or another bounded real-data run requires a new frozen design receipt and separate explicit authorization.
5. Keep P3 sealed; main, Production and customer delivery remain unchanged.


## Guitar-TECHS V1 failure diagnosis frozen — 2026-09-21

- Static comparison against pinned upstream revision `f50309ad06dc734ddae5e3a0eda756fca221e2e7` found a concrete V1 training-semantics mismatch.
- Upstream `guitarProFx.py` uses **200-frame** dataset samples. Shared `train.py` defines one training iteration as a complete loop through the DataLoader; each track supplies one random contiguous 200-frame slice per loop before batching.
- Astra V1 instead treated 2,500 as exactly 2,500 optimizer steps and sampled **one isolated frame** for each of 32 batch elements.
- V1 therefore supervised only **80,000 frame positions/fold**. Even with the same 2,500 optimizer-step count, 200-frame sequences would provide **16,000,000 positions**, a **200×** exposure difference.
- V1 also accepted ordinary silence (`-1`) as a valid random sample because it rejected only `MASK=-100`, creating a secondary silence-dominance risk.
- Pinned GuitarProfile/TabCNN output semantics were verified correct: 19 frets -> 20 playable states including open, plus silence -> 21 classes/string -> 126 logits. Output shape is not the primary failure.
- Frozen diagnosis receipt: `docs/astra/GUITARTECHS_V1_TRAINING_FAILURE_DIAGNOSIS_V1.json`; SHA-256 **`c9ec7f099b57451bdaaa683c3d644a3f11e340b296916f9771702f4699462848`**.
- Added deterministic V2 sampler `astra_backend/guitartechs_training_v2/sampling.py`: one 200-frame contiguous sequence per underlying performance per epoch, deterministic accepted-view rotation, seeded segment start, correlated views do not add performance weight, and the final partial batch is not dropped.
- Added focused synthetic tests covering performance balance, deterministic rotation, 200-frame bounds, no dropped tail, fail-closed short captures and exact 200× same-step exposure arithmetic.
- V2 keeps the already-frozen development quality thresholds unchanged.
- **V2 real training is not authorized by the consumed V1 authorization. P3 remains sealed.**

## Next authorization gate — corrected V2 P1/P2 training

Before any V2 real-data run, freeze the full V2 implementation and resource budget around the 200-frame performance-balanced semantics, including pretraining label-balance receipts. Then obtain separate explicit user authorization. Do not reinterpret or erase the V1 failure; it remains historical evidence of the incorrect single-frame training implementation.


## V2 synthetic test coverage correction — 2026-09-21

- Commit `81293a6a02d3f24b00c2a518158f7a3a65d431e3` passed **294/294 Node tests**, but the focused Python workflow remained at 78 tests because that workflow uses an explicit test-file list.
- `test_guitartechs_v2_sampling.py` is now explicitly included in `.github/workflows/astra-backend-tests.yml`; the V2 sampling design is not considered fully verified until this updated run passes.


## V2 synthetic CPU benchmark launched — 2026-09-21

- Corrected sampling commit `419f8bb625486b0f50ecd518a8fe19103ac45f4f` passed run `35629845567`: **294/294 Node tests** and **85/85 focused Python tests**. Node output SHA-256 `3454a4f0a7fa4d5ca72fc6b511d3d8f80f85945016972c2b8a37fb1148d727ae`; focused output SHA-256 `7dda0bf7052a6a153e7e15205e1ced554cb684b338249926667ce29ace554fdb`.
- Before choosing a V2 real-training budget, a no-media CPU benchmark is launched against the exact pinned TabCNN source/runtime.
- It measures one effective batch of 32 sequences × 200 frames using gradient accumulation at sequence microbatches 1/2/4/8, recording effective-step wall time and peak RSS.
- Synthetic random features/labels only. No Guitar-TECHS archive, P3, model checkpoint or customer data is accessed.


## Guitar-TECHS V2 CPU budget + implementation frozen — 2026-09-21

- Synthetic CPU benchmark run `35630098935` completed microbatch 1/2/4/8 with no real media.
- Microbatch 1 was selected: median **7.597 s** per effective 32-sequence × 200-frame optimizer step, peak RSS **704,840 KiB**. Larger microbatches were not faster and used more memory.
- Frozen budget receipt: `docs/astra/GUITARTECHS_V2_CPU_BUDGET_V1.json`; SHA-256 **`8705df7cde4456dc17b5973d84404981387a322ea195a3f995a72ae6b236b430`**.
- V2 budget: 1,000 performance-balanced epochs/fold, batch 32, sequence microbatch 1 with gradient accumulation, 50 checkpoints every 20 epochs, no dropped tail, max 2,000 optimizer steps/fold, 345-minute runner timeout.
- Supervised exposure: P1 **8.2M frames** (102.5× V1); P2 **8.0M** (100× V1). Benchmark-scaled training-only estimates are ~2.70 h and ~2.64 h respectively.
- Full V2 trainer frozen at Git blob `4db5add96c58a8e54868ea06dacb1da724675163`; deterministic sampler blob `9eb62fde56f592646077afa1e0ff3013a5dc6560`; V1 preparation-only source remains blob `d4a3dd99c4a2c3cda16c10bde1a5dc63f6380254`.
- V2 trainer uses one 200-frame contiguous sequence per underlying performance per epoch, rotates only among alignment-accepted correlated views without extra performance weight, includes every performance tail batch, averages gradients over performance batches, and requires pretraining active/silence/mask/fret-distribution diagnostics.
- V2 implementation receipt Git blob: `32424b78d8423d6a87e37a8ad3f1698fa99073ab`.
- V2 real training is still **not authorized**. P3 remains sealed and thresholds remain unchanged.
- Branch-only synthetic implementation smoke installs the exact runtime, verifies all frozen identities and runs a 200-frame TabCNN backward pass without media.


## V2 implementation verification complete — 2026-09-21

- Latest implementation commit `3c5949e263552b63398fc62b8710d0a8dc1b8620` passed both required no-real-data verification workflows.
- Astra backend run `35630956072`: **295/295 Node tests passed**, **85/85 focused Python tests passed**. Node output SHA-256 `a5c99a7de47fee240b9506dc9c58b373c63d921db6666ec75207e8e5bebbe8c0`; focused evaluation output SHA-256 `45e89b4c3a14f2ee8dddb137087b21803bd4fb261295ed0f53ef96c6a38e0a42`.
- V2 implementation smoke run `35630956102`: **PASS**.
  - trainer Git blob verified: `4db5add96c58a8e54868ea06dacb1da724675163`;
  - sampler Git blob verified: `9eb62fde56f592646077afa1e0ff3013a5dc6560`;
  - CPU budget SHA-256 verified: `8705df7cde4456dc17b5973d84404981387a322ea195a3f995a72ae6b236b430`;
  - implementation receipt Git blob verified: `32424b78d8423d6a87e37a8ad3f1698fa99073ab`;
  - exact pinned TabCNN source loaded and the 200-frame synthetic backward self-test emitted `V2_SELF_TEST_PASS`.
- Smoke guards explicitly recorded: `GUITAR_TECHS_V2_REAL_TRAINING_AUTHORIZED=false`, `GUITAR_TECHS_P3_OPENED=false`, `CUSTOMER_DELIVERY_ELIGIBLE=false`.
- No V2 Guitar-TECHS archive was downloaded or opened, no optimizer was run on real data, P3 remained sealed, and no Production/main/customer-delivery state changed.

## NEXT AUTHORIZATION GATE — corrected V2 P1/P2 real training

All V2 design work that can be completed without another real-data run is now frozen and verified: root-cause diagnosis, 200-frame deterministic sampler, CPU budget, trainer implementation, exact identities, synthetic backward smoke and unchanged development thresholds.

A new explicit user authorization is required before V2 can access P1/P2 media or run real optimizer steps. The prior V1 authorization is consumed and does not carry forward.

If authorized, the scope must remain bounded to the frozen V2 P1/P2 design only:
- P1/P2 development media only;
- 1,000 performance-balanced epochs/fold;
- at most 2,000 optimizer steps/fold;
- batch 32 performances;
- 200-frame sequences;
- sequence microbatch 1 with gradient accumulation;
- seed 20260921;
- 50 checkpoints every 20 epochs;
- unchanged frozen development thresholds and exact 256-path alignment allowlist;
- CPU-only public GitHub-hosted runners;
- P3 sealed;
- no paid compute, main/Production mutation or customer delivery.


## V2 P1/P2 real training authorized — 2026-09-21

- User explicitly authorized the corrected V2 bounded real-training gate.
- Authorization scope: `guitar-techs-p1-p2-v2-real-training-v1`.
- Receipt: `docs/astra/GUITARTECHS_V2_REAL_TRAINING_AUTHORIZATION_V1.json`; SHA-256 **`0edfb4656675e31fce0c8cbd1ba42f37619e877b43793d3386781572dea8cb69`**.
- Authorized only: frozen V2 P1/P2 design, 1,000 performance-balanced epochs/fold, max 2,000 optimizer steps/fold, batch 32, 200-frame sequences, microbatch 1 + gradient accumulation, seed 20260921, 50 checkpoint evaluations, exact 256-path alignment allowlist, unchanged development thresholds, public GitHub-hosted CPU runners.
- Not authorized: P3 access, threshold retuning, published checkpoint loading, paid compute, main/Production mutation or customer delivery.
- Branch-only workflow `.github/workflows/guitar-techs-v2-real-training.yml` verifies all frozen V2 identities and the authorization receipt before media access, runs the V2 synthetic self-test, serializes folds, reuses the hardened Zenodo fetch + byte/MD5/SHA verification, prepares exactly 256 paths, runs `train_v2.py`, uploads development-only model/result artifacts, and deletes raw/prepared media.
- V1 failed models remain historical evidence and are not used for V2 initialization.


## Corrected V2 P1/P2 real training active — 2026-09-21

- V2 authorization receipt SHA-256: `0edfb4656675e31fce0c8cbd1ba42f37619e877b43793d3386781572dea8cb69`.
- Launch commit: `33b1f222d29ec25a3602b1b85a58f57e2e7dd8d0`.
- Active GitHub Actions run: **`35662028832`**.
- Preflight job `106539242502`: **PASS**, including V2 authorization/identity checks, exact pinned runtime install, exact pinned TabCNN source identity checks and `V2_SELF_TEST_PASS` 200-frame backward smoke.
- Fold 1 job `106539518639` (`P1 -> P2`) is active; fold 2 job `106539518543` (`P2 -> P1`) is queued by the intentional `max-parallel: 1` serialization.
- Frozen V2 limits remain unchanged: 1,000 performance-balanced epochs/fold, <=2,000 optimizer steps/fold, 200-frame sequences, batch 32, microbatch 1 + gradient accumulation, seed 20260921, 50 checkpoints every 20 epochs, unchanged development thresholds and exact 256-path alignment allowlist.
- P3 remains sealed; paid compute, published-checkpoint initialization, threshold retuning, main/Production mutation and customer delivery remain forbidden.
- Do not launch a duplicate V2 run while `35662028832` is active.

## NEXT ACTION TO RESUME — active V2 training

Inspect run `35662028832` first. If fold 1 completes, collect its development-only result/model artifact and exact pretraining label-balance diagnostics plus full opposite-performer validation metrics. Then allow serialized fold 2 to complete. Evaluate both folds only against the already-frozen thresholds; do not retune thresholds after seeing V2 results. Do not open P3 unless a later checkpoint establishes that both V2 development folds pass and separately authorizes the sealed final gate.


## V2 result-admission contract frozen while Fold 1 trains — 2026-09-21

- Active real-training run `35662028832` has completed the exact 256-path preparation for Fold 1 and entered the frozen V2 optimizer loop.
- No live-training parameter or threshold was changed.
- Frozen post-run admission receipt: `docs/astra/GUITARTECHS_V2_RESULT_ADMISSION_CONTRACT_V1.json`; SHA-256 **`58184ff3c60499c2ba6b89ef1042ea3c0eb20603d5a3a10e2eb11700de7a41db`**.
- Any future V2 fold artifact must prove the exact fold identity, seed, 1,000 epochs, 2,000 optimizer steps, 200-frame sequences, batch 32, microbatch 1, 50 checkpoints, exact prepared capture counts, expected performance counts, exact supervised exposure (P1 8.2M / P2 8.0M frame positions), frozen budget/failure-diagnosis receipts, pretraining label-balance hard sanity and all guard flags.
- Only after both fold artifacts pass those structural checks are their full opposite-performer metrics passed into the already-frozen development metric evaluator.
- Even if both development folds pass, this contract does **not** authorize P3; it only marks P3 as eligible for a separate explicit authorization.
- Added `astra_backend/guitarTechsV2ResultAdmission.mjs` and fail-closed structural/metric/P3/customer-delivery tests.
- The running workflow checkout remains launch commit `33b1f222d29ec25a3602b1b85a58f57e2e7dd8d0`; this documentation/evaluator commit does not modify it.
- Verification on commit `d2e8e29994c6a3fabb250455274070328fe2e76e`: GitHub Actions run `35665163937` **PASS**; **302/302 Node tests passed**, **85/85 focused Python tests passed**. Node output SHA-256 `eb1caa8fd52a96218162b85a1cd37b2868290096f4655a9a55f6f2c0b3787287`; focused evaluation output SHA-256 `99f558455baee2087d597d36ab8738e5b2cf073b5a1680045f57d7bd64b271a9`.


## EXPLICIT NEXT STEP TO RESUME — do this first

1. **Inspect GitHub Actions run `35662028832` before doing anything else.**
   - Preflight job `106539242502` already passed.
   - Fold 1 job `106539518639` (`P1 -> P2`) is currently in the real V2 optimizer/full-validation step.
   - Fold 2 job `106539518543` (`P2 -> P1`) is queued behind Fold 1 by the intentional serial policy.
   - **Do not launch a duplicate V2 run while `35662028832` is active.**

2. **When Fold 1 finishes, collect its development-only artifact before changing anything.**
   - Record Actions artifact ID + digest.
   - Record result JSON SHA-256 and model SHA-256.
   - Verify V2 structural evidence against `docs/astra/GUITARTECHS_V2_RESULT_ADMISSION_CONTRACT_V1.json` (SHA-256 `58184ff3c60499c2ba6b89ef1042ea3c0eb20603d5a3a10e2eb11700de7a41db`).
   - Require exact fold identity, seed, 1,000 epochs, 2,000 optimizer steps, 200-frame sequences, batch 32, microbatch 1, 50 checkpoints, P1 training performance count 41, P2 validation capture count 120, P1 supervised exposure 8.2M frame positions, frozen source receipts, guard flags, and pretraining label-balance hard sanity.
   - Preserve the selected checkpoint and full opposite-performer validation metrics exactly as emitted.

3. **Allow the same run to continue into Fold 2; do not relaunch it separately.**
   - When Fold 2 finishes, collect the corresponding artifact IDs/digests, result/model SHA-256 values, label-balance diagnostics, selected checkpoint, and full opposite-performer validation metrics.
   - Require P2 training performance count 40, P1 validation capture count 136, and P2 supervised exposure 8.0M frame positions, plus all other frozen V2 admission requirements.

4. **After both fold artifacts exist, run only the frozen V2 result admission + development metric evaluation.**
   - Use `astra_backend/guitarTechsV2ResultAdmission.mjs`.
   - Development thresholds remain those in `docs/astra/GUITARTECHS_DEVELOPMENT_METRIC_THRESHOLDS_V1.json` (SHA-256 `fba6c921f17ec2ba3bace55b50823ea33bbf7828b61c0705da78b48ac8cfbe15`).
   - **Do not retune thresholds, alter the 256-path allowlist, change checkpoint selection, or rescue a weak result after seeing V2 metrics.**

5. **Freeze the V2 development result into repo evidence and update this checkpoint.**
   - If either structural admission or development thresholds fail: mark V2 development FAIL, keep both models development-only, keep P3 sealed, diagnose using P1/P2 evidence only, and require a new design + new authorization for another real-data run.
   - If both folds pass every frozen gate: mark V2 development PASS/eligible-for-next-gate only. **Do not open P3 yet.** P3 still requires a separate explicit authorization.

6. **Invariant constraints while resuming:**
   - P3 stays sealed until separately authorized.
   - No paid compute.
   - No published checkpoint initialization.
   - No `main` or Production mutation.
   - No customer delivery/promotion from these development models.
   - Preserve V1 failure evidence unchanged.


## Copy-paste handoff

Continue Jimmy PAIge from `docs/checkpoints/CURRENT_STATE.md` on branch `astra-work` in `dadrockyt-sys/dadrock-tabs-android`. Read AGENTS.md first. Both V143/Gomyway and Songsterr Fresh are archived; do not resume their old task queues. Work on the active Astra milestone, preserve historical outcomes, and commit/push clean backend work plus this checkpoint after each major step. Do not modify main or Production.

## V2 resume observation — 2026-09-21

- Resumed from this canonical checkpoint and re-read `AGENTS.md` before any repository write.
- Read-only inspection of authoritative GitHub Actions run `35662028832`: preflight job `106539242502` remains **PASS**; Fold 1 job `106539518639` (`P1 -> P2`) remains **in progress** in the frozen optimizer/full-validation step; Fold 2 job `106539518543` (`P2 -> P1`) remains intentionally queued by `max-parallel: 1`.
- Workflow artifacts currently returned: **0**. Therefore no fold artifact, result JSON, model SHA-256, label-balance receipt, selected checkpoint, or full-validation metric is yet available for admission.
- Re-verified the frozen admission path on `astra-work`: `docs/astra/GUITARTECHS_V2_RESULT_ADMISSION_CONTRACT_V1.json` receipt SHA-256 `58184ff3c60499c2ba6b89ef1042ea3c0eb20603d5a3a10e2eb11700de7a41db`; development threshold receipt SHA-256 `fba6c921f17ec2ba3bace55b50823ea33bbf7828b61c0705da78b48ac8cfbe15`; evaluator `astra_backend/guitarTechsV2ResultAdmission.mjs` still requires exact fold identities/counts/exposures, pretraining label-balance sanity and guard flags before metrics can be evaluated.
- In-progress job-log archive fetch returned `BlobNotFound`; this is **not** treated as a workflow failure because the job itself remains `in_progress` via the authoritative Actions jobs endpoint.
- No duplicate V2 run was launched. No training parameter, threshold, checkpoint-selection rule, 256-path allowlist, workflow checkout, `main`, Production or customer-delivery state was changed. **P3 remains sealed.**

### EXPLICIT NEXT STEP TO RESUME

Inspect run `35662028832` first. When Fold 1 completes and its artifact appears, collect the Actions artifact ID/digest, download the artifact, compute/record result JSON and model SHA-256, and structurally admit it against the frozen V2 contract before doing anything else. Then allow the same serialized run to continue into Fold 2; do not relaunch either fold. After both artifacts exist, run only the frozen V2 admission + development metric evaluator. Keep P3 sealed unless a later checkpoint records both-fold PASS and the user separately authorizes the P3 gate.

## V2 frozen trainer/admission compatibility audit — 2026-09-21

- While authoritative run `35662028832` remained active with Fold 1 in progress and zero artifacts, performed a read-only static audit of the exact launch-commit trainer (`33b1f222d29ec25a3602b1b85a58f57e2e7dd8d0`) against the already-frozen V2 admission/evaluation code.
- `train_v2.py` emits the exact structural fields required by `guitarTechsV2ResultAdmission.mjs`: schema/candidate/fold identities, seed `20260921`, 1,000 epochs, 2,000 optimizer steps, 200-frame sequences, batch 32, microbatch 1, 50 checkpoints, training performance count, validation capture count, supervised frame exposure, prepared capture counts, source receipt hashes, pretraining label balance, selected checkpoint, full validation metrics and all required guard flags.
- Exposure arithmetic in the frozen trainer is exact by construction: P1 has 41 performances × 200 frames × 1,000 epochs = **8,200,000** supervised frame positions; P2 has 40 × 200 × 1,000 = **8,000,000**. With batch 32 and no dropped tail, both folds execute exactly 2 optimizer steps/epoch = **2,000 optimizer steps**.
- The frozen `aggregate_metrics()` output matches the development evaluator input schema exactly: `precision`, `recall`, `f1`, `completeness`, `frameAccuracy`, `abstentionRate`, and `contentF1` for `chords`, `scales`, `singlenotes`, and `PalmMute`.
- No schema mismatch, threshold drift, checkpoint-selection drift, or structural reason to modify/relaunch the active run was found.
- Latest read-only Actions check remains unchanged: Fold 1 in progress, Fold 2 queued, artifacts **0**. **Do not relaunch. P3 remains sealed.**

### EXPLICIT NEXT STEP TO RESUME

Inspect run `35662028832` first. If Fold 1 is complete, collect and cryptographically verify its artifact immediately and run structural admission only; otherwise leave the workflow untouched and preserve the serialized run. Continue with Fold 2 only through this same run.

## SAVED NEXT STEP — active V2 run

1. **Inspect GitHub Actions run `35662028832` first. Do not launch a duplicate.**
2. If Fold 1 job `106539518639` (`P1 -> P2`) has completed and its artifact exists:
   - record the Actions artifact ID and digest;
   - obtain the fold artifact containing `training-result.json` and `model.pt`;
   - compute and record the result JSON SHA-256 and model SHA-256;
   - verify the fold structurally against `docs/astra/GUITARTECHS_V2_RESULT_ADMISSION_CONTRACT_V1.json` before interpreting its quality metrics;
   - preserve the emitted pretraining label-balance diagnostics, selected checkpoint, supervised exposure, and full opposite-performer validation metrics exactly.
3. **Do not relaunch Fold 2.** Allow this same serialized workflow run to continue into job `106539518543` (`P2 -> P1`), then perform the same artifact collection and structural admission when it completes.
4. Only after both fold artifacts pass structural admission, run the already-frozen V2 development metric evaluator with the unchanged thresholds in `docs/astra/GUITARTECHS_DEVELOPMENT_METRIC_THRESHOLDS_V1.json`.
5. If either structural admission or frozen development thresholds fail, freeze V2 development as FAIL and diagnose using P1/P2 evidence only. Another real-data run requires a new frozen design and separate explicit authorization.
6. If both folds pass every frozen development gate, record only **eligible for a separate P3 authorization**. **Do not open P3 automatically.**
7. Invariants: P3 sealed; no paid compute; no published-checkpoint initialization; no threshold retuning; no 256-path allowlist changes; no `main`/Production mutation; no customer delivery or promotion from development models.

This block is the authoritative next action unless a later checkpoint explicitly supersedes it.



## V2 Fold 1 runtime timeout frozen — 2026-09-22

- Authoritative run `35662028832`, Fold 1 job `106539518639` (`P1 -> P2`), exhausted its frozen GitHub-hosted CPU job window and completed with conclusion **cancelled**.
- Runner began at `2026-09-21T22:20:08.2774701Z`; the training step was cancelled at `2026-09-22T04:05:53.3961278Z` under the workflow's `timeout-minutes: 345` cap.
- Last fully emitted checkpoint before cancellation: **epoch 600**, **optimizer step 1200**, state SHA-256 `508e6b8de3839e053e1a245a2cd79f666bfd15dde5a6991367732def4780f56d`.
- The epoch-600 selection-subset checkpoint was not qualified, but **this is not an admissible V2 model-quality verdict**: the frozen protocol requires 1,000 epochs plus full opposite-performer validation and a complete result/model artifact.
- Artifact upload was skipped and run artifact count remained **0**. Therefore Fold 1 cannot enter structural admission and no final development metric decision may be made from this partial run.
- Cleanup completed and emitted `GUITAR_TECHS_P3_OPENED=false` and `CUSTOMER_DELIVERY_ELIGIBLE=false`. P3 remains sealed.
- Frozen evidence receipt: `docs/astra/GUITARTECHS_V2_RUNTIME_TIMEOUT_EVIDENCE_V1.json`.
- Fold 2 job `106539518543` began automatically because the matrix is serialized with `fail-fast: false`; at the first post-timeout inspection it was only installing the exact runtime. It should not be treated as a replacement for the missing Fold 1 result.

### EXPLICIT NEXT STEP TO RESUME — timeout recovery

1. Do **not** structurally admit or quality-score Fold 1; no complete artifact exists.
2. Stop/leave stopped any continuation of run `35662028832` once the runtime failure is recognized; do not relaunch either fold under the same non-resumable 345-minute design.
3. Design and synthetically verify a **resumable V2 execution layer** that preserves the already-frozen statistical protocol: 1,000 epochs/fold, 2,000 optimizer steps/fold, 200-frame sequences, batch 32, seed 20260921, 50 checkpoint evaluations and the same thresholds/allowlist.
4. Resume state must preserve model weights, optimizer state, deterministic RNG/sampling state, current epoch/optimizer-step/supervised-exposure counters, all checkpoint summaries, best-qualified/best-any checkpoint-selection state, and integrity identities. A resumed execution must be equivalent to one uninterrupted frozen run except for orchestration boundaries.
5. Perform CPU synthetic/resume-equivalence tests only. **Do not access P1/P2 again and do not launch a new real-data run without a new frozen design receipt and separate explicit user authorization.**
6. P3 stays sealed; no paid compute, threshold retuning, allowlist changes, main/Production mutation or customer delivery.

This timeout-recovery block supersedes the prior instruction to wait for a Fold 1 artifact from run `35662028832`.


## V2 timeout run closed + resumable recovery implementation — 2026-09-22

- Run `35662028832` is now closed. Fold 1 job `106539518639` timed out/cancelled after the epoch-600 checkpoint; Fold 2 job `106539518543` was then manually cancelled while its 256-path preparation step was in progress.
- Fold 2's actual training step was **skipped**. Neither fold uploaded a development model/result artifact; there is no structurally admissible V2 fold result from this run.
- P1 partial checkpoint evidence remains runtime/diagnostic evidence only and must not be promoted into a final development-quality verdict.
- Added `astra_backend/guitartechs_training_v2/train_v2_resumable.py` implementing fail-closed resumable execution at frozen epoch boundaries **400 -> 800 -> 1000**.
- Added `docs/astra/GUITARTECHS_V2_RESUMABLE_EXECUTION_DESIGN_V1.json`. The statistical protocol is unchanged: 1,000 epochs, 2,000 optimizer steps, 200-frame sequences, batch 32, seed 20260921, 50 validations, unchanged thresholds and unchanged alignment population.
- Resume state preserves model, optimizer, Python/NumPy/Torch RNG state, counters/exposure, complete checkpoint history, best-qualified/best-any checkpoint state, cumulative training time and frozen identities. Resume input is SHA-256 verified before loading.
- Added branch-only no-real-data workflow `.github/workflows/guitar-techs-v2-resume-smoke.yml` to verify exact frozen runtime/source identities, original V2 backward smoke and split/resume equivalence.
- First smoke run `35686049240` failed only because frozen Torch 1.11 does not accept the newer `weights_only=` loader argument; no real media was accessed.
- Second smoke run `35686192070` advanced through model/optimizer equivalence but exposed a NumPy-array comparison bug in the RNG test helper; no real media was accessed.
- Both compatibility issues were corrected and identities repinned. Final synthetic verification is still required before this recovery design may be called verified.
- **No new P1/P2 real-data authorization exists. Do not launch the resumable workflow on real media yet. P3 remains sealed.**

### EXPLICIT NEXT STEP TO RESUME — resumable verification gate

1. Inspect final resumable smoke run associated with commit `72a6430fe1c0b0871f89f277d63e73722a6e541d`.
2. Require both `V2_SELF_TEST_PASS` and `V2_RESUME_SELF_TEST_PASS` plus the no-real-media guard step.
3. If smoke fails, correct the synthetic/resume implementation only and repin identities; do not access P1/P2.
4. If smoke passes, freeze the verified resumable implementation/receipt and design the real-data orchestration that chains epoch boundaries 400 -> 800 -> 1000 for each fold.
5. A new real P1/P2 run requires a **separate explicit user authorization** after that orchestration is frozen. Do not infer authorization from the prior V2 run.
6. P3 sealed; no paid compute; no threshold/allowlist changes; no main/Production mutation; no customer delivery.


## V2 resumable recovery verified + next authorization gate — 2026-09-22

- The failed non-resumable run `35662028832` is closed with **no admissible fold artifact**. Fold 1 timed out after epoch 600 / optimizer step 1200; Fold 2 was cancelled before its training step.
- Resumable implementation: `astra_backend/guitartechs_training_v2/train_v2_resumable.py`; verified Git blob **`86684be13ca6880a89d47bccd0d2b90c22b378fb`**.
- Resumable design receipt: `docs/astra/GUITARTECHS_V2_RESUMABLE_EXECUTION_DESIGN_V1.json`; verified Git blob **`b120b711c77ffa3bc98078da2dd8b1ec9f24788a`**.
- Synthetic verification receipt: `docs/astra/GUITARTECHS_V2_RESUMABLE_EXECUTION_VERIFICATION_V1.json`.
- Final exact-runtime resume smoke run **`35686293546`**, job `106613697500`: **PASS**.
  - `V2_SELF_TEST_PASS`
  - `V2_RESUME_SELF_TEST_PASS`
  - `GUITAR_TECHS_V2_REAL_TRAINING_AUTHORIZED=false`
  - `GUITAR_TECHS_P3_OPENED=false`
  - `CUSTOMER_DELIVERY_ELIGIBLE=false`
- The resume smoke proves SHA-verified resume loading plus exact uninterrupted-vs-resumed equality for model state, optimizer state and Python/NumPy/Torch RNG state on the frozen TabCNN/Torch runtime.
- Frozen real orchestration design: `docs/astra/GUITARTECHS_V2_RESUMABLE_REAL_ORCHESTRATION_V1.json`.
  - Fold 1: epoch boundaries **400 -> 800 -> 1000**.
  - Fold 2: epoch boundaries **400 -> 800 -> 1000**.
  - Only one real-training segment may run at a time.
  - Intermediate jobs emit verified resume state only; the epoch-1000 segment alone may emit the complete development result/model after full opposite-performer validation.
  - Every segment must reverify the exact runtime/source identities, exact frozen 256-path development population, unchanged thresholds/allowlist and P3/customer/paid-compute guards.
- Branch-wide regression on run **`35686453636`**: **PASS**.
  - Node: **302 tests**, output SHA-256 `9ad393c28c47222cbccf70dbdd2e288ccae69120d6dde21e251f5822ec9d84ad`.
  - Focused Python evaluation: **85 tests**, **OK**, output SHA-256 `3bd31bdbf42693eba5df295ae12d9d7525cfc4d235cb4ac4e9a42ce8348cefd5`.
- No real P1/P2 data was accessed by the recovery smoke. No new real optimizer run was launched. P3 remains sealed and no main/Production/customer-delivery state changed.

### EXPLICIT NEXT STEP TO RESUME — authorization gate

1. **Do not relaunch the old non-resumable workflow.**
2. The resumable execution layer and six-segment orchestration are now frozen and synthetically verified.
3. Before any new P1/P2 access, obtain a **new explicit user authorization** for the resumable V2 real-training run. The prior authorization was consumed by run `35662028832` and does not carry forward.
4. If the user authorizes:
   - create a new authorization receipt scoped only to the frozen resumable orchestration;
   - pin its exact digest plus the verified resumable trainer/design/orchestration identities in a dispatch-only real-training workflow;
   - verify preflight before media access;
   - execute only the serialized 400 -> 800 -> 1000 segments for P1->P2, then P2->P1;
   - SHA-verify each resume artifact before loading it;
   - collect complete final fold artifacts only at epoch 1000 and admit them against the already-frozen V2 result-admission contract and unchanged development thresholds.
5. If either complete fold fails structural admission or frozen thresholds, freeze V2 development FAIL and diagnose P1/P2 only. Do not retune thresholds or rescue a weak result.
6. If both complete folds pass, record only **eligible for separate P3 authorization**. **Do not open P3 automatically.**
7. Invariants: P3 sealed; no paid compute; no published-checkpoint initialization; no threshold/allowlist changes; no `main`/Production mutation; no customer delivery.

This block is the authoritative next action unless a later checkpoint explicitly supersedes it.


## Resumable recovery record reconciliation — 2026-09-22

- Canonical resumable verification receipt: `docs/astra/GUITARTECHS_V2_RESUMABLE_EXECUTION_VERIFICATION_V1.json`.
- Canonical frozen real-run orchestration receipt: `docs/astra/GUITARTECHS_V2_RESUMABLE_REAL_ORCHESTRATION_V1.json`.
- The later files `docs/astra/GUITARTECHS_V2_RESUMABLE_VERIFICATION_V1.json` and `docs/astra/GUITARTECHS_V2_RESUMABLE_REAL_ORCHESTRATION_DESIGN_V1.json` contain consistent supplemental detail only and are explicitly marked non-authoritative mirrors.
- Canonical smoke run `35686293546` / job `106613697500`: **PASS**, with `V2_SELF_TEST_PASS` and `V2_RESUME_SELF_TEST_PASS`.
- Canonical branch regression run `35686453636`: **PASS**, 302 Node tests and 85 focused Python tests; Node output SHA-256 `9ad393c28c47222cbccf70dbdd2e288ccae69120d6dde21e251f5822ec9d84ad`; focused evaluation output SHA-256 `3bd31bdbf42693eba5df295ae12d9d7525cfc4d235cb4ac4e9a42ce8348cefd5`.
- A later supplemental regression run `35687158345` also passed 302 Node tests and 85 focused Python tests after the more detailed planning receipt was added; this does not create a second gate or authorization.
- **Authoritative next action remains the preceding `EXPLICIT NEXT STEP TO RESUME — authorization gate`.** No new P1/P2 real-data run is authorized. P3 remains sealed.


## Resumable V2 P1/P2 real training authorized + launch preflight verified — 2026-09-22

- User explicitly authorized: **"I authorize the resumable V2 P1/P2 real training exactly as frozen in CURRENT_STATE.md. P3 remains sealed."**
- New authorization receipt: `docs/astra/GUITARTECHS_V2_RESUMABLE_REAL_TRAINING_AUTHORIZATION_V1.json`.
  - SHA-256: `ec2ba853b82c7d57f6da3d87c483967b85c01718599bf73f7cbd9099dbb0d85e`.
  - Git blob: `c893b345ed40a6835eb3a25f2f3e8834d687452a`.
- Authorized scope remains exactly the canonical resumable orchestration:
  - P1->P2: epoch boundaries 400 -> 800 -> 1000.
  - P2->P1: epoch boundaries 400 -> 800 -> 1000.
  - 1,000 epochs/fold; exactly 2,000 optimizer steps/fold.
  - 200-frame sequences; batch 32; microbatch 1; seed 20260921.
  - 50 checkpoint evaluations every 20 epochs.
  - Exact frozen 256-path P1/P2 development population and unchanged development thresholds.
  - Public GitHub-hosted CPU runners only.
- Explicitly still forbidden: P3 access, paid compute, published-checkpoint initialization, threshold retuning, alignment allowlist changes, `main`/Production mutation and customer delivery.
- Reusable segment runner: `.github/workflows/guitar-techs-v2-resumable-segment.yml`; Git blob `51c7cb76c25130d954976041044869dbabc784f6`.
- Dispatch-only controller: `.github/workflows/guitar-techs-v2-resumable-real-training.yml`; Git blob `51ac7753dfbd9e138eff28ddcf3af35536a7066c`.
- No-media authorization preflight: `.github/workflows/guitar-techs-v2-resumable-preflight.yml`; Git blob `7d77d8ea628fdcf215c40d43cd592a2e5deebe6d`.
- Authorization preflight run `35687686704`, job `106617937105`: **PASS**.
  - Exact authorization/orchestration/trainer/runtime/alignment/threshold identities: PASS.
  - Exact frozen runtime install: PASS.
  - Exact pinned TabCNN source acquisition: PASS.
  - `V2_SELF_TEST_PASS`.
  - `V2_RESUME_SELF_TEST_PASS`.
  - `GUITAR_TECHS_V2_REAL_TRAINING_AUTHORIZED=true`.
  - `GUITAR_TECHS_P3_OPENED=false`.
  - `CUSTOMER_DELIVERY_ELIGIBLE=false`.
- The preflight accessed **no P1/P2 media** and performed no real optimizer training.
- The controller is intentionally `workflow_dispatch` only. The active GitHub connector cannot issue a workflow-dispatch POST, so the authorized real run has **not yet been launched** from this chat.

### EXPLICIT NEXT STEP TO RESUME — launch the authorized resumable run exactly once

1. From a Codespace terminal already authenticated to this repository, run exactly:
   `gh workflow run guitar-techs-v2-resumable-real-training.yml --ref astra-work`
2. **Do not run that command twice.** The workflow also has a single concurrency group, but a second dispatch must still be treated as an unauthorized duplicate attempt.
3. Immediately after dispatch, identify the new run with:
   `gh run list --workflow guitar-techs-v2-resumable-real-training.yml --branch astra-work --limit 3`
4. Resume by inspecting that new run first. Its own preflight must pass before the first P1 media-preparation segment is allowed to proceed.
5. The real execution order is fixed:
   - P1 0->400;
   - P1 400->800;
   - P1 800->1000 + full P2 validation + final Fold 1 artifact;
   - P2 0->400;
   - P2 400->800;
   - P2 800->1000 + full P1 validation + final Fold 2 artifact.
6. At each 400/800 boundary, require the exact resume artifact SHA-256 before loading it. Intermediate resume artifacts are not development-quality results.
7. Only after both epoch-1000 fold artifacts exist may structural admission and the frozen development metric evaluator run.
8. **P3 remains sealed regardless of development outcome until separately authorized.**

This block supersedes the preceding authorization gate and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## Resumable V2 launch workaround + active real run — 2026-09-22

- The first manual launch attempt returned **404 Not Found** because the dispatch-only workflow exists only on branch `astra-work`; no real training was launched by that failed attempt and no duplicate exists.
- Launch mechanism was changed without touching `main`: `.github/workflows/guitar-techs-v2-resumable-real-training.yml` now also accepts a push on `astra-work` only when `docs/astra/GUITARTECHS_V2_RESUMABLE_LAUNCH_V1.json` changes.
- Updated controller Git blob: `bedd65b5b450fbd2f3a04f4afa5b726c01df4d63`.
- The authorization preflight was repinned and rerun before launch: run `35688406394`, job `106620037252` **PASS**. It accessed no P1/P2 media.
- One-time launch marker committed at `ef395f705c050c913f935e19a23cee013f6fcfde`.
- Authorized real GitHub Actions run: **`35688531407`**.
- Real-run preflight job `106620407443`: **PASS**.
  - authorization/frozen identities: PASS;
  - exact frozen runtime: PASS;
  - exact pinned TabCNN source: PASS;
  - original V2 self-test: PASS;
  - resumable equivalence self-test: PASS;
  - P3 remained sealed.
- First real segment job `106620631615` (`P1 0->400`) has started and is currently in progress.
- The training is running on GitHub-hosted `ubuntu-22.04` Actions runners, not in Codespaces. Codespaces may be stopped/closed without interrupting this Actions run.
- Do not create or dispatch any second launch marker/workflow run. Run `35688531407` is the single authoritative resumable real-training run.

### EXPLICIT NEXT STEP TO RESUME — active run 35688531407

1. Inspect run `35688531407` first; do not launch another run.
2. Allow `P1 0->400` to complete. Require artifact `guitar-techs-v2-p1-resume-e400` and verify its receipt/state SHA-256 before `P1 400->800` loads it.
3. Continue only through the same serialized run: P1 400->800 -> P1 800->1000 + full P2 validation -> P2 0->400 -> P2 400->800 -> P2 800->1000 + full P1 validation.
4. Intermediate 400/800 resume artifacts are orchestration state only and are not admissible model-quality results.
5. After both epoch-1000 final fold artifacts exist, perform structural admission first, then the unchanged frozen development metric evaluation.
6. P3 remains sealed and requires a separate later authorization even if both folds pass.

This block supersedes the prior manual-dispatch instruction and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## Guitar-TECHS V2 resumable development result frozen — 2026-09-22

- Authorized resumable run `35688531407` completed **all six serialized segments successfully**.
- Final P1 artifact: `guitar-techs-v2-p1-final-development-result`, artifact ID `10700342658`, archive digest `sha256:29a9b055a6a54528a118914298cf72a39b3c84b6006c4674e17791cfe799c272`.
  - `training-result.json` SHA-256 `e9bc6861641a691fdaddc9bcf1a449d0d60a902c2121322f0ec26187f469232a`.
  - `model.pt` SHA-256 `93fdb69757454c75dae07e3333ca2506680c7d80359bbdfa5e4816efe0da6d65`, exactly matching the emitted receipt.
  - Selected checkpoint epoch **720**.
  - Full P2 validation: precision **0.198748**, recall **0.355212**, F1 **0.239542**, completeness **0.253153**, frame accuracy **0.310546**.
- Final P2 artifact: `guitar-techs-v2-p2-final-development-result`, artifact ID `10722879510`, archive digest `sha256:87be095fdbce81f55cb0fad0ebf5e898fc1f12ceb9cff686d660dcdfe2dae66b`.
  - `training-result.json` SHA-256 `270f67d4015848befb50aa968561ec0143e368f3dfe7a3d92eea754ddfe0e866`.
  - `model.pt` SHA-256 `f6954a89e7cfd5a6cad733fbcecacb4fa113d7842f1279f6586cefe5618f214c`, exactly matching the emitted receipt.
  - Selected checkpoint epoch **840**.
  - Full P1 validation: precision **0.150962**, recall **0.317509**, F1 **0.192875**, completeness **0.176767**, frame accuracy **0.251310**.
- Frozen structural admission: **PASS / evidence accepted**.
  - Zero structural blockers.
  - Both folds have exact identities/counts/exposures, 1,000 epochs, 2,000 optimizer steps, 50 checkpoints, valid label-balance receipts and all guard flags false.
  - Both internal model hashes match their receipts.
- Frozen development metric decision: **FAIL**.
  - Exact frozen evaluator reports `developmentAccepted=false`, `modelTrainingEvidenceComplete=true`, and **20 quality-threshold blockers**.
  - Two-fold macro F1: **0.216208** vs required **>=0.70**.
  - Two-fold macro completeness: **0.214960** vs required **>=0.65**.
  - Cross-performer F1 gap: **0.046667**, which **passes** the <=0.10 consistency limit.
  - Cross-performer frame-accuracy gap: **0.059236**, which **passes** the <=0.10 consistency limit.
  - Abstention is 0.0 in both folds and passes its threshold.
  - Both folds fail precision, recall, F1, completeness, frame accuracy and all four per-content F1 minimums.
- Frozen result receipt: `docs/astra/GUITARTECHS_V2_DEVELOPMENT_RESULT_V1.json`.
- P1/P2-only diagnosis receipt: `docs/astra/GUITARTECHS_V2_DEVELOPMENT_FAILURE_DIAGNOSIS_V1.json`.
- Evidence indicates a broadly weak model/design rather than a single asymmetric performer split: both directions fail similarly, selected checkpoints are before epoch 1000, recall exceeds precision, scales are relatively strongest, and single-note/chord exact-string/fret quality is especially weak.
- **V2 is development FAIL. P3 remains sealed. These models are development-only and are not eligible for customer delivery or P3 opening.**

### EXPLICIT NEXT STEP TO RESUME — V3 design diagnosis only

1. Do **not** retune the frozen V2 thresholds and do not launch another real-data optimizer run.
2. Use only P1/P2 development evidence to decompose errors by onset, string assignment, fret classification, temporal run decoding and content class.
3. Investigate class/activity imbalance, especially sparse PalmMute and singlenote targets, plus false-positive behavior implied by recall > precision.
4. Design V3 changes offline/synthetically first (candidate areas: loss weighting/sampling, decoding/confidence calibration, representation/context or architecture).
5. Freeze a new V3 design + synthetic verification before requesting any new real P1/P2 authorization.
6. P3 remains sealed; no paid compute; no threshold/allowlist changes; no `main`/Production mutation; no customer delivery.

This block supersedes the active-run monitoring instructions and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## SAVED NEXT STEPS — V3 diagnosis/design gate — 2026-09-22

These steps are the explicit authoritative resume point after the frozen V2 development FAIL.

1. **Start with P1/P2-only error decomposition; do not launch new training.**
   - Use only the completed V2 development evidence from run `35688531407` and the frozen receipts:
     - `docs/astra/GUITARTECHS_V2_DEVELOPMENT_RESULT_V1.json`
     - `docs/astra/GUITARTECHS_V2_DEVELOPMENT_FAILURE_DIAGNOSIS_V1.json`
   - Do not touch P3.
   - Do not retune the frozen V2 thresholds or alter the accepted 256-path development population.

2. **Quantify where exact-string/fret quality is being lost.**
   - Decompose P1 and P2 errors separately into:
     - onset detection error;
     - string-assignment error;
     - fret-classification error;
     - temporal run segmentation/decoding error;
     - false-positive vs false-negative event balance;
     - per-content-class behavior for chords, scales, singlenotes and PalmMute.
   - Preserve performer-disjoint reporting and do not merge away asymmetries before inspection.

3. **Inspect imbalance and supervision quality before changing architecture.**
   - Measure active/silent balance, per-string activity, fret-frequency imbalance, content-class imbalance and performer-specific activity.
   - Pay special attention to very sparse PalmMute supervision and weak singlenote/chord F1.
   - Determine whether the current loss/sampling scheme over-rewards common active states or produces excessive false positives.

4. **Evaluate decoder/calibration failure separately from representation failure.**
   - Use frozen V2 checkpoints/results to test offline diagnostics such as:
     - confidence distributions for correct vs incorrect string/fret predictions;
     - precision/recall tradeoff under confidence gating;
     - temporal smoothing/run-merging sensitivity;
     - string/fret confusion structure;
     - whether confidence-aware abstention could improve precision without collapsing recall.
   - These diagnostics are development analysis only and must not change the frozen V2 verdict.

5. **Form V3 hypotheses only after diagnosis.**
   Candidate design areas to compare offline/synthetically:
   - class-aware or activity-aware loss weighting;
   - performer-balanced/content-balanced sampling;
   - improved silence/active handling;
   - confidence-calibrated decoding;
   - richer temporal/context representation;
   - architectural changes only where diagnostics show representation capacity is the bottleneck.

6. **Build a V3 synthetic verification harness before real-data authorization.**
   - Require deterministic CPU tests for:
     - revised loss/sampling behavior;
     - resume equivalence if resumable training is retained;
     - exposure/counter integrity;
     - checkpoint-selection integrity;
     - fail-closed guards for P3, customer delivery and paid compute.
   - Preserve the existing branch regression suite.

7. **Freeze a V3 design receipt before requesting another real-data run.**
   - Record exact candidate ID, source/runtime identities, seed, sampling, loss, sequence length, batch/microbatch, epoch/step budget, checkpoint cadence, resume boundaries, development population and unchanged evaluator thresholds unless a wholly new evaluation protocol is separately justified before seeing new results.
   - No real P1/P2 optimizer run is authorized by this checkpoint.

8. **Only after V3 design + synthetic verification are frozen may a new P1/P2 authorization be requested.**
   - Any future real-data run requires a new explicit user authorization.
   - P3 remains separately sealed even if a later V3 development run passes.
   - No paid compute, published-checkpoint initialization, threshold rescue, allowlist mutation, `main`/Production mutation or customer delivery.

### Immediate next task

Implement the **V3 development error-decomposition tooling and tests** against the already-completed P1/P2 V2 evidence, starting with exact onset/string/fret confusion and false-positive/false-negative accounting. Commit the tooling, tests and resulting diagnostic receipt to `astra-work`, then update this checkpoint again before proposing any V3 training architecture.

This block is the authoritative next action unless a later checkpoint explicitly supersedes it.


## V3 diagnosis tooling active — 2026-09-22

- The immediate V3 diagnosis task from the preceding checkpoint has been implemented on `astra-work`.
- Committed diagnosis components:
  - `astra_backend/guitartechs_training_v2/diagnostics.py` — Git blob `500fa8f9ead07c6d8b444c7ed8ed04e23494e97e`.
  - `astra_backend/guitartechs_training_v2/run_v2_diagnostics.py` — Git blob `cf5348104f2686ad5b16e8e8cdbfd3b9dfedf343`.
  - `.github/workflows/guitar-techs-v3-diagnosis.yml` — Git blob `b3cca652bb7f4ef067491170f400166871423edd`.
  - `docs/astra/GUITARTECHS_V3_DIAGNOSIS_LAUNCH_V1.json` — Git blob `d454f5fc8a579bf2818a8ed5df433b0e567a7268`.
- The diagnostic is intentionally zero-optimizer, P1/P2-development-only analysis. It reproduces the frozen V2 fold metrics before reporting onset/string/fret confusion, temporal run behavior, frame activity, and false-positive/false-negative accounting.
- Two pre-media-access retries are recorded in the launch receipt:
  - run `35801475036`: checkout-expression failure; no P1/P2 media accessed.
  - run `35801584371`: unit-test ordering failure before NumPy install; no P1/P2 media accessed.
- Corrected diagnosis run `35801706358` from commit `43709e19f4b876c020ee4418f2591affb90421dc` is the single active diagnostic run.
- In run `35801706358`, the following have already passed:
  - checkout;
  - exact launch/frozen-identity preflight;
  - exact frozen runtime install plus diagnostic unit tests;
  - pinned TabCNN source acquisition;
  - both frozen V2 final-fold artifact downloads;
  - exact frozen artifact SHA-256 verification.
- Current active step at this checkpoint save: **Prepare exact frozen 256-path P1/P2 development set**.
- Still pending in the same run: zero-optimizer error decomposition, diagnostic guard verification, artifact upload, and cleanup.
- Invariants remain unchanged: V2 development verdict remains FAIL; optimizer steps authorized/executed for diagnosis = 0; P3 sealed; no paid compute; no threshold retuning; no alignment allowlist mutation; no `main`/Production mutation; no customer delivery.

### EXPLICIT NEXT STEP TO RESUME — active V3 diagnosis run 35801706358

1. Inspect run `35801706358` first. **Do not launch a duplicate diagnosis while it is active.**
2. If it completes successfully:
   - fetch artifact `guitar-techs-v2-error-decomposition-v1`;
   - verify the uploaded JSON and its guard block;
   - commit the diagnostic receipt under `docs/astra/`;
   - summarize the P1 and P2 onset/string/fret, temporal-run, activity, FP/FN, and per-content findings without altering the frozen V2 verdict;
   - run/confirm branch regression;
   - update this checkpoint before proposing any V3 architecture or training design.
3. If run `35801706358` fails:
   - inspect the failed step/logs;
   - fix only the diagnosis tooling/orchestration needed to obtain the frozen P1/P2 diagnostic;
   - preserve zero optimizer steps and all existing guards;
   - record the retry reason in the launch receipt before any retry.
4. No real V3 P1/P2 training is authorized by this checkpoint. Any future optimizer run requires a new explicit user authorization after a V3 design + synthetic verification are frozen.
5. P3 remains separately sealed under all outcomes.

This block supersedes only the preceding immediate-task wording and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## V3 diagnosis complete + result frozen — 2026-09-22

- Corrected diagnosis run `35801706358`, job `106993298624`: **PASS**.
- Run head: `43709e19f4b876c020ee4418f2591affb90421dc`.
- Raw diagnostic artifact:
  - name: `guitar-techs-v2-error-decomposition-v1`;
  - artifact ID: `10727022388`;
  - file: `GUITARTECHS_V2_ERROR_DECOMPOSITION_V1.json`;
  - SHA-256: `edf8607c99bebbc19381c602fd06ab8cfcbb647aff0af665b2b0aa81948989b7`.
- Frozen repository diagnosis receipt:
  - `docs/astra/GUITARTECHS_V3_DIAGNOSIS_RESULT_V1.json`;
  - commit: `c5fb60bf9d60a9dd3c919c77ea86a7573007e6fc`.
- Both frozen V2 fold metrics reproduced exactly before diagnosis:
  - P1->P2 selected epoch 720: precision 0.198748, recall 0.355212, F1 0.239542, completeness 0.253153, frame accuracy 0.310546.
  - P2->P1 selected epoch 840: precision 0.150962, recall 0.317509, F1 0.192875, completeness 0.176767, frame accuracy 0.251310.
- Aggregate 256-capture diagnostic:
  - 49,163 reference events vs 106,992 predicted events.
  - 16,693 exact onset+string+fret true positives.
  - 90,299 false-positive events vs 32,470 false negatives; FP/FN ratio **2.781**.
  - exact event micro F1 **0.2138**.
  - onset-only F1 **0.4164**, with onset-only recall **0.6613**.
  - staged onset matching covers 98.51% of the onset-only maximum, so the label-decomposition evidence is representative of onset-matched errors.
- String/fret identity loss is substantial:
  - 11,661 onset-matched events have both string and fret wrong.
  - 8,041 are pitch-correct but assigned to the wrong string.
  - 3,041 have wrong fret on the correct string.
  - strongest off-diagonal string confusions include reference 3->predicted 4 (1,265), 2->3 (1,024), 4->5 (941), and 0->1 (864).
- Temporal decoding is also a primary failure:
  - mean onset-start absolute error is only **18.53 ms**;
  - mean event-end absolute error is **839.66 ms**;
  - mean duration absolute error is **852.57 ms**;
  - 10,490 fragmented reference runs;
  - predicted/reference run ratio **2.176**.
- Content-class pooled diagnostic:
  - scales: event F1 **0.3237**, strongest class;
  - PalmMute: event F1 **0.2807** but very sparse;
  - chords: event F1 **0.1521**, FP/FN **4.491**;
  - singlenotes: event F1 **0.1028**, FP/FN **3.673**.
- Diagnosis conclusion: the V2 failure is not explained by onset start timing or one performer. The main actionable losses are **event over-generation/fragmentation, string/fret identity confusion, and poor run termination/duration decoding**, with chords and singlenotes especially weak.
- Frozen V2 verdict remains **FAIL**. The diagnosis made no threshold or verdict change.
- Diagnosis guards verified:
  - optimizer steps executed: 0;
  - model weights modified: false;
  - thresholds retuned: false;
  - alignment allowlist changed: false;
  - P3 opened: false;
  - paid compute used: false;
  - customer delivery eligible: false;
  - main/Production modified: false.
- Branch regression after the receipt commit was triggered as run `35806272185`; at checkpoint-save time it is still queued. The preceding checkpoint-only regression run `35802127312` passed.

### EXPLICIT NEXT STEP TO RESUME — V3 offline design + synthetic verification

1. **Do not launch real P1/P2 V3 training yet.** No optimizer authorization exists.
2. Convert the frozen diagnosis into a bounded V3 design that directly targets the measured failure modes:
   - activity/silence-aware and class-aware loss/sampling to suppress false-positive event generation without collapsing recall;
   - string/fret representation or loss changes that penalize pitch-correct/wrong-string substitutions and adjacent-string confusion;
   - confidence-aware temporal decoding with minimum-run/merge/termination handling aimed at fragmentation and ~0.85 s end/duration error;
   - preserve onset-start behavior unless synthetic evidence shows a regression.
3. Prefer the smallest architecture/representation changes supported by the diagnosis; do not change architecture merely because V2 failed.
4. Build deterministic synthetic tests that prove:
   - over-generation penalties behave as intended;
   - sparse PalmMute and singlenote examples receive bounded nonzero supervision;
   - adjacent-string/pitch-equivalent confusions receive stronger loss than exact assignments;
   - temporal run decoding reduces synthetic fragmentation and duration error;
   - resume equivalence/counters/checkpoint integrity remain intact if resumable training is retained;
   - P3/customer/paid-compute/main guards fail closed.
5. Freeze a V3 design receipt with exact seed, runtime/source identities, model/representation/loss/sampling/decoder definitions, sequence/batch/microbatch, epoch/step budget, checkpoint cadence and resume boundaries.
6. Run branch regression and a dedicated V3 synthetic verification workflow. No P1/P2 media access is required for this gate.
7. Only after the V3 design + synthetic verification are frozen may a **new explicit user authorization** be requested for a real P1/P2 V3 optimizer run.
8. P3 remains separately sealed regardless of future V3 development outcome.

This block supersedes the active diagnosis-run instructions and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## Guitar-TECHS V3 design + synthetic verification frozen — 2026-09-22

- V3 diagnosis is complete and frozen. The bounded V3 candidate is now:
  - candidate ID: `astra_guitartechs_tabcnn_v3_objective_decoder`;
  - architecture: **unchanged TabCNN**;
  - random initialization only;
  - exact V2 sequence/batch/epoch/optimizer/checkpoint/resume budget retained.
- Frozen V3 design receipt:
  - `docs/astra/GUITARTECHS_V3_DESIGN_V1.json`;
  - Git blob `5074c691c5ec97625849d364a764c73694a86ce5`.
- V3 implementation components:
  - `astra_backend/guitartechs_training_v3/objective_decoder.py`;
  - Git blob `87e127c87851ea9a43b9a9e6240f1a7c4624424b`.
  - `astra_backend/evaluation/test_guitartechs_v3_components.py`;
  - Git blob `18a3c0ffd03366b5c11aa9cac1bb280e9d934dc0`.
  - `astra_backend/guitartechs_training_v3/verify_synthetic_v3.py`;
  - Git blob `36cc9197ae274ab0eee12892813f487427592692`.
- V3 changes are diagnosis-driven and bounded:
  - active-frame loss weight 1.20;
  - bounded inverse-square-root primary-content weighting, cap 0.75..1.50;
  - stable-reference-state continuity regularizer lambda 0.10;
  - exact-string pitch-equivalent margin loss lambda 0.25, margin 0.15;
  - confidence hysteresis decoder: start 0.55, continue 0.35;
  - same-fret silence-gap merge <=2 frames (<=40 ms);
  - active runs shorter than 2 frames (<40 ms) suppressed.
- The architecture itself was intentionally not expanded because the frozen V2 diagnosis did not establish a capacity bottleneck.

### Synthetic verification history

- First V3 synthetic run `35806781928`: **FAIL before TabCNN source acquisition / synthetic optimizer smoke**.
  - runtime + source/guard preflight: PASS;
  - failure: objective reshaped logits using the fixed six-string dimension as the time dimension;
  - no P1/P2 media accessed;
  - no P3 accessed;
  - no real optimizer steps;
  - failure is recorded in `docs/astra/GUITARTECHS_V3_SYNTHETIC_LAUNCH_V1.json`.
- Shape defect fixed in `objective_decoder.py`; design/workflow identities were repinned before retry.
- Corrected V3 synthetic run `35806927973`: **PASS**.
  - exact frozen identity/guard preflight: PASS;
  - exact pinned runtime: Python 3.10.15, NumPy 1.21.6, Torch 1.11.0+cpu;
  - deterministic V3 component unit tests: PASS;
  - exact pinned TabCNN source acquisition: PASS;
  - finite-gradient V3 objective smoke: PASS;
  - bounded content weighting: PASS;
  - pitch-equivalent wrong-string margin behavior: PASS;
  - stable-run continuity penalty behavior: PASS;
  - temporal fragmentation merge + singleton suppression: PASS;
  - true-onset preservation: PASS;
  - uninterrupted vs serialized-resumed TabCNN V3 synthetic optimization:
    - model state equality: PASS;
    - optimizer state equality: PASS;
    - Python/NumPy/Torch RNG equality: PASS.
- Synthetic verification artifact:
  - name: `guitar-techs-v3-synthetic-verification-v1`;
  - artifact ID: `10728630446`;
  - JSON SHA-256: `cf2066cac6da63322d2898b0f4423c461730e7c76fd9bbca56580209b30b6d51`.
- Frozen repository verification receipt:
  - `docs/astra/GUITARTECHS_V3_SYNTHETIC_VERIFICATION_V1.json`;
  - Git blob `e3cc2a9b15c9ee9be779d5e45a547efcae543087`;
  - commit `5f16ef12d4718c83dc60cbd029b01b202554d1d6`.
- Branch regression:
  - launch commit regression run `35806928017`: **PASS**;
  - verification-receipt commit regression run `35807070994`: **PASS**.
- No P1/P2 development media was accessed by either synthetic run.
- P3 was not accessed.
- Real P1/P2 optimizer steps executed: **0**.
- Paid compute used: false.
- Frozen V2 thresholds unchanged.
- Frozen alignment population unchanged.
- `main`/Production/customer delivery unchanged.

### EXPLICIT NEXT STEP TO RESUME — V3 real P1/P2 authorization gate

1. **Do not launch any real V3 optimizer run without a new explicit user authorization.**
2. The V3 design and exact-runtime synthetic verification are now frozen and satisfy the prerequisite gate for requesting authorization.
3. If the user explicitly authorizes the frozen V3 P1/P2 development run:
   - create a new V3 real-training authorization receipt scoped only to `astra_guitartechs_tabcnn_v3_objective_decoder`;
   - preserve the exact frozen 256-path P1/P2 development population;
   - preserve the frozen V2 development thresholds and alignment allowlist;
   - preserve the 1,000-epoch/fold, 200-frame, batch-32, microbatch-1, Adadelta lr=1.0, seed 20260921 budget;
   - preserve serialized resume boundaries 400 -> 800 -> 1000 for P1->P2 and P2->P1;
   - initialize from random weights only;
   - run on public GitHub-hosted CPU runners only;
   - verify every source/runtime/design/authorization identity before P1/P2 media access;
   - SHA-verify every resume artifact before loading;
   - collect final fold results only at epoch 1000;
   - run structural admission first, then the unchanged frozen development metric evaluator.
4. If either V3 fold fails structural admission or frozen development thresholds:
   - freeze V3 development FAIL;
   - diagnose P1/P2 only;
   - do not retune thresholds or rescue the result.
5. If both V3 folds pass:
   - record only **eligible for separate P3 authorization**;
   - **do not open P3 automatically**.
6. Still forbidden without separate authorization:
   - P3 access;
   - paid compute;
   - published-checkpoint initialization;
   - threshold retuning;
   - alignment allowlist mutation;
   - `main`/Production mutation;
   - customer delivery.

This block supersedes the V3 offline-design instructions and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## V3 P1/P2 real training authorized + active launch — 2026-09-22

- User explicitly authorized the immediately preceding frozen V3 P1/P2 development-run gate with: **"I authorize"**.
- Authorization is scoped only to candidate `astra_guitartechs_tabcnn_v3_objective_decoder` exactly as frozen in the preceding checkpoint.
- New authorization receipt:
  - `docs/astra/GUITARTECHS_V3_REAL_TRAINING_AUTHORIZATION_V1.json`;
  - Git blob `133da867fa98b432fa3f7f2248c52cec330181ef`.
- V3 resumable trainer:
  - `astra_backend/guitartechs_training_v3/train_v3_resumable.py`;
  - Git blob `464293f9a7c8fdfe1feb76460c5c370900fc1d53`.
- The trainer preserves the frozen V2 orchestration mechanics but uses the frozen V3 objective and confidence/hysteresis decoder for checkpoint and full-fold evaluation.
- V3 serialized segment workflow:
  - `.github/workflows/guitar-techs-v3-resumable-segment.yml`;
  - Git blob `0565748a7ecf8820023bdec5ba0228ca9d911bbf`.
- V3 controller workflow:
  - `.github/workflows/guitar-techs-v3-resumable-real-training.yml`;
  - Git blob `a0624437940d4f40dd75ddf6234646513cb7c18c`.
- One-time launch marker:
  - `docs/astra/GUITARTECHS_V3_RESUMABLE_LAUNCH_V1.json`;
  - launch commit `d3daf167fad3a04c91d34fe243b371f6c2b9743b`.
- Single authoritative V3 real-training run: **`35808420395`**.
- Fixed execution order:
  - P1 0->400;
  - P1 400->800;
  - P1 800->1000 + full P2 validation;
  - P2 0->400;
  - P2 400->800;
  - P2 800->1000 + full P1 validation.
- Controller preflight authorization/source-identity verification: **PASS**.
- Current state at this checkpoint save: exact frozen runtime installation is in progress. P1/P2 media has not yet been accessed by run `35808420395`.
- No duplicate V3 real-training run may be launched.
- Invariants remain:
  - P3 sealed and unauthorized;
  - public GitHub-hosted CPU only;
  - random initialization only;
  - frozen 256-path P1/P2 population unchanged;
  - frozen development thresholds unchanged;
  - alignment allowlist unchanged;
  - no paid compute;
  - no `main`/Production mutation;
  - no customer delivery.

### EXPLICIT NEXT STEP TO RESUME — active V3 run 35808420395

1. Inspect run `35808420395` first; **do not launch another V3 run**.
2. Require its complete no-media preflight to pass: exact runtime, exact pinned TabCNN source, V3 component/synthetic checks and V3 resumable equality.
3. Only after preflight passes may P1 0->400 reconstruct/access the exact frozen P1/P2 development population and train.
4. At each 400/800 boundary, require the emitted V3 resume receipt and exact resume-state SHA-256 before loading the next segment.
5. Intermediate resume artifacts are orchestration state only, not admissible model-quality evidence.
6. Only epoch-1000 segments may emit final fold model/result artifacts.
7. After both final fold artifacts exist, perform V3 structural admission first, then the unchanged frozen development metric evaluation.
8. If either fold fails, freeze V3 development FAIL and diagnose P1/P2 only; no threshold rescue.
9. If both folds pass, record only **eligible for separate P3 authorization**. P3 remains sealed until a separate explicit authorization.

This block supersedes the V3 authorization-gate instructions and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## V3 launch preflight passed; P1 0->400 active — 2026-09-22

- Authoritative V3 real-training run remains **`35808420395`**; no duplicate run exists or is authorized.
- Controller no-media preflight job `107014273846`: **PASS**.
  - authorization + launch marker identities: PASS;
  - frozen V3 design/objective/trainer/segment identities: PASS;
  - exact runtime installation: PASS;
  - exact pinned TabCNN source acquisition: PASS;
  - V3 component tests: PASS;
  - V3 synthetic objective/decoder smoke: PASS;
  - V3 resumable model/optimizer/RNG equality smoke: PASS.
- No P1/P2 media was accessed by the controller preflight.
- First serialized real segment job `107014479747` (`P1 0->400`) has started.
- At this save point its checkout has completed and runner setup is in progress; its own mandatory authorization/identity gate still precedes media preparation.
- P3 remains sealed and unauthorized.

### EXPLICIT NEXT STEP TO RESUME — run 35808420395 / P1 0->400

1. Inspect run `35808420395` and job `107014479747`; do not launch another run.
2. Require the segment's own authorization/identity and frozen-segment validation steps to pass before media preparation.
3. Allow only the fixed P1 0->400 segment to proceed.
4. On completion require artifact `guitar-techs-v3-p1-resume-e400`, verify its `astra-guitar-techs-v3-resume-receipt-v1` receipt and exact resume-state SHA-256 before P1 400->800 loads it.
5. Continue only through the same serialized controller run.
6. P3 remains sealed regardless of V3 development outcome until separately authorized.

This block supersedes the immediately preceding in-progress preflight status and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## V3 P1 0->400 segment gate passed — 2026-09-22

- Run `35808420395` remains the single authoritative V3 real-training run.
- P1 0->400 job `107014479747`:
  - checkout: PASS;
  - setup Python: PASS;
  - V3 authorization/frozen identity gate before media access: PASS;
  - requested frozen segment validation: PASS;
  - current step: exact frozen runtime installation.
- P1/P2 media preparation has not yet begun at this checkpoint save.
- Continue the same job only; next permitted steps are pinned runtime -> pinned TabCNN source -> exact 256-path P1/P2 preparation -> P1 0->400 training.
- No duplicate launch. P3 remains sealed.

This is the latest active-run status and supersedes the prior P1 setup-status wording.


## V3 real training complete — structural PASS / development FAIL — 2026-09-23

- Authoritative V3 real-training run `35808420395`: **completed successfully**.
- All serialized jobs passed:
  - preflight;
  - P1 0->400;
  - P1 400->800;
  - P1 800->1000;
  - P2 0->400;
  - P2 400->800;
  - P2 800->1000.
- Frozen V3 development result:
  - `docs/astra/GUITARTECHS_V3_DEVELOPMENT_RESULT_V1.json`;
  - Git blob `b044d5c0fe95dfceb6218b202935e78f2c3d82b7`;
  - commit `10f683cd0059edaac51b8add06ba609b07c1d0bb`.
- Frozen V3 result-level failure diagnosis:
  - `docs/astra/GUITARTECHS_V3_DEVELOPMENT_FAILURE_DIAGNOSIS_V1.json`;
  - Git blob `8cfca668c425de2159fc01902d91734adac68e15`;
  - commit `4ccffa1a2b39580bf82c049a7a9dcfc2857048f1`.

### V3 structural admission

- **PASS** with zero structural blockers.
- Both final model SHA-256 values match their fold receipts.
- Both embedded selected-state hashes match the selected checkpoint receipts.
- All four resume-state artifacts were downloaded and SHA-verified:
  - P1 e400: `1d2dd005f6172882e8a6550ef46241d2c8c44237eb071448802293e4e03a0ad3`;
  - P1 e800: `5a00b535e80ee8ed45927bf9553162e7a6592d519a5d7c73791bef0c0c437540`;
  - P2 e400: `351679f922b7051b6872f5c9ea6dd9d03aacd74a1bad988b7055de51fda83684`;
  - P2 e800: `f2139c5f9a410d0914d103b4556c6988f73da96058a79695022af5ac9872c565`.
- Resume receipts have the expected V3 schema, candidate, fold, epoch, optimizer-step, supervised-frame, frozen source identities and sealed guards.
- Final fold evidence has the expected:
  - candidate `astra_guitartechs_tabcnn_v3_objective_decoder`;
  - seed 20260921;
  - 1,000 epochs;
  - 2,000 optimizer steps;
  - 200-frame sequences;
  - batch 32 / microbatch 1;
  - 50 validation checkpoints;
  - P1/P2 capture counts 136/120;
  - 41/40 training performances;
  - 8.2M / 8.0M supervised frame positions.
- P3 false, published checkpoint false, paid compute false, customer delivery false.

### V3 frozen development metrics

- P1->P2:
  - selected checkpoint epoch **1000**;
  - precision **0.252871**;
  - recall **0.330380**;
  - F1 **0.282208**;
  - completeness **0.275084**;
  - frame accuracy **0.302055**;
  - content F1: chords **0.264675**, scales **0.327514**, singlenotes **0.201161**, PalmMute **0.275417**.
- P2->P1:
  - selected checkpoint epoch **880**;
  - precision **0.169037**;
  - recall **0.232989**;
  - F1 **0.192695**;
  - completeness **0.152408**;
  - frame accuracy **0.250116**;
  - content F1: chords **0.135705**, scales **0.325041**, singlenotes **0.085388**, PalmMute **0.250606**.
- Aggregate:
  - macro F1 **0.237452** vs frozen minimum **0.70**;
  - macro completeness **0.213746** vs frozen minimum **0.65**;
  - cross-performer F1 gap **0.089512** -> PASS <= 0.10;
  - cross-performer frame-accuracy gap **0.051938** -> PASS <= 0.10;
  - abstention 0.0 both folds -> PASS.
- Frozen metric decision: **FAIL**, 20 threshold blockers.
- Both folds fail precision, recall, F1, completeness, frame accuracy, and all four per-content F1 minimums.
- Thresholds were not changed or retuned.

### V3 vs V2 evidence

- Macro F1 improved from **0.216208** to **0.237452**:
  - absolute +**0.021243**;
  - about **+9.8% relative**.
- Macro completeness was essentially flat/slightly worse:
  - **0.214960 -> 0.213746**.
- P1->P2 improved materially:
  - precision +0.054122;
  - F1 +0.042666;
  - completeness +0.021931;
  - chords +0.066444 F1;
  - singlenotes +0.070401 F1;
  - but recall -0.024832 and frame accuracy -0.008491.
- P2->P1 did not improve:
  - precision +0.018075;
  - F1 -0.000179;
  - recall -0.084519;
  - completeness -0.024359.
- Result-level interpretation:
  - V3 improved precision more than recall and appears too conservative on part of the P1/P2 population;
  - gains are concentrated in P1->P2 rather than symmetric across folds;
  - scales remain strongest and singlenotes weakest;
  - P2->P1 selection-subset performance peaked before epoch 1000, so simply adding epochs is not an evidence-supported next move.

### Decision

- **V3 development status: FAIL.**
- P3 is **not eligible** to open and remains sealed.
- No customer delivery.
- No threshold rescue.
- No further real P1/P2 optimizer run is authorized.
- Any future real-data optimizer run requires a new frozen design and new explicit user authorization.

### EXPLICIT NEXT STEP TO RESUME — zero-optimizer V3 P1/P2 error decomposition

1. Do **not** launch another real V3 optimizer run.
2. Build/run a zero-optimizer diagnostic against the already-completed V3 P1/P2 evidence only.
3. Reconstruct exact V3 predictions with the frozen V3 decoder and decompose:
   - onset detection;
   - activity FP/FN balance;
   - string assignment;
   - fret assignment;
   - pitch-correct wrong-string substitutions;
   - fragmentation/merge behavior;
   - event-end/duration error;
   - chords/scales/singlenotes/PalmMute;
   - performer-disjoint differences.
4. Compare the V3 decomposition directly against the frozen V2 decomposition to identify which V3 changes helped and which over-corrected recall/completeness.
5. No optimizer steps, no threshold retuning, no alignment changes, no P3, no paid compute, no `main`/Production/customer-delivery changes.
6. Freeze that diagnostic before forming any V4 design hypothesis.
7. Any V4 real P1/P2 run requires a new frozen design + synthetic verification + new explicit user authorization.

This block supersedes the active-training instructions and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## V3 zero-optimizer error decomposition active — 2026-09-23

- User requested learning from V3 and rewiring for better results.
- Per the frozen V3 FAIL checkpoint, no V4 design is to be frozen until a zero-optimizer V3 P1/P2 decomposition is complete.
- New diagnostic runner:
  - `astra_backend/guitartechs_training_v3/run_v3_diagnostics.py`;
  - Git blob `899c09f0c1e1928f85e29cb1437437d99764f5d0`.
- New diagnostic workflow:
  - `.github/workflows/guitar-techs-v3-error-decomposition.yml`;
  - Git blob `61b9396cafe192277dd97e9b77f7b4781ec2a2c4`.
- Launch receipt:
  - `docs/astra/GUITARTECHS_V3_ERROR_DECOMPOSITION_LAUNCH_V1.json`;
  - Git blob `141c39d170939e2fe1d676bf9400b241e31eab3d`;
  - launch commit `21bfe44692ba81c02c54a841470d1ff5ff02d150`.
- Single authoritative diagnostic run: **`35953249703`**.
- Diagnostic job: `107486086247`.
- Frozen-identity/zero-optimizer guard: **PASS**.
- Exact runtime: **PASS**.
- Exact pinned TabCNN source: **PASS**.
- Frozen V3 P1/P2 final artifacts downloaded and SHA-verified: **PASS**.
- Current active step: reconstructing the exact frozen 256-path P1/P2 development set.
- No optimizer steps are authorized or executed by this diagnostic.
- P3 remains sealed.
- Thresholds, alignment allowlist, main/Production, and customer delivery remain unchanged.

### EXPLICIT NEXT STEP TO RESUME — V3 decomposition run 35953249703

1. Inspect run `35953249703` first; do not launch a duplicate diagnostic.
2. Allow only the zero-optimizer decomposition to complete against the exact frozen 256-path P1/P2 population.
3. Require exact reproduction of both frozen V3 fold metrics before accepting the diagnostic output.
4. Freeze the resulting V3 decomposition receipt and compare it directly to the frozen V2 decomposition.
5. Only after that comparison is frozen may a bounded V4 design hypothesis be committed.
6. Any V4 real P1/P2 optimizer run requires a new frozen V4 design, exact-runtime synthetic verification, and a new explicit user authorization.
7. P3 remains separately sealed regardless of V4 development work.

This block supersedes the completed-V3 next-step wording and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## V3 zero-optimizer diagnosis retry after path-only failure — 2026-09-23

- First V3 decomposition run `35953249703`: **FAIL**.
- All frozen-evidence preparation steps passed before failure:
  - launch/source guard PASS;
  - exact runtime PASS;
  - pinned TabCNN source PASS;
  - frozen V3 P1/P2 final artifact download + SHA verification PASS;
  - exact frozen 256-path P1/P2 reconstruction PASS.
- Failure occurred at the decomposition invocation itself before any model inference:
  - workflow incorrectly called `astra_backend/guitartechs_training_v2/run_v3_diagnostics.py`;
  - frozen runner actually exists at `astra_backend/guitartechs_training_v3/run_v3_diagnostics.py`.
- No model weights changed.
- Optimizer steps executed: **0**.
- P3 opened: **false**.
- Failed run produced no accepted diagnostic artifact.
- Workflow path-only fix:
  - commit `5b898bfda0e00239326902853d55662c914b98dd`;
  - corrected workflow Git blob `4f045f64cb12e1cd84096ef156c7d7ecfe08fefe`.
- Launch receipt was repinned and failure/retry history recorded:
  - commit `cbbadd4bb7bac0e98ca770ea27f1ee241c77ea4a`;
  - launch receipt Git blob `0af38d29a831c45ac74d5aa4d574ce4540daca5e`.
- Corrected authoritative retry run: **`35955722006`**.
- Retry diagnostic job: `107493514365`.
- At this checkpoint save, checkout has passed and setup Python is in progress.
- No model/decoder/threshold/data-population/guard change was made for the retry.

### EXPLICIT NEXT STEP TO RESUME — corrected V3 decomposition retry 35955722006

1. Inspect run `35955722006` first; do not launch another retry.
2. Require zero-optimizer/source-identity preflight to pass.
3. Require exact runtime, pinned TabCNN source, frozen V3 fold artifacts and exact 256-path population to pass again.
4. Run only `astra_backend/guitartechs_training_v3/run_v3_diagnostics.py`.
5. Require exact reproduction of both frozen V3 fold metrics before accepting the decomposition.
6. Freeze the resulting V3 error-decomposition receipt and compare it directly with the frozen V2 decomposition.
7. Do not freeze V4 real-training authorization from this retry alone; V4 requires frozen design + synthetic verification + new explicit user authorization.
8. P3 remains sealed.

This block supersedes the prior active-decomposition run ID and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## V3 diagnosis frozen; V4 design + synthetic verification PASS — 2026-09-24

- Corrected V3 zero-optimizer decomposition run `35955722006`: **SUCCESS**.
- Job `107493514365`: **SUCCESS**.
- Raw diagnostic artifact:
  - `guitar-techs-v3-error-decomposition-v1`;
  - artifact ID `10791358034`;
  - archive digest `sha256:7237285c4b94e800c6d06a561de266ac4f14cbf30a5fd38190a22179e3e53400`;
  - JSON SHA-256 `542ceafa228022d80efccf642c393ebb57e131958f9ebff488cfc62af4776297`.
- Frozen V3 decomposition result:
  - `docs/astra/GUITARTECHS_V3_ERROR_DECOMPOSITION_RESULT_V1.json`;
  - Git blob `87ec9fb53fd025bd2d5c2b00a15b9bcd035b4433`;
  - commit `35da86244a902a369bb473b14241b82808cc8c09`.
- Both frozen V3 fold metrics reproduced exactly: **PASS**.
- Guards:
  - optimizer steps executed 0;
  - model weights modified false;
  - thresholds retuned false;
  - alignment allowlist changed false;
  - P3 opened false;
  - paid compute false;
  - main/Production unchanged;
  - customer delivery false.

### What V3 actually fixed

- Predicted event runs: **106,992 -> 66,876** (-37.5%).
- Event false positives: **90,299 -> 52,308** (-42.1%).
- Event micro F1: **0.2138 -> 0.2511** (+17.4% relative).
- Onset-only F1: **0.4164 -> 0.5065** (+21.6% relative).
- Fragmented reference runs: **10,490 -> 4,219** (-59.8%).
- Predicted/reference run ratio: **2.176 -> 1.360**.
- Mean end absolute error: **839.7 ms -> 588.1 ms**.
- Mean duration absolute error: **852.6 ms -> 600.7 ms**.
- Mean reference overlap: **0.6358 -> 0.7481**.

### What V3 over-corrected / failed to fix

- Exact event true positives: **16,693 -> 14,568** (-12.7%).
- Event false negatives: **32,470 -> 34,595** (+6.5%).
- Onset-only recall: **0.6613 -> 0.5977**.
- Predicted active frames were almost unchanged: **2,545,696 -> 2,547,272**.
- Exact-active frames fell: **1,474,195 -> 1,445,215**.
- Activity false positives rose: **421,527 -> 489,796**.
- Activity false negatives rose: **1,499,216 -> 1,565,909**.
- Pitch-correct wrong-string onset matches rose: **8,041 -> 8,695**.
- The P2->P1 fold carries the strongest recall/completeness regression.
- Scales remain comparatively stable; chords and singlenotes remain the key weak classes.

### Frozen V4 candidate

- Candidate ID: `astra_guitartechs_tabcnn_v4_recall_routing`.
- Frozen V4 design:
  - `docs/astra/GUITARTECHS_V4_DESIGN_V1.json`;
  - Git blob `376ece1578d9adfb998600e85cfbb6b39523951f`;
  - commit `6b83b5244ba95733c6129536c1355d752f64f20b`.
- V4 objective/decoder:
  - `astra_backend/guitartechs_training_v4/objective_decoder.py`;
  - Git blob `b9a96f6b256de52bfbb5076482a03263415213cb`.
- V4 component tests:
  - `astra_backend/evaluation/test_guitartechs_v4_components.py`;
  - Git blob `b494fa2ef8cae8cece9a5e9a98fe308e86c6ed64`.
- V4 exact-runtime synthetic harness:
  - `astra_backend/guitartechs_training_v4/verify_synthetic_v4.py`;
  - Git blob `dad761b59668969669a785ec89f0aed4b29a8248`.

### V4 diagnosis-driven changes

- Architecture remains unchanged TabCNN.
- Training budget remains frozen from V3/V2.
- Preserve V3 temporal scaffold that improved fragmentation:
  - strong start confidence 0.55;
  - continuation confidence 0.35;
  - continuation vs silence ratio 0.80;
  - same-fret silence-gap merge <=2 frames;
  - minimum active run 2 frames.
- Active-reference supervision increases modestly **1.20 -> 1.30**.
- Add a bounded confirmed-start path:
  - first-frame active confidence >=0.42;
  - first-frame active/silence ratio >=0.90;
  - same fret next frame confidence >=0.35;
  - next-frame active/silence ratio >=0.80;
  - admits the onset at its original first frame;
  - unconfirmed weak spikes remain rejected.
- Pitch-equivalent wrong-string margin strength remains 0.25 / margin 0.15, but semantics are repaired:
  - do not penalize an alternative string when its reference target is MASK;
  - do not penalize it when that alternative string is legitimately labeled at the exact same-pitch fret.
- Continuity regularizer and bounded content weighting remain unchanged.
- Frozen acceptance thresholds and alignment population remain unchanged.

### V4 exact-runtime synthetic verification

- Run `35960496515`: **SUCCESS**.
- Head `19ffb70bae9ca670f7eac847052c140b2670e322`.
- Artifact:
  - `guitar-techs-v4-synthetic-verification-v1`;
  - artifact ID `10792295752`;
  - archive digest `sha256:c1e50fff51b86908c21c5ef1ac57471460923b8c05dbf005bafebdda2ce9b13c`;
  - JSON SHA-256 `736acd0961cdfa3dde8ed1f00c543df8ae54e87f1488549b65b0ffe354f9ca1a`.
- Frozen repository verification receipt:
  - `docs/astra/GUITARTECHS_V4_SYNTHETIC_VERIFICATION_V1.json`;
  - Git blob `892ce3c88d68accef4c13aea6220c6ffd1cd22a5`;
  - commit `c1fc6b31f81d3487f3aa7e1f903a2d7728c85ab4`.
- Exact runtime:
  - Python 3.10.15;
  - NumPy 1.21.6;
  - Torch 1.11.0+cpu.
- PASS:
  - component unit tests;
  - finite-gradient V4 objective;
  - bounded content weights;
  - stronger active-reference weighting;
  - wrong-string pitch-equivalent routing penalty;
  - no penalty for legitimate same-pitch multi-string reference note;
  - continuity penalty;
  - V3-style gap merge + singleton suppression;
  - confirmed low-confidence onset recovery;
  - unconfirmed low-confidence spike rejection;
  - strong onset preservation;
  - exact model-state resume equality;
  - exact optimizer-state resume equality;
  - exact Python/NumPy/Torch RNG resume equality.
- P1/P2 media accessed: false.
- P3 accessed: false.
- Real optimizer steps executed: 0.
- Paid compute used: false.

### EXPLICIT NEXT STEP TO RESUME — V4 real P1/P2 authorization gate

1. **Do not launch any V4 real optimizer run without a new explicit user authorization.**
2. V4 design and exact-runtime synthetic verification are frozen and satisfy the offline prerequisite gate.
3. If the user explicitly authorizes the frozen V4 P1/P2 development run:
   - create a V4 real-training authorization receipt scoped only to `astra_guitartechs_tabcnn_v4_recall_routing`;
   - preserve the exact frozen 256-path P1/P2 population;
   - preserve frozen development thresholds and alignment allowlist;
   - preserve 1,000 epochs/fold, 200-frame sequences, batch 32, microbatch 1, Adadelta lr=1.0, seed 20260921;
   - preserve serialized resume boundaries 400 -> 800 -> 1000 for P1->P2 and P2->P1;
   - random weights only;
   - public GitHub-hosted CPU only;
   - verify all source/runtime/design/authorization identities before P1/P2 media access;
   - SHA-verify every resume artifact before loading;
   - evaluate with the frozen V4 decoder;
   - collect final fold evidence only at epoch 1000;
   - run structural admission first, then the unchanged frozen development metric evaluator.
4. If either V4 fold fails structural admission or frozen development thresholds:
   - freeze V4 development FAIL;
   - diagnose P1/P2 only;
   - no threshold rescue.
5. If both pass:
   - record only eligible for separate P3 authorization;
   - do not open P3 automatically.
6. Still forbidden without separate authorization:
   - P3 access;
   - paid compute;
   - published-checkpoint initialization;
   - threshold retuning;
   - alignment allowlist mutation;
   - main/Production mutation;
   - customer delivery.

This block supersedes the V3 diagnosis-retry instructions and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## V4 P1/P2 real training authorized + active launch — 2026-09-24

- User explicitly authorized preparation and execution of the frozen V4 development run with: **"Please prepare and run V4"**.
- Authorization is scoped only to candidate `astra_guitartechs_tabcnn_v4_recall_routing` and the frozen P1/P2 development protocol.
- Authorization receipt:
  - `docs/astra/GUITARTECHS_V4_REAL_TRAINING_AUTHORIZATION_V1.json`;
  - Git blob `427ca9fb3ccd7a406b2935ae75216d7591816efe`;
  - authorization commit `01e850e54257d55e11c2c183ffcbbae4fc3c16d4`.
- V4 resumable trainer:
  - `astra_backend/guitartechs_training_v4/train_v4_resumable.py`;
  - Git blob `33892a222825a2713d3955cc34139b730f4adc3d`.
- V4 serialized segment workflow:
  - `.github/workflows/guitar-techs-v4-resumable-segment.yml`;
  - Git blob `d017f2c322a46cfefa6b9e939394c40142c6fb8a`.
- V4 controller workflow:
  - `.github/workflows/guitar-techs-v4-resumable-real-training.yml`;
  - Git blob `1b30139da602a2a11bfdebf2c53d856141a833f8`.
- One-time launch marker:
  - `docs/astra/GUITARTECHS_V4_RESUMABLE_LAUNCH_V1.json`;
  - launch commit `19b629c549f11eedae0e7c22a2a2a42f9adc342e`.
- Single authoritative V4 real-training run: **`35961115171`**.
- Fixed execution order:
  - P1 0->400;
  - P1 400->800;
  - P1 800->1000 + full P2 validation;
  - P2 0->400;
  - P2 400->800;
  - P2 800->1000 + full P1 validation.
- Controller launch/source identity gate: **PASS**.
- Current state at this checkpoint save: exact frozen runtime installation is in progress.
- No P1/P2 media has been accessed by the controller preflight.
- No duplicate V4 real-training run may be launched.
- Invariants remain:
  - P3 sealed and unauthorized;
  - public GitHub-hosted CPU only;
  - random initialization only;
  - frozen 256-path P1/P2 population unchanged;
  - frozen development thresholds unchanged;
  - alignment allowlist unchanged;
  - no paid compute;
  - no published-checkpoint initialization;
  - no `main`/Production mutation;
  - no customer delivery.

### EXPLICIT NEXT STEP TO RESUME — active V4 run 35961115171

1. Inspect run `35961115171` first; **do not launch another V4 run**.
2. Require its complete no-media preflight to pass: exact runtime, exact pinned TabCNN source, V4 component/synthetic checks and V4 resumable equality.
3. Only after preflight passes may P1 0->400 reconstruct/access the exact frozen P1/P2 development population and train.
4. At each 400/800 boundary, require the emitted V4 resume receipt and exact resume-state SHA-256 before loading the next segment.
5. Intermediate resume artifacts are orchestration state only, not admissible model-quality evidence.
6. Only epoch-1000 segments may emit final fold model/result artifacts.
7. After both final fold artifacts exist, perform V4 structural admission first, then the unchanged frozen development metric evaluation.
8. If either fold fails, freeze V4 development FAIL and diagnose P1/P2 only; no threshold rescue.
9. If both folds pass, record only **eligible for separate P3 authorization**. P3 remains sealed until separately authorized.

This block supersedes the V4 authorization-gate instructions and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## V4 controller preflight PASS; P1 0->400 gate PASS — 2026-09-24

- Authoritative V4 real-training run remains **`35961115171`**; no duplicate V4 run exists or is authorized.
- Controller preflight job `107509698358`: **PASS**.
  - V4 authorization + launch source identities: PASS;
  - exact frozen runtime: PASS;
  - exact pinned TabCNN source: PASS;
  - deterministic V4 component tests: PASS;
  - exact-runtime V4 synthetic objective/decoder smoke: PASS;
  - V4 resumable model/optimizer/Python/NumPy/Torch RNG equality: PASS.
- Controller preflight accessed no P1/P2 media.
- First serialized segment job `107509990950` (`P1 0->400`) is active.
- P1 0->400:
  - checkout: PASS;
  - setup Python: PASS;
  - V4 authorization/frozen identity gate before media access: PASS;
  - requested frozen segment validation: PASS;
  - current step: exact frozen runtime installation.
- P1/P2 media preparation had not yet begun at this checkpoint save.
- Continue the same controller run only. No duplicate launch.
- P3 remains sealed and unauthorized.

### EXPLICIT NEXT STEP TO RESUME — run 35961115171 / P1 0->400

1. Inspect run `35961115171` and job `107509990950`; do not launch another V4 run.
2. Continue the fixed P1 0->400 segment through pinned runtime -> pinned TabCNN source -> exact frozen 256-path preparation -> bounded V4 training.
3. On completion require artifact `guitar-techs-v4-p1-resume-e400`.
4. Verify its `astra-guitar-techs-v4-resume-receipt-v1` receipt and exact resume-state SHA-256 before P1 400->800 loads it.
5. Continue only through this same serialized controller:
   P1 0->400 -> 400->800 -> 800->1000 -> P2 0->400 -> 400->800 -> 800->1000.
6. Intermediate resume states are not model-quality evidence.
7. P3 remains sealed regardless of V4 development outcome until separately authorized.

This block supersedes the immediately preceding V4 launch-preflight status and is the authoritative next action unless a later checkpoint explicitly supersedes it.


## V4 real training complete — structural PASS / development FAIL — 2026-09-25

- Authoritative V4 real-training run `35961115171`: **completed successfully**.
- All serialized jobs passed:
  - preflight;
  - P1 0->400;
  - P1 400->800;
  - P1 800->1000;
  - P2 0->400;
  - P2 400->800;
  - P2 800->1000.
- Frozen V4 development result:
  - `docs/astra/GUITARTECHS_V4_DEVELOPMENT_RESULT_V1.json`;
  - Git blob `f4ceb5858265f5e6d90bc1efe052a494e7449217`;
  - commit `87877ed481738b6523dd3d3e3359158b554d0d86`.
- Frozen V4 result-level failure diagnosis:
  - `docs/astra/GUITARTECHS_V4_DEVELOPMENT_FAILURE_DIAGNOSIS_V1.json`;
  - Git blob `c973b0699153cd7661dfe9b90613a0583e0602d0`;
  - commit `5bbc3df5008a626f8e40641eeec9c31d7c15e563`.

### V4 structural admission

- **PASS** with zero structural blockers.
- Both final model SHA-256 values match their fold receipts.
- Both embedded selected checkpoint state hashes match their receipts.
- All four resume-state artifacts were downloaded and SHA-verified:
  - P1 e400: `94f9451231d112a0f3544a2ae085ef3679cfc80741e69f11dee302089e14ee02`;
  - P1 e800: `9ca1e1f0a8a69d0e3fd168ab1f759a3dc7b32968ad3829f28184af4186ac4e0f`;
  - P2 e400: `16f0ccb94a985d29c1a43ed63aec5d42beef0cefd0e3429c0e077abd9c713d77`;
  - P2 e800: `c021b0d81a1e3e3cb105bd9426f6e6d0be559599bf228ec71f7a1af99e1cec11`.
- Resume receipts have the expected V4 schema, candidate, fold, epoch, optimizer-step, supervised-frame, frozen source identities and sealed guards.
- Final fold evidence has the expected:
  - candidate `astra_guitartechs_tabcnn_v4_recall_routing`;
  - seed 20260921;
  - 1,000 epochs;
  - 2,000 optimizer steps;
  - 200-frame sequences;
  - batch 32 / microbatch 1;
  - 50 validation checkpoints;
  - P1/P2 capture counts 136/120;
  - 41/40 training performances;
  - 8.2M / 8.0M supervised frame positions.
- P3 false, published checkpoint false, paid compute false, customer delivery false.

### V4 frozen development metrics

- P1->P2:
  - selected checkpoint epoch **720**;
  - precision **0.253222**;
  - recall **0.352063**;
  - F1 **0.286036**;
  - completeness **0.273441**;
  - frame accuracy **0.312087**;
  - content F1: chords **0.262774**, scales **0.340622**, singlenotes **0.180278**, PalmMute **0.341584**.
- P2->P1:
  - selected checkpoint epoch **400**;
  - precision **0.165136**;
  - recall **0.271663**;
  - F1 **0.201009**;
  - completeness **0.170875**;
  - frame accuracy **0.245870**;
  - content F1: chords **0.129230**, scales **0.365168**, singlenotes **0.094804**, PalmMute **0.275348**.
- Aggregate:
  - macro F1 **0.243523** vs frozen minimum **0.70**;
  - macro completeness **0.222158** vs frozen minimum **0.65**;
  - cross-performer F1 gap **0.085027** -> PASS <= 0.10;
  - cross-performer frame-accuracy gap **0.066217** -> PASS <= 0.10;
  - abstention 0.0 both folds -> PASS.
- Frozen metric decision: **FAIL**, 20 threshold blockers.
- Both folds fail precision, recall, F1, completeness, frame accuracy, and all four per-content F1 minimums.
- Thresholds were not changed or retuned.

### V4 vs V3 evidence

- Macro F1:
  - **0.237452 -> 0.243523**;
  - absolute +**0.006071**;
  - about **+2.56% relative**.
- Macro completeness:
  - **0.213746 -> 0.222158**;
  - absolute +**0.008412**.
- P1->P2:
  - recall +0.021683;
  - F1 +0.003829;
  - frame accuracy +0.010032;
  - PalmMute F1 +0.066167;
  - scales +0.013108;
  - singlenotes -0.020884;
  - chords -0.001901.
- P2->P1:
  - recall +0.038674;
  - F1 +0.008314;
  - completeness +0.018466;
  - scales +0.040128;
  - PalmMute +0.024742;
  - singlenotes +0.009416;
  - chords -0.006475.
- Relative to V2, V4 macro F1 is about **12.6% higher**, but absolute quality remains far below the frozen acceptance target.
- Both selected checkpoints moved earlier than V3 (P1 epoch 720, P2 epoch 400), so simply adding epochs is not evidence-supported.

### Decision

- **V4 development status: FAIL.**
- P3 is **not eligible** to open and remains sealed.
- No customer delivery.
- No threshold rescue.
- No further real P1/P2 optimizer run is authorized.
- Any future real-data optimizer run requires a new frozen design and new explicit user authorization.

### EXPLICIT NEXT STEP TO RESUME — zero-optimizer V4 P1/P2 error decomposition

1. Do **not** launch another V4 optimizer run.
2. Build/run a zero-optimizer V4 diagnostic against the completed V4 P1/P2 evidence only.
3. Reconstruct exact V4 predictions with the frozen V4 decoder and compare directly against V3:
   - event TP/FP/FN;
   - onset-only precision/recall/F1;
   - frame activity exact/FP/FN;
   - pitch-correct wrong-string and string/fret confusion;
   - fragmentation/merge behavior;
   - event-end/duration error;
   - chords/scales/singlenotes/PalmMute;
   - performer-disjoint differences.
4. Determine whether the V4 recall gains preserved V3's temporal improvements and whether remaining chord/singlenote/string-routing failures justify a V5 architecture or representation change rather than another global decoder tweak.
5. No optimizer steps, no threshold retuning, no alignment changes, no P3, no paid compute, no `main`/Production/customer-delivery changes.
6. Freeze that diagnostic before any V5 design hypothesis.
7. Any V5 real P1/P2 run requires a new frozen design + synthetic verification + new explicit user authorization.

This block supersedes the active-V4-run instructions and is the authoritative next action unless a later checkpoint explicitly supersedes it.
