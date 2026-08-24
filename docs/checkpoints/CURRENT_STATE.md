# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 14:57 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; do not modify/merge `main` or live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference is scorer-only; runtime/shadows may never read/train/tune/select from it.
- Retired scored render identities must never be rerun/rescored:
  - `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
  - `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- Any future score requires a genuinely new approved-audio/frozen-evidence corrected candidate identity → immutable freeze/PDF → lock → exactly one professional score.
- Completion requires score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**
- **No more Modal/L4 unless the user explicitly reopens paid usage.** Continue with cryptographically bound historical evidence and CPU-only/reference-free development.
- Professional scorer/reference is CLOSED. Do not inspect/tune against per-event professional mismatches.

## Immutable historical score state
### First retired professional score
- 725 selected attacks → 985 rendered notes, 113 measures, PDF fidelity 1.0.
- score run `32731885778`: coverage `1.0`; pitch F1 `0.23718280683583634`; pitch+timing F1 `0.033143448990160536`; critical mismatches `1723`.

### Harmonic duplicate fix
- 144 fundamental promotions; 96 contradictory strongest upper harmonics suppressed (+12=78, +19=11, +24=6, +28=1).
- Attack identity and primaries intentionally preserved.
- Corrected retired canonical render identity: `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`.
- CPU reconstruction/preholdout passed; 889 events / 113 measures / PDF-event fidelity `1.0`.

### Second retired professional score
- run `32752374788`, attempt 1.
- generated `889`; reference `946`; coverage recall `1.0`.
- pitch-content F1 `0.24305177111716622`.
- pitch+timing tolerant F1 `0.03051771117166212`.
- string/fret+timing F1 `0.01852861035422343`.
- chord pitch-set and exact voicing F1 `0.012048192771084336`.
- unmatched generated `789`; unmatched reference `846`; critical mismatches `1635`.
- near-100 gate false; `rhythmComplete=false`.
- Conclusion: harmonic contradiction was real, but broad pitch identity and timing/grid identity remain fundamentally wrong.

## Frozen reference-free source available
- `debug/v143-contextual-prune/frozen-approved-audio-preholdout-evidence.json`
- approved source SHA exact `215bd5...`; 725 attacks; 113 measures; `tempoBpm=129.19921875`.
- pre-scorer provenance; `professionalReferenceUsed=false`; `referenceRuntimeInputUsed=false`.
- No fresh separator inference is allowed under current quota boundary.

## Timing diagnosis — global fixes rejected
### Attack physics
- 176 short same-primary repeat pairs.
- only 14 weak carryover suspects; 0 strict weak-front/strong-body suspects.
- Retrigger suppression is not currently supported as the dominant correction.

### Edge-safe / sectional phase
Reports:
- `debug/v143-contextual-prune/frozen-evidence-phase-stability-diagnostic.json`
- `debug/v143-contextual-prune/frozen-evidence-phase-section-diagnostic.json`

Findings:
- Global physical attack accent favors offset 8, but local evidence is split: 8-measure windows 7–7; 16-measure stride-8 windows 6–7.
- Classification `sectional-or-mixed-phase-accent-clue`; `stablePhase8PhysicalAccentClue=false`.
- 8-measure coarse phase runs: m1–32→8, 33–40→0, 41–64→8, 65–72→4, 73–112→12.
- Unrestricted 4-measure phase is highly volatile: 24 changes in 27 transitions; 12 large jumps; only 37.5% of changes are 1–2 steps.
- **Reject global half-bar origin shift and attack-accent phase as a timing mutation.**

### Timestamp/grid consistency
Report: `debug/v143-contextual-prune/frozen-evidence-grid-timestamp-diagnostic.json`.
- Metadata BPM `129.19921875`; global timestamp-vs-labeled-step fit `129.2881694947` (+0.06885%).
- Therefore no meaningful simple global BPM error.
- Nominal residual span `7.375` sixteenth steps; best global fit still spans `7.965` steps.
- Local 8-measure fits vary about `125.33–131.63 BPM`; residual trend is nonmonotonic (`correlation=-0.1607`).
- Adjacent selected-attack pairs center exactly on metadata tempo (median implied BPM `129.19921875`).
- **Reject global BPM replacement.** Any future timing correction would need locally varying/reference-free physical grid reconstruction; none is yet justified.

