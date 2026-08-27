# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-27 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 broad-Other CPU recognition output is COMPLETE / FROZEN / STRUCTURAL-QC PASS. Rhythm, Bass, and Lead are now preserved machine-readably. Bass and Lead remain visual-order references without frozen exact 16-step scorer timing. Professional-reference scoring has NOT run.**

## History preservation
- Full earlier checkpoint: commit `3705b8aba3f166000867f7c68e5dfc104bc71fd9`; checkpoint blob `5a19f89583af89e777380d5ddb453c4957afe5f5`.
- Pre-QC compact checkpoint blob: `dbb058e24212022ad4f28b8bb13fccfec2cc8af8`.
- Earlier pre-compaction archive: `docs/checkpoints/archive/CURRENT_STATE-pre-phase-c-auth-intake-20260827.md`; blob `f71ba11394e6f2f46843055e748e8717ff484158`.
- Consumed V147–V153 runs and consumed V154 one-use runs remain sealed/non-reusable.

## Standing authorization / safety
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- Freeze generated outputs before reference access. No silent variant search and no post-score retuning of a consumed output.
- Do not commit user-provided professional-tab screenshot bytes. By explicit user direction, machine-readable reference transcriptions may be stored only under `research/v154-professional-references/` on research branch `v143-contextual-prune-lobo`; never promote them to `main`/Production and never expose them to candidate generation.
- Target remains fully automatic audio -> professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## V153 sealed conclusion
- V153 event-347 attribution showed its aggregate pitch-content deficit was a coarse measure-level `(measure, MIDI)` histogram effect, not evidence of local event timing/chord failure.
- Per-measure pitch-content is diagnostic only in V154; V154 is an architecture reset rather than further one-event Gold-guided micro-correction.

## V154 early engineering history — SEALED
- A1 `33087772583`: TFLite/NumPy ABI failure before transcription.
- A2 `33088418439`: CPU Basic Pitch inference succeeded; JSON persistence failed on nested NumPy scalar metadata.
- A3 `33088829644`: raw CPU Basic Pitch succeeded with 572 events, but branch persistence failed non-fast-forward; Demucs/reference score did not run. Do not rerun A3 as-is.
- A3 established deterministic normalization: 44.1 kHz, stereo, PCM s16le. Runtime: Python 3.10, NumPy 1.26.4, PyTorch 2.8.0+cpu, CUDA unavailable.

## Frozen professional reference identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Rhythm: `main:public/Professionalexample.jpg`; Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`.
- Bass: 17 user screenshots, visible measures 1–113; frozen set SHA256 `abd1748066966ceb93fe40bf8c8df3168f6c871ba006e44d28f8840184e3cde3`; measure-88 `Timing mishap here` is an uncertainty flag.
- Lead: 22 user screenshots, visible measures 1–113; frozen set SHA256 `de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c`; opening tempo quarter=129, 4/4; measures 39–40 annotation remains an uncertainty flag.
- Reference-set manifest: `debug/v154-cpu-autonomous/reference-receipts/reference-set-manifest-20260827.json`; commit `4eae3fa541c1cbede282db20c113a22f7b906fbb`.
- Bass is preserved under `research/v154-professional-references/` with its canonical bytes identity-matched. Lead has now also been re-provided and preserved visually machine-readably. The active-chat Lead copies are platform-rendered/re-encoded, so their byte hashes differ from the earlier frozen upload receipt; the 22-page order, measures 1–113, tempo/time-signature opening, green UI overlay, and measures 39–40 source annotation visually corroborate the frozen Lead identity. Exact 16-step Bass/Lead timing is intentionally not frozen yet, so those files are not scorer-ready.

