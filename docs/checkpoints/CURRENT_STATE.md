# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 17:42 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. Runtime/shadows may never read/train/tune/select from it.
- Retired scored render identities must never be rerun/rescored:
  - `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
  - `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- Any future professional score requires a genuinely new approved-audio corrected candidate → immutable freeze/PDF → lock → exactly one score.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**
- **No Modal/L4 unless the user explicitly reopens paid usage.** Current work remains CPU-only/reference-free.

## Immutable historical score state
### Score 1 — retired
- 725 attacks → 985 rendered notes, 113 measures, PDF fidelity `1.0`.
- run `32731885778`: pitch F1 `0.23718280683583634`; pitch+timing F1 `0.033143448990160536`; critical mismatches `1723`.

### Harmonic contradiction fix + Score 2 — retired
- 144 fundamental promotions; 96 contradictory strongest upper harmonics suppressed (+12=78, +19=11, +24=6, +28=1).
- corrected retired render `07b12...`; 889 events; PDF fidelity `1.0`.
- run `32752374788`: pitch F1 `0.24305177111716622`; pitch+timing F1 `0.03051771117166212`; string/fret+timing F1 `0.01852861035422343`; chord F1 `0.012048192771084336`; critical mismatches `1635`.
- Harmonic contradiction was real but not the dominant failure.

## Frozen / historical source identity
- Frozen pre-scorer evidence: `debug/v143-contextual-prune/frozen-approved-audio-preholdout-evidence.json`.
- 725 retained attacks; 113 measures; `tempoBpm=129.19921875`; reference-free provenance exact.
- Historical candidate generation run `32699399835`, job `97347696711`; preholdout run `32702772593`.
- Candidate launch commit `1861f7a2a4aec814dd8b8504e5cca7c1f8ce6ae1`; product commit `289a04e0fe30b5668ddaf39427404d8472ca1f51`.
- Historical carrier blob `99866aa8af14dc243d226c6fb28d68af14d003ac`; legacy precision blob `feeaafea511bf727099d1532a323f9106af75b7a`.

# Pitch diagnosis — dominant known defect
## Carrier was NOT pitch-starved
- Same 725 retained attacks entered legacy precision with **7,535 observed pitch hypotheses** (mean `10.393`, max 26).
- Only 2/725 were single-hypothesis before precision.
- Legacy precision retained only `987`; `487/725` became single-hypothesis.
- **6,548 observed pitches were suppressed.**
- Therefore dominant retained-diversity collapse occurs in legacy precision, not upstream Basic Pitch proposal.

## Exact legacy secondary gate
- Primary may promote a physically present lower fundamental via harmonic-family evidence.
- Secondaries compare against the strongest raw candidate independently for score, attack and body.
- Normal floor `0.80`; exact upper-harmonic intervals `{12,19,24,28,31,36}` use `0.92`.
- Legacy secondary survives only if **score AND attack AND body** all pass.
- No MIDI64 hard-code exists.

## Exact optional-candidate accounting
Files:
- `analyzer/v143_precision_optional_candidate_accounting.py`
- `debug/v143-contextual-prune/precision-optional-candidate-accounting.json`

- 7,535 original − 725 primaries = 6,810 non-primary.
- 144 promoted-fundamental attacks force a distinct strongest-raw survivor.
- Genuine optional secondary universe = **6,666**.
- Only **118/6,666 = 1.7702%** survived.
- **6,548/6,666 = 98.2298%** optional candidates were suppressed, exactly reconciling historical suppression.

## Retained-survivor brittleness
Files:
- `analyzer/v143_precision_survivorship_gate_brittleness_diagnostic.py`
- `debug/v143-contextual-prune/precision-survivorship-gate-brittleness-diagnostic.json`

- 987 retained = 725 primaries + 262 secondaries.
- 144/262 secondaries are forced strongest-raw survivors; only 118 are nontrivial gate survivors.
- Limiting dimension: attack 57; body 47; total score 14.
- 61/118 survive within 0.05 of floor; 94/118 within 0.10.
- Classification: `hard-intersection-survivorship-brittleness-clue`.

## MIDI64 symptom
- primary MIDI64=202; non64=523.
- MIDI64 single-hypothesis `179/202 = 88.61%`; non64 `308/523 = 58.89%`.
- Only 15/202 MIDI64 attacks retain a nontrivial secondary vs 93/523 non64.
- Treat as strong-primary/gate interaction, not an E4 rule.
- Correct primary-open partition: 264 open / 461 fretted. Older 423/303 values are invalid.

