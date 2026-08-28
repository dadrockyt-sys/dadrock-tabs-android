# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 broad-Other CPU recognition is COMPLETE / FROZEN / SCORED EXACTLY ONCE. Rhythm, Lead, and Bass references are FROZEN SCORER-READY and the immutable three-part scorer payload is FROZEN. The one-time reference-facing CPU score is now COMPLETE and both preregistered acoustic-recognition gates FAILED: combined Guitar primary timing-aware pitch F1 = 0.0491539 (<0.80), Bass = 0.1116751 (<0.80). This V154 generated candidate is permanently consumed and MUST NEVER be retuned/corrected against the reference. Next is architecture diagnosis and a new preregistered recognition architecture/experiment; do not proceed to role/string/fret/PDF quality work as though acoustic recognition passed.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- Frozen generated output must not be altered, retuned, variant-searched, or corrected after reference access/scoring.
- **V154 scored candidate is consumed forever.** It may be inspected diagnostically but never modified, threshold-swept, corrected, selected among variants, or rescored as a tuned replacement.
- Do not commit professional-tab screenshot bytes. Machine-readable private reference transcriptions/timing may exist only under `research/v154-professional-references/` on this research branch; never promote them to `main`/Production or expose them to candidate generation.
- Target remains fully automatic audio -> professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Frozen song / protocol
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Audio: `public/gomywayfullaitest.m4a`, SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Grid: tempo `129.19921875`, 4 steps/beat, nominal 16 steps/4-4 measure, 113 source measures.
- Source meter exception: source measure 104 = 2/4 (8 sixteenth steps); all others 4/4.
- Frozen meter mapping: `research/v154-professional-references/source-meter-to-fixed-grid-mapping.json`; SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`; source m105 begins at scorer m104 step8; never stretch/pad the 2/4 bar.
- CPU separator: `demucs==4.1.0`, `htdemucs`, shifts 1, jobs 1. `Other` = combined Rhythm+Lead; Bass independent.
- Basic Pitch `0.4.0`: onset 0.5, frame 0.3, minimum 127.7 ms, melodia enabled, no threshold sweep.
- Scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`; frozen blob `9644e65719fbd361a9b39778ae9950c5e983e855`.

## Frozen generated candidate — CONSUMED / DO NOT TOUCH
- Authoritative CPU run `33096559281`, job `98602884120`, head `986e2a69a6cb877a203d2f8b04115914dc8fd2e6`.
- `debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json`.
- Frozen generated SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`.
- Counts: 1089 combined-Guitar events; 635 Bass events.
- Reference-facing score calls: **1 and permanently closed**. Generated candidate modified: **NO**.

## Architecture gates — FROZEN
- Combined Rhythm+Lead timing-aware note/pitch F1 >= 0.80 — **V154 FAIL: 0.04915390813859791**.
- Bass timing-aware note/pitch F1 >= 0.80 — **V154 FAIL: 0.1116751269035533**.
- Onset-aware note F1 >= 0.75 — later/conditional metric; V154 front-end score already fails earlier recognition gates.
- Later conditional Rhythm/Lead role accuracy >= 0.85.
- Later conditional string/fret correctness >= 0.85.
- A missed gate diagnoses architecture; it never authorizes post-score tuning of the consumed output.

## Reference + score locations — RESUME HERE
Authoritative frozen files:
- **Rhythm:** `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json` — 946 rows — SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`.
- **Lead:** `research/v154-professional-references/scorer-ready/lead-scorer-ready.json` — 447 pitched rows — SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`.
- **Bass:** `research/v154-professional-references/scorer-ready/bass-scorer-ready.json` — 547 pitched rows — SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- **Immutable combined scorer payload:** `research/v154-professional-references/scorer-ready/frontend-reference-payload.json` — Guitar 1393 + Bass 547 — SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- **Immutable payload receipt:** `research/v154-professional-references/scorer-ready/frontend-reference-payload-receipt.json` — PASS.
- **Consumed frozen generated candidate:** `debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json` — SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`.
- **Frozen scorer:** `validation/v154_cpu_multitrack/score_frontend_reference.py` — Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- **Frozen V154 score:** `debug/v154-cpu-autonomous/v154-frontend-reference-score/score.json` — SHA256 `c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b`.
- **Frozen score receipt:** `debug/v154-cpu-autonomous/v154-frontend-reference-score/score-receipt.json`; Git blob `d7f5027d0db6bf5d7ea005e0ed8ca7c01b51c53b`; validation PASS; records exactly one scorer invocation.