## V154 frozen broad-Other protocol
- Preregistration: `debug/v154-cpu-autonomous/broad-other-preregistration.json`; Git blob `eb81efbb1ed25b023b5bce6e1159ae7785875b4a`.
- Historical audio: commit `74b0f815ff3f66f325220975c410621503de440f`, `public/gomywayfullaitest.m4a`, 3,478,611 bytes, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Grid: tempo `129.19921875`, 4 steps/beat, 16 steps/measure, 113 measures.
- CPU separator: `demucs==4.1.0`, `htdemucs`, shifts 1, jobs 1. `Other` is combined Rhythm+Lead acoustic source; Bass is independent.
- Basic Pitch `0.4.0`: onset 0.5, frame 0.3, minimum 127.7 ms, melodia enabled, no threshold sweep. Combined Guitar MIDI 40–88; Bass 28–67.
- Reference-free transcriber: `validation/v154_cpu_multitrack/transcribe_broad_other.py`; blob `2f09ca1b8bc012749468f0079497ded71d318782`.
- Stage-one scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`; blob `13936b70555bb1b3a9e4f83767376fd5d8b1bc51`.
- Stage-one synthetic tests: run `33096282137`, job `98601930286`: PASS / SEALED.

## Architecture gates — FROZEN
- Combined Rhythm+Lead timing-aware note/pitch F1 >= 0.80.
- Bass timing-aware note/pitch F1 >= 0.80.
- Onset-aware note F1 >= 0.75.
- Later conditional Rhythm/Lead role accuracy >= 0.85.
- Later conditional string/fret correctness >= 0.85.
- A missed gate diagnoses architecture; it does not authorize tuning the consumed output against reference truth.

## Broad-Other CPU benchmark — COMPLETE / SUCCESS / SEALED
- Authoritative run `33096559281`, job `98602884120`, head `986e2a69a6cb877a203d2f8b04115914dc8fd2e6`.
- All stages passed: exact frozen protocol/audio checks, CPU-only/CUDA guards, normalization, CPU Demucs, Basic Pitch Other+Bass transcription, manifest, artifact upload.
- Benchmark workflow sealed/deleted at commit `e969790e760dba4cf544521f2640cc130dc05d44`; never rerun it.
- Artifact ID `9656706944`, digest `sha256:f0944432c37b369ac38cd25d058265a76f36b23e2f0bcf9808880d9e141dc518`.
- Normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Other stem SHA256 `c288232d1fff42f0fcf57e3e46dfd274428cb2d4e1c916f7fe663d28d42b1440`; Bass stem SHA256 `918670e9293b5aa633593fbe491ff520a045774ead7cbdba0a851301d4e86b0f`.
- Frozen `generated.json`: 1,145,129 bytes, SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`.
- Frozen counts: **1089 combined-Guitar events**, **635 Bass events**. Counts are identity only, not accuracy evidence.
- Durable result manifest: `debug/v154-cpu-autonomous/broad-other-run-33096559281-result.json`; commit `07ca01dc67c8e4fd68af8fd20d7acf62b61c3bde`.
- Full frozen output plus identities persisted under `debug/v154-cpu-autonomous/broad-other-run-33096559281/` at commit `decc2d022db11a1689cc6f15e72982c934107f6f`; artifact receipt blob `716278235a8ee489c384da08a57c6d12d572a40f`.
- Persistence v2 run `33097100130`, job `98604755260`: SUCCESS. Its one-use workflow self-deleted/sealed. Earlier v1 persistence workflow failed before any job and was removed; do not rerun either.
- Generation safety: reference read NO; score calls 0; human correction NO; threshold sweep NO; Modal/L4/CUDA/GPU NO; main/Production NO.