## Historical suppressed-row recovery — exhausted
- Exact generation run uploaded zero artifacts.
- Logs contain aggregate counts only; no `candidateMidis`, raw carrier rows or suppressed hypotheses.
- Preholdout raw/freeze/PDF evidence also lacks suppressed rows.
- Historical stems/carrier lived only in a temporary directory and were not persisted.
- Exact relaxed-policy replay on the old 7,535 rows therefore requires one new carrier capture.

# Precision v2 — CPU PREFLIGHT GREEN, PAID CAPTURE NOT RUN
Module: `analyzer/v143_contextual_prune_precision_shadow_v2.py`.
Policy: `envelope-balanced-secondary-v2`.

- Attack selection, fail-safe, primary/fundamental promotion, no-invention invariants and harmonic protections unchanged.
- Non-harmonic observed secondaries use **2-of-3 physical consensus** across score/attack/body at the existing `0.80` floor.
- Exact upper-harmonic intervals remain strict legacy 3-of-3 at `0.92`.
- No new numeric threshold, pitch, attack, key/chord/song rule, runtime label, or professional information.

CPU guard:
- `debug/v143-contextual-prune/precision-v2-cpu-guard-result.json`
- run `32777140959`, job `97590681839`, success.
- `passed=true`; policy self-test, replay comparison self-test, historical optional accounting and single-paid-capture static guard all true.
- `modalInvoked=false`; `newInferenceUsed=false`; `professionalReferenceUsed=false`; `productionModified=false`.
- protected runtime blob exact.

## Replay-complete one-shot candidate path — prepared, NOT RUN
- Producer: `analyzer/v143_repaired_timing_precision_candidate_product_modal.py`.
- Future v2 candidate persists `precisionReplayEvidence` containing every original candidate MIDI and physical attack/early/sustain/body/continuity/score evidence, plus selected/primary flags, for every retained attack.
- Replay evidence is captured after the common promoted-harmonic guard so stored selected sets match candidate output.
- CPU comparison: `analyzer/v143_precision_replay_policy_compare.py` recomputes legacy vs v2 on one captured universe and checks exact additions/removals and stored-v2 agreement.
- Workflow: `.github/workflows/v143-repaired-timing-precision-candidate-product.yml`.
- Manual dispatch only; input `paid_capture_authorized=YES` required; default `NO`.
- One-shot lock: `debug/v143-contextual-prune/precision-v2-capture-lock.json`.
- Static guard requires exactly one `python -m modal run` and one producer `.remote(` call.
- After one successful capture, all further precision experiments can be CPU-only from persisted replay evidence.

# Timing diagnosis — relative grid is strong; absolute bar phase is ambiguous
## Global tempo / guitar-accent tests
- Metadata BPM `129.19921875`; global timestamp fit `129.2881694947` (+0.06885%): reject simple global BPM replacement.
- Guitar-attack phase clues are sectional/mixed: reject a global half-bar shift based on guitar accents.

## Physical IOI vs labeled grid-gap audit — GREEN
Files:
- `analyzer/v143_frozen_evidence_ioi_grid_gap_diagnostic.py`
- `debug/v143-contextual-prune/frozen-evidence-ioi-grid-gap-diagnostic.json`

All 725 attacks / 724 consecutive pairs:
- nominal sixteenth = `0.11609977324263039 s`.
- residual <=0.10 step: **638/638 exact labeled-gap matches**.
- <=0.15: **680/680 exact**.
- <=0.20: **697/697 exact**.
- <=0.25: **710/710 exact**.
- At <=0.20 there are zero nonzero step-gap offsets.
- Every 8-measure window has exact high-confidence gap-match rate `1.0`.
- Conclusion: attack ordering and **relative integer sixteenth spacing are physically self-consistent**. Broad timing failure is not widespread local integer step-gap corruption.

## Full-mix bar-phase stability — GREEN DIAGNOSTIC, PHASE NOT STABLE
Files:
- `analyzer/v143_reference_free_fullmix_bar_phase_stability_diagnostic.py`
- `debug/v143-contextual-prune/fullmix-bar-phase-stability-diagnostic.json`
- `debug/v143-contextual-prune/fullmix-bar-phase-stability-run-status.json`

Run status: `passed=true`, `exitCode=0`, no Modal/reference/Production.

Full-mix timing front end reproduces exactly:
- 447 tracked beats.
- first tracked beat `0.6733786848072563 s`; last `203.03528344671201 s`.
- tempo **`129.19921875` exactly**, delta from historical 0.
- historical phase: `downbeatIndexMod4=1`, `firstBeatInMeasure=3`.

