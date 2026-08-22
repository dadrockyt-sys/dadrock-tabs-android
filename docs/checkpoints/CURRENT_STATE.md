# DadRock V1.43 — Current Research State

> **Purpose:** durable recovery record for ChatGPT/session continuity.
>
> **Rule:** GitHub evidence and commit history are authoritative. Chat history/screenshots are supporting context only.
>
> **Checkpoint discipline:** after every major work unit on `v143-contextual-prune-lobo`, update and commit this file before beginning the next major unit.

## Quick recovery

Start a fresh chat with:

**`Continue DadRock from docs/checkpoints/CURRENT_STATE.md on branch v143-contextual-prune-lobo.`**

Then fetch the branch tip, verify the evidence commits below, and continue from **Next objective**.

---

## Repository / branch

- Repository: `dadrockyt-sys/dadrock-tabs-android`
- Active branch: `v143-contextual-prune-lobo`
- Historical Codespace intro source HEAD: `4d735846fbd834cc4c722f2cb48727e4629647f1`
- Intro archive commit: `9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d`
- Closed 17–113 checkpoint: `fd8905d34175f9f20d9973807fed18c1e23c737a`
- Phase A original intro audit: `200fc992b44556837897ecb1192044e5e9547a86`
- 16→17 boundary artifact: `f547866fb0cda873b8e9125fdabc0f21d1683489`
- Boundary checkpoint: `78cbeca4cb35fc65bf5ac529ac4ec2d185c7b9cb`
- 1–113 provenance artifact: `0c288ed553c354519b8480514a371e729c7c850a`
- Initial 36-feature recovery artifact: `dd2d256678e5d877825504c658b467a44d49982b`
- Corrected 36-feature recovery artifact: `c6cb268511f6888675fde666fbdeecdda41bba62`

Always fetch the current branch tip before writing; no SHA above should be assumed to remain HEAD.

### Housekeeping disclosure

An empty placeholder `docs/checkpoints/INTENTIONAL_NOOP` was accidentally created in `f497f744a93665856904a4fd5c8dfdd92597359c` and immediately removed in `1a1cfed37ea32b0710767483998cbc45c71385e0`. These commits have zero lasting tree effect. Do not rewrite history to hide them.

---

## Frozen project constraints

- **No retraining** to make historical pieces fit.
- **No threshold/tolerance changes** to force agreement.
- **No production edits** as part of historical recovery/provenance work.
- Preserve old findings when later evidence corrects them; append explicit corrections rather than rewriting history.
- Treat the closed 17–113 chain as immutable unless new evidence proves a factual error.
- Use read-only forensics wherever possible; writes are research evidence/checkpoints only.
- Do not reimplement missing source and call it historical recovery.
- Do not claim complete deterministic raw-audio replay until every required upstream layer is independently proven.

---

## What is already closed

### Measures 17–113

Measures **17–113 are formally closed** at:

`fd8905d34175f9f20d9973807fed18c1e23c737a` — `Checkpoint V143 17-113 research closure`

Recovered 17–32 evidence includes:

- historical generator: `analyzer/v143_fresh_verse1_reference_free_capture.py`;
- historical/current generator blob exact: `c8ea8eca33819fb506f06105f87075dadd133214`;
- section boundary: measures 17–32;
- carrier lineage: direct Demucs6s Guitar plus BS-RoFormer Instrumental → Demucs6s Guitar;
- deterministic separator: shifts 1, overlap 0.10, segment 6, seed 143;
- historical Verse1 cache SHA-256 `fbb2c6ca28e1e142ea5fdbc8e55dd7b67d1a55009c179fe4e8e3ec3a02251e15`, regenerated exactly;
- frozen scoring core preserved/replayed;
- base threshold 0.27 retained;
- no threshold/model/prediction-set changes used.

Resolution artifact:

`debug/v143-contextual-prune/measure-17-32-evidence-gap-resolution.json`

Structure remains:

- 17–96: closed development/research chain.
- 97–113: closed reserve.
- 17–113: consolidated provenance closure.

### Measures 1–113 provenance/carrier chain

Phase C artifact:

`debug/v143-contextual-prune/research-evidence-closure-1-113.json`

Commit:

`0c288ed553c354519b8480514a371e729c7c850a`

