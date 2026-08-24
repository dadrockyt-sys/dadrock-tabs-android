# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 15:20 America/Montreal
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
- **487/725 attacks (67.17%) have only one retained pitch hypothesis after precision pruning.** Downstream re-ranking of the retained set cannot repair most broad pitch errors.
- Best retained hypothesis differs from primary on only 144/725 attacks; 96 of those are the already-known upper-harmonic family defect.
- Any retained lower hypothesis than primary appears on only 19 attacks; exact lower octave on only 5; exact upper octave on 78.
- Primary MIDI median `64`; MIDI 64 occurs `202` times; pitch class E occurs `337` times.
- Primary strings: string0=325, string1=127, string2=81, string3=92, string4=65, string5=35; top two strings total 452/725.
- Adjacent primary jumps >=12 semitones: 133; >=19: 71. 117 could become <=7 semitones by octave-equivalent folding, but neighbor evidence does not support a safe blanket octave-fold rule.
- Selected voicings: 500 single-note attacks, 203 double, 17 triple, 4 quad, 1 quintuple; 82 exact-octave pairs; 98 harmonic-family multi-note attacks; 55 disconnected string sets; 95 fret spans >=6.
- **The older conclusion that the 487 single-hypothesis attacks prove upstream proposal starvation is superseded by the source-ancestry finding below.**

## Open-string / E64 hypothesis-collapse diagnostic — 2026-08-24 14:42 America/Montreal
Files:
- `analyzer/v143_frozen_evidence_open_string_bias_diagnostic.py`
- `.github/workflows/v143-frozen-evidence-open-string-bias-diagnostic.yml`
- `debug/v143-contextual-prune/frozen-evidence-open-string-bias-diagnostic.json`

Reference-free result recorded at 14:42:
- Diagnostic classification: `open-high-e-persistence-bias-clue`.
- Open high E / MIDI 64 as canonical open string occurs on **186/725 attacks (25.66%)**.
- **179/186 E64 attacks (96.24%) are single-hypothesis after precision pruning**.
- E64 alone accounts for **179/487 = 36.76% of every retained single-hypothesis attack**.
- The 14:42 checkpoint text also recorded `423/725` any-open-string primaries and `303` fretted primaries. **Those two values are known wrong and must not be used.**

## Open-string definition audit — 2026-08-24 14:57 America/Montreal
- Exact primary-mapped-open count = `264`; primary-mapped-fretted = `461`; partition = 725.
- Distinguish primary MIDI64, physically mapped open-high-E64, any selected open note, and primary MIDI equal to a standard-tuning open pitch.

## MIDI64 retained-diversity audit — 2026-08-24 15:02 America/Montreal
Files:
- `analyzer/v143_frozen_evidence_open_string_candidate_audit.py`
- `.github/workflows/v143-frozen-evidence-open-string-candidate-audit.yml`
- `debug/v143-contextual-prune/frozen-evidence-open-string-candidate-audit.json`

Findings on the **post-precision retained pitch sets**:
- primary MIDI64 = `202`; non64 = `523`.
- open-high-E mapped string0/fret0 = `186`.
- primary mapped open = `264`; primary mapped fretted = `461`.
- any selected voicing note open = `277`; none open = `448`.
- MIDI64 retained single-hypothesis rate `179/202 = 88.61%`; non64 `308/523 = 58.89%`; excess `+29.72` points.
- Generic open-note presence does not explain it.
- On the 23 multi-hypothesis MIDI64 attacks, persistence does not explain the primary win.
- This remains a useful symptom, but **it must not be interpreted as evidence that the upstream carrier lacked alternatives**.

## Exact pitch-source ancestry correction — 2026-08-24 15:18 America/Montreal
Historical source identity traced from preholdout run `32702772593` back through:
- preholdout source commit `23a64776333a8fd44dd092890d87e08a4a767e14`
- candidate product commit `289a04e0fe30b5668ddaf39427404d8472ca1f51`
- candidate launch commit `1861f7a2a4aec814dd8b8504e5cca7c1f8ce6ae1`

