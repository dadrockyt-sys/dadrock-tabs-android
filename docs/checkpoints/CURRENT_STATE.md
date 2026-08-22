# DadRock V1.43 — Current Research State

> **Purpose:** durable recovery record for ChatGPT/session continuity. This file is the first thing to read when a chat crashes, closes, branches, or becomes too large.
>
> **Rule:** GitHub evidence and commit history are authoritative. Chat history is supporting context only.
>
> **Checkpoint discipline:** after every major unit of work on `v143-contextual-prune-lobo`, update and commit this `docs/checkpoints/CURRENT_STATE.md` record before proceeding to the next major unit. Record what was established, the evidence/commit involved, what remains unresolved, and the next exact objective.

## Quick recovery

When starting a fresh chat, use:

**`Continue DadRock from docs/checkpoints/CURRENT_STATE.md on branch v143-contextual-prune-lobo.`**

The assistant should then:

1. Read this file from GitHub.
2. Fetch the current branch tip before making any changes.
3. Verify the important evidence commits below still exist in ancestry.
4. Continue from **Next objective** without reconstructing state from screenshots unless GitHub evidence is insufficient.

---

## Repository / branch

- Repository: `dadrockyt-sys/dadrock-tabs-android`
- Active research branch: `v143-contextual-prune-lobo`
- Historical Codespace intro source HEAD: `4d735846fbd834cc4c722f2cb48727e4629647f1`
- Intro archive commit: `9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d`
- Closed 17–113 checkpoint: `fd8905d34175f9f20d9973807fed18c1e23c737a`
- Continuity-rule checkpoint: `4e80db2498727a06aa0ddd29e298338b59d0b907`
- Phase A intro-carrier audit checkpoint: `200fc992b44556837897ecb1192044e5e9547a86`
- Phase B boundary-proof artifact commit: `f547866fb0cda873b8e9125fdabc0f21d1683489`
- Phase B checkpoint: `78cbeca4cb35fc65bf5ac529ac4ec2d185c7b9cb`
- Phase C 1–113 provenance artifact commit: `0c288ed553c354519b8480514a371e729c7c850a`
- Historical 36-feature assembler recovery artifact commit: `dd2d256678e5d877825504c658b467a44d49982b`

**Important:** always fetch the current branch tip before writing. Do not assume any older checkpoint SHA remains HEAD.

### Housekeeping disclosure

During the Codespace-recovery pass an empty placeholder file `docs/checkpoints/INTENTIONAL_NOOP` was accidentally created in commit `f497f744a93665856904a4fd5c8dfdd92597359c` and immediately removed in commit `1a1cfed37ea32b0710767483998cbc45c71385e0`. The two commits have zero lasting tree effect. Do not rewrite or force-push history to hide them.

---

## Frozen project constraints

Unless the user explicitly changes them:

- **No retraining** to make historical pieces fit.
- **No threshold/tolerance changes** to force agreement.
- **No production edits** as part of historical recovery/provenance closure.
- Preserve historical evidence rather than rewriting contradictory or incomplete records.
- Treat the closed 17–113 chain as immutable research evidence unless new evidence proves a factual error.
- Current recovery work should be read-only / forensic except for research artifacts and this checkpoint.
- Historical use of Codespaces is part of provenance; measures **1–16 were trained in Codespaces**.
- Do not reconstruct missing historical source from guesswork and describe it as recovered history.
- Do not upgrade to a complete raw-audio deterministic replay claim until the upstream raw-audio→intro-cache carrier generation is independently proven.

---

## What is already closed

### Measures 17–113

Measures **17–113 are formally closed as one research/provenance chain** at:

`fd8905d34175f9f20d9973807fed18c1e23c737a` — `Checkpoint V143 17-113 research closure`

The recovered 17–32 evidence remains authoritative:

- historical generator: `analyzer/v143_fresh_verse1_reference_free_capture.py`;
- historical/current generator blob exact: `c8ea8eca33819fb506f06105f87075dadd133214`;
- boundary explicitly starts at measure 17 and ends at 32;
- carrier lineage: direct Demucs6s Guitar plus BS-RoFormer Instrumental → Demucs6s Guitar;
- deterministic separator: shifts 1, overlap 0.10, segment size 6, seed 143;
- historical Verse1 carrier SHA-256: `fbb2c6ca28e1e142ea5fdbc8e55dd7b67d1a55009c179fe4e8e3ec3a02251e15`;
- recovered generator reproduced that carrier SHA-256 exactly;
- historical/current scoring core blob exact: `ee62a86adc5f60119d00b5b57a25ee8f0b06f4fe`;
- historical target-sequence replay exact for 1051 events;
- sealed contextual replay retained base threshold 0.27 and exact discrete selected-event keys.

