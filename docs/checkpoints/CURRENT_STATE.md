# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-24 17:32 America/Montreal
Branch: `v143-contextual-prune-lobo`
Priority: **finish Rhythm end-to-end before Bass/Lead**.

## Hard boundaries
- Work only on `v143-contextual-prune-lobo`; do not modify/merge `main` or live Production.
- Protected `analyzer/v143_reference_free_rhythm_pipeline.py` must remain blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1` (reverified unchanged after v2 integration).
- Approved fixture SHA256: `215bd5a657c5326f08f132ae358595a95c30b39bb7493a52c2f910d5a608149f`.
- Professional reference/scorer is CLOSED. Runtime/shadows may never read/train/tune/select from it.
- Retired scored render identities must never be rerun/rescored:
  - `a81190d05b5dbaa745e003a8c0c43c1b8f8edc629f3ce01975c4f1af8c51dfdb`
  - `07b12f807295219d39198641de3a9e170c684de60d274befd2b6f6f50af9588c`
- Any future score requires a genuinely new approved-audio/frozen-evidence corrected candidate identity → immutable freeze/PDF → lock → exactly one professional score.
- Completion gate: score >= `0.99`, critical mismatches `0`, PDF-event fidelity `1.0`. **Rhythm is NOT complete.**
- **No more Modal/L4 unless the user explicitly reopens paid usage.** Current work remains CPU-only/reference-free.

## Immutable historical score state
### Score 1 — retired
- 725 selected attacks → 985 rendered notes, 113 measures, PDF fidelity 1.0.
- run `32731885778`: coverage `1.0`; pitch F1 `0.23718280683583634`; pitch+timing F1 `0.033143448990160536`; critical mismatches `1723`.

### Harmonic contradiction correction + Score 2 — retired
- 144 fundamental promotions; 96 contradictory strongest upper harmonics suppressed (+12=78, +19=11, +24=6, +28=1).
- Corrected retired render identity `07b12...`; 889 events; PDF-event fidelity 1.0.
- run `32752374788`: generated 889; reference 946; pitch F1 `0.24305177111716622`; pitch+timing F1 `0.03051771117166212`; string/fret+timing F1 `0.01852861035422343`; chord F1 `0.012048192771084336`; critical mismatches `1635`.
- Harmonic contradiction was real but not the dominant broad failure.

## Frozen/reference-free evidence identity
- `debug/v143-contextual-prune/frozen-approved-audio-preholdout-evidence.json`
- 725 retained attacks, 113 measures, `tempoBpm=129.19921875`, approved source SHA exact.
- Historical preholdout run `32702772593`; candidate generation run `32699399835`, job `97347696711`.
- Candidate launch commit `1861f7a2a4aec814dd8b8504e5cca7c1f8ce6ae1`; historical product commit `289a04e0fe30b5668ddaf39427404d8472ca1f51`.
- Historical carrier source blob `99866aa8af14dc243d226c6fb28d68af14d003ac`; legacy precision source blob `feeaafea511bf727099d1532a323f9106af75b7a`.

## Timing diagnosis
### Earlier global tests
- Global physical attack accent/phase is sectional/mixed; do not justify a global half-bar mutation from guitar-attack accents alone.
- Metadata BPM `129.19921875`; best global timestamp fit `129.2881694947` (+0.06885%); reject simple global BPM replacement.

### Physical IOI vs labeled grid-gap audit — 2026-08-24 17:27 America/Montreal
Files:
- `analyzer/v143_frozen_evidence_ioi_grid_gap_diagnostic.py`
- `.github/workflows/v143-frozen-evidence-ioi-grid-gap-diagnostic.yml`
- `debug/v143-contextual-prune/frozen-evidence-ioi-grid-gap-diagnostic.json`

Result on all 725 frozen attacks / 724 consecutive pairs:
- Metadata sixteenth duration `0.11609977324263039 s`.
- For pairs whose physical IOI lies within `0.10` sixteenth of an integer multiple: **638/638 exact labeled-gap matches**.
- Within `0.15`: **680/680 exact**.
- Within `0.20`: **697/697 exact**.
- Within `0.25`: **710/710 exact**.
- At the `0.20` high-confidence band there are **zero** nonzero step-gap offsets.
- Every 8-measure window has `exactGapMatchRate=1.0` for its high-confidence pairs.
- This strongly rejects the earlier idea that the broad timing failure is caused by local integer sixteenth-gap corruption or widespread local step relabeling.
- Current attack ordering and **relative integer sixteenth spacing are physically self-consistent**. Remaining timing investigation should focus on absolute subdivision/bar phase/origin (and possibly beat-track absolute coordinate identity), not local gap replacement.
- No event/grid mutation was made.

### Full-mix bar-phase stability diagnostic — in progress, CPU only
Prepared:
- `analyzer/v143_reference_free_fullmix_bar_phase_stability_diagnostic.py`
- `.github/workflows/v143-fullmix-bar-phase-stability-diagnostic.yml`
- Uses the existing reference-free full-mix timing front end and compares combined/onset-only/low-band 4/4 phase stability globally plus 16-beat and 32-beat windows.
- No Modal, professional reference, runtime labels, or event mutation.
- Workflow now persists a run-status JSON even if the diagnostic fails, so this investigation cannot disappear silently.
- Do not claim a bar-phase conclusion until the persisted result/status is observed.

## Pivotal pitch diagnosis
The upstream carrier was **not pitch-starved**.
- Same 725 retained attacks entered precision with `7,535` observed pitch hypotheses (mean `10.393`, max 26).
- Only 2/725 attacks were single-hypothesis before precision.
- Legacy precision retained only `987` hypotheses, leaving 487/725 attacks single-hypothesis.
- `6,548` observed pitches were suppressed.
- Dominant diversity collapse is inside the legacy precision secondary gate, not Basic Pitch proposal.

### Exact legacy gate semantics
- Primary selection may promote a physically present lower fundamental using harmonic-family evidence.
- Every secondary is compared to the **strongest raw candidate** independently for score, attack, and body.
- Normal floor `0.80`; exact upper-harmonic intervals `{12,19,24,28,31,36}` use `0.92`.
- Legacy retention requires `score AND attack AND body` all to clear the floor.
- No MIDI64 special-case exists.

### Exact optional-candidate accounting
Files:
- `analyzer/v143_precision_optional_candidate_accounting.py`
- `debug/v143-contextual-prune/precision-optional-candidate-accounting.json`

Arithmetic:
- 7,535 original − 725 primaries = 6,810 non-primary.
- 144 promoted-fundamental attacks force the distinct strongest-raw candidate to survive at ratio 1.0.
- Genuine optional secondary universe = **6,666**.
- Only **118/6,666 = 1.7702%** survived.
- **6,548/6,666 = 98.2298%** of optional candidates were suppressed, exactly reconciling historical `suppressedPitchCount=6548`.

### Retained-survivor brittleness
Files:
- `analyzer/v143_precision_survivorship_gate_brittleness_diagnostic.py`
- `debug/v143-contextual-prune/precision-survivorship-gate-brittleness-diagnostic.json`

Findings:
- 987 retained = 725 primaries + 262 secondaries.
- 144/262 secondaries are forced strongest-raw survivors; only 118 are nontrivial gate survivors.
- Limiting dimension among those 118: attack 57, body 47, total score 14.
- 61/118 survive within 0.05 of the floor; 94/118 within 0.10.
- Classification: `hard-intersection-survivorship-brittleness-clue`.

### MIDI64 symptom
- primary MIDI64=202; non64=523.
- MIDI64 single-hypothesis 179/202=88.61%; non64 308/523=58.89%.
- Only 15/202 MIDI64-primary attacks retain a nontrivial secondary vs 93/523 non64.
- Treat this as gate interaction, not a hard-coded E4 rule.
- Correct primary-open partition: 264 open / 461 fretted. Older 423/303 values are invalid.

## Historical raw-row recovery — exhausted
- Exact generation run `32699399835` uploaded zero artifacts.
- Job logs contain aggregate counts only; no `candidateMidis`, `rawPhysicalAttacks`, or suppressed rows.
- Preholdout raw/freeze/PDF evidence also lacks suppressed per-event rows.
- Producer used a temporary directory; stems/carrier rows were ephemeral, not stored in a persistent Modal volume.
- Repo searches found no carrier/stem snapshot.
- Therefore exact relaxed-policy replay on the historical 7,535 rows is impossible without one new carrier capture.

## Precision v2 — CPU PREFLIGHT GREEN, PAID CANDIDATE NOT RUN
Module:
- `analyzer/v143_contextual_prune_precision_shadow_v2.py`
- policy `envelope-balanced-secondary-v2`.

Policy:
- Attack selection, local prominence, fail-safe, fundamental promotion, no-invention invariants, and harmonic protections stay unchanged.
- Non-harmonic observed secondaries use **2-of-3 physical consensus** across score/attack/body at the existing 0.80 floor.
- Exact upper-harmonic intervals `{12,19,24,28,31,36}` keep the full legacy 3-of-3 0.92 gate.
- No new numeric threshold, pitch, attack, key/chord/song rule, runtime label, or professional information introduced.

### CPU guard — GREEN
Persisted result:
- `debug/v143-contextual-prune/precision-v2-cpu-guard-result.json`
- run `32777140959`, job `97590681839`, conclusion `success`.
- `passed=true`.
- `policySelfTestPassed=true`.
- `replayCompareSelfTestPassed=true`.
- `historicalOptionalAccountingPassed=true`.
- `singlePaidCaptureStaticGuardPassed=true`.
- `newInferenceUsed=false`.
- `modalInvoked=false`.
- `professionalReferenceUsed=false`.
- `productionModified=false`.
- protected pipeline blob exact `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Guard source SHA `930b768107b9f6e93382a5ddf00462fc36543e78`.
- Logs explicitly passed v2 policy self-test, replay comparison self-test, historical 6,666 optional-candidate accounting, anti-leakage grep, protected-runtime check, and static single-paid-capture checks.

