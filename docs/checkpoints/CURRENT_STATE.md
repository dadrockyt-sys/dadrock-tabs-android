# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-27 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 broad-Other CPU recognition is COMPLETE / FROZEN / STRUCTURAL-QC PASS. Rhythm is FROZEN SCORER-READY and its two independently frozen scorer representations are now proven row-identity equivalent. Bass is FROZEN SCORER-READY with 547 validated pitched rows. Lead timing is the remaining reference-normalization blocker and requires recovery of its actual 22 source pages; do not infer Lead timing from visual-order JSON alone. Reference-facing scoring has NOT run.**

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
### Rhythm — SCORER-READY / FROZEN / EQUIVALENCE-AUDITED
- Visual/timing source: `research/v154-professional-references/rhythm-professional-reference.json`; Git blob `248741bade9665a34648c59a2994bd27d73fc406`; SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Authoritative scorer part: `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`; Git blob `99623721b13e63770829b91d0409b919b88aaa53`; SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`; 946 rows.
- Authoritative receipt: `research/v154-professional-references/scorer-ready/rhythm-scorer-ready-receipt.json`; Git blob `0125726643b3b8f455f6a0e38e1ba4873c05d9c1`.
- Supplemental independently frozen flatten: `research/v154-professional-references/rhythm-professional-reference-scorer-ready.json`; SHA256 `d6c9416979f25e6a81b9cd4583389b584a59421a0529fcccb4ca6f5dd47e679f`; 946 rows.
- Frozen row-identity audit: `research/v154-professional-references/rhythm-scorer-ready-equivalence-audit.json`; Git blob `e20b96dca1fc5306754acad7dffd770ff72c4ba0`; CPU run `33124191005`, job `98698230518`: SUCCESS; freeze commit `ca4697483cc789022b6e66e3d54990cc3fbd302f`.
- Audit result: **PASS**. Exact normalized `(measure, step, midi)` row multisets are identical: 946/946 rows, 946/946 unique rows, 0 duplicate extras, 0 authoritative-only identities, 0 supplemental-only identities. Input sequence order differs only because simultaneous chord-note order differs; sorted normalized rows are identical.
- Audit policy: frozen inputs rewritten NO; generated candidate read/modified NO; score calls 0; human correction NO; threshold sweep NO; GPU NO; main/Production NO.

### Bass — SCORER-READY / FROZEN
- Canonical 17-page set SHA256 `abd1748066966ceb93fe40bf8c8df3168f6c871ba006e44d28f8840184e3cde3`.
- Machine-readable source: `research/v154-professional-references/bass-professional-reference-machine-readable.json`; Git blob `0773c98556d00837eaea28ee77cfc513498cc21f`; SHA256 `a8e1d123f8a19e69d9c160d78aea7637b5a2012232b23e1f1ddff051e9bc40b3`.
- Frozen timing skeleton: `research/v154-professional-references/bass-timing-normalization-skeleton.json`; commit `635da435f8c87a625539d4e40d27707247621399`; Git blob `79bf9ef3706bee13e3cf61c2bedabec561031ac8`.
- Frozen exact source-local timing: `research/v154-professional-references/bass-source-local-attack-timing.json`; commit `b4b5e29d8338a1f3b1b0c71259f97c626648ca71`; Git blob `251d4986965c823b288d4a7d0428ec32cc9231cf`; SHA256 `7d2f4eed21413c6169ec8fcea75274b64c6dc8bb5f3c8de9cbc536b94afab244`.
- Candidate-blind builder: `validation/v154_cpu_multitrack/build_bass_scorer_ready.py`; commit `7d46ce2cdcd6c7663c7c09b20cf1e71bbb8b49c3`.
- CPU one-use freeze workflow run `33124074101`, job `98697844991`: SUCCESS; freeze commit `88004ad7743c8f39705661afddddb7de6bd353dc`.
- Authoritative Bass: `research/v154-professional-references/scorer-ready/bass-scorer-ready.json`; Git blob `7c39468170fe61ac3137af94278254468c19620c`; SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- Receipt: `research/v154-professional-references/scorer-ready/bass-scorer-ready-receipt.json`; Git blob `75a05467129ac58512ddfd0159678930e82c5958`.
- Final audit: 113 source measures; 569 events; **547 pitched scorer rows**; 8 continuation-only suppressed; 7 dead notes timed but suppressed from pitch rows; all 7 events in source measure 88 excluded due explicit `Timing mishap here`; total source duration 1800 sixteenth steps preserving source m104 = 2/4.
- Canonical pages `1000120387.jpg`–`1000120403.jpg` were the timing authority; screenshot bytes were not committed. m35/m36 grace flags preserved; m43 visualOrder0 visibly reduced-size/slurred grace collocated with its principal onset reference-side only.
- Candidate read NO; scoring NO; generated candidate modified NO; candidate human correction NO; threshold sweep NO; GPU NO; main/Production NO.

### Lead — visual machine-readable, exact timing BLOCKED ON SOURCE RECOVERY
- Frozen 22-page set SHA256 `de2f20c330e52aca6125e29ca2cf5c4b719406fc267a98d43d98f3ab1453ff3c`.
- `research/v154-professional-references/lead-professional-reference-machine-readable.json`; Git blob `b018d93bb5e2119ee843fbd3fbc9139484fde0d1`; SHA256 `122e0f6b2fa63fb2ea701e9cefe897dd4337fd08de0792e11579f4933804b716`.
- 113 measure objects; 487 events; 476 pitched; 11 dead notes; 23 continuation-only; MIDI 45–81.
- Measures 39–40 note `Probably a mistake they left in` remains source uncertainty; detached gray dot at measure 81 remains unassigned.
- Prior checkpoint search found the Bass pages but not the actual 22 Lead source pages in current Library. **Do not invent Lead timing from visual-order JSON alone.** Search Library/history again; if still absent, recovery remains the hard blocker before scorer payload assembly.

## V154 reference meter audit + fixed-grid mapping — COMPLETE / FROZEN
- Meter audit: `research/v154-professional-references/reference-meter-audit.json`; commit `a438eba76c2dc2749b44257689c941665d6590db`; Git blob `cc0bb40ee8af9094ba78f7e9ced9cbbcc9d88f55`.
- Bass and Lead independently declare **source measure 104 = 2/4**; all other preserved source measures are 4/4.
- Fixed mapping: `research/v154-professional-references/source-meter-to-fixed-grid-mapping.json`; commit `331e756d0299de6b9fbde04c868f7d3a18363164`; Git blob `c7856d2879f4ac1524e68016e979728c92c487fd`; SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`.
- Preserve absolute source time in 16th units: `absoluteSourceStep = cumulative prior source lengths + sourceLocalStep`; scorer measure=`floor(abs/16)+1`; scorer step=`abs mod 16`. Never stretch/pad the 2/4 bar.
- Source m104 occupies scorer m104 steps 0–7; source m105 begins scorer m104 step 8; later source measures retain the 8-step shift.
- Mapping frozen without candidate access and without scoring.