Resolution artifact:

`debug/v143-contextual-prune/measure-17-32-evidence-gap-resolution.json`

Known structure:

- 17–96: closed development/research chain.
- 97–113: closed reserve.
- 17–113: consolidated research provenance closure.

Do not reopen or modify 17–113 merely to make the intro fit.

### Measures 1–113 provenance/carrier chain

The research provenance/carrier chain remains closed by:

`debug/v143-contextual-prune/research-evidence-closure-1-113.json`

Commit:

`0c288ed553c354519b8480514a371e729c7c850a` — `Close V143 1-113 research provenance chain`

That artifact truthfully recorded the strongest claim supported at the time:

`closed_research_provenance_carrier_chain_with_intro_deterministic_replay_source_gap_disclosed`

**Do not rewrite that historical artifact merely because later source recovery strengthened part of the evidence.** The later recovery below supersedes one specific limitation: the late ordered 36-feature assembler is now recovered. A narrower upstream raw-audio→intro-cache generation gap remains.

---

## Measures 1–16: historical truth and archive

- Measures 1–16 were historically trained in GitHub Codespaces.
- A forensic snapshot was copied unchanged from the historical Codespace and archived at commit `9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d`.
- Archive path: `analyzer/v143-intro-1-16-evidence/codespace-snapshot/`.
- `PROVENANCE.txt` records historical source HEAD `4d735846fbd834cc4c722f2cb48727e4629647f1` and states that no retraining, threshold changes, model changes, or production edits were performed during capture.
- The snapshot contains 52 historical `intro*.json` artifacts plus provenance/hashes.

Important preserved artifacts include:

- `intro-analysis-cache.json`
- `intro-onset-spectrum-cache.json`
- `intro-spectral-pitch-cache.json`
- `intro-raw-attack-cache.json`
- `intro-raw-attack-harmonic-cache.json`
- `intro-correlation-safe-grid-event-selector-model.json`
- `intro-correlation-safe-grid-event-selector-report.json`
- `intro-correlation-safe-grid-event-selector-threshold027-candidate.json`
- `intro-correlation-safe-grid-event-selector-threshold045-incumbent.json`
- sequence, temporal-assignment, pitch-ranking, structured-event, repetition-recovery, and diagnostic artifacts.

---

## Frozen intro selector contract

The archived active base selector is:

`intro-correlation-safe-grid-event-selector-model.json`

Frozen contract:

- model: `v143-correlation-safe-grid-event-selector`;
- training measures: **1–8**;
- validation measures: **9–12**;
- development measures: **1–12**;
- diagnostic measures: **13–16**;
- window: **100 ms**;
- L2: **10.0**;
- active threshold: **0.27**;
- 36 feature means + 36 feature standard deviations;
- bias plus 36 normalized feature weights;
- neutralized feature columns: **19, 26, 33**;
- neutralized feature names:
  - `attackMax:viewCorrelation`
  - `earlyMean:viewCorrelation`
  - `sustainMean:viewCorrelation`
- neutralized raw value: 1.0;
- professional reference required at runtime: false;
- Verse1 reference used for training: false;
- production modified: false.

**Correction preserved:** the frozen window is **100 ms**, not 10 ms.

The active selector and the preserved 0.27 candidate have the same Git blob SHA `2540c428333aeef8d1f4bb470ab3d02e99cb6b4d`. The 0.45 incumbent is a different blob. The earlier selector report records 0.45 as its best validation configuration; later repetition-recovery evidence explicitly identifies a validated 0.27 base selector. Preserve that chronology rather than rewriting the older report.

### Diagnostic-value correction

The often-cited measures 13–16 diagnostic F1 ≈ 0.955 with 100% recall belongs to the later correlation-safe **sequence** experiment, not the frozen 0.27 base grid selector. The sequence report records F1 `0.955223880597015`, recall 1.0, and no production promotion. The base selector's earlier report gives diagnostic location F1 `0.8333333333333334` at its recorded report configuration.

---

## Intro reference-free carrier evidence

`intro-onset-spectrum-cache.json` is a preserved reference-free physical-onset whole-spectrum carrier. It records:

- sample rate 22050;
- hop length 128;
- 36 bins/octave;
- spectrum MIDI 28–112;
- guitar MIDI 40–88;
- onset grouping tolerance 30 ms;
- two candidate stem views;
- `viewA` / `viewB` spectra for `attackMax`, `earlyMean`, and `sustainMean`.