## Replay-complete candidate path — prepared, NOT RUN
Candidate producer:
- `analyzer/v143_repaired_timing_precision_candidate_product_modal.py`.
- Future candidate uses precision v2 then the existing promoted-harmonic guard.
- It persists `precisionReplayEvidence` for every retained attack: every original candidate MIDI plus attack/early/sustain/body/continuity/score evidence and selected/primary flags.
- Replay evidence is generated **after** the common promoted-harmonic guard so stored selected flags match the actual candidate pitch sets.

Replay comparison tool:
- `analyzer/v143_precision_replay_policy_compare.py`.
- Recomputes legacy vs v2 on one captured source universe, applies the common promoted-harmonic guard to both policies, verifies stored v2 selection, reports exact additions/removals and failed physical dimensions, and requires zero professional/reference input.
- Synthetic self-test passed in CPU guard run `32777140959`.

Candidate workflow:
- `.github/workflows/v143-repaired-timing-precision-candidate-product.yml`.
- Manual `workflow_dispatch` only.
- Requires explicit input `paid_capture_authorized=YES`; default is `NO`.
- One-shot lock `debug/v143-contextual-prune/precision-v2-capture-lock.json` prevents a second successful paid capture.
- Static guard verifies exactly one `python -m modal run` in workflow and exactly one `.remote(` producer invocation.
- Before paid invocation it compiles/self-tests v2 and checks protected-runtime/source/anti-leakage invariants.
- After capture it rejects the product unless replay attack/pitch counts reconcile exactly with `precisionDiagnostics`, every candidate identity is unique/complete, exactly one selected primary exists per attack, all physical fields are finite, and selected totals reconcile.
- It cryptographically binds replay evidence in `preFreezeTrace.replayEvidenceSha256`.
- It then runs the CPU replay comparison and commits candidate product + comparison + one-shot lock.
- This prevents another evidence-loss cycle: after one future carrier capture, further precision experiments can be CPU-only.

