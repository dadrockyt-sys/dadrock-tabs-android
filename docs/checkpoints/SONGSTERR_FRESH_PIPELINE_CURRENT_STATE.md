# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-12 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT, reference/pro scoring, duration research, broad threshold/optimizer sweeps, training/fine-tuning remain closed unless explicitly reopened.
- Never silently alter/drop MIDI or event identity. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP work stays under `scripts/songsterr-fresh/`.
- Authority remains fail-closed: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, persistent Policy C `UNENROLLED`.
- Protected song remains embargoed until V5 passes external validation and a separate policy review explicitly approves it.

## HISTORICAL CLOSED LINES

V1/V2 are rejected research diagnostics. V3/GuitarSet and V4/IDMT are closed and contaminated for future untouched-holdout use. Do not rerun/tune them.

V4 final: 568/568 files, 7,619 decoded, 1,644 positive, 1,292 correct, precision `0.7858880778588808`, one-sided 95% Wilson LB `0.7687844934184139` vs required `0.9900` → FAIL. Artifact SHA-256 `d97ea2c7f004876fc43f6c3d2e28e4838df86a4a4c4a8bc8f8a2a98ab5e37d2c`; result commit `303e048f07d58370ab3256cdc226cdfd3628cf8a`; policy rejection `01a276045d32b643aa17013b959e89e41b0f305e`.

## V5 — ACTIVE / SYNTHETIC CONTRACT GREEN

User explicitly authorized V5 on 2026-09-12.

Preregistration: `docs/checkpoints/SONGSTERR_FRESH_MODEL_EVIDENCE_ADMISSION_PREREGISTRATION_V5.md`, commit `beb80f32311bd0b713b78d81049d68dbeec7afe3`.
Contract: `songsterr-fresh-polyphonic-harmonic-necessity-corroboration-research-v5`.
Implementation: `scripts/songsterr-fresh/independent_pitch_corroboration_v5.py`, commit `0b02fc949ba9fa0e3fac6b2edb9f19002f58fc99`.

Frozen V5 constants: mono 44.1 kHz; MIDI 40..88; 8192-sample windows at offsets 2048/8192/14336; FFT 32768; 8 harmonics; NNLS; RMS min `1e-4`; necessity fraction min `0.01`; fundamental/max-harmonic ratio min `0.05`; all 3 views required; NumPy 1.26.4; SciPy 1.15.3. No duration/end, confidence/activation, reference truth, performer/style/dataset identity or event rewriting.

20-case synthetic contract is green (`13 corroborated / 4 not / 3 insufficient`). Synthetic success is not admission evidence.

## FLGD HOLDOUT — FROZEN SOURCE

François Leduc Guitar Dataset:
- HF `xavriley/FrancoisLeducGuitarDataset`
- canonical origin `https://huggingface.co/datasets/xavriley/FrancoisLeducGuitarDataset`
- exact revision `a38306c244b3ea81496ad58b4514622185e58211`
- selected release declares MIT
- media stays outside app repo / must not be redistributed.

### Stage A — COMPLETE / NO SCORING

Real inventory run `34719034991`, job `103621353045`: SUCCESS.
Immutable record `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_EXTERNAL_VALIDATION_STAGE_A_RESULT.md`, commit `b536f5c5eb479689fdd0d4d949b2715175d712aa`.
Report SHA-256 `f03d6e3b9549a13dbcc9557ec6f13516fb52ac9d4fbf64138a0bb008b7a891b3`.

Observed: 79 canonical `audio/` MP3 + 79 canonical `midi/`, 79 exact pairs, zero ambiguous/unpaired. `metadata.csv` SHA `05047b224d65dcf37b6f2e85e3c1457e9a3f26a50d4a9a87526b7ea4bde8048b`, 79 rows. `test_set/` duplicates/model outputs are forbidden as reference truth.

### Stage B — COMPLETE / IMMUTABLE / NO SCORING