The archived cache is part of the frozen selector feature lineage.

---

## Phase A original carrier audit — historical finding and correction

At commit `200fc992b44556837897ecb1192044e5e9547a86`, the available evidence was interpreted as missing the late executable that assembled the final ordered 36-feature selector input. That finding was valid for the source set inspected at that moment and must remain in history.

The checkpoint-referenced files were also absent from the copied snapshot:

- `intro-correlation-safe-grid-events-1-12.json`
- `intro-correlation-safe-grid-events-13-16.json`
- `intro-onset-rhythm-cache.json`
- `ARTIFACTS.md`
- `analyzer/WINDOWS_ONE_SHOT_INTRO_TIMING.ps1`

### Superseding correction — historical 36-feature assembler recovered

A later read-only inspection of the surviving Codespace exposed:

`analyzer/v143_intro_learned_grid_event_selector.py`

This is not a reconstruction. It exists at the historical source HEAD `4d735846fbd834cc4c722f2cb48727e4629647f1` with Git blob SHA:

`f26e6afb9f6335231271378dec48d18a43d60fea`

The current tracked copy has the **same Git blob SHA**. The Codespace also contained a compiled `__pycache__/v143_intro_learned_grid_event_selector.cpython-311.pyc`, independently showing that this source had been executed there.

Recovery artifact:

`debug/v143-contextual-prune/intro-36-feature-assembler-recovery.json`

Artifact commit:

`dd2d256678e5d877825504c658b467a44d49982b` — `Recover historical V143 intro 36-feature assembler`

### Exact ordered 36-feature construction recovered

Historical `_grid_feature(...)` constructs exactly 36 values:

**Indices 0–12 — timing/support/base features**

0. constant `1.0`
1. signed grid residual / window seconds
2. absolute grid residual / window seconds
3. duration
4. detection count / 8
5. max amplitude
6. step / 16
7. stem support / 2
8. sweep support / 3
9. `(step % 4) / 3`
10. quarter-step indicator (`step % 4 == 0`)
11. half-step indicator (`step % 2 == 0`)
12. candidate count

**Indices 13–33 — three 7-value spectral summaries, in window order `attackMax`, `earlyMean`, `sustainMean`**

Each window contributes, in order:

1. local peak − view floor
2. local mean − view floor
3. harmonic max − view floor
4. peak margin
5. view floor
6. global peak − view floor
7. view correlation

Therefore the three view-correlation positions are exactly:

- index 19: `attackMax:viewCorrelation`
- index 26: `earlyMean:viewCorrelation`
- index 33: `sustainMean:viewCorrelation`

**Indices 34–35 — phase features**

- `sin(2π(step % 16)/16)`
- `cos(2π(step % 16)/16)`

### Frozen correlation-safe linkage proved

Comparison of the preserved learned selector model and frozen correlation-safe selector shows:

- all **33 non-neutralized feature means are identical**;
- mean differences occur **only** at indices `[19,26,33]`;
- all **33 non-neutralized feature standard deviations are identical**;
- std differences occur **only** at `[19,26,33]`;
- those are exactly the three historical assembler positions containing `viewCorrelation`;
- the final frozen model weights for those neutralized columns are zero.

This is strong structural evidence that the frozen correlation-safe 0.27 selector reused this exact historical 36-feature construction and neutralized only the three correlation columns. The older public v1 ordering no longer needs to be substituted or guessed.

**Major correction:** the late ordered 36-feature assembler is now recovered. The previous claim that it was unavailable is superseded by this historical source recovery.

### What is now deterministically specified

Given the preserved intro raw/grid/onset-spectrum caches, the historical source now specifies:

`preserved cache rows → exact ordered 36-feature vector → frozen normalization/weights → frozen selector score/decision`

This does not involve retraining, retuning, or reconstructed feature semantics.

---

## Surviving Codespace replay-directory inspection

Screenshots from the historical Codespace showed untracked `public/v143-modal-replay/`. A read-only inspection confirmed the directory survives and contains five WAV files only:

- `gomyway-modal-cpu-historical-command-guitar.wav`
- `gomyway-modal-l4-direct-guitar.wav`
- `gomyway-modal-l4-historical-defaults-guitar.wav`
- `gomyway-modal-l4-seed143-a.wav`
- `gomyway-modal-l4-seed143-b.wav`

No targeted assembler/replay source matches were found inside that directory. Its significance is as preserved audio/stem evidence, not as the recovered 36-feature assembler.

The wider workspace search, not the replay directory itself, surfaced the historical `v143_intro_learned_grid_event_selector.py` source.

