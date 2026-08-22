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
- Previous continuity-rule checkpoint: `4e80db2498727a06aa0ddd29e298338b59d0b907`

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

---

## What is already closed

### Measures 17–113

Measures **17–113 are formally closed as one research/provenance chain** at:

`fd8905d34175f9f20d9973807fed18c1e23c737a` — `Checkpoint V143 17-113 research closure`

The recovered 17–32 evidence is especially important for the future 16→17 proof:

- authoritative historical generator: `analyzer/v143_fresh_verse1_reference_free_capture.py`;
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

Known research structure from the closed chain:

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

The archived onset-spectrum cache is explicitly a reference-free physical-onset whole-spectrum carrier. It records, among other things:

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

### Deterministic replay limitation now established

The historical checkpoint at source HEAD `4d735846...` references the generator/script:

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

## Current forensic question

Phase A has narrowed the remaining problem.

The next question is no longer simply whether `intro-onset-spectrum-cache.json` existed in the inference lineage; it demonstrably did. The unresolved issue is:

> Can the preserved intro carrier be joined to the independently recovered measure-17 carrier at a historically justified common boundary/schema **without inventing the missing late 36-feature assembly logic**?

The 17-side generator is unusually useful here because it emits the same broad reference-free onset-spectrum concepts (`viewA`/`viewB`, `attackMax`, `earlyMean`, `sustainMean`) under a deterministic historical carrier that was regenerated byte-identically.

---

## Historical split to preserve

- **1–8:** training
- **9–12:** validation
- **13–16:** diagnostic only

Do not relabel 13–16 as a new untouched holdout. Do not use later sequence-model diagnostic success to rewrite the frozen base-selector history.

---

## Next objective

Proceed with **Phase B — research-only 16→17 boundary proof**.

1. Read the end of the preserved intro onset-spectrum carrier (measure 16) and the recovered historical Verse1 generator contract (measure 17).
2. Compare carrier schema and invariants at the boundary, including:
   - sample rate;
   - hop length;
   - bins per octave and MIDI range;
   - two-view stem lineage;
   - onset grouping behavior;
   - `attackMax` / `earlyMean` / `sustainMean` windows;
   - timing/grid fields and measure numbering.
3. Determine whether a common research carrier boundary can be proven independently of the missing intro 36-feature assembler.
4. If the boundary can be proven, create a research-only boundary artifact documenting exactly what is proven and what is not.
5. If it cannot be proven, record the irreducible source gap rather than changing either side.
6. **Before any Phase C work, update and commit this checkpoint again.**

### Phase C — only if Phase B passes

Only after the boundary proof is valid may the final provenance artifact join:

`1–16 frozen intro → 17–96 closed development chain → 97–113 closed reserve`

A final 1–113 claim must clearly distinguish:

- frozen model preservation;
- carrier/schema continuity;
- deterministic replay coverage;
- any historical source gap that remains.

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
- Production modification or promotion during this research closure.

---

## Important new commits / artifacts

Evidence consulted in this Phase A audit includes:

- `9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d` — archived historical intro evidence;
- source provenance HEAD `4d735846fbd834cc4c722f2cb48727e4629647f1`;
- `fd8905d34175f9f20d9973807fed18c1e23c737a` — closed 17–113 research chain;
- `analyzer/v143-intro-1-16-evidence/codespace-snapshot/intro-correlation-safe-grid-event-selector-model.json`;
- `.../intro-correlation-safe-grid-event-selector-report.json`;
- `.../intro-correlation-safe-grid-event-selector-threshold027-candidate.json`;
- `.../intro-correlation-safe-grid-event-selector-threshold045-incumbent.json`;
- `.../intro-correlation-safe-sequence-event-model-report.json`;
- `.../intro-onset-spectrum-cache.json`;
- `.../PROVENANCE.txt`;
- `debug/v143-contextual-prune/measure-17-32-evidence-gap-resolution.json`;
- `analyzer/v143_fresh_verse1_reference_free_capture.py`.

No runtime or production code was changed during this audit. This checkpoint update is the only write authorized by the continuity rule.

---

## Codespace preservation note

The historical Codespace remains part of provenance, but the copied GitHub archive is the durable first source for current forensics. Do not ask the user to reopen Codespaces merely to inspect preserved intro JSON evidence.

If some future independent source recovers the missing historical late feature assembler or omitted grid-event intermediates, verify hashes/provenance first and then append that evidence; do not rewrite this source-gap finding retroactively.

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

_Last updated on 2026-08-21 (user local date) after the Phase A frozen-intro carrier audit; next authorized work is the 16→17 boundary proof._
