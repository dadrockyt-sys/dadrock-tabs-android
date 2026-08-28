# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 broad-Other CPU recognition remains COMPLETE / FROZEN / STRUCTURAL-QC PASS. Rhythm, Lead, and Bass are now all FROZEN SCORER-READY: Rhythm 946 rows (equivalence PASS), Lead 447 rows, Bass 547 rows. The full 22-page Lead source was recovered and exactly authenticated before timing normalization. Reference-facing scoring has NOT run. The immutable three-part reference payload builder is now staged; next is to run/freeze that payload and receipt, checkpoint, then perform the preregistered one-time CPU score.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- Frozen generated output must not be altered, retuned, variant-searched, or corrected after reference access/scoring.
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

## Frozen generated candidate — DO NOT TOUCH
- Authoritative CPU run `33096559281`, job `98602884120`, head `986e2a69a6cb877a203d2f8b04115914dc8fd2e6`.
- `debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json`.
- Frozen generated SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`.
- Counts: 1089 combined-Guitar events; 635 Bass events.
- Reference-facing score calls: **0**. Generated candidate modified: **NO**.

## Architecture gates — FROZEN
- Combined Rhythm+Lead timing-aware note/pitch F1 >= 0.80.
- Bass timing-aware note/pitch F1 >= 0.80.
- Onset-aware note F1 >= 0.75.
- Later conditional Rhythm/Lead role accuracy >= 0.85.
- Later conditional string/fret correctness >= 0.85.
- A missed gate diagnoses architecture; it never authorizes post-score tuning of the consumed output.

## Reference locations — RESUME HERE
These are the authoritative frozen scorer-ready files to use when resuming:
- **Rhythm:** `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json` — 946 rows — SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`.
- **Lead:** `research/v154-professional-references/scorer-ready/lead-scorer-ready.json` — 447 pitched rows — SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`.
- **Bass:** `research/v154-professional-references/scorer-ready/bass-scorer-ready.json` — 547 pitched rows — SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- **Combined immutable reference payload builder already staged:** `validation/v154_cpu_multitrack/build_frontend_reference_payload.py` — added in commit `0828bb6d7cc2d0a6396e244f6397289e3f745366`.
- Builder output targets when run: `research/v154-professional-references/scorer-ready/frontend-reference-payload.json` and `research/v154-professional-references/scorer-ready/frontend-reference-payload-receipt.json`.

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
- **2026-08-28 recovery:** Lead pages 1–11 were re-provided as rendered `84.jpg`–`94.jpg`; Lead pages 12–22 as `95.jpg`–`105.jpg`. Local audit exactly matched every frozen rendered receipt filename, size, page order, and SHA256.
- Final source-local timing: `research/v154-professional-references/lead-source-local-attack-timing.json`; Git blob `577a4a07514cdca63d544998f6c5b590ccd2b125`; SHA256 `a1c30e9a14048fac6da6801d1ace1db203daf8807511f26c76a268e3cbf426c3`.
- Timing freeze run `33135091568`, job `98733161996`: SUCCESS; freeze commit `57d76df`; audit 487 events / 23 continuations / 11 dead / 1800 source 16ths / expected 447 pitched rows.
- Candidate-blind builder: `validation/v154_cpu_multitrack/build_lead_scorer_ready.py`; build run `33135216747`, job `98733549558`: SUCCESS; freeze commit `3c6d7f7`.
- Authoritative scorer-ready: `research/v154-professional-references/scorer-ready/lead-scorer-ready.json`; Git blob `7644e65a17f0714bfe5d44e04858d7dcc4ccc0ab`; SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`; **447 pitched rows**.
- Receipt: `research/v154-professional-references/scorer-ready/lead-scorer-ready-receipt.json`; validation PASS.
- Exclusions are frozen/reference-side only: m28 = 10 events excluded because crop omits rhythm stems; m39 = 1 event excluded because source explicitly says `Probably a mistake they left in`. Continuation-only events and dead notes are suppressed from pitch rows.
- Mechanical meter anchors PASS: source m107 step0 -> scorer m106 step8; m107 step6 -> m106 step14; m108 step0 -> m107 step8; m108 step6 -> m107 step14.
- m78/m81 slashed grace notes are collocated reference-side; m92 visible triplet provenance retained with deterministic 16th-grid quantization `[14,15,15]`.
- Screenshot bytes remain uncommitted. Generated candidate read/modified NO; scoring NO; GPU NO; main/Production NO.

## Current continuation status
- Rhythm scorer-ready: **COMPLETE / FROZEN / 946 rows / EQUIVALENCE PASS**.
- Lead scorer-ready: **COMPLETE / FROZEN / 447 rows**.
- Bass scorer-ready: **COMPLETE / FROZEN / 547 rows**.
- Combined Rhythm+Lead reference expected rows: **1393** before immutable-payload audit.
- Immutable reference payload builder: **STAGED / NOT YET RUN** at `validation/v154_cpu_multitrack/build_frontend_reference_payload.py`.
- Reference-facing score calls: **0**.
- Frozen generated candidate modified: **NO**.
- Modal/L4/CUDA/GPU used: **NO**.
- `main` / Production modified: **NO**.

## Exact next steps
1. Run `validation/v154_cpu_multitrack/build_frontend_reference_payload.py` CPU-only. It must read only the three frozen scorer-ready references and frozen scorer interface, never the generated candidate; it must write the immutable payload + receipt exactly once.
2. Verify the payload audit passes with exact counts: Rhythm 946 + Lead 447 = **1393 combined Guitar rows**, Bass = **547 rows**; verify pinned SHA identities, preserve cross-part multiplicity, and confirm scorer interface audit calls only `load_reference` with `score_stream` **not called**.
3. Freeze/checkpoint `research/v154-professional-references/scorer-ready/frontend-reference-payload.json` and `frontend-reference-payload-receipt.json`, recording their SHA256 and builder run/commit identities in this file.
4. Only after that checkpoint, perform the preregistered CPU reference-facing score **exactly once** using frozen generated candidate `debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json`, frozen reference payload, and frozen scorer `validation/v154_cpu_multitrack/score_frontend_reference.py`.
5. Record combined-Guitar and Bass metrics/gates plus an immutable score receipt. Never retune, modify, threshold-sweep, or correct the consumed generated output after that score.
6. Only after acoustic recognition is scored/frozen: continue Rhythm/Lead role separation, string/fret assignment, techniques, and professional PDF work.