---

## Phase B 16→17 boundary proof — completed

Boundary artifact:

`debug/v143-contextual-prune/intro-16-to-17-boundary-proof.json`

Artifact commit:

`f547866fb0cda873b8e9125fdabc0f21d1683489`

Recorded status:

`passed_with_disclosed_intro_replay_source_gap`

The supported common seam is the reference-free physical-onset/two-view whole-spectrum carrier. Both sides directly support:

- 22050 Hz target sample rate;
- hop length 128;
- 36 bins/octave;
- spectrum/CQT MIDI 28–112;
- guitar MIDI 40–88;
- 30 ms physical-onset grouping;
- two candidate stem views;
- onset-group measure/onset/candidate/support concepts;
- `viewA` / `viewB`;
- `attackMax`, `earlyMean`, `sustainMean`.

The recovered measure-17 generator explicitly says it uses the same frozen V143 deterministic separator and reference-free timing stack used by intro calibration, while writing a separate fresh-section cache.

For Verse1, exact recovered spectral windows are:

- `attackMax`: onset −0.020 s to +0.045 s, max reducer;
- `earlyMean`: onset +0.020 s to +0.095 s, mean reducer;
- `sustainMean`: onset +0.070 s to +0.180 s, mean reducer.

**Historical note:** the Phase B artifact did not claim recovery of the late intro 36-feature assembler because that source had not yet been identified. The later recovery above strengthens the intro side but does not invalidate the boundary proof.

---

## Phase C 1–113 research provenance closure — completed, with later strengthening

Final Phase C artifact:

`debug/v143-contextual-prune/research-evidence-closure-1-113.json`

Commit:

`0c288ed553c354519b8480514a371e729c7c850a`

Phase C closed:

`1–16 archived frozen intro evidence/carrier → proven 16→17 carrier seam → 17–96 closed development/research chain → 97–113 closed reserve`

No retraining, threshold changes, tolerance weakening, model changes, prediction-set changes, or production changes were used.

### Later strengthening without rewriting Phase C

The Phase C artifact's reason for declining a complete raw-audio replay claim specifically cited the then-missing late ordered 36-feature assembler. That particular source gap is now resolved by `dd2d256678e5d877825504c658b467a44d49982b`.

However, **do not yet change `completeDeterministicRawAudioReplay1To113Closed` to true.** The remaining replay-completeness question has moved upstream to historical generation of the preserved intro raw/onset-spectrum carrier caches from raw audio.

---

## Current forensic question

There is no open 16→17 carrier problem and no open 17–113 provenance problem.

The late 36-feature selector assembler is also no longer missing.

The remaining historical replay question is now narrowly:

> Can authoritative historical source be recovered that regenerates the preserved measures 1–16 raw-attack / physical-onset / whole-spectrum carrier caches from raw audio with the historical deterministic separator/timing semantics?

In particular, determine whether the functionality referenced by `analyzer/WINDOWS_ONE_SHOT_INTRO_TIMING.ps1` survives under another tracked source filename, compiled source/history artifact, or recoverable Codespace history entry.

Until that is proven, the strongest safe deterministic statement is:

**preserved intro cache → exact historical 36-feature vector → frozen correlation-safe selector is specified; raw audio → preserved intro cache is not yet proven byte-identically.**

---

## Historical split to preserve

- **1–8:** training
- **9–12:** validation
- **13–16:** diagnostic only

Do not relabel 13–16 as a new untouched holdout. Do not use later sequence-model diagnostic success to rewrite frozen base-selector history.

---

## Next objective

Proceed with a **focused, read-only upstream intro-carrier generator recovery** before any downstream engineering.

1. Search historical/current tracked source for producers of:
   - `intro-raw-attack-cache.json`
   - `intro-onset-spectrum-cache.json`
   - `intro-onset-rhythm-cache.json`
   - `intro-correlation-safe-grid-events-1-12.json`
   - `intro-correlation-safe-grid-events-13-16.json`.
2. Search exact constants/logic visible in the caches, including 22050 Hz, hop 128, 36 bins/octave, MIDI 28–112, guitar 40–88, 30 ms grouping, two-view stem construction, and the three spectral-window names.
3. Verify candidate source against historical HEAD `4d735846...` and compare Git blob SHAs before accepting it as recovered history.
4. If tracked source is absent, inspect the surviving Codespace read-only for likely `.py`, `.ps1`, compiled `.pyc`, shell-history, or VS Code local-history remnants. Do not modify the Codespace.
5. If the upstream generator is recovered, prove raw-audio→cache replay independently before strengthening the final 1–113 replay claim.
6. If it is not recovered, preserve that upstream source gap and do not retrain/reimplement it as historical truth.
7. **After the next major recovery unit, update and commit this checkpoint before proceeding.**