Initial Stage B failed closed on a structural duplicate note-off before producing a report. A preregistered structural audit then found across all 79 canonical MIDIs: 76,392 valid FIFO note pairs, 24 extra note-offs in 7 files, zero unmatched note-ons, zero same-key overlaps. Every extra off followed an earlier completed pair for that same `(channel,MIDI)`.

Audit report SHA `111661c52b3cc5c5bd647d84bdd74af8fcef38799ff829e6edf23b2bd2f8fd24`; edge identity SHA `375029c7a0e2d80f25083743aa2d65c24c0de061f0e476db68987f218fcedef6`.

Frozen pairing amendment: an off with no active onset may be ignored only if the same key already completed >=1 valid pair earlier in the file; leading orphan offs and unmatched ons still fail. Exactly 24 ignored duplicate releases are required for this exact release.

Official Stage B run `34719744595`, job `103623274603`: SUCCESS at source `ac57c6c5379f00ad97c292415efec90c9ed32860`.
Immutable record `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_STAGE_B_RESULT.md`, commit `0bc647b112745953464f24eb0980e49ff348ebb2`.

Frozen Stage B identities:
- report SHA-256 `065335aac5a6cd46ef713bae9f19d6f7ca7d764233419f6d8eb9ec6bace9911e`
- included-population SHA-256 `def77a45baf1b453e3f8ec0feed82e1cd3964bd85d50fb30f4912c0564425b02`
- reference-event identity SHA-256 `e34b360515d35dc77a6f423eb8a36e860e46f9469c16a499243186aea1f6223a`
- ignored-duplicate-release identity SHA-256 `8751a5425e3348b4e7005b09121bd43425c23a9f296b8f2e58c8da1c245fcfd3`
- all 79 rows included; split train 62 / validate 8 / test 9
- guitar types nylon 40 / electric 35 / acoustic 3 / electric-band 1
- reference note events 76,392
- MIDI range 38..88
- all canonical MIDI format 1 / 2 tracks / PPQ 220 / tempo 500000 us/qn / channel 0.

All Stage B model/correctness/authority fields remained false/zero. FLGD correctness was still unseen.

### Alignment semantics — FROZEN / NO SCORING

Audit preregistration `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_ALIGNMENT_SEMANTICS_AUDIT.md`, commit `9ae2ffea5207373425f721fa8497124bd758ca6d`.
Audit workflow run `34719868249`, job `103623610804`: SUCCESS.
Result `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_ALIGNMENT_SEMANTICS_RESULT.md`, commit `e62de24d49aa83d3f099da9a8ce723111961c27c`.

Frozen decision: canonical metadata-named MIDI note times under standard SMF/PrettyMIDI tempo semantics are the authoritative audio-aligned reference times. Syncpoints are auxiliary score/downbeat metadata and are not used to warp note onsets/offsets for correctness scoring.

### Final V5 scoring preregistration — FROZEN / CORRECTNESS UNSEEN

Final contract: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_FINAL_SCORING_PREREGISTRATION.md`, commit `846cdedad46c10553569011a28ae01c72a9f6504`.
Numerical inclusive-boundary amendment: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_SCORING_NUMERICAL_AMENDMENT.md`, commit `2d547c6d034defebf8369db7f48fafcf15a02cec`.

Frozen scoring path:
- all 79 Stage B performances; no result-based exclusions;
- no Demucs; canonical MP3 decoded mono at 44.1 kHz with librosa 0.11.0, written/read as SoundFile 0.13.1 FLOAT WAV;
- Basic Pitch 0.4.0, CPU only, MIDI 40..88, onset threshold 0.5, frame threshold 0.3, minimum note length 127.7 ms, `multiple_pitch_bends=False`, `melodia_trick=True`;
- every decoded event preserved and classified by V5 exactly once;
- only `independently-corroborated-candidate` is V5-positive;
- matching per performance, deterministic maximum-cardinality, onset <=50 ms inclusive and pitch <=50 cents inclusive; offsets/durations ignored;
- numerical boundary uses only `delta < limit OR math.isclose(delta,limit,rel_tol=0,abs_tol=1e-12)`;
- primary metric V5-positive precision; one-sided 95% Wilson LB z `1.6448536269514722`;
- pooled positives >=1000 and pooled Wilson LB >=0.9900;
- each split/guitar-type stratum with >=100 positives requires point precision >=0.9500;
- all runtime/identity/event-preservation/policy guards must pass;
- a passing execution still cannot promote without separate policy review.