## Reference-free structural QC — COMPLETE / PASS
- QC file: `debug/v154-cpu-autonomous/broad-other-run-33096559281/structural-qc.json`; creation commit `4a215d5dce3755438e6a284c96fa237d3a0d86a2`.
- QC was computed against the exact frozen generated SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`; generated output was not modified.
- **Combined Guitar:** 1089 events; structural errors 0; MIDI observed 40–83 within frozen 40–88; measures 1–113 all populated; exact duplicates 0; duplicate onset+MIDI extras 0; same-MIDI temporal overlaps 0; duration median 0.19737 s, p95 0.53406 s, max 2.85862 s; onset distance to nearest grid step median 0.26493, p90 0.45529, max 0.5.
- **Bass:** 635 events; structural errors 0; MIDI observed 29–64 within frozen 28–67; populated measures 102/113; empty measures `[1,2,3,40,71,72,73,74,75,111,112]`; exact duplicates 0; duplicate onset+MIDI extras 0; same-MIDI temporal overlaps 0; duration median 0.22059 s, p95 0.47601 s, max 6.62154 s; onset distance to nearest grid step median 0.25860, p90 0.45388, max 0.49953.
- Bass max-duration event is source index 0, measure 110, step 7.82798, MIDI 30, duration 6.62154 s. This and Bass-empty measures are **diagnostic flags only**, not proven musical defects without reference scoring; no correction/retuning was made.
- QC conclusion: all events are finite, grid/mapping/duration consistent, in frozen MIDI ranges, and free of duplicate/overlap structural defects. This is an engineering-contract pass, **not an accuracy claim**.

## Current execution status
- Reference-facing score calls this continuation: **0**.
- Professional reference note data opened this continuation: **YES — Bass and Lead, for explicit user-authorized research preservation; no scoring performed. Rhythm was already preserved.**
- Frozen recognition generation: **PASS / PERSISTED / SEALED**.
- Reference-free structural QC: **PASS / FROZEN**.
- Modal/L4/CUDA/GPU used: **NO**.
- `main` / Production modified: **NO**.

## Exact next steps
1. Do not alter or retune `debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json`.
2. Do not perform professional-reference scoring yet. Bass and Lead are preserved visually machine-readably but do not have frozen exact 16-step scorer timing.
3. Run a dedicated three-part reference-normalization pass that freezes exact scorer-ready `(measure, step, MIDI)` identities for Rhythm/Lead/Bass without consulting or altering the frozen generated candidate. Then score this exact combined Guitar first and Bass second **exactly once** with `score_frontend_reference.py`.
4. Interpret the prerecorded >=0.80 recognition gates; no post-score tuning of this consumed output.
5. Only after acoustic recognition is scored/frozen should Rhythm/Lead role separation, fret/string assignment, techniques, and PDF work continue.
6. Continue saving this checkpoint after every meaningful private-reference normalization, score, or architecture decision.


## V154 professional Rhythm preservation — COMPLETE / FROZEN
- User explicitly requested the professional Rhythm reconstruction be durably saved on research branch `v143-contextual-prune-lobo` before re-providing Bass and Lead.
- Frozen source image verified directly from `main:public/Professionalexample.jpg`, Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`. The image is not present on the research branch itself.
- Existing complete machine-readable Rhythm reconstruction on the research branch was verified as instrument `rhythm`, declared measures 1–113, then copied byte-for-byte to `research/v154-professional-references/rhythm-professional-reference.json`.
- Preserved Rhythm SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; stored measure objects `113`; events `603`; note entries `946`.
- Provenance receipt: `research/v154-professional-references/rhythm-professional-reference-provenance.json`.
- Failed preservation runs `33098155353` and `33098431086` wrote no reference copy and were sealed before this v3.
- Preservation modified no generated candidate, made no reference-facing score call, and did not modify `main`/Production or use Modal/L4/CUDA/GPU.
- When Bass and Lead screenshots are re-provided, reconstruct them into sibling files in `research/v154-professional-references/` and checkpoint each identity.


