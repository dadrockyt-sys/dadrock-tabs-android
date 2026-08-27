# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-27 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 CPU multitrack architecture reset — broad-Other protocol is frozen; reference-facing scoring has NOT run in this continuation.**

## History preservation
- The full checkpoint immediately before this compact continuation is preserved in Git at branch commit `3705b8aba3f166000867f7c68e5dfc104bc71fd9`; checkpoint Git blob `5a19f89583af89e777380d5ddb453c4957afe5f5`.
- Earlier pre-compaction history remains preserved at `docs/checkpoints/archive/CURRENT_STATE-pre-phase-c-auth-intake-20260827.md`; historical Git blob `f71ba11394e6f2f46843055e748e8717ff484158`.
- Do not reinterpret old consumed one-use V147–V153 runs as reusable. Their sealed status remains in force.

## Standing authorization / safety policy
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify, merge, promote, or otherwise touch `main` or Production unless the user explicitly changes that policy.
- Professional references are scoring-only. Candidate generation/transcription must not read them.
- Freeze generated outputs before reference access. No silent variant search and no post-score retuning of the same scored output.
- Do not commit user-uploaded professional-tab screenshot bytes or note-by-note copyrighted reference data to this public repository.
- Target remains fully automatic audio -> professional-quality Rhythm/Lead/Bass tablature PDF with **no human correction**.

## Sealed V153 conclusion
- V153 Phase D event-347 CPU Gold attribution is COMPLETE / SEALED.
- The V153 aggregate pitch-content deficit was explained as a measure-level `(measure, MIDI)` histogram effect rather than a local event timing/chord correctness loss.
- Per-measure pitch-content/histogram scoring is therefore **diagnostic only** for V154 and must not drive event-level candidate selection.
- V153 one-event Gold-guided micro-correction is not the main path anymore; V154 is an architecture benchmark/reset.

## V154 pre-reset engineering history
- A1 run `33087772583`: engineering failure before transcription due TFLite / NumPy ABI mismatch; reference access NO; sealed.
- A2 run `33088418439`: CPU Basic Pitch inference succeeded after runtime repair, but JSON persistence failed on nested NumPy scalar pitch-bend metadata; reference access NO; sealed.
- A3 run `33088829644`: CPU Basic Pitch 0.4.0 inference succeeded on the raw normalized mix with **572 note events**; persistence commit was rejected non-fast-forward after local write; Demucs did not run; reference access NO; score calls `0`; sealed as engineering/concurrency failure. Do not rerun consumed A3 as-is.
- A3 runtime evidence: Python 3.10, NumPy 1.26.4, PyTorch 2.8.0+cpu, `torch.version.cuda=None`, CUDA unavailable.

## Frozen professional reference identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.