Global accent views:
- combined existing estimator → phase 1, but normalized winner margin only `0.0879734141`.
- onset-only → phase 1, normalized margin `0.0753847804`.
- low-band-only → **phase 0**, normalized margin `0.0705845507`.
- Only 2/3 global views agree with historical phase.

Local combined-view votes:
- 16-beat windows: phase counts `{0:3, 1:12, 2:7, 3:5}`; historical phase1 only `12/27 = 44.44%`.
- 32-beat windows stride16: `{0:3, 1:9, 2:6, 3:8}`; historical phase1 only `9/26 = 34.62%`.
- Therefore full-mix evidence does **not** support any stable single global 4/4 phase correction. Do not mutate to phase0/1/2/3 from these accents.

## Beat-repair phase-coordinate audit — GREEN; no prepend-phase bug
Files:
- `analyzer/v143_reference_free_beat_repair_phase_consistency_diagnostic.py`
- `debug/v143-contextual-prune/beat-repair-phase-consistency-diagnostic.json`

Fresh CPU replay of the exact timing + repair path:
- original beats 447; repaired beats 449.
- original first beat `0.6733786848072563`; repaired first beat `0.6965986394557823`.
- original interval outliers 38 → repaired interval outliers 0.
- **leadingExtendedBeatCount=0**; trailingExtendedBeatCount=13; lookaheadBridgeBeatCount=3.
- `leadingExtensionModulo4=0`; repaired `firstBeatInMeasure=3` and `downbeatIndexMod4=1` are coordinate-consistent.
- Thus the suspected bug “repair prepends beats but forgets to reindex bar phase” does **not** occur on this approved fixture.

## Current timing conclusion
- Relative sixteenth spacing is exceptionally well supported physically.
- Global tempo is reproduced exactly.
- Repair does not introduce a leading phase-index error.
- Absolute 4/4 downbeat/bar phase remains weak and section-dependent in unlabeled full-mix accents.
- Therefore **do not mutate timing/grid yet**. The low historical pitch+timing score cannot safely be attributed to a simple tempo, local-step, half-bar, or repair-index bug from current reference-free evidence.
- Pitch correction remains the strongest justified next technical move.

# Current mutation / cost state
- No new candidate generated.
- No Modal/L4 invoked during current v2/timing work.
- No professional scorer/reference invoked.
- No render events mutated.
- Protected runtime unchanged.
- `main` and Production untouched.

## Checkpoint save — 2026-08-24 17:42 America/Montreal
- User explicitly requested that the current state and next steps be saved here before continuing.
- Precision v2 CPU guard is confirmed green from persisted result and successful job logs; no paid inference was used.
- Timing remains frozen because reference-free IOI, tempo, bar-phase-stability and beat-repair audits do not justify a timing mutation.
- The strongest justified correction remains precision v2, but the one-shot candidate capture is still behind the explicit paid-usage authorization gate.
- No paid candidate workflow was dispatched, no professional reference was opened, no render was scored, and no Production/main mutation occurred.
- Safe work can continue with CPU-only capture-readiness/invariant auditing so that, if paid usage is explicitly reopened later, the single permitted carrier capture has the highest chance of succeeding and preserving all replay evidence.

# Next exact actions
1. Reverify branch and protected runtime blob before every candidate-path mutation; keep `main` and Production untouched.
2. Keep timing frozen: current CPU evidence rejects simple tempo/local-gap/global-phase/repair-index fixes.
3. Continue **CPU-only** preauthorization readiness work: audit the one-shot workflow, producer, replay serializer, lock, hash binding and failure paths so one future capture cannot lose the full source universe again.
4. Precision v2 remains the strongest justified pitch correction; do not weaken its source identity or tune it against professional mismatches.
5. **Do not dispatch the paid candidate workflow unless the user explicitly authorizes Modal/L4 usage.**
6. If explicit authorization is later given, dispatch exactly once with `paid_capture_authorized=YES`; require the one-shot lock to prevent repeats.
7. Immediately require persisted `precisionReplayEvidence` + `precision-v2-replay-policy-compare.json` to reconcile exactly before any later inference or mutation.
8. Use persisted replay evidence for every subsequent precision experiment CPU-only; no repeated separator inference.
9. Only when source-only evidence supports a genuinely corrected candidate: immutable freeze/PDF → fidelity `1.0` → lock → exactly one professional score.
10. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
