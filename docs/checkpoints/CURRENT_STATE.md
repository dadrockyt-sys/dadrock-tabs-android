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
- Intro archive commit: `9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d`
- Closed 17–113 checkpoint: `fd8905d34175f9f20d9973807fed18c1e23c737a`
- Historical Codespace intro source HEAD recorded by provenance: `4d735846fbd834cc4c722f2cb48727e4629647f1`
- Continuity-rule checkpoint: `4e80db2498727a06aa0ddd29e298338b59d0b907`
- Phase A intro-carrier audit checkpoint: `200fc992b44556837897ecb1192044e5e9547a86`
- Phase B 16→17 boundary-proof artifact commit: `f547866fb0cda873b8e9125fdabc0f21d1683489`

**Important:** always fetch the current branch tip before writing. Do not assume any older checkpoint SHA remains HEAD.

---

## Frozen project constraints

Unless the user explicitly changes them:

- **No retraining** to make historical pieces fit.
- **No threshold/tolerance changes** to force agreement.
- **No production edits** as part of the research/provenance closure.
- Preserve historical evidence rather than rewriting contradictory or incomplete records.
- Treat the closed 17–113 chain as immutable research evidence unless new evidence proves a factual error.
- Current work should be read-only / forensic wherever possible.
- Historical use of Codespaces is part of provenance; **measures 1–16 were trained in Codespaces**.
- Do not require new Codespaces work when GitHub evidence is sufficient.
- Do not invent the missing late intro 36-feature assembler or substitute an older feature ordering for it.

---

## What is already closed

### Measures 17–113

Measures **17–113 are formally closed as one research/provenance chain** at:

`fd8905d34175f9f20d9973807fed18c1e23c737a` — `Checkpoint V143 17-113 research closure`

The recovered 17–32 evidence remains authoritative:

- historical generator: `analyzer/v143_fresh_verse1_reference_free_capture.py`;
- historical/current generator blob exact: `c8ea8eca33819fb506f06105f87075dadd133214`;
- target boundary explicitly starts at measure **17** and ends at 32;
- carrier lineage: direct Demucs6s Guitar plus BS-RoFormer Instrumental → Demucs6s Guitar;
- deterministic separator: shifts 1, overlap 0.10, segment size 6, seed 143;
- old uncommitted Verse1 carrier SHA-256: `fbb2c6ca28e1e142ea5fdbc8e55dd7b67d1a55009c179fe4e8e3ec3a02251e15`;
- recovered generator reproduced that carrier SHA-256 exactly;
- historical/current scoring core is blob-identical at SHA-256 `ee62a86adc5f60119d00b5b57a25ee8f0b06f4fe`;
- historical target sequence replay was exact for 1051 events;
- sealed contextual replay retained the frozen base threshold 0.27 and exact discrete selected-event keys.

The 17–32 evidence-gap resolution is preserved at:

`debug/v143-contextual-prune/measure-17-32-evidence-gap-resolution.json`

Known research structure:

- 17–96: closed development/research chain.
- 97–113: closed reserve.
- 17–113: consolidated research provenance closure.

Do not reopen or modify 17–113 merely to make the intro fit.

---

## Measures 1–16: historical truth and archive

- Measures **1–16 were historically trained in GitHub Codespaces**.
- A forensic snapshot was copied unchanged from the historical Codespace and archived on GitHub.
- Archive commit: `9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d`.
- Archive location: `analyzer/v143-intro-1-16-evidence/codespace-snapshot/`.
- `PROVENANCE.txt` records source HEAD `4d735846fbd834cc4c722f2cb48727e4629647f1` and states no retraining, threshold changes, model changes, or production edits were performed during capture.
- The archive contains 52 historical `intro*.json` artifacts plus hashes/provenance.

Important preserved caches/models include:

