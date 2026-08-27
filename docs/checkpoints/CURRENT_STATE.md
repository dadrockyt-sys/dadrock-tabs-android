# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-27 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 broad-Other CPU recognition is COMPLETE / FROZEN / STRUCTURAL-QC PASS. Professional Rhythm/Bass/Lead visual references are preserved. Rhythm is FROZEN SCORER-READY. Bass canonical pages are recovered, a reference-only timing skeleton and meter audit are FROZEN, and exact attack timing normalization is in progress. Lead timing remains blocked until its actual source pages are recovered. Reference-facing scoring has NOT run.**

## History preservation
- Immediate pre-continuation checkpoint blob: `2f506ec99dbad7ec6fbf64b43ea1624df7fdffc3`.
- Continuation-resume checkpoint commit `c74622090860d3cd0f6720af6a1dfb77e483cd09`; blob `9821d0c7f2d2ec61e3888bddeaccf7f338d22964`.
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
- Scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`; blob `9644e65719fbd361a9b39778ae9950c5e983e855`.

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
### Rhythm — SCORER-READY / FROZEN
- Visual/timing source: `research/v154-professional-references/rhythm-professional-reference.json`; Git blob `248741bade9665a34648c59a2994bd27d73fc406`; SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Source identity also traces to `main:public/Professionalexample.jpg`; Git blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`.
- CPU one-use normalization run `33121683834`, job `98689826186`: SUCCESS.
- **Authoritative frozen scorer part:** `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`; current Git blob `99623721b13e63770829b91d0409b919b88aaa53`.
- Frozen normalization receipt: `research/v154-professional-references/scorer-ready/rhythm-scorer-ready-receipt.json`; current Git blob `0125726643b3b8f455f6a0e38e1ba4873c05d9c1`.
- Authoritative output SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`.
- Counts verified: 113 measures, 603 source events, **946 scorer note rows**.
- Policy verified by receipt: `timingInferred=false`, `generatedCandidateRead=false`, `scoringPerformed=false`.
- A later independently frozen flatten exists at `research/v154-professional-references/rhythm-professional-reference-scorer-ready.json` (SHA256 `d6c9416979f25e6a81b9cd4583389b584a59421a0529fcccb4ca6f5dd47e679f`). It is supplemental/redundant until a row-identity equivalence audit is frozen; do not replace the authoritative `scorer-ready/rhythm-scorer-ready.json` with it.

### Bass — canonical pages recovered; timing normalization IN PROGRESS
- Canonical 17-page set SHA256 `abd1748066966ceb93fe40bf8c8df3168f6c871ba006e44d28f8840184e3cde3`.
- `research/v154-professional-references/bass-professional-reference-machine-readable.json`; Git blob `0773c98556d00837eaea28ee77cfc513498cc21f`; SHA256 `a8e1d123f8a19e69d9c160d78aea7637b5a2012232b23e1f1ddff051e9bc40b3`.
- 113 measure objects; 569 event objects; 562 pitched; 7 dead notes; 8 continuation-only; observed MIDI 28–56.
- Measure 88 source annotation `Timing mishap here` remains an uncertainty and must not be silently repaired.
- Canonical Bass screenshots are recoverable in the user Library: `1000120387.jpg` through `1000120403.jpg` cover measures 1–113; `1000120386.jpg` is the known supplemental overlapping view and is excluded from canonical identity.
- All canonical Bass pages have been visually reopened in this continuation. Their explicit stems, beams, rests, ties, meter change at measure 104, and continuation notation are available for exact timing normalization.
- Frozen reference-only timing skeleton: `research/v154-professional-references/bass-timing-normalization-skeleton.json`; commit `635da435f8c87a625539d4e40d27707247621399`; Git blob `79bf9ef3706bee13e3cf61c2bedabec561031ac8`; schema `dadrock.tabs.v154.bass-timing-normalization-skeleton.v1`.
- Skeleton preserves source measure/page, visual event order, pitched/dead/continuation class, MIDI where present, ties/slurs/grace flags, and source exclusion flags. It read no generated candidate and performed no scoring.

### Lead — visual machine-readable, exact timing blocked on source recovery
- Frozen 22-page set SHA256 `de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c`.
- `research/v154-professional-references/lead-professional-reference-machine-readable.json`; Git blob `b018d93bb5e2119ee843fbd3fbc9139484fde0d1`; SHA256 `122e0f6b2fa63fb2ea701e9cefe897dd4337fd08de0792e11579f4933804b716`.
- 113 measure objects; 487 event objects; 476 pitched; 11 dead notes; 23 continuation-only; observed MIDI 45–81.
- Measures 39–40 `Probably a mistake they left in` remains source uncertainty; detached gray dot at measure 81 remains unassigned.
- The current Library exposes the Bass page set but not the prior 22 Lead source pages. **Do not invent Lead timing from visual-order JSON alone.** Recover actual Lead pages before freezing Lead timing.

## V154 reference meter audit — COMPLETE / FROZEN
- Frozen reference-only audit: `research/v154-professional-references/reference-meter-audit.json`; commit `a438eba76c2dc2749b44257689c941665d6590db`; Git blob `cc0bb40ee8af9094ba78f7e9ced9cbbcc9d88f55`.
- Bass and Lead independently declare **measure 104 = 2/4**; their other song measures are 4/4 under the preserved metadata.
- The preregistered generation/scorer coordinate system remains fixed at 4 steps/beat, 16 steps/measure, nominal 4/4.
- This audit intentionally made **no meter-to-fixed-grid mapping decision**. A deterministic source-meter -> frozen scorer-grid transform must be frozen before Bass scorer rows are finalized; the generated candidate must not be read to choose that transform.
- Audit policy: generated candidate read NO; generated candidate modified NO; reference-facing score calls 0; human correction NO; GPU NO; main/Production NO.

## Current continuation status
- Reference-facing score calls: **0**.
- Frozen generated candidate modified: **NO**.
- `main` / Production modified: **NO**.
- Modal/L4/CUDA/GPU used: **NO**.
- Rhythm timing normalization: **COMPLETE / FROZEN / SCORER-READY**; authoritative artifact identified above; supplemental flatten awaits equivalence audit.
- Bass source-page recovery/inspection: **COMPLETE**.
- Bass timing skeleton: **COMPLETE / FROZEN**; exact source-local attack steps + deterministic 2/4-to-fixed-grid mapping are next.
- Lead source-page recovery: **BLOCKED / not present in current Library**.

## Exact next steps
1. Freeze a reference-only deterministic mapping from source-local meter/16th positions into the preregistered fixed 16-step scorer coordinate space, explicitly accounting for measure 104 = 2/4. Do not read the generated candidate and do not score while choosing this mapping. Save checkpoint.
2. Build Bass exact source-local 16th attack timing page-by-page from canonical notation. Preserve dead-note attacks for rhythmic ordering, suppress continuation-only non-attacks, and exclude measure 88 unless its source timing can be resolved without invention. Apply only the frozen meter mapping; freeze scorer-ready Bass rows + receipt. Save checkpoint frequently.
3. Freeze a reference-only row-identity equivalence audit between the authoritative Rhythm scorer-ready artifact and the later supplemental Rhythm flatten. Preserve both frozen files; do not silently rewrite either.
4. Recover actual 22 Lead source pages. Normalize Lead from source notation, preserve uncertainty flags, then freeze scorer-ready Lead rows + receipt. Save checkpoint.
5. Assemble one immutable scorer reference payload with authorization flags and frozen Rhythm/Lead/Bass rows. Verify its identity before any score call.
6. Score exact frozen combined Guitar first and Bass second **exactly once** with `score_frontend_reference.py`; interpret preregistered gates; never retune this consumed output afterward.
7. Only after acoustic recognition is scored/frozen: continue Rhythm/Lead role separation, fret/string assignment, techniques, and PDF work.

## V154 supplemental Rhythm normalization — COMPLETE / FROZEN
- One-use CPU GitHub Actions run `33121732460` completed successfully and sealed its workflow.
- Frozen source: `research/v154-professional-references/rhythm-professional-reference.json`, SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Supplemental frozen output: `research/v154-professional-references/rhythm-professional-reference-scorer-ready.json`, SHA256 `d6c9416979f25e6a81b9cd4583389b584a59421a0529fcccb4ca6f5dd47e679f`.
- Receipt: `research/v154-professional-references/rhythm-professional-reference-scorer-ready-receipt.json`; Git blob `a62aad39bbc8a05c38c03c1461fc750246110270`.
- Deterministic flatten: 113 measures, 603 source events, **946 scorer rows**, MIDI 40–71, step range 0–15, exact duplicate-row extras 0.
- Candidate read **NO**; generated candidate modified **NO**; reference-facing score calls **0**; human correction **NO**; threshold sweep **NO**; Modal/L4/CUDA/GPU **NO**; `main`/Production modified **NO**.
