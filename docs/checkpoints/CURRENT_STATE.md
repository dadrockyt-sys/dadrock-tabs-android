# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-28 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V154 and V157 are permanently consumed after one failed reference score each. V155 is protocol-invalid and never scoreable. V156 is permanently aborted before candidate. V157 post-score diagnosis is COMPLETE / FROZEN. V158 is PREREGISTERED BEFORE GENERATION and its numeric implementation contract is now SEALED BEFORE GENERATION CODE. No V158 transcriber/QC/candidate/workflow exists yet; V158 professional-reference reads/score calls = 0. Next: implement canonical V158 transcriber + independent QC exactly to the sealed architecture/numeric contract, pin their blobs, then seal a pre-run identity receipt before any generation workflow.**

## Standing authorization / safety — MUST PRESERVE
- CPU-only work and CPU scoring are at assistant discretion.
- Fresh explicit user authorization is required immediately before **Modal, NVIDIA L4, CUDA, or any GPU execution**.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Professional references are scoring-only; generation/transcription must not read them.
- Do not commit professional-tab screenshot bytes. Private machine-readable references remain research-branch-only.
- Never retune/correct/select a replacement for a consumed scored candidate.
- Target remains fully automatic audio → professional-quality Rhythm/Lead/Bass tablature PDF with no human correction.

## Immutable shared song / reference identities
Song: **Lenny Kravitz — Are You Gonna Go My Way**.
- Historical audio commit `74b0f815ff3f66f325220975c410621503de440f`.
- Audio SHA256 `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`; bytes `3478611`.
- Normalized WAV SHA256 `3e61b7926eabc21b758c750f826c7426a29d6de5aafdd5c93f8045ecdc67f87e`.
- Source m104 = 2/4 (8 sixteenth steps), others 4/4; meter map SHA256 `1c8ed50839f4fa365616281c70fa490d47a7e222600b34ae4f1545e09f587648`.
- Frozen scorer Git blob `9644e65719fbd361a9b39778ae9950c5e983e855`.
- Combined frozen reference SHA256 `b39a203aec3f45800891fe4eca156e37e7571b91ea5c4ccc41b30bbc95fc89e7`; Guitar 1393 / Bass 547.

## Closed historical versions
- **V154:** score count 1 forever; Guitar F1 `0.04915390813859791`, Bass F1 `0.1116751269035533`; failed.
- **V155:** protocol-invalid duplicate generation; score count 0 forever.
- **V156:** aborted before candidate; score count 0 forever.
- **V157:** sole generation run `33143471258`; candidate SHA256 `f5dc7094b72f8e3a988b1fdd59808cb056461d7e12a6d41508942cf499de3e71`; sole score run `33143986627`; Guitar F1 `0.07692307692307694`, Bass F1 `0.05757575757575757`; score count 1 forever.

## V157 frozen post-score diagnosis
- Diagnostic run `33144115704`, job `98761292358`; frozen diagnostic Git blob `fb0460f158f97230bb5c82193f9409306bfa2960`; freeze commit `51fcd9b93a495f939ce85a7ec578f7ea3d70c5de`.
- Additional official score calls 0; no candidate modification/variant.
- Architecture evidence only: stable beat clock but wrong 4/4 phase; CQT-only Guitar completion low-value/high-FP; Bass onset detection dense but pYIN event formation sparse with low-register/fundamental failure.
- Exact diagnostic alignment values are forbidden future generation constants.
- Quartile diagnostic #4 is invalid due a range predicate bug; ignore it.

## V158 — PREREGISTERED + NUMERIC CONTRACT SEALED BEFORE CODE
### Architecture preregistration
- `debug/v158-cpu-autonomous/preregistration.json`
- Commit `cdb2eca7ec16479a5868f9a3ca18624fc0892c44`
- Git blob `728cf28646db225f3c266a4bb73a6112b1f60330`
- Status `PREREGISTERED_BEFORE_GENERATION`.

### Numeric implementation contract
- `debug/v158-cpu-autonomous/implementation-contract.json`
- Commit `90c878c50afcd70a6a2f7e58f2605ed2a7b2ba27`
- Git blob `68f01df155cd27077cea3de5a0cd048ddcb7bd76`
- Status `SEALED_BEFORE_GENERATION_CODE`.
- Canonical schemas are frozen: candidate `dadrock.tabs.v158.cpu-sequential-onset-first-generated.v1`; generation receipt `dadrock.tabs.v158.cpu-generation-receipt.v1`; environment receipt `dadrock.tabs.v158.cpu-environment-receipt.v1`; QC `dadrock.tabs.v158.reference-blind-structural-qc.v1`; pre-run receipt `dadrock.tabs.v158.pre-run-identity-receipt.v1`.
- Timebase numeric contract: sr 22050 / hop 256 / start BPM 120 / tightness 100; four-state Viterbi with transitions next `.985`, same `.0075`, skip-one `.0075`; state-0 emission weights drums/mix/Bass/low-flux/chroma-change `1.0/.5/.5/.75/.75`; non-downbeat emission 0; low-frequency maximum 200 Hz; deterministic tie rules; piecewise beat grid and Python-round sixteenth quantization.
- Bass numeric contract: onset-first, backtrack true, 35 ms onset collapse, 180 ms pitch window, pYIN 2048/256 as soft evidence, harmonic-template MIDI 28–67, pYIN sigma `.75`, fusion weight `.75`, global octave/fundamental comparison, source `onset_harmonic_pyin`.
- Guitar numeric contract: Basic Pitch fixed `.5/.3/90ms`, MIDI 40–88; three-frame persistent harmonic-template tracks, max six pitches, explicit ±12 register repair, no free-standing single-frame CQT, source labels only `basic_pitch`/`harmonic_track`.
- QC contract requires Viterbi path length = beat count, valid states 0–3, Bass onset provenance, forbidden CQT-only source labels absent, write-once candidate/receipts, referenceRead=false, reference paths opened=0, score calls=0, exactly one generation workflow run.
- Hard isolation: no professional reference, prior generated candidate, prior score/diagnostic, reference-derived numeric correction, threshold sweep, variant selection or GPU may enter V158 generation.

## Current V158 boundary
- **No V158 transcriber exists yet.**
- **No V158 structural-QC script exists yet.**
- **No V158 candidate, generation receipt, environment receipt, pre-run receipt, generation workflow or score exists.**
- **V158 professional-reference reads = 0; reference-facing score calls = 0.**

## Exact next steps — RESUME HERE
1. Re-fetch latest checkpoint/head before writes because concurrent continuations exist.
2. Implement `validation/v158_cpu_multitrack/transcribe_v158.py` exactly to prereg blob `728cf286...` + numeric-contract blob `68f01df1...`; it must contain no professional-reference/scorer/prior-output read path.
3. Implement independent `validation/v158_cpu_multitrack/structural_qc.py` exactly to the frozen schemas/invariants.
4. Pin both code blobs and perform a static isolation/schema audit.
5. Seal `debug/v158-cpu-autonomous/pre-run-receipt.json` while candidate/receipt/workflow are absent and score calls remain 0.
6. Only then create the V158 generation workflow exactly once; creation itself is the sole trigger, with no arm edit and no branch writes while active.
7. Generate exactly one deterministic CPU candidate; independent QC/freeze before reference access; only afterward seal a separate one-use score guard/workflow.
8. If a future candidate passes both 0.80 acoustic gates, only then resume Rhythm/Lead role separation, string/fret assignment, techniques and professional PDF work.
9. Fresh explicit authorization remains required immediately before Modal/NVIDIA L4/CUDA/GPU execution; remain CPU-only otherwise.
