# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 broad-Other CPU recognition is COMPLETE / FROZEN / SCORED EXACTLY ONCE / BOTH FRONT-END GATES FAILED. Post-score diagnostic is also COMPLETE / FROZEN. The consumed V154 candidate must never be retuned or corrected against the professional references. Diagnostic evidence shows a shared grid-origin/phase error plus substantial residual pitch/polyphony errors. Next: trace the V154 time-to-grid conversion and preregister a genuinely new reference-blind CPU recognition architecture (V155 or next unused version).**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; candidate generation/transcription must not read them.
- **V154 scored candidate is consumed forever.** Diagnostic inspection may read it/reference because scoring is finished, but no modification, threshold sweep, correction, variant selection, tuned replacement, or rescoring of a modified V154 candidate is allowed.
- Do not commit professional-tab screenshot bytes. Private machine-readable reference artifacts remain research-branch-only.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Frozen song / protocol
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Audio: `public/gomywayfullaitest.m4a`; SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Grid: tempo `129.19921875`, 4 steps/beat, nominal 16 steps/4-4 measure, 113 source measures.
- Source m104 = 2/4 (8 sixteenth steps), others 4/4.
- Frozen meter map: `research/v154-professional-references/source-meter-to-fixed-grid-mapping.json`; SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`.
- V154 CPU separator: `demucs==4.1.0`, `htdemucs`, shifts 1, jobs 1; `Other` = combined Rhythm+Lead; Bass independent.
- Basic Pitch `0.4.0`: onset 0.5, frame 0.3, min 127.7 ms, melodia enabled, no threshold sweep.
- Frozen scorer: `validation/v154_cpu_multitrack/score_frontend_reference.py`; Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.

## Authoritative locations — RESUME HERE
### Consumed generated V154 candidate
- `debug/v154-cpu-autonomous/broad-other-run-33096559281/generated.json`
- SHA256 `1be86f86bb08e164342aa0c52db7a4d77beb938621e00d7d2e3b0e03f2dbfc37`
- Original generation run `33096559281`, job `98602884120`, head `986e2a69a6cb877a203d2f8b04115914dc8fd2e6`.
- Counts: combined Guitar 1089; Bass 635.

### Frozen professional references
- **Rhythm:** `research/v154-professional-references/scorer-ready/rhythm-scorer-ready.json`; 946 rows; SHA256 `d51083800bfcf30ee15f31a4349eaa2c439f1b8662acd91618ab31bdca321555`; equivalence PASS.
- **Lead:** `research/v154-professional-references/scorer-ready/lead-scorer-ready.json`; 447 pitched rows; SHA256 `8fa39681bb7eb8cf214c364a3abd2f295488b123fddec3f2cebd3f19f014c0be`.
- Lead source-local timing: `research/v154-professional-references/lead-source-local-attack-timing.json`; SHA256 `a1c30e9a14048fac6da6801d1ace1db203daf8807511f26c76a268e3cbf426c3`.
- Lead 22 rendered source pages 84–105 were recovered and byte-authenticated; screenshot bytes remain uncommitted. Lead timing freeze run `33135091568` / job `98733161996`; scorer-ready freeze run `33135216747` / job `98733549558`.
- **Bass:** `research/v154-professional-references/scorer-ready/bass-scorer-ready.json`; 547 pitched rows; SHA256 `39eba52495fe81a3602f191334d71fe4bc643ed3062287fbde812fbde3c2c2f1`.
- Bass source-local timing: `research/v154-professional-references/bass-source-local-attack-timing.json`; SHA256 `7d2f4eed21413c6169ec8fcea75274b64c6dc8bb5f3c8de9cbc536b94afab244`.

### Immutable combined reference
- `research/v154-professional-references/scorer-ready/frontend-reference-payload.json`
- SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`.
- Counts: Rhythm 946 + Lead 447 = combined Guitar 1393; Bass 547.
- Exact Rhythm/Lead multiset overlap 75 intentionally preserved; no within-part duplicate extras.
- Freeze run `33138868905`, job `98744968281`, commit `46e42ab`; interface audit called `load_reference` only and never `score_stream`.

### Frozen one-time V154 score
- Score: `debug/v154-cpu-autonomous/v154-frontend-reference-score/score.json`; SHA256 `c206f6bc951c6bd9b6cc19e6758c4aef6654f349cc1f5712df1f052e46fa798b`.
- Receipt: `debug/v154-cpu-autonomous/v154-frontend-reference-score/score-receipt.json`; validation PASS; `referenceFacingScoreCalls=1`; `scorerInvocationCountInWrapper=1`.
- Guard wrapper: `validation/v154_cpu_multitrack/run_frontend_reference_score_once.py`.
- One-use score run `33139017517`, job `98745430956`; trigger `2c1155f73b99b804267763e97fcf750f985f40c7`; score freeze commit `f687153`.
- Pre-score checkpoint: `a5fa74575f503e08fa8b39fc129d4fe31cb8dbcc`.