It closed the strongest defensible chain available at that time:

`1–16 archived frozen intro evidence/carrier → proven 16→17 carrier seam → 17–96 closed development/research chain → 97–113 closed reserve`

Do **not** rewrite this historical artifact after later source recovery. Later evidence may strengthen the chain by supplemental artifacts/checkpoints.

---

## Measures 1–16 archive / frozen truth

Measures 1–16 were historically trained in GitHub Codespaces. A forensic snapshot was copied unchanged and archived at:

`9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d`

Path:

`analyzer/v143-intro-1-16-evidence/codespace-snapshot/`

The archive preserves 52 historical `intro*.json` artifacts plus provenance/hashes. Important files include:

- `intro-analysis-cache.json`
- `intro-onset-spectrum-cache.json`
- `intro-spectral-pitch-cache.json`
- `intro-raw-attack-cache.json`
- `intro-raw-attack-harmonic-cache.json`
- `intro-correlation-safe-grid-event-selector-model.json`
- `intro-correlation-safe-grid-event-selector-report.json`
- 0.27 candidate and 0.45 incumbent selector artifacts
- sequence, temporal-assignment, pitch-ranking, structured-event, repetition-recovery and diagnostics.

Historical split remains:

- **1–8:** training
- **9–12:** validation
- **13–16:** diagnostic only

Do not relabel 13–16 as an untouched holdout.

---

## Frozen intro selector contract

Active archived model:

`intro-correlation-safe-grid-event-selector-model.json`

Contract:

- model `v143-correlation-safe-grid-event-selector`;
- 100 ms window (**not 10 ms**);
- L2 10.0;
- active threshold 0.27;
- 36 feature means/stds;
- bias + 36 normalized feature weights;
- neutralized columns `[19,26,33]`;
- neutralized names:
  - `attackMax:viewCorrelation`
  - `earlyMean:viewCorrelation`
  - `sustainMean:viewCorrelation`
- neutralized raw value 1.0;
- runtime professional reference not required;
- Verse1 reference not used for training;
- production modified false.

The active model and preserved 0.27 candidate share blob `2540c428333aeef8d1f4bb470ab3d02e99cb6b4d`.

### Diagnostic correction retained

F1 ≈ 0.955 with recall 1.0 on measures 13–16 belongs to the later **correlation-safe sequence experiment**, not the frozen 0.27 base selector. Do not use that result as the frozen base selector's diagnostic score.

---

## Intro reference-free carrier

`intro-onset-spectrum-cache.json` preserves a reference-free physical-onset whole-spectrum carrier with:

- target SR 22050;
- hop 128;
- 36 bins/octave;
- spectrum MIDI 28–112;
- guitar MIDI 40–88;
- 30 ms onset grouping;
- two candidate stem views;
- `viewA` / `viewB`;
- windows `attackMax`, `earlyMean`, `sustainMean`.

This cache is part of the frozen selector feature lineage.

---

## 36-feature assembler recovery — corrected authoritative finding

### Historical context

The original Phase A audit (`200fc992...`) concluded that the late ordered 36-feature assembler was missing from the inspected evidence. A later read-only Codespace search surfaced tracked historical source:

`analyzer/v143_intro_learned_grid_event_selector.py`

The source exists at historical HEAD `4d735846...` and on the current branch with the **same Git blob**:

`f26e622f8277d68f3649191879789f87acd4f77e`

Therefore the assembler is surviving historical source, not a reconstruction.

The Codespace also showed a compiled `analyzer/__pycache__/v143_intro_learned_grid_event_selector.cpython-311.pyc`, consistent with the source having run there.

### Correction to the first supplemental recovery artifact

`debug/v143-contextual-prune/intro-36-feature-assembler-recovery.json` at `dd2d256...` correctly concluded that the historical assembler survives, but its detailed feature formulas and recorded source blob were mis-transcribed from another feature family.

That factual detail is corrected—not erased—by:

`debug/v143-contextual-prune/intro-36-feature-assembler-recovery-correction.json`

Commit:

`c6cb268511f6888675fde666fbdeecdda41bba62` — `Correct V143 intro 36-feature recovery details`

The authoritative implementation is `_grid_feature(...)` plus `_spectral_summary(...)` in blob `f26e622...`.