- `intro-analysis-cache.json`
- `intro-onset-spectrum-cache.json`
- `intro-spectral-pitch-cache.json`
- `intro-raw-attack-cache.json`
- `intro-raw-attack-harmonic-cache.json`
- `intro-correlation-safe-grid-event-selector-model.json`
- `intro-correlation-safe-grid-event-selector-report.json`
- the 0.27 candidate and 0.45 incumbent selector files
- sequence-model artifacts
- temporal-assignment, pitch-ranking, structured-event, repetition-recovery, and diagnostic artifacts.

---

## Phase A carrier audit — completed forensic finding

### Frozen base selector identified

The archived active base selector is:

`intro-correlation-safe-grid-event-selector-model.json`

Its preserved contract is:

- model: `v143-correlation-safe-grid-event-selector`;
- training measures: **1–8**;
- validation measures: **9–12**;
- development measures: **1–12**;
- diagnostic measures: **13–16**;
- window: **100 ms**;
- L2: **10.0**;
- active decision threshold: **0.27**;
- feature normalization arrays: **36 feature means + 36 feature standard deviations**;
- linear weight vector: bias plus the 36 normalized feature inputs;
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

The active selector file and `intro-correlation-safe-grid-event-selector-threshold027-candidate.json` have the same Git blob SHA (`2540c428333aeef8d1f4bb470ab3d02e99cb6b4d`), proving that the archived active model is literally the preserved 0.27 candidate. The 0.45 incumbent is a different blob.

The selector report records 0.45 as the earlier best validation configuration, while later preserved repetition-recovery evidence explicitly refers to a **validated 0.27 base selector**. Preserve this as historical progression; do not rewrite the earlier report.

### Diagnostic-value correction

The previously cited **F1 ≈ 0.955 with 100% recall on measures 13–16** is verified, but it belongs to:

`intro-correlation-safe-sequence-event-model-report.json`

That sequence experiment reports diagnostic F1 `0.955223880597015`, recall `1.0`, and `productionPromotionAllowed: false`.

It is **not** the diagnostic score of the frozen 0.27 base grid selector. The base correlation-safe selector report gives measures 13–16 diagnostic location F1 `0.8333333333333334` at its recorded earlier report configuration.

Therefore the 0.955 number must never be used as evidence that the active frozen base selector itself achieved that diagnostic score.

### What `intro-onset-spectrum-cache.json` proves

The archived onset-spectrum cache is explicitly a reference-free physical-onset whole-spectrum carrier. It records:

- sample rate 22050;
- hop length 128;
- 36 bins/octave;
- MIDI spectrum range 28–112;
- guitar MIDI range 40–88;
- onset grouping tolerance 30 ms;
- two candidate stem views;
- per-onset `viewA` and `viewB` spectra for the windows:
  - `attackMax`
  - `earlyMean`
  - `sustainMean`.

Those window names line up directly with the three correlation-derived selector features that were neutralized in the frozen model. This establishes that the cache belongs to the historical frozen selector's feature lineage.

However, **do not overclaim the dependency**: the archive does not preserve enough executable source to prove that this cache file itself was opened at runtime by the final selector rather than being an intermediate from which the final 36-vector carrier was assembled.

### Deterministic replay limitation established

The historical checkpoint at source HEAD `4d735846...` references:

`analyzer/WINDOWS_ONE_SHOT_INTRO_TIMING.ps1`

but that file is not present at the recorded source HEAD, is not in the copied Codespace snapshot, and repository searches have not recovered the late feature-assembly implementation.

The copied snapshot also does **not** contain the checkpoint-referenced intermediates:

- `intro-correlation-safe-grid-events-1-12.json`
- `intro-correlation-safe-grid-events-13-16.json`
- `intro-onset-rhythm-cache.json`
- the referenced `ARTIFACTS.md` manifest.

The earlier public historical selector at source HEAD is useful provenance, but it is an older stage (`intro-correlation-safe-grid-event-selector-v1`, threshold 0.45) and its flat named 36-feature ordering must **not** be silently substituted for the later active frozen selector's input assembly.