Exact source files used by that candidate:
- `analyzer/v143_contextual_prune_reference_free_carrier.py` blob `99866aa8af14dc243d226c6fb28d68af14d003ac` (still identical on current branch).
- `analyzer/v143_contextual_prune_precision_shadow.py` blob `feeaafea511bf727099d1532a323f9106af75b7a` (still identical on current branch).
- `analyzer/v143_contextual_prune_precision_candidate_events.py` supplies the post-precision render adapter.

**Pivotal correction:** the carrier was not pitch-starved before precision.
- Committed `debug/v143-contextual-prune/repaired-timing-precision-single-pass-smoke.json` proves that on the same 725 retained attacks the precision stage received **7,535 original observed pitch hypotheses**, mean **10.393 pitches/attack**, maximum 26.
- Before precision, only **2/725** attacks were single-hypothesis.
- Precision retained only **987** hypotheses, mean **1.361/attack**, with **487/725** single-hypothesis afterward.
- It explicitly reports **6,548 pitches suppressed** by precision: about **86.9%** of the observed pitch universe for retained attacks.
- Therefore the previous diagnosis “broad pitch failure is mainly upstream candidate proposal starvation” is **rejected**.
- The dominant retained-diversity collapse is caused inside `apply_reference_free_precision_shadow()` / `_precision_pitch_set()`.
- `_precision_pitch_set()` starts from the observed carrier `candidateMidis`, then keeps a primary plus secondaries only when score/attack/body each clear aggressive relative gates: `SECONDARY_RAW_RATIO=0.80`; harmonic-above-primary uses `HARMONIC_SECONDARY_RAW_RATIO=0.92`.
- The carrier itself computes two-view whole-onset CQT evidence across MIDI 28–112, while `candidateMidis` come from four wide-recall Basic Pitch sweeps on both deterministic guitar views. Thus rich physical evidence existed before the precision collapse.
- There is no MIDI64 special-case in these source files. The MIDI64 symptom is likely an interaction between its strong primary evidence and the aggressive precision secondary gates, not a hard-coded E4 boundary.
- No event mutation has been made; scorer/reference closed; Modal/L4 closed; protected runtime and Production untouched.

## Historical pre-holdout artifact recovery — 2026-08-24 15:20 America/Montreal
- Exact run `32702772593` artifact `rhythm-professional-preholdout-real-audio` is still available and was recovered without new inference.
- Artifact contains the immutable raw product/freeze/PDF evidence, including `.preholdout/raw-product-output.json` and final `precisionDiagnostics`.
- It reconfirms `984` precision input attacks → `725` retained attacks and `7,535` original observed pitch hypotheses → `987` retained, with `6,548` suppressed and `144` fundamental promotions.
- The artifact does **not** itself expose the 5,624 carrier rows or per-event `original_pitch_sets`; the next search is historical workflow/debug artifacts for those source rows.
- No event/runtime mutation made. Modal/L4 remains closed. Professional reference remains closed.

## Next exact actions
1. Search historical CPU/GitHub workflow/debug artifacts for persisted carrier rows or per-event `original_pitch_sets` from the exact historical candidate.
2. If recoverable, build a fully reference-free threshold-sensitivity diagnostic over the exact retained attacks.
3. Quantify separately how the score, attack, body, harmonic-above-primary `0.92` gate, and fundamental-primary promotion contribute to the `7,535→987` collapse.
4. Test conservative physically supported alternatives to the `0.80/0.92` hard intersection only on source evidence; do not inspect/tune against professional mismatches.
5. Do **not** mutate events yet. First prove a less destructive precision rule on frozen/pre-precision evidence.
6. Only after a genuinely new corrected candidate is frozen/locked may the professional scorer be considered again.