### Correct ordered 36-feature construction

When a nearby onset row exists, indices 0–12 are:

0. `1.0`
1. nearest onset residual / window seconds
2. absolute nearest residual / window seconds
3. second-nearest absolute residual / window seconds (defaults to 1.0 normalized when only one row exists)
4. `min(number_of_nearby_rows / 8, 2)`
5. nearest `candidateCount / 49`
6. nearest `sourceClusterCount / 16`
7. nearest `stemSupportMax / 2`
8. nearest `sweepSupportMax / 4`
9. `min(nearest.detectionCountSum / 32, 2)`
10. max `stemSupportMax` across nearby rows / 2
11. max `sweepSupportMax` across nearby rows / 4
12. `min(sum(detectionCountSum across nearby rows) / 96, 2)`

If there is no nearby onset row, indices 0–33 are zero.

Indices 13–33 are three 7-value summaries in window order:

`attackMax → earlyMean → sustainMean`

For each window, source clamps each view nonnegative, forms `mean_view = 0.5*(viewA + viewB)`, and emits:

1. mean of `mean_view`
2. std of `mean_view`
3. largest value (`top1`)
4. `top1 - top2`
5. L2 norm of nonnegative view A
6. L2 norm of nonnegative view B
7. cosine similarity / `viewCorrelation`

Therefore view-correlation positions are exactly:

- 19: `attackMax:viewCorrelation`
- 26: `earlyMean:viewCorrelation`
- 33: `sustainMean:viewCorrelation`

Indices 34–35 are always the grid phase terms:

- `sin(2π * step / 16)`
- `cos(2π * step / 16)`

### Frozen model linkage

The preserved learned selector model's feature means numerically match the above implementation. Comparing it with the frozen correlation-safe selector:

- means match at every non-neutralized feature;
- stds match at every non-neutralized feature;
- differences occur only at `[19,26,33]`;
- those are exactly the three view-correlation source positions;
- frozen weights at those three feature columns are zero.

Thus the substantive recovery conclusion is strong: the frozen correlation-safe selector reused this historical 36-feature construction with the three view correlations neutralized.

### Deterministic coverage now established

Given preserved onset-spectrum rows and the grid, the surviving historical source specifies:

`preserved intro carrier/cache → exact 36-feature vector → frozen normalization/weights → selector score/decision`

No retraining, retuning or invented semantics are required for this layer.

---

## Surviving Codespace `public/v143-modal-replay/`

Read-only inspection found five WAV files only:

- `gomyway-modal-cpu-historical-command-guitar.wav`
- `gomyway-modal-l4-direct-guitar.wav`
- `gomyway-modal-l4-historical-defaults-guitar.wav`
- `gomyway-modal-l4-seed143-a.wav`
- `gomyway-modal-l4-seed143-b.wav`

No assembler/source-code matches were present there. The wider workspace search—not this directory—led to the tracked assembler source.

---

## 16→17 boundary proof

Artifact:

`debug/v143-contextual-prune/intro-16-to-17-boundary-proof.json`

Commit `f547866...` records a passed carrier/schema seam at the reference-free physical-onset/two-view spectral layer. Shared directly evidenced invariants include:

- 22050 Hz;
- hop 128;
- 36 bins/octave;
- MIDI 28–112, guitar 40–88;
- 30 ms grouping;
- two stem views;
- `viewA` / `viewB`;
- `attackMax`, `earlyMean`, `sustainMean`.

Verse1 exact spectral windows recovered from its historical generator:

- `attackMax`: onset −0.020 to +0.045 s, max;
- `earlyMean`: +0.020 to +0.095 s, mean;
- `sustainMean`: +0.070 to +0.180 s, mean.

The later 36-feature assembler recovery strengthens the intro side but does not invalidate or require rewriting the boundary artifact.

---

## Current forensic question

There is no open 16→17 carrier problem, no open 17–113 provenance problem, and the late 36-feature selector assembler is no longer missing.

The remaining deterministic-replay gap is **upstream**:

> Can authoritative historical source be recovered/proven that regenerates the measures 1–16 raw-attack / physical-onset / whole-spectrum carrier caches from raw audio using the historical deterministic separator/timing semantics?

Specifically, the historical checkpoint referenced but the archive did not preserve:

