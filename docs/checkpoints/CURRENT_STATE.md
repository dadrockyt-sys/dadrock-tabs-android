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
- Checkpoint parent / evidence head at creation: `9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d`
- Previous closed 17–113 checkpoint: `fd8905d34175f9f20d9973807fed18c1e23c737a`

**Important:** the branch tip will move when this file or later research artifacts are committed. Always fetch the current branch tip instead of assuming `9b0f417f...` remains HEAD.

---

## Frozen project constraints

Unless the user explicitly changes them:

- **No retraining** to make historical pieces fit.
- **No threshold/tolerance changes** to force agreement.
- **No production edits** as part of the research/provenance closure.
- Preserve historical evidence rather than rewriting contradictory or incomplete records.
- Treat the closed 17–113 chain as immutable research evidence unless new evidence proves a factual error.
- Current work should be read-only / forensic wherever possible.
- Historical use of Codespaces is part of provenance; **measures 1–16 were trained in Codespaces**. The current "no Codespaces" preference means do not depend on Codespaces for new reconstruction work when GitHub evidence is sufficient.

---

## What is already closed

### Measures 17–113

Measures **17–113 are formally closed as one research/provenance chain** at commit:

`fd8905d34175f9f20d9973807fed18c1e23c737a` — `Checkpoint V143 17-113 research closure`

That closure includes the recovered historical 17–32 evidence and preserves the historical gap record rather than rewriting it.

Known research structure from the closed chain:

- 17–96: closed development/research chain.
- 97–113: closed reserve.
- Historical evidence for 17–32 was recovered and incorporated into the provenance record.

Do not reopen 17–113 merely to make the 1–16 front end fit it.

---

## Measures 1–16: historical truth now established

- Measures **1–16 were historically trained in GitHub Codespaces**.
- The original Codespace retained substantial intro-model evidence that was not previously present on the research branch.
- A forensic snapshot was copied unchanged from the Codespace and archived on GitHub.
- No retraining, model changes, threshold changes, or production edits were performed during archival.

Archive commit:

`9b0f417f8f927e6d5102e4c8bf6c42e3f6a4c10d` — `Archive historical Codespace intro 1-16 evidence`

Archive location:

`analyzer/v143-intro-1-16-evidence/codespace-snapshot/`

The archive contains:

- 52 historical `intro*.json` artifacts.
- `PROVENANCE.txt` describing the source branch/HEAD and capture context.
- `SHA256SUMS.txt` containing SHA-256 hashes for the copied JSON evidence.

The snapshot was safety-checked before commit for obvious secret-like JSON keys and GitHub file-size problems. The largest visible file was about 17.8 MB, below GitHub's normal single-file limit.

---

## Important 1–16 artifacts now preserved

The snapshot includes historically significant artifacts such as:

- `intro-sequence-event-model.json`
- `intro-onset-group-sequence-model.json`
- `intro-learned-onset-spectral-set-model.json`
- `intro-onset-spectrum-cache.json`
- `intro-spectral-pitch-cache.json`
- `intro-analysis-cache.json`
- `intro-raw-attack-cache.json`
- `intro-raw-attack-harmonic-cache.json`
- supervised temporal-assignment model/report artifacts
- supervised pitch-ranker model/report artifacts
- structured-event decoder model/report artifacts
- repetition-recovery artifacts
- multiple stage, harmonic-rank, raw-attack, sequence, selector, and diagnostic reports

This list is illustrative, not exhaustive. Use the archived directory as the authoritative inventory.

---

## Current forensic question

The remaining structural problem before claiming a clean **1–113 end-to-end research chain** is the **1–16 frozen inference/replay path and the 16→17 boundary**.

The key question is:

> Was `intro-onset-spectrum-cache.json` only a historical Codespaces training/reference artifact, or was it required by the frozen 1–16 inference path?

Do **not** infer the answer from the filename. Trace actual consumers, models, reports, and replay scripts.

---

## Historical split to preserve

The historical intro separation must remain intact while investigating:

- **1–8:** training
- **9–12:** validation
- **13–16:** independent diagnostic

Earlier independent diagnostics for 13–16 were reported as approximately **F1 ≈ 0.955 with 100% recall**. Treat that as a claim to verify against preserved artifacts, not as a value to tune toward.

---

## Next objective

Proceed with **GitHub-only, read-only forensics** unless a write artifact is explicitly needed for documentation.

### Phase A — trace the frozen 1–16 carrier

1. Inventory the archived 1–16 artifacts and identify model/config/report relationships.
2. Search repository history and scripts for all consumers/producers of:
   - `intro-onset-spectrum-cache.json`
   - `intro-sequence-event-model.json`
   - `intro-onset-group-sequence-model.json`
   - `intro-learned-onset-spectral-set-model.json`
   - `intro-spectral-pitch-cache.json`
   - related temporal-assignment / structured-event / pitch-ranking models.
3. Determine the exact data required for **frozen inference**, distinguishing it from training-only/reference-only inputs.
4. Verify the historical 1–8 / 9–12 / 13–16 split and diagnostic outputs from preserved evidence.
5. Identify the exact prediction/inference carrier that can replay measures 1–16 without retraining.

### Phase B — prove the boundary

6. Compare the frozen measure-16 output/carrier with the established measure-17 entry conditions.
7. Build a research-only boundary proof for **16→17**.
8. Do not alter either side simply to make the handoff pass.

### Phase C — close 1–113

9. Only after independent 1–16 replay and the 16→17 boundary are proven, create the final provenance artifact joining:

`1–16 frozen intro → 17–96 closed development chain → 97–113 closed reserve`

10. Update this file immediately after that milestone.

---

## Things specifically ruled out

- Retraining 1–16 to reproduce later behavior.
- Adjusting thresholds/tolerances to make 1–16 and 17–113 agree.
- Force-pushing over the 17–113 closure.
- Treating the old Codespace as the only surviving source of truth now that its intro evidence has been archived on GitHub.
- Assuming `intro-onset-spectrum-cache.json` is an inference dependency merely because it exists.

---

## Codespace preservation note

During the archive transfer, local Codespace working changes were intentionally preserved rather than destroyed, and the historical untracked training artifacts were not deleted. The GitHub archive is now the durable copy needed for current forensics.

Do not require the user to reopen Codespaces merely to inspect the 52 archived intro artifacts; read them from GitHub first.

---

## Chat continuity workflow

To avoid losing hours when a long chat crashes:

1. **After every major work unit, commit an updated `docs/checkpoints/CURRENT_STATE.md` on `v143-contextual-prune-lobo` before beginning the next major work unit.**
2. Include the latest evidence commit(s), conclusion, unresolved question, and next exact objective.
3. Start a fresh chat when the UI becomes heavy rather than waiting for a crash.
4. In the new chat, say only:
   **`Continue DadRock from docs/checkpoints/CURRENT_STATE.md on branch v143-contextual-prune-lobo.`**
5. The assistant should verify GitHub and continue directly from the checkpoint.
6. Screenshots are secondary evidence once their underlying files/results have been preserved in GitHub.

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

_Last updated on 2026-08-21 (user local date) to make the major-work checkpoint discipline explicit._
