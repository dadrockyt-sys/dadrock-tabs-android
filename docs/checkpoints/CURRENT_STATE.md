# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-27 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 broad-Other CPU recognition is COMPLETE / FROZEN / STRUCTURAL-QC PASS. Professional Rhythm/Bass/Lead visual references are preserved. Reference-facing scoring has NOT run. This continuation has resumed the dedicated reference timing-normalization phase.**

## History preservation
- Immediate pre-continuation checkpoint blob: `2f506ec99dbad7ec6fbf64b43ea1624df7fdffc3`.
- Full earlier checkpoint: commit `3705b8aba3f166000867f7c68e5dfc104bc71fd9`; checkpoint blob `5a19f89583af89e777380d5ddb453c4957afe5f5`.
- Earlier archive: `docs/checkpoints/archive/CURRENT_STATE-pre-phase-c-auth-intake-20260827.md`; blob `f71ba11394e6f2f46843055e748e8717ff484158`.
- Consumed V147–V153 and consumed V154 one-use runs remain sealed/non-reusable.

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- Frozen generated output must not be altered, retuned, variant-searched, or corrected after reference access/scoring.
- Do not commit professional-tab screenshot bytes. Machine-readable private reference transcriptions may exist only under `research/v154-professional-references/` on this research branch; never promote them to `main`/Production or expose them to candidate generation.
- Target remains fully automatic audio -> professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Frozen song / protocol
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Audio: `public/gomywayfullaitest.m4a`, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Grid: tempo `129.19921875`, 4 steps/beat, 16 steps/measure, 113 measures.
- CPU separator: `demucs==4.1.0`, `htdemucs`, shifts 1, jobs 1. `Other` = combined Rhythm+Lead; Bass independent.
- Basic Pitch `0.4.0`: onset 0.5, frame 0.3, minimum 127.7 ms, melodia enabled, no threshold sweep. Combined Guitar MIDI 40–88; Bass 28–67.
- Frozen preregistration: `debug/v154-cpu-autonomous/broad-other-preregistration.json`; blob `eb81efbb1ed25b023b5bce6e1159ae7785875b4a`.
- Scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`; current branch blob `9644e65719fbd361a9b39778ae9950c5e983e855`.

## Architecture gates — FROZEN
- Combined Rhythm+Lead timing-aware note/pitch F1 >= 0.80.
- Bass timing-aware note/pitch F1 >= 0.80.
- Onset-aware note F1 >= 0.75.
- Later conditional Rhythm/Lead role accuracy >= 0.85.
- Later conditional string/fret correctness >= 0.85.
- A missed gate diagnoses architecture; it never authorizes post-score tuning of the consumed output.

## Frozen generated candidate — DO NOT TOUCH
- Authoritative CPU run `33096559281`, job `98602884120`, head `986e2a69a6cb877a203d2f8b04115914dc8fd2e6`.
- `debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json`.
- Frozen generated SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`.
- Counts: 1089 combined-Guitar events; 635 Bass events.
- Full persistence commit `decc2d022db11a1689cc6f15e72982c934107f6f`.
- Reference-free structural QC: PASS; `debug/v154-cpu-autonomous/broad-other-run-33096559281/structural-qc.json`; commit `4a215d5dce3755438e6a284c96fa237d3a0d86a2`.
- Generation safety remains: reference read NO; human correction NO; threshold sweep NO; Modal/L4/CUDA/GPU NO; main/Production NO.

## Frozen professional references
### Rhythm — visual/timing reference frozen
- Source identity: `main:public/Professionalexample.jpg`; Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`.
- `research/v154-professional-references/rhythm-professional-reference.json`; Git blob `248741bade9665a34648c59a2994bd27d73fc406`.
- Declared measures 1–113; 603 events; 946 note entries.
- It already contains exact per-event `step` fields on the 16-step measure grid and can be transformed losslessly into scorer rows.

### Bass — visual machine-readable, timing normalization in progress
- Canonical 17-page set SHA256 `abd1748066966ceb93fe40bf8c8df3168f6c871ba006e44d28f8840184e3cde3`.
- `research/v154-professional-references/bass-professional-reference-machine-readable.json`; Git blob `0773c98556d00837eaea28ee77cfc513498cc21f`; SHA256 `a8e1d123f8a19e69d9c160d78aea7637b5a2012232b23e1f1ddff051e9bc40b3`.
- 113 measure objects; 569 event objects; 562 pitched; 7 dead notes; 8 continuation-only; observed MIDI 28–56.
- Measure 88 source annotation `Timing mishap here` remains an uncertainty and must not be silently repaired.
- **Continuation recovery:** canonical Bass screenshot sequence is still accessible in the user Library (e.g. `1000120387.jpg` starts measures 1–12; subsequent `10001203xx.jpg` pages continue the set). Source notation can therefore be used for exact rhythmic normalization instead of inventing timing from horizontal spacing.

### Lead — visual machine-readable, exact timing not yet frozen
- Frozen 22-page set SHA256 `de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c`.
- `research/v154-professional-references/lead-professional-reference-machine-readable.json`; Git blob `b018d93bb5e2119ee843fbd3fbc9139484fde0d1`; SHA256 `122e0f6b2fa63fb2ea701e9cefe897dd4337fd08de0792e11579f4933804b716`.
- 113 measure objects; 487 event objects; 476 pitched; 11 dead notes; 23 continuation-only; observed MIDI 45–81.
- Measures 39–40 `Probably a mistake they left in` remains source uncertainty; detached gray dot at measure 81 remains unassigned.
- Exact `step` onset fields are not frozen yet.
- **Continuation recovery status:** the current Library exposes the Bass page set but not the prior 22 Lead source pages. Do not invent Lead timing from visual-order JSON alone. Recover actual Lead pages before freezing Lead timing.

## Current continuation status
- Reference-facing score calls: **0**.
- Frozen generated candidate modified: **NO**.
- `main` / Production modified: **NO**.
- Modal/L4/CUDA/GPU used: **NO**.
- Professional reference access this continuation: **Rhythm/Bass metadata and Bass source page inspection only; no scoring.**
- Bass source page 1 was directly re-opened and confirms explicit rhythmic stems/beams for measures 7–12, so exact timing can be normalized from notation rather than spacing.

## Exact next steps
1. Freeze a scorer-ready Rhythm normalization derived only from the already-frozen Rhythm reference (`measure`, `step`, `midi`), with provenance/count/hash receipt. Save checkpoint.
2. Normalize Bass exact 16-step attacks from the canonical source notation page-by-page. Preserve dead notes/continuations appropriately; exclude only explicitly justified uncertainty (including measure 88 until resolved). Freeze scorer-ready Bass rows and provenance/count/hash receipt. Save checkpoint frequently.
3. Recover the actual 22 Lead source pages. **Do not** infer exact Lead timing from visual-order JSON alone. Normalize Lead from source notation, preserve uncertainty flags, then freeze scorer-ready Lead rows and receipt. Save checkpoint.
4. Assemble one immutable scorer reference payload with authorized private-scoring flags and Rhythm/Lead/Bass rows. Verify its identity before any score call.
5. Score the exact frozen combined Guitar first and Bass second **exactly once** with `score_frontend_reference.py`; interpret preregistered gates; never retune this consumed output afterward.
6. Only after acoustic recognition is scored/frozen: continue Rhythm/Lead role separation, fret/string assignment, techniques, and PDF work.