## Broad pitch/register diagnosis
Report: `debug/v143-contextual-prune/frozen-evidence-pitch-register-diagnostic.json`.
- **487/725 attacks (67.17%) have only one pitch hypothesis.** Downstream re-ranking cannot repair most broad pitch errors.
- Best hypothesis differs from primary on only 144/725 attacks; 96 of those are the already-known upper-harmonic family defect.
- Any lower hypothesis than primary appears on only 19 attacks; exact lower octave on only 5; exact upper octave on 78.
- Primary MIDI median `64`; MIDI 64 occurs `202` times; pitch class E occurs `337` times.
- Primary strings: string0=325, string1=127, string2=81, string3=92, string4=65, string5=35; top two strings total 452/725.
- Adjacent primary jumps >=12 semitones: 133; >=19: 71. 117 could become <=7 semitones by octave-equivalent folding, but neighbor evidence does not support a safe blanket octave-fold rule.
- Selected voicings: 500 single-note attacks, 203 double, 17 triple, 4 quad, 1 quintuple; 82 exact-octave pairs; 98 harmonic-family multi-note attacks; 55 disconnected string sets; 95 fret spans >=6.
- Conclusion: broad pitch failure is largely upstream candidate-generation/proposal quality, not merely final hypothesis ranking.

## Open-string / E64 hypothesis-collapse diagnostic — 2026-08-24 14:42 America/Montreal
Files:
- `analyzer/v143_frozen_evidence_open_string_bias_diagnostic.py`
- `.github/workflows/v143-frozen-evidence-open-string-bias-diagnostic.yml`
- `debug/v143-contextual-prune/frozen-evidence-open-string-bias-diagnostic.json`

Reference-free result recorded at 14:42:
- Diagnostic classification: `open-high-e-persistence-bias-clue`.
- Open high E / MIDI 64 as canonical open string occurs on **186/725 attacks (25.66%)**.
- **179/186 E64 attacks (96.24%) are single-hypothesis attacks** — no alternative pitch candidate exists to re-rank.
- E64 alone accounts for **179/487 = 36.76% of every single-hypothesis attack**.
- The 14:42 checkpoint text also recorded `423/725` any-open-string primaries and `303` fretted primaries. **Those two values are now known to be inconsistent with the committed report/source and must not be used.**
- No event mutation, no scorer/reference, no Modal/L4, protected runtime unchanged, Production untouched.

## Open-string definition audit — 2026-08-24 14:57 America/Montreal
- Re-read the committed diagnostic source and its committed JSON report at branch head `98e95060a0cef65a2d253f48e0580c5cb7da4941`.
- Source definition `primaryHasOpenStringMapping` is exact: the selected note whose MIDI equals the primary must have a validated standard-tuning mapping with `fret == 0`.
- Under that exact definition, the committed report says:
  - `anyOpenStringPrimary.count = 264`
  - `frettedPrimary.count = 461`
  - partition check: `264 + 461 = 725`
- Therefore the earlier `423 open / 303 fretted` statement is stale or misclassified and is rejected. It does not reconcile to 725 and is not what the committed diagnostic computed.
- This materially weakens any generic “most attacks are open strings” interpretation. The useful clue is narrower: high-E/MIDI64 candidate diversity must be audited distinctly from generic open-string mapping.
- Also keep distinct:
  - primary MIDI value equals `64`
  - primary is physically mapped to string 0 / fret 0 (`openHighE64`)
  - any note in the selected voicing is open
  - primary MIDI equals one of standard-tuning open pitches
  These are not interchangeable classes.
- Current E64 hypothesis-collapse conclusion is therefore **under audit, not a correction**.
- No events changed; professional reference/scorer remains closed; Modal/L4 remains closed; protected runtime and Production untouched.

## Next exact actions
1. Build one CPU-only/reference-free candidate-diversity audit from the already persisted frozen evidence that reports all open-string definitions side-by-side and reconciles every partition to 725 where applicable.
2. For primary MIDI64 attacks, measure hypothesis count, single-hypothesis rate, strongest non-64 rival when available, and attack/body/persistence/combined-score margins; compare against non-64/common-primary baselines.
3. Test whether MIDI64 wins combined score while losing attack support, and whether its single-hypothesis rate is uniquely abnormal after controlling for primary frequency/register.
4. If E64 is uniquely proposal-starved, trace upstream hypothesis proposal/pruning source ancestry. If not, abandon the E64-collapse premise and follow the broader actual candidate-generation failure.
5. Do **not** mutate events until a source-level defect is independently proven.
6. Only after a genuinely new corrected candidate is frozen/locked may the professional scorer be considered again.