**Phase A conclusion:** the final model bytes, 100 ms window, normalization, weights, neutralizations, threshold 0.27, split, and substantial reference-free carrier evidence are preserved. But the exact historical executable that transforms the raw/cache evidence into the final ordered 36-feature input vector is not currently preserved in GitHub evidence. Therefore the 52-file intro snapshot is **not, by itself, a complete raw-audio-to-prediction deterministic replay carrier**.

Do not reconstruct missing late feature semantics from guesswork and label them historical truth.

---

## Phase B 16→17 boundary proof — completed

Boundary artifact:

`debug/v143-contextual-prune/intro-16-to-17-boundary-proof.json`

Artifact commit:

`f547866fb0cda873b8e9125fdabc0f21d1683489` — `Prove V143 intro 16-17 carrier boundary`

Status recorded in the artifact:

`passed_with_disclosed_intro_replay_source_gap`

### What is proven

The historically supported common seam is the **reference-free physical-onset / two-view whole-spectrum carrier**, not a guessed late 36-feature vector.

The intro side is authoritatively bounded through measure 16 by the preserved raw-attack cache scope:

`professional-measures-1-16-raw-reference-free-attacks`

The recovered historical Verse1 generator explicitly begins at measure 17 and ends at 32.

The two sides share the following directly evidenced carrier contract:

- target sample rate: **22050 Hz**;
- hop length: **128**;
- bins per octave: **36**;
- spectrum/CQT MIDI range: **28–112**;
- guitar MIDI range: **40–88**;
- physical-onset grouping tolerance: **30 ms**;
- candidate stem views: **2**;
- physical onset-group rows with measure/onset/candidate/support concepts;
- two spectral views named `viewA` and `viewB`;
- spectral window names `attackMax`, `earlyMean`, and `sustainMean`.

The recovered measure-17 generator also explicitly states that it uses the **same frozen V143 deterministic separator and reference-free timing stack used by the intro calibration work** while writing a separate fresh-section cache.

The measure-17 side has stronger replay evidence than the intro side: the historical/current generator blob is exact and regenerates the historical Verse1 cache SHA-256 exactly.

No carrier-format discontinuity requiring retraining, threshold changes, tolerance changes, model changes, or production changes was found at 16→17.

### Exact Verse1 spectral windows recovered

For the recovered historical measure-17 generator, the exact spectral windows are:

- `attackMax`: onset −0.020 s to +0.045 s, max reducer;
- `earlyMean`: onset +0.020 s to +0.095 s, mean reducer;
- `sustainMean`: onset +0.070 s to +0.180 s, mean reducer.

**Important limitation:** the intro cache directly proves those three window names and resulting carrier structure, but the missing intro generator prevents an independent claim that the same numeric offsets are recovered from intro executable source. Do not upgrade the common contract beyond the evidence.

### What Phase B does not prove

The boundary artifact explicitly does **not** claim:

- byte-identical regeneration of the complete 1–16 onset-spectrum cache from raw audio;
- complete raw-audio-to-final-36-feature-vector deterministic replay for the intro selector;
- recovery of the exact historical late intro 36-feature ordering/assembly executable;
- that any stateful learned feature should flow across 16→17;
- that the same classifier must be used on both sides;
- independently recovered numeric intro spectral-window offsets from the missing intro generator.

**Phase B conclusion:** carrier/schema continuity at 16→17 is proven at the strongest level the surviving historical evidence supports. The missing intro assembler remains a disclosed source gap and was not invented or bypassed.

---

## Current forensic question

Phase A and Phase B are complete.

The remaining question is now:

> What is the strongest defensible final 1–113 research statement that joins the archived frozen intro, the proven 16→17 carrier seam, and the independently closed 17–113 chain without falsely claiming a complete raw-audio deterministic replay for measures 1–16?

The answer must distinguish **research provenance/carrier closure** from **complete deterministic raw-audio replay closure**.

---

## Historical split to preserve

- **1–8:** training
- **9–12:** validation
- **13–16:** diagnostic only

Do not relabel 13–16 as a new untouched holdout. Do not use later sequence-model diagnostic success to rewrite the frozen base-selector history.

---

## Next objective

Proceed with **Phase C — maximal truthful 1–113 provenance closure**.