## V154 professional Bass preservation — COMPLETE VISUAL MACHINE-READABLE / TIMING NOT YET SCORER-NORMALIZED
- User re-provided the complete Bass reference and explicitly requested machine-readable preservation on research branch `v143-contextual-prune-lobo`.
- The 17 canonical pages match the previously frozen page SHA256 identities exactly; prior set SHA256 remains `abd1748066966ceb93fe40bf8c8df3168f6c871ba006e44d28f8840184e3cde3`. A supplemental overlapping screenshot `1000120386.jpg` covers measures 63–67 but is excluded from the canonical 17-page identity.
- Source-set receipt: `research/v154-professional-references/bass-source-set-receipt.json`. Screenshot bytes are **not committed**.
- Complete visual machine-readable Bass reference: `research/v154-professional-references/bass-professional-reference-machine-readable.json`; SHA256 `a8e1d123f8a19e69d9c160d78aea7637b5a2012232b23e1f1ddff051e9bc40b3`; Git blob `0773c98556d00837eaea28ee77cfc513498cc21f`.
- Coverage: measures 1–113 / 113 measure objects; 569 event objects; 562 pitched event objects; 7 dead-note objects; 8 tie/sustain continuation-only objects; observed MIDI 28–56; tuning/MIDI mapping errors 0.
- Measure 10 green selection UI is ignored as interface overlay. Measure 88 retains the visible `Timing mishap here` uncertainty and is explicitly excluded from scoring until timing normalization is resolved.
- This file preserves left-to-right note/string/fret/MIDI/technique identity but intentionally contains **no `step` onset fields**. It is machine-readable but **not yet V154 scorer-normalized**; a dedicated timing-normalization pass must occur before scoring.
- Provenance: `research/v154-professional-references/bass-professional-reference-provenance.json`.
- Candidate generation remains frozen and reference-blind. Reference-facing score calls remain `0`; generated candidate unchanged; `main`/Production unchanged; Modal/L4/CUDA/GPU not used.
- Lead is now preserved beside Rhythm and Bass. Next freeze exact three-part scoring timing identity before the one-time reference-facing score.


## V154 professional Lead preservation — COMPLETE VISUAL MACHINE-READABLE / TIMING NOT YET SCORER-NORMALIZED
- User re-provided all 22 Lead pages in two batches (Lead 1–11 and Lead 12–22) and explicitly requested machine-readable preservation on research branch `v143-contextual-prune-lobo`.
- Prior frozen Lead receipt remains `debug/v154-cpu-autonomous/reference-receipts/lead-user-upload-20260827.json`, 22 pages / measures 1–113 / opening quarter=129 / 4/4 / frozen set SHA256 `de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c`.
- The active-chat copies are platform-rendered/re-encoded and therefore are **not falsely claimed as byte-identical** to the earlier upload. Current rendered-copy hashes, sizes, dimensions, page-order mapping, and the previous frozen identity are recorded in `research/v154-professional-references/lead-source-set-receipt.json`. Screenshot bytes are **not committed**.
- Complete visual machine-readable Lead reference: `research/v154-professional-references/lead-professional-reference-machine-readable.json`; SHA256 `122e0f6b2fa63fb2ea701e9cefe897dd4337fd08de0792e11579f4933804b716`; Git blob `b018d93bb5e2119ee843fbd3fbc9139484fde0d1`.
- Coverage: measures 1–113 / 113 measure objects; 487 event objects; 476 pitched event objects; 11 dead-note objects; 23 tie/sustain/bend-continuation-only objects; observed MIDI 45–81; tuning/MIDI mapping errors 0.
- Measure 10 green selection highlight is ignored as interface UI. The visible measures 39–40 annotation `Probably a mistake they left in` is preserved as source uncertainty and is not silently repaired. The detached gray dot at measure 81 remains unassigned because its notation/UI meaning is ambiguous.
- Direct staff-line recheck corrected string assignments in measures 25–27, 35–36, 55–57, 65–66, 84–87, 89, and 107–108; measure 89 also retains the distinct B12 at the end of the first printed system plus the following e12 at the wrapped continuation. This corrected audit is authoritative for the visual Lead reference.
- Chord stacks preserve simultaneous string/fret/MIDI identities through `chordGroup`; solo bends/slides/slurs/vibrato and visible picking marks are preserved as flags/raw labels where legible.
- This Lead file intentionally contains **no `step` onset fields**. It preserves visual note/string/fret/MIDI/technique order but is **not yet V154 scorer-normalized**; exact timing must be frozen in a dedicated normalization pass before scoring.
- Provenance: `research/v154-professional-references/lead-professional-reference-provenance.json`.
- Candidate generation remains frozen and reference-blind. Reference-facing score calls remain `0`; generated candidate unchanged; `main`/Production unchanged; Modal/L4/CUDA/GPU not used.
- Rhythm ✅ Bass ✅ Lead ✅. Next action is exact three-part timing normalization, then the preregistered one-time reference-facing score.