### Scoring harness — FROZEN CONTROLLED GREEN / CORRECTNESS UNSEEN

Harness: `scripts/songsterr-fresh/external_flgd_v5_validation.py`.
Initial harness commit `b7561defee0ec39d3be8ba877592b13d39d8e8d2`.
Controlled test: `scripts/songsterr-fresh/test_external_flgd_v5_validation.py`.
Method record: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_SCORING_HARNESS.md`, commit `2509ccfe24ded590148110d8485f1b2e0ff6173d`.

Final controlled workflow source `2ae9b6b797449b5b11de370b2e5836c4707fd5c9`.
Run `34720390259`, job `103625060255`: **SUCCESS**.

Green controlled checks include compile, frozen identities/constants, exact 50-ms/50-cent inclusive numerics, deterministic maximum-cardinality matching, duration/end irrelevance, fake-V5 event preservation/class bookkeeping, Wilson/stratum gates, runtime drift rejection, Basic Pitch payload guards without installing Basic Pitch, fake Stage B rejection, and synthetic MP3 → librosa 44.1-kHz mono → SoundFile FLOAT WAV → reread canonicalization. The final job had no real FLGD checkout and no Basic Pitch model invocation.

An earlier synthetic-audio attempt failed only because the runner lacked `ffmpeg`; the final workflow explicitly installed it. This changed CI fixture infrastructure only, not the scoring contract.

**No FLGD Basic Pitch/V5 correctness result exists at this checkpoint.**

## NEXT ALLOWED ACTION — ONE OFFICIAL FLGD V5 CORRECTNESS RUN

The preregistered prerequisites are satisfied. Exactly one official full 79-performance FLGD V5 correctness run is now authorized on one exact clean source commit.

The official execution must:
- use the exact frozen FLGD revision and exact immutable Stage B JSON;
- use the pinned Python/package/runtime contract and CPU-only Basic Pitch path;
- use the frozen scoring harness unchanged;
- process all 79 performances with no result-based exclusions;
- write one deterministic result artifact and preserve its SHA-256/provenance;
- emit policy authority false/zero with separate review required.

After any correctness result is observed: do not tune V5, Basic Pitch settings, matching/tolerances/gates, files or strata; do not rerun FLGD under this preregistration to seek a better result. Next steps become immutable result record → separate policy review only.

## FRESH-CHAT HANDOFF — V5 OFFICIAL-RUN LAUNCH GATE

This section is the canonical resume point for a new chat. Read this file first and continue only on `songsterr-fresh-pipeline-v1`. Do not reopen archived V143/Gomyway, V1/V2, GuitarSet/V3, IDMT/V4, GOAT, duration research, broad optimizer work, or protected-song execution.

### Exact frozen experimental source

The exact V5 source approved for the one official FLGD correctness evaluation remains:

`6a3ea0808676ead13518e258fa912fd62a4eb33c`

The commit that adds this fresh-chat handoff is **documentation-only**. It advances the branch for checkpointing but does **not** re-freeze, replace, or rebind the V5 experimental source. A fresh chat must not silently use the later documentation HEAD as the scoring source.

If the official execution path can explicitly checkout/pin an exact source commit, it must use `6a3ea0808676ead13518e258fa912fd62a4eb33c`. If the execution path instead requires the branch HEAD itself to equal the experimental source and cannot pin that commit, **STOP** and resolve the source-binding mechanism before launch; do not reinterpret the documentation-only HEAD as authorized experimental code.

### Current result state

- No official FLGD Basic Pitch/V5 correctness result has been recorded.
- Exactly one official 79-performance evaluation is authorized under the frozen V5 preregistration, subject to the launch-gate checks below.
- The controlled V5 workflow is only a guard/self-test surface. Its successful run did not perform a real FLGD checkout and did not invoke the Basic Pitch model. **Do not dispatch or rerun that controlled workflow as a substitute for the official evaluation.**
- Do not create a second scoring implementation, alternate runner, new thresholds, new holdout selection, or replacement workflow merely to make execution easier.

### Launch-gate checks to perform before any official execution

1. In the tree rooted at the exact frozen source commit `6a3ea0808676ead13518e258fa912fd62a4eb33c`, identify the **pre-existing** official V5 runner/workflow/holdout entrypoint. Do not guess a filename and do not create a new execution path.
2. Inspect that exact workflow/script path and prove it executes the real frozen contract: exact FLGD revision, immutable Stage B population/identities, canonical MP3 decoding, CPU-only Basic Pitch 0.4.0 with frozen settings, unchanged V5 classifier, all 79 performances, frozen deterministic matching and gates, and one deterministic result artifact.
3. Inspect Actions run/job/artifact history for evidence that an official correctness execution from the frozen source has already run or is currently running. This duplicate-run check must distinguish the controlled self-test workflow from a true FLGD + Basic Pitch correctness execution.
4. If an existing official run is found, **do not launch another one**. Inspect that run and its artifact, preserve its run/job/source/artifact identities, and move directly to immutable result recording.
5. If source identity, Stage B identity, holdout population, runtime contract, official entrypoint identity, or duplicate-run status is ambiguous, **STOP fail-closed**. No scoring run is allowed until the ambiguity is resolved without looking at correctness results.

### Current ChatGPT GitHub-connector limitation

The GitHub connection available in the chat can inspect repository files, workflow runs, jobs, logs and artifacts, and it can rerun certain existing failed jobs. It currently exposes **no action to create/dispatch a brand-new `workflow_dispatch` run**.

Therefore a fresh chat must not substitute any of the following for a missing dispatch capability:
- rerunning an unrelated/controlled workflow;
- committing a new workflow solely to bypass the missing dispatch action;
- using DigitalOcean, an old Codespace, another VM, or another environment without a separately authorized execution contract;
- changing the frozen source so a different trigger fires.

If the launch-gate checks prove there is no prior official run and the correct pre-existing manual workflow exists, identify its exact name/path and provide the user the precise GitHub UI steps/inputs needed to launch **one** run, pinned to `6a3ea0808676ead13518e258fa912fd62a4eb33c` if the workflow supports explicit source selection. If exact source pinning cannot be guaranteed, stop rather than launch.

### After the one official run exists

- Capture and checkpoint the workflow run ID, job ID(s), exact experimental source SHA, exact workflow/file path, FLGD revision, Stage B/report identities, artifact name(s), artifact SHA-256/provenance, and all frozen correctness/gate outputs.
- Verify from logs/artifacts that all 79 performances were processed once with no result-based exclusions and that the event-preservation/runtime/policy guards remained green.
- Record the result immutably before interpretation.
- Do **not** tune or rerun V5, Basic Pitch, thresholds, tolerances, matching, files, strata, or gates after seeing correctness.
- Do **not** set `modelValidationComplete:true`, make any event customer-eligible, advance delivery, resume duration research, or run the protected song based solely on the external result.
- The only next decision after immutable result recording is a **separate policy review** under the frozen preregistration.

### Fresh-chat first move

Start by fetching this checkpoint, confirming branch `songsterr-fresh-pipeline-v1`, and verifying the frozen experimental source commit `6a3ea0808676ead13518e258fa912fd62a4eb33c` still exists unchanged. Resume at **launch-gate verification**, not at pipeline redesign, retuning, or an archived research line.

## STILL FORBIDDEN

- any post-result tuning/rerun under this preregistration
- post-hoc FLGD row/stratum selection
- `test_set/` model outputs as truth
- GuitarSet/IDMT rerun/tuning
- protected-song execution before V5 passes external validation + policy approval
- duration research
- archived V143/Gomyway / GOAT / reference scoring
- broad threshold sweeps / training / fine-tuning
- customer promotion without passing preregistered external validation and separate policy approval.