## Rhythm — COMPLETE / FROZEN / SCORER-READY
- Authoritative scorer-ready: `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`; Git blob `99623721b13e63770829b91d0409b919b88aaa53`; SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`; **946 rows**.
- Independent supplemental flatten: SHA256 `d6c9416979f25e6a81b9cd4583389b584a59421a0529fcccb4ca6f5dd47e679f`; 946 rows.
- Frozen equivalence audit: PASS; exact normalized `(measure, step, midi)` multisets identical.

## Bass — COMPLETE / FROZEN / SCORER-READY
- Machine-readable source SHA256 `a8e1d123f8a19e69d9c160d78aea7637b5a2012232b23e1f1ddff051e9bc40b3`.
- Exact source-local timing: `research/v154-professional-references/bass-source-local-attack-timing.json`; SHA256 `7d2f4eed21413c6169ec8fcea75274b64c6dc8bb5f3c8de9cbc536b94afab244`.
- Authoritative scorer-ready: `research/v154-professional-references/scorer-ready/bass-scorer-ready.json`; Git blob `7c39468170fe61ac3137af94278254468c19620c`; SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`; **547 pitched rows**.
- Bass source screenshot bytes remain uncommitted.

## Lead — COMPLETE / FROZEN / SCORER-READY
- Machine-readable visual source: `research/v154-professional-references/lead-professional-reference-machine-readable.json`; Git blob `b018d93bb5e2119ee843fbd3fbc9139484fde0d1`; SHA256 `122e0f6b2fa63fb2ea701e9cefe897dd4337fd08de0792e11579f4933804b716`.
- Source audit: 113 measures; 487 events; 476 pitched; 11 dead notes; 23 continuation-only; MIDI 45–81.
- Frozen original upload set SHA256: `de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c`.
- Frozen platform-rendered set SHA256: `e54a76bca81fdcfc8333d774a66175a00da5090fb32200a980c25f8e78b616cb`.
- **2026-08-28 recovery:** Lead pages 1–11 were re-provided as rendered `84.jpg`–`94.jpg`; Lead pages 12–22 as `95.jpg`–`105.jpg`; exact rendered receipt match.
- Final source-local timing: `research/v154-professional-references/lead-source-local-attack-timing.json`; Git blob `577a4a07514cdca63d544998f6c5b590ccd2b125`; SHA256 `a1c30e9a14048fac6da6801d1ace1db203daf8807511f26c76a268e3cbf426c3`.
- Timing freeze run `33135091568`, job `98733161996`: SUCCESS; freeze commit `57d76df`.
- Scorer-ready build run `33135216747`, job `98733549558`: SUCCESS; freeze commit `3c6d7f7`.
- Authoritative scorer-ready: `research/v154-professional-references/scorer-ready/lead-scorer-ready.json`; Git blob `7644e65a17f0714bfe5d44e04858d7dcc4ccc0ab`; SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`; **447 pitched rows**.
- Exclusions frozen: m28 10 events (crop omits rhythm stems); m39 1 event (source explicitly flags probable mistake). Continuations/dead notes suppressed from pitch rows.
- Screenshot bytes remain uncommitted.

## Immutable three-part reference payload — COMPLETE / FROZEN / PASS
- Builder: `validation/v154_cpu_multitrack/build_frontend_reference_payload.py`.
- One-use CPU freeze run `33138868905`, job `98744968281`: SUCCESS.
- Freeze commit `46e42ab`; one-use workflow self-sealed/deleted.
- Output SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Counts: Rhythm 946; Lead 447; combined Guitar 1393; Bass 547.
- Combined Guitar unique rows 1318; exact Rhythm/Lead overlap 75 preserved; no within-part duplicate extras.
- Interface-only audit called `load_reference` only; `score_stream=false`; score calls remained 0 at freeze.

## V154 one-time reference-facing CPU score — COMPLETE / FROZEN / GATES FAILED
- Guard wrapper: `validation/v154_cpu_multitrack/run_frontend_reference_score_once.py`.
- One-use CPU workflow run `33139017517`, job `98745430956`: **SUCCESS**.
- Trigger commit `2c1155f73b99b804267763e97fcf750f985f40c7` after pre-score checkpoint `a5fa74575f503e08fa8b39fc129d4fe31cb8dbcc`.
- Frozen score commit `f687153` (`validation: freeze V154 frontend reference score [skip ci]`); workflow self-sealed/deleted.
- Score: `debug/v154-cpu-autonomous/v154-frontend-reference-score/score.json`; SHA256 `c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b`.
- Receipt: `debug/v154-cpu-autonomous/v154-frontend-reference-score/score-receipt.json`; validation PASS; **referenceFacingScoreCalls=1**, `scorerInvocationCountInWrapper=1`.
- Input identities passed before and after scoring: generated `1be86f86...`; reference `b39a203a...`; scorer blob `9644e657...`.
- **Combined Guitar primary timing-aware pitch:** matched 61 / generated 1089 / reference 1393; precision 0.0560146924; recall 0.0437903805; **F1 0.0491539081 — FAIL vs 0.80**.
- Combined Guitar gross (±2 steps) timing-aware pitch: matched 208; precision 0.1910009183; recall 0.1493180187; F1 0.1676067687.
- Combined Guitar pitch-content-by-measure diagnostic: matched 575; precision 0.5280073462; recall 0.4127781766; F1 **0.4633360193**.
- **Bass primary timing-aware pitch:** matched 66 / generated 635 / reference 547; precision 0.1039370079; recall 0.1206581353; **F1 0.1116751269 — FAIL vs 0.80**.
- Bass gross (±2 steps) timing-aware pitch: matched 156; precision 0.2456692913; recall 0.2851919561; F1 0.2639593909.
- Bass pitch-content-by-measure diagnostic: matched 333; precision 0.5244094488; recall 0.6087751371; F1 **0.5634517766**.
- Among primary matched events, local timing error is not the dominant issue: Guitar median 0.2904 steps / p90 0.4635; Bass median 0.2346 / p90 0.4284. The much higher measure-level pitch-content diagnostics than primary timing F1 show substantial onset/grid placement failure layered on top of incomplete/extra pitch recognition.
- CPU only; generated candidate hash unchanged; no human correction; no threshold sweep; no GPU; no main/Production change.
- **Permanent rule:** never retune, correct, threshold-search, variant-select, or rescore a modified form of this V154 candidate against these references.

## Current continuation status
- Rhythm reference: COMPLETE / FROZEN / 946.
- Lead reference: COMPLETE / FROZEN / 447.
- Bass reference: COMPLETE / FROZEN / 547.
- Immutable reference payload: COMPLETE / FROZEN / PASS.
- V154 reference-facing score: **COMPLETE / FROZEN / EXACTLY ONE CALL / BOTH ACOUSTIC GATES FAIL**.
- V154 candidate: **CONSUMED / PERMANENTLY NON-TUNABLE**.
- Modal/L4/CUDA/GPU used: NO.
- `main` / Production modified: NO.

## Exact next steps
1. **Do not continue to Rhythm/Lead role separation, fret/string assignment, techniques, or PDF quality work on the assumption that V154 acoustic recognition is adequate.** The front-end recognition architecture failed first.
2. Run CPU-only, post-score **diagnostic analysis** on the frozen V154 candidate/reference/score without modifying the candidate: quantify systematic grid/onset offset patterns, measure-wise error concentration, pitch-class/octave error patterns, over/under-generation, and whether errors cluster by sparse riff vs chordal/solo regions. Diagnostics may read reference because V154 is already consumed; they must write analysis only and must not produce a corrected candidate.
3. Freeze/checkpoint that diagnostic report. Use it only to choose a **new architecture**, not to retune V154.
4. Define a new preregistered CPU recognition experiment (V155 or next unused version) with candidate generation fully reference-blind. Architecture changes should target the observed failure modes (especially onset/grid alignment plus polyphonic pitch recall/precision), not threshold-sweep the consumed Basic Pitch output.
5. Generate one new frozen candidate under that preregistered architecture, structural-QC it reference-blind, then score it under a newly sealed protocol. Do not reuse V154 as a selectable/tunable variant.
6. Fresh explicit user authorization remains required before any Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only unless separately authorized.
7. Only after a future acoustic-recognition candidate passes the frozen front-end gates should role separation, string/fret assignment, techniques, and professional PDF work resume.
