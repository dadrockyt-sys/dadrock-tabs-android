# New Astra Work — CURRENT STATE

Updated: 2026-09-20 UTC
Active branch: `astra-work`
Canonical handoff: `docs/checkpoints/CURRENT_STATE.md`
Status: **SOURCE RHYTHM + SOUNDING-ATTACK PITCH REVIEW COMPLETE FOR M1–16 — INDEPENDENT AUDIO TIMING MAP STILL OPEN**

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

## Exact next step — Independently align and validate scoring labels

1. Keep the 87-event candidate frozen. Pitch/rhythm source review is now complete in private revision6; do not reopen the15 later bends. Build the independent timing map from the exact recording and professional-source beat positions, never from prediction matching. The repeated-opening attack observations may be used as audio evidence but are not automatically approved anchors.
2. Use private `Gomyway-Reference-Draft-M1-16-r6.json` SHA256 `5f040af4d7daa2eb6b74445bfe46e72f5847e2410ec21d3f01d603630edcd977` as the frozen musical-side source. Its only unresolved items are timing/alignment. Map its reviewed beat positions onto independently confirmed audio anchors; keep normalized labels outside public Git.
3. Freeze the verified scoring map and pitch/bend rules, populate the reviewed-bundle spec with exact private file hashes, then use score_reviewed_bundle.py once on the frozen candidate. Report TP/FP/FN and timing separately from role accuracy. The whole-mix baseline has no role labels and cannot demonstrate three-role separation.
4. Preserve existing CPU/model/resource gates. Save actual results or unresolved blockers with this checkpoint on astra-work, verify remote/tree and clean local status. Avoid unnecessary full-suite/model reruns and do not alter main/Production.

## Copy-paste handoff

Continue Jimmy PAIge from `docs/checkpoints/CURRENT_STATE.md` on branch `astra-work` in `dadrockyt-sys/dadrock-tabs-android`. Read AGENTS.md first. Both V143/Gomyway and Songsterr Fresh are archived; do not resume their old task queues. Work on the active Astra milestone, preserve historical outcomes, and commit/push clean backend work plus this checkpoint after each major step. Do not modify main or Production.