1. Verify that no existing final 1–113 closure artifact would be overwritten.
2. Create a research-only final provenance artifact that joins:

   `1–16 archived frozen intro evidence/carrier → proven 16→17 carrier seam → 17–96 closed development chain → 97–113 closed reserve`

3. The final artifact may close the **research provenance/carrier chain** if all inherited evidence remains consistent.
4. It must **not** claim complete raw-audio deterministic replay across 1–113 because the late historical intro 36-feature assembler remains missing.
5. Preserve the exact split, frozen threshold/window/model, 17–113 closure, boundary-proof scope, and all no-retraining/no-production invariants.
6. Explicitly label the unresolved intro source gap as a limitation of replay completeness, not as a reason to rewrite or retrain the frozen model.
7. After creating the final artifact, **update and commit this checkpoint again before any further work**.

A suitable strongest status, if the evidence remains consistent, is conceptually:

**closed 1–113 research provenance/carrier chain with the intro deterministic-replay source gap explicitly disclosed**.

Do not call it a complete deterministic 1–113 raw-audio replay closure.

---

## Things specifically ruled out

- Retraining 1–16 to reproduce later behavior.
- Adjusting thresholds/tolerances to make 1–16 and 17–113 agree.
- Substituting the older public v1 36-feature ordering for the missing later assembler.
- Treating the sequence-model F1≈0.955 diagnostic as the frozen base selector's score.
- Force-pushing over the 17–113 closure.
- Reopening 17–113 to make the intro fit.
- Calling `intro-onset-spectrum-cache.json` a proven direct runtime file dependency without consumer-source evidence.
- Inventing missing generator semantics and presenting them as recovered history.
- Claiming that Phase B recovered the missing intro assembler.
- Claiming numeric intro spectral-window offsets were independently recovered when only the window names/carrier are directly preserved.
- Calling the final chain a complete raw-audio deterministic 1–113 replay unless new authoritative intro source is recovered.
- Production modification or promotion during this research closure.

---

## Important new commits / artifacts

Phase A evidence/checkpoint:

- `200fc992b44556837897ecb1192044e5e9547a86` — `Checkpoint V143 intro carrier audit`.

Phase B artifact:

- `f547866fb0cda873b8e9125fdabc0f21d1683489` — `Prove V143 intro 16-17 carrier boundary`;
- `debug/v143-contextual-prune/intro-16-to-17-boundary-proof.json`.

Foundational evidence retained:

- `9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d` — archived historical intro evidence;
- source provenance HEAD `4d735846fbd834cc4c722f2cb48727e4629647f1`;
- `fd8905d34175f9f20d9973807fed18c1e23c737a` — closed 17–113 research chain;
- `debug/v143-contextual-prune/measure-17-32-evidence-gap-resolution.json`;
- `analyzer/v143_fresh_verse1_reference_free_capture.py` blob `c8ea8eca33819fb506f06105f87075dadd133214`;
- intro onset-spectrum-cache blob `4651f14ed15df3f9e596f9cd4fa3f8afe8a9b45d`;
- intro raw-attack-cache blob `b58275e5fa846fe655747cd26bbd8139025d5072`;
- active frozen intro selector blob `2540c428333aeef8d1f4bb470ab3d02e99cb6b4d`.

No runtime or production code was changed during Phase A or Phase B. The only writes were research evidence/checkpoint documentation.

---

## Codespace preservation note

The historical Codespace remains part of provenance, but the copied GitHub archive is the durable first source for current forensics. Do not ask the user to reopen Codespaces merely to inspect preserved intro JSON evidence.

If some future independent source recovers the missing historical late feature assembler or omitted grid-event intermediates, verify hashes/provenance first and then append that evidence; do not rewrite the current source-gap finding retroactively.

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

Never delete old provenance merely because a later conclusion is cleaner. Record corrections explicitly.

---

_Last updated on 2026-08-21 (user local date) after the Phase B 16→17 carrier-boundary proof; next authorized work is the maximal truthful 1–113 provenance closure._
