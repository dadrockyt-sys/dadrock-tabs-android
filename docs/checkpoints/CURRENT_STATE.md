# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 broad-Other CPU recognition remains COMPLETE / FROZEN / STRUCTURAL-QC PASS. Rhythm is FROZEN SCORER-READY with row-identity equivalence PASS. Bass is FROZEN SCORER-READY with 547 pitched rows. The full 22-page Lead notation source has now been RECOVERED and byte-authenticated against the frozen rendered Lead receipt; exact Lead timing normalization is ACTIVE. Reference-facing scoring has NOT run.**

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

## Rhythm — COMPLETE / FROZEN
- Authoritative scorer-ready: `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`; SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`; 946 rows.
- Independent supplemental flatten: SHA256 `d6c9416979f25e6a81b9cd4583389b584a59421a0529fcccb4ca6f5dd47e679f`; 946 rows.
- Frozen equivalence audit: PASS; exact normalized `(measure, step, midi)` multisets identical.

## Bass — COMPLETE / FROZEN
- Machine-readable source SHA256 `a8e1d123f8a19e69d9c160d78aea7637b5a2012232b23e1f1ddff051e9bc40b3`.
- Exact source-local timing: `research/v154-professional-references/bass-source-local-attack-timing.json`; SHA256 `7d2f4eed21413c6169ec8fcea75274b64c6dc8bb5f3c8de9cbc536b94afab244`.
- Authoritative scorer-ready: `research/v154-professional-references/scorer-ready/bass-scorer-ready.json`; SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`; 547 pitched rows.
- Bass source screenshot bytes remain uncommitted.

## Lead — FULL SOURCE RECOVERED / TIMING NORMALIZATION ACTIVE
- Machine-readable visual source: `research/v154-professional-references/lead-professional-reference-machine-readable.json`; Git blob `b018d93bb5e2119ee843fbd3fbc9139484fde0d1`; SHA256 `122e0f6b2fa63fb2ea701e9cefe897dd4337fd08de0792e11579f4933804b716`.
- Source audit: 113 measures; 487 events; 476 pitched; 11 dead notes; 23 continuation-only; MIDI 45–81.
- Frozen original upload set SHA256: `de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c`.
- Frozen platform-rendered set SHA256: `e54a76bca81fdcfc8333d774a66175a00da5090fb32200a980c25f8e78b616cb`.
- **2026-08-28 recovery:** user re-provided Lead pages 1–11 as rendered `84.jpg`–`94.jpg`, then Lead pages 12–22 as `95.jpg`–`105.jpg` (user corrected an initial “Bass 1–11” label to Lead 1–11).
- Local byte audit of all 22 current uploads exactly matches every `currentRenderedPages` record in `research/v154-professional-references/lead-source-set-receipt.json`: filename, byte size, page order, and SHA256 all match. This is exact authentication to the frozen rendered receipt, not merely visual similarity.
- Page coverage is measures 1–113; page 1 shows quarter=129 and 4/4; measure 104 explicitly shows 2/4; measure 105 returns to 4/4.
- Known source uncertainty remains: measures 39–40 visibly say `Probably a mistake they left in`; detached gray dot at m81 remains unassigned; green m10 selection highlight is UI only.
- Screenshot bytes are available in the active conversation for visual timing normalization but **must not be committed**.

## Current Lead timing decisions being normalized from notation
- Repeating Em/transpose riff rhythm is read from explicit rhythm stems, not from machine-readable visual order alone.
- Visible grace rendering will be preserved as reference-side timing corrections without rewriting the frozen visual source (e.g. m78 first small/slashed note collocated with its principal; m81 small/slashed notes similarly treated).
- Continuation-only parenthesized notes remain null timing/no scorer row.
- Source-measure 104 2/4 mapping will be applied only after source-local timing is frozen.
- Measures whose exact rhythm is not actually recoverable from the rendered page crop will be excluded rather than guessed; current candidate for such treatment is m28 because its rhythm-stem line is cropped off. Measure 39 is also a candidate scoring exclusion because the source itself labels the passage as a probable mistake.
- m92 contains a visible triplet; preserve exact tupleting provenance and use an explicit deterministic 16th-grid quantization policy for scorer rows rather than hiding the tuplet.

## Current continuation status
- Rhythm scorer-ready: **COMPLETE / FROZEN / EQUIVALENCE PASS**.
- Bass scorer-ready: **COMPLETE / FROZEN / 547 rows**.
- Lead source-page recovery: **COMPLETE / EXACT RENDERED-RECEIPT BYTE MATCH**.
- Lead exact source-local timing: **IN PROGRESS**.
- Lead scorer-ready: **NOT YET FROZEN**.
- Reference-facing score calls: **0**.
- Frozen generated candidate modified: **NO**.
- Modal/L4/CUDA/GPU used: **NO**.
- `main` / Production modified: **NO**.

## Exact next steps
1. Finish visual source-local Lead attack normalization across measures 1–113 using recovered pages 84–105; preserve grace/continuation/tuplets and explicit source uncertainties.
2. Freeze `lead-source-local-attack-timing.json` with safety flags and page-set authentication; checkpoint.
3. Build and validate write-once `scorer-ready/lead-scorer-ready.json` + receipt using only frozen Lead source/timing/meter mapping; no generated-candidate read and no scoring.
4. Assemble one immutable combined Rhythm+Lead guitar reference payload plus frozen Bass reference; verify counts/identities before score call.
5. Score the exact frozen combined Guitar and Bass output **exactly once** with `score_frontend_reference.py`; never retune the consumed output afterward.