- Rhythm identity: existing `main:public/Professionalexample.jpg`; Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`. Research receipt: `debug/v154-cpu-autonomous/reference-receipts/rhythm-existing-professionalexample-20260827.json`; receipt blob `258eb10fe44951d5f1f5969959ff0ca69bd852db`.
- Bass identity: user-provided 17 screenshots, visible measures 1–113; frozen set SHA256 `abd1748066966ceb93fe40bf8c8df3168f6c871ba006e44d28f8840184e3cde3`. Receipt: `debug/v154-cpu-autonomous/reference-receipts/bass-user-upload-20260827.json`; receipt blob `0cd7a2e451ae4ea17b4ba15e6c2e2508f27518fd`. Visible measure-88 `Timing mishap here` remains an uncertainty flag.
- Lead identity: user-provided 22 screenshots, visible measures 1–113, opening tempo quarter=129, 4/4; frozen set SHA256 `de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c`. Receipt: `debug/v154-cpu-autonomous/reference-receipts/lead-user-upload-20260827.json`; receipt blob `e4cfa0a3c1f9c53bcdcb5b6ae8d73f9def5f7937`. Visible `Probably a mistake they left in` near measures 39–40 remains an uncertainty flag.
- Three-part manifest: `debug/v154-cpu-autonomous/reference-receipts/reference-set-manifest-20260827.json`; creation commit `4eae3fa541c1cbede282db20c113a22f7b906fbb`.
- The raw Bass/Lead screenshot bytes are **not attached to the current ChatGPT conversation** as of this checkpoint. Their frozen identities remain valid, but private note-by-note normalization cannot be faithfully reconstructed here by guessing from receipts or memory.

## V154 reference/scoring contract already present
- Contract: `validation/v154_cpu_multitrack/REFERENCE_FORMAT.md`.
- Empty copyright-safe template: `validation/v154_cpu_multitrack/reference-template.json`.
- Existing post-role scorer: `validation/v154_cpu_multitrack/score_multitrack_reference.py`; Git blob `f58b6cf7349a6f6e5f49b241a585ba5bf3648966`.
- Existing scorer separates combined recognition, role separation, per-part transcription, and fretboard assignment, but it assumes Rhythm/Lead generated parts exist. V154 now also has a dedicated stage-one scorer so combined Guitar can be evaluated **before** role splitting.

## New continuation work — 2026-08-27

### Broad-Other CPU preregistration — FROZEN / REFERENCE-INDEPENDENT
- File: `debug/v154-cpu-autonomous/broad-other-preregistration.json`.
- Creation commit: `69102364d79c315044c994ff0acaf52dbc827dd5`.
- Historical audio is frozen to commit `74b0f815ff3f66f325220975c410621503de440f`, path `public/gomywayfullaitest.m4a`, bytes `3478611`, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Grid stays frozen at tempo `129.19921875`, 4 steps/beat, 16 steps/measure, 113 measures.
- Separator is frozen to CPU `demucs==4.1.0`, model `htdemucs`, shifts `1`, jobs `1`.
- `Other` is intentionally the **combined Rhythm+Lead acoustic source**; `Bass` is independent. Do not ask the separator to split Rhythm versus Lead at this stage.
- Basic Pitch is frozen to `0.4.0`, onset threshold `0.5`, frame threshold `0.3`, minimum note length `127.7 ms`, melodia trick enabled, no threshold sweep.
- Combined Guitar MIDI range is frozen to `40–88`; Bass MIDI range is frozen separately to `28–67` so the stage does not inherit the old guitar-only lower bound for Bass.
- Runtime target remains Python 3.10, NumPy 1.26.4, PyTorch 2.8.0+cpu, imageio-ffmpeg 0.6.0; CUDA must be absent/unavailable.

### New reference-free transcriber
- File: `validation/v154_cpu_multitrack/transcribe_broad_other.py`.
- Creation commit: `c4a707d34b1a44dc34a8245f922773d43f0538cf`.
- Inputs: already-separated `Other` and `Bass` audio stems.
- Output schema: `dadrock.tabs.v154.cpu-multitrack-generated.v1` with frozen `combinedGuitar` and `bass` note/onset streams.
- The transcriber contains no reference input and records `referenceRead=false`, `humanCorrection=false`, `referenceGuidedFiltering=false`, `modalUsed=false`, `cudaGpuUsed=false`.
- NumPy/nested Basic Pitch metadata is converted recursively to JSON-native values, preserving the A3 serialization repair.

### New stage-one combined-Guitar/Bass scorer
- File: `validation/v154_cpu_multitrack/score_frontend_reference.py`.
- Creation commit: `a5cab589b3efca8ec454311c49120543c04277fb`.
- It scores frozen generated `combinedGuitar` directly against the private union of professional Rhythm+Lead, **before any generated Rhythm/Lead role split**.
- It scores frozen generated `bass` independently against professional Bass.
- Primary metric: same-MIDI one-to-one timing-aware F1 within ±0.5 grid step. Gross ±2-step F1 and per-measure pitch-content are diagnostics.
- Optional private reference events can carry `excludeFromScoring=true` for explicitly uncertain annotated spots; this masks uncertainty without silently correcting/replacing the reference note.
- The scorer checks private-reference authorization flags and generated anti-leakage flags before scoring.

## V154 architecture decision gates — FROZEN
- Combined Rhythm+Lead timing-aware note/pitch F1 target: **>= 0.80**.
- Bass timing-aware note/pitch F1 target: **>= 0.80**.
- Onset-aware note F1 target: **>= 0.75**.
- Rhythm/Lead role accuracy conditional on correctly recognized guitar notes: **>= 0.85** (later stage only).
- String/fret correctness conditional on correct pitch+role: **>= 0.85** (later stage only).
- Missing a gate is evidence about the responsible architecture stage, not permission to tune the already-scored output against reference truth.

## Current execution status
- Reference-facing score calls in this continuation: **0**.
- Professional reference note data opened in this continuation: **NO**.
- Demucs separation executed in this continuation: **NO**.
- Broad-Other/Bass Basic Pitch transcription executed in this continuation: **NO**.
- Modal/L4/CUDA/GPU used: **NO**.
- `main` / Production modified: **NO**.
- A temporary checkpoint-writer workflow was attempted at commit `1088abf215d71cda2231120abd8bca4c00f1811a`; GitHub marked the run failed before any job started, so it did not alter this checkpoint. Remove/seal that workflow before further execution.

## Exact next steps
1. Remove/seal `.github/workflows/v154-resume-checkpoint-writer-once.yml`; it is a failed temporary writer and must not remain armed.
2. Validate the new stage-one scorer/transcriber with reference-free synthetic/unit tests only.
3. If CPU execution proceeds, create a **new one-use** broad-Other benchmark workflow from the frozen preregistration; do not rerun A3. It must verify exact historical audio identity, CPU-only runtime, normalize audio, run `htdemucs` to produce `other` + `bass`, then run `transcribe_broad_other.py` and persist/hash generated outputs **before any professional reference access**.
4. Do not score those outputs until the privately normalized Rhythm/Lead/Bass reference payload is accessible and its normalized identity is frozen. The current conversation has no attached Bass/Lead screenshots, so do not reconstruct note content from memory.
5. Once private normalized references are accessible, score combined Guitar first and Bass second with `score_frontend_reference.py`. Freeze the score as one consumed evaluation of the generated output; no post-score retuning of that output.
6. Only after acoustic recognition is frozen should Rhythm/Lead role separation, fret/string assignment, techniques, and PDF work continue.
7. Continue saving this file frequently after each meaningful freeze/run/result.