## Current continuation status
- Reference-facing score calls: **0**.
- Frozen generated candidate modified: **NO**.
- `main` / Production modified: **NO**.
- Modal/L4/CUDA/GPU used: **NO**.
- Rhythm scorer-ready: **COMPLETE / FROZEN / EQUIVALENCE AUDIT PASS**.
- Bass scorer-ready: **COMPLETE / FROZEN / VALIDATED — 547 rows**.
- Lead source-page recovery: **ACTIVE NEXT TASK / currently blocked unless pages can be recovered**.
- Lead scorer-ready: **NOT STARTED; source pages required**.

## Exact next steps
1. **DONE / FROZEN:** Rhythm row-identity equivalence audit; preserve both frozen Rhythm files unchanged.
2. Search Library/prior accessible file context for the exact 22 Lead source pages corresponding to frozen Lead page-set SHA256 `de2f20c...`. Do not substitute Bass pages and do not invent timing from visual-order JSON.
3. If recovered, visually normalize Lead source-local attacks from notation, preserve source uncertainties, apply only the frozen meter mapping, and freeze scorer-ready Lead rows + receipt. Save checkpoint often.
4. Only after Lead is scorer-ready, assemble one immutable scorer reference payload with frozen authorization flags and exact Rhythm/Lead/Bass rows. Verify identities/counts before any score call.
5. Score the exact frozen combined Guitar and Bass output **exactly once** using `score_frontend_reference.py`; interpret preregistered gates; never retune this consumed output afterward.
6. Only after acoustic recognition is scored/frozen: continue Rhythm/Lead role separation, fret/string assignment, techniques, and PDF work.

## Historical incremental Bass batch — preserve only
- `research/v154-professional-references/scorer-ready/bass-source-local-timing-pages-01-05.json`; one-use CPU run `33123146413`; freeze commit `4b05b50c913834ff1c036ae097804338c4e7a7ea`; SHA256 `327316cc677468bfbbd0b59e29e0cb5b9c3619dc49613be2241f491c14f09e5e`.
- This is historical progress only; the final all-pages timing/scorer-ready artifacts above are authoritative. Score calls remain 0.