## Current mutation/cost state
- No new candidate generated.
- No Modal/L4 invoked during current v2/timing diagnostic work.
- No professional scorer/reference invoked.
- No render events mutated.
- Protected runtime unchanged.
- `main` and Production untouched.

## Next exact actions
1. Observe the persisted full-mix bar-phase stability diagnostic or its persisted run-status and resolve any CPU-only failure.
2. Use full-mix source evidence plus the 100%-consistent IOI gap result to determine whether absolute bar/subdivision phase has a stable reference-free correction; do not mutate if it remains ambiguous.
3. CPU precision-v2 preflight is already complete and green.
4. Under the current hard boundary, **do not dispatch the candidate workflow** until the user explicitly authorizes paid Modal/L4 usage.
5. If explicitly authorized, dispatch exactly one capture with `paid_capture_authorized=YES`; the one-shot lock must prevent repeats.
6. Immediately require persisted candidate replay evidence + `precision-v2-replay-policy-compare.json` to reconcile exactly before any further inference or mutation.
7. Use captured replay evidence for all later precision experiments CPU-only; do not repeat separator inference.
8. Only if source-only replay evidence supports the corrected candidate: immutable freeze/PDF → fidelity 1.0 → lock → exactly one professional score.
9. Do not claim Rhythm complete until score >=0.99, critical mismatches=0, fidelity=1.0.