- `analyzer/WINDOWS_ONE_SHOT_INTRO_TIMING.ps1`
- `intro-onset-rhythm-cache.json`
- `intro-correlation-safe-grid-events-1-12.json`
- `intro-correlation-safe-grid-events-13-16.json`
- `ARTIFACTS.md`

Current strongest deterministic statement:

**preserved intro cache → exact historical 36-feature vector → frozen correlation-safe selector is specified; raw audio → preserved intro cache is not yet proven byte-identically.**

Do not yet claim complete raw-audio replay for 1–16 or 1–113.

---

## Next objective

Proceed with **focused read-only upstream intro-carrier generator recovery**:

1. Search current and historical tracked source for producers of `intro-raw-attack-cache.json`, `intro-onset-spectrum-cache.json`, `intro-onset-rhythm-cache.json`, and the correlation-safe grid-event intermediates.
2. Search by implementation fingerprints as well as filenames: 22050 Hz, hop 128, 36 bins/octave, MIDI 28–112, guitar 40–88, 30 ms grouping, two deterministic views, `attackMax`/`earlyMean`/`sustainMean`, `librosa.cqt`, historical wide-recall onset sweeps, reference-free timing, deterministic stem bundle.
3. Search commit history for deleted/renamed producer source.
4. Verify every candidate against historical HEAD `4d735846...` and Git blob provenance.
5. If Git history is exhausted without a producer, perform one targeted read-only Codespace search for `.py`, `.ps1`, `.pyc`, shell-history and VS Code local-history remnants.
6. If a historical generator is recovered, independently prove raw-audio→cache replay before strengthening the final deterministic claim.
7. If it cannot be recovered, preserve the narrower upstream source gap; do not reimplement it as historical truth.
8. **After this upstream-recovery unit, update and commit this checkpoint before proceeding.**

---

## Things specifically ruled out

- Retraining or retuning 1–16.
- Weakening tolerances to make replay pass.
- Reopening 17–113 to make intro fit.
- Treating sequence-model F1≈0.955 as the base selector's diagnostic score.
- Using the incorrect detailed formulas from the superseded `dd2d256...` recovery artifact after correction `c6cb268...`.
- Calling a newly reimplemented upstream generator historical recovery.
- Claiming raw-audio→intro-cache byte-exact replay before it is independently proven.
- Claiming full deterministic raw-audio 1–113 replay solely because the 36-feature assembler is recovered.
- Production modification/promotion during historical recovery.

---

## Important evidence / artifacts

- Historical source HEAD: `4d735846fbd834cc4c722f2cb48727e4629647f1`
- Intro archive: `9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d`
- Closed 17–113: `fd8905d34175f9f20d9973807fed18c1e23c737a`
- Original Phase A audit: `200fc992b44556837897ecb1192044e5e9547a86`
- Boundary proof: `f547866fb0cda873b8e9125fdabc0f21d1683489`
- Boundary checkpoint: `78cbeca4cb35fc65bf5ac529ac4ec2d185c7b9cb`
- 1–113 provenance closure: `0c288ed553c354519b8480514a371e729c7c850a`
- Initial assembler recovery artifact: `dd2d256678e5d877825504c658b467a44d49982b` (substantive recovery correct; detailed formulas/blob corrected later)
- Authoritative assembler correction: `c6cb268511f6888675fde666fbdeecdda41bba62`
- Correct historical assembler blob: `f26e622f8277d68f3649191879789f87acd4f77e`
- Frozen selector blob: `2540c428333aeef8d1f4bb470ab3d02e99cb6b4d`
- Learned selector model blob: `fedd15e1886ab50d4c48e8b70f38dd4c080d9154`
- Verse1 generator blob: `c8ea8eca33819fb506f06105f87075dadd133214`

No runtime or production code was changed by this correction. The correction consists of research evidence and continuity documentation only.

---

## Codespace preservation note

Do not delete, clean, reset, rebase, or otherwise modify the surviving historical Codespace for recovery purposes. Prefer GitHub history whenever source is tracked; use Codespace read-only only for evidence that never reached Git.

---

_Last updated 2026-08-21 (user local date) after correcting the detailed historical 36-feature assembler recovery. The remaining replay gap is upstream raw-audio→intro-carrier/cache generation._