---

## Things specifically ruled out

- Retraining 1–16 to reproduce later behavior.
- Adjusting thresholds/tolerances to make 1–16 and 17–113 agree.
- Replacing recovered historical feature semantics with a newly invented ordering.
- Treating the sequence-model F1≈0.955 diagnostic as the frozen base selector's score.
- Force-pushing or rewriting closed provenance history.
- Reopening 17–113 merely to make the intro fit.
- Calling a newly reimplemented/tuned upstream cache generator historical recovery.
- Claiming raw-audio→intro-cache byte-exact replay before it is independently proven.
- Claiming complete deterministic raw-audio replay 1–113 solely because the 36-feature assembler is now recovered.
- Production modification or promotion during this historical recovery work.

---

## Important new commits / artifacts

Continuity:

- `4e80db2498727a06aa0ddd29e298338b59d0b907` — checkpoint discipline.

Phase A:

- `200fc992b44556837897ecb1192044e5e9547a86` — original intro carrier audit.

Phase B:

- `f547866fb0cda873b8e9125fdabc0f21d1683489` — 16→17 boundary proof artifact.
- `78cbeca4cb35fc65bf5ac529ac4ec2d185c7b9cb` — Phase B checkpoint.

Phase C:

- `0c288ed553c354519b8480514a371e729c7c850a` — 1–113 research provenance closure.
- `debug/v143-contextual-prune/research-evidence-closure-1-113.json`.

Supplemental historical source recovery:

- `dd2d256678e5d877825504c658b467a44d49982b` — `Recover historical V143 intro 36-feature assembler`.
- `debug/v143-contextual-prune/intro-36-feature-assembler-recovery.json`.
- historical/current assembler path: `analyzer/v143_intro_learned_grid_event_selector.py`.
- historical/current assembler blob: `f26e6afb9f6335231271378dec48d18a43d60fea`.

Foundational evidence:

- `9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d` — archived Codespace intro evidence.
- historical source HEAD `4d735846fbd834cc4c722f2cb48727e4629647f1`.
- `fd8905d34175f9f20d9973807fed18c1e23c737a` — closed 17–113 chain.
- historical/current Verse1 generator blob `c8ea8eca33819fb506f06105f87075dadd133214`.
- intro onset-spectrum-cache blob `4651f14ed15df3f9e596f9cd4fa3f8afe8a9b45d`.
- intro raw-attack-cache blob `b58275e5fa846fe655747cd26bbd8139025d5072`.
- active frozen intro selector blob `2540c428333aeef8d1f4bb470ab3d02e99cb6b4d`.

No runtime or production code was changed by the supplemental recovery. The write was research evidence plus this continuity checkpoint.

---

## Codespace preservation note

The historical Codespace remains part of provenance. It has now provided supplemental read-only evidence beyond the original 52-file JSON snapshot, including the existence of the five untracked modal-replay WAV captures and the workspace path that led to the already-tracked historical 36-feature assembler source.

Do not delete, clean, reset, rebase, or otherwise modify the surviving Codespace merely for recovery. Prefer GitHub history when a source candidate is already tracked; use the Codespace only to identify otherwise-hidden historical remnants.

---

## Chat continuity workflow

1. **After every major work unit, commit an updated `docs/checkpoints/CURRENT_STATE.md` on `v143-contextual-prune-lobo` before beginning the next major work unit.**
2. Include latest evidence commit(s), conclusions, unresolved questions, and the next exact objective.
3. Start a fresh chat when the UI becomes heavy rather than waiting for a crash.
4. In the new chat say:
   **`Continue DadRock from docs/checkpoints/CURRENT_STATE.md on branch v143-contextual-prune-lobo.`**
5. Verify GitHub and continue directly from the checkpoint.
6. Screenshots are secondary evidence once their underlying repository evidence is preserved.

---

## Updating this record

Every checkpoint update should preserve these headings and change only what the evidence supports:

- Repository / branch
- Frozen project constraints
- What is already closed
- Current forensic question
- Next objective
- Things specifically ruled out
- Important new commits/artifacts

Never erase an earlier provenance conclusion merely because later evidence corrects it. Preserve the old conclusion as historical context and state the correction explicitly.

---

_Last updated on 2026-08-21 (user local date) after recovering the historical ordered 36-feature intro assembler. The remaining deterministic-replay gap is now upstream raw-audio→intro-carrier/cache generation._