### Frozen post-score architecture diagnostic
- `debug/v154-cpu-autonomous/v154-frontend-reference-score/architecture-diagnostic.json`
- SHA256 `bcc7aa275fb9c8dab3e0e9350043c5d85d48788bc13c672d97ad949d4d5595cd`.
- Diagnostic script: `validation/v154_cpu_multitrack/diagnose_frontend_failure.py`.
- One-use CPU diagnostic run `33139198143`, job `98746009145`; freeze commit `b6a7637`.
- Diagnostic imported/called **no official scorer**, made **0 additional reference-facing score calls**, wrote no corrected candidate, CPU-only.

## V154 frozen score results — BOTH GATES FAIL
### Combined Guitar
- Primary ±0.5-step same-MIDI: matched 61 / generated 1089 / reference 1393.
- Precision `0.05601469237832874`; recall `0.04379038047379756`; **F1 `0.04915390813859791` — FAIL vs 0.80**.
- Gross ±2-step F1 `0.16760676873489122`.
- Pitch-content-by-measure diagnostic F1 `0.46333601933924257`.
- Primary matched timing errors: median ~0.2904 step; p90 ~0.4635.

### Bass
- Primary ±0.5-step same-MIDI: matched 66 / generated 635 / reference 547.
- Precision `0.10393700787401575`; recall `0.1206581352833638`; **F1 `0.1116751269035533` — FAIL vs 0.80**.
- Gross ±2-step F1 `0.2639593908629442`.
- Pitch-content-by-measure diagnostic F1 `0.5634517766497462`.
- Primary matched timing errors: median ~0.2346 step; p90 ~0.4284.

## Frozen post-score diagnostic findings
- Timing/grid placement is a major failure mode in both streams: measure-level exact-pitch content is dramatically better than strict timing-aware matching.
- **Both Guitar and Bass independently prefer the same global absolute-time shift of `-13.25` sixteenth-grid steps.**
  - Guitar diagnostic same-MIDI F1: ~`0.052 → 0.200` under this shift.
  - Bass diagnostic same-MIDI F1: ~`0.130 → 0.315` under this shift.
- At 129.19921875 BPM, 13.25 sixteenth steps correspond to about **1.54 seconds**, making a shared audio/grid-origin or downbeat-phase problem a strong architecture diagnosis.
- The shift does **not** solve the front end; residual pitch/polyphony errors remain large.
- Guitar pitch-class relaxation improves enough to indicate material octave/register errors; Bass pitch-class relaxation gives only modest gain, so Bass is not mainly an octave-error problem.
- Weakest strict-timing sections in diagnostic: Guitar bridge/verse2/verse1; Bass chorus1/bridge/solo.
- Therefore V155 must address **automatic reference-blind grid/downbeat origin estimation** plus stronger pitch/polyphonic recognition; simply applying a reference-derived `-13.25` correction to V154 is forbidden and would not be sufficient anyway.

## Permanent V154 rules
- Reference-facing score count is permanently **1**.
- V154 generated candidate remains byte-identical and permanently consumed.
- Never use the discovered `-13.25` shift as a correction to V154 or as a hardcoded song-specific offset in a new candidate.
- Diagnostic evidence may motivate a general reference-blind downbeat/phase estimator in a new preregistered architecture.
- No GPU used; no `main`/Production changes.

## Exact next steps
1. Trace the historical V154 generation workflow/code at head `986e2a69a6cb877a203d2f8b04115914dc8fd2e6` and run/job logs to identify exactly how Basic Pitch onset seconds became `(measure, step)`, including any audio-origin/count-in/downbeat assumptions.
2. Determine whether the shared ~1.54 s phase error is explained by a fixed `t=0` grid origin, audio leading silence/count-in, Demucs/decoder latency, or another common conversion bug. This is diagnosis only; do not rewrite V154.
3. Freeze/checkpoint the root-cause audit.
4. Preregister V155 (or next unused version) before generation. Candidate generation must be fully reference-blind. At minimum, replace fixed grid origin with an automatic audio-derived beat/downbeat/phase estimator; also change recognition architecture to address residual polyphonic pitch recall/precision rather than threshold-sweeping Basic Pitch.
5. Generate exactly one new CPU candidate under the preregistered architecture; structural-QC it reference-blind; freeze it before any reference read/score.
6. Score the new candidate under a newly sealed protocol. Do not reuse V154 as a selectable/tunable variant.
7. Fresh explicit user authorization remains required before any Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only unless separately authorized.
8. Only after a future front-end candidate passes the frozen acoustic gates should Rhythm/Lead role separation, string/fret assignment, techniques, and professional PDF work resume.
