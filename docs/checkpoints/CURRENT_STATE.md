# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 00:52 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Rhythm-first; do not begin Bass/Lead unless V144 quality is proven or the user explicitly redirects.**

## Product target
- `/ai-tab`: upload audio → choose Rhythm/Bass/Lead → professional PDF preview → optional purchase unlocks full professional PDF.
- Current target is musically accurate professional Rhythm transcription. Keep frontend behavior unchanged while engine quality is proven.

## Permanent V5 safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected analyzer Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1` at `analyzer/v143_reference_free_rhythm_pipeline.py`.
- Frozen final-result sentinel Git blob `511fd244f231b66d08306f97b5a47ed41f5415c7` at `debug/v143-contextual-prune/v5-professional-pdf/final-professional-holdout-result.json`.
- V5 render stream SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical scorer/PDF-event SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- V5 shape 891 attacks / 1214 selected / 1209 rendered / 5 voicing drops / 113 measures; tempo `129.19921875`.
- Original V5 professional one-shot holdout is permanently consumed. Never rerun/retry its final workflow, change its trigger, alter its candidate/thresholds/result, or retune V5 from V144 calibration evidence.
- Immutable V5 may be re-evaluated only as explicitly labeled **V144 calibration baseline** evidence.
- Existing `freezeReady=false` sentinels remain false.
- **No Modal/L4/GPU without fresh explicit user authorization. None has been used in V144.**

## Immutable V5 diagnostic result
- Final workflow run `32919666736`; result bot commit `4af2bf9046a5f038106a855eb03fbaefaebf299e`.
- Critical mismatches `1875` = 1069 unmatched generated + 806 unmatched reference; PDF fidelity `1.0`; measure coverage `1.0`.
- F1: pitch `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.03062645011600928`; chord pitch-set `0.022757697456492636`; exact voicing `0.022757697456492636`.

## V144 gold calibration target
- Read-only visual target `main/public/Professionalexample.jpg`, main-tree blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- Structured source SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`.
- Exact reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`; 113 measures / 603 onsets / 946 notes / 104 populated measures.
- Semantics: **gold calibration benchmark, not unseen holdout**; never claim unbiased generalization from it.
- Exact reference build run `32934718066` SUCCESS; persisted bot commit `0df6204909ca79bdd3a5bf1be4f1ca4d55cca53f` under `debug/v144-rhythm-calibration/reference/`.

## Reproducible V144 baseline
- Baseline run `32934939964` SUCCESS; persisted bot commit `4511f05493cff7dc8828e61329b4ba439db168aa` at `debug/v144-rhythm-calibration/baseline/v5-frozen-calibration-baseline.json` (blob `ad5fa9d0b6c552035405c1cca81ee4e3f25b5764`).
- Exact historical metrics reproduced and relabeled `calibration-baseline-not-unseen-holdout`.
- Aggregate pitch content: 305 matched / 904 FP / 641 FN. PDF fidelity remains `1.0`.

## Deterministic split baseline
- Split run `32935079594` SUCCESS; report bot commit `5dd431f65eec0dfb99fd3c3d8d77b5590190dd2a`, blob `d69671de73debcea47b7ab86d8392077f48e201d`.
- Split by measure+step, seed 144: 60% fit / 20% validation / 20% canary; cross-split matching forbidden.
- **Fit labels may drive calibration. Validation/canary may only gate an already locked candidate.**
- Fit: 688 generated / 594 reference; pitch F1 `0.21528861154446177`; pitch/timing `0.043681747269890804`; string/fret/timing `0.031201248049921994`; chord/voicing `0.024858757062146894`; critical `1150`; gross unmatched 622 generated / 528 reference.
- Validation baseline: pitch F1 `0.13733905579399142`; critical `426`.
- Canary baseline: pitch F1 `0.15233415233415235`; critical `385`.
- Fit-only broad FP signals include `register::high` 401, `stepParity::0` 365, `stepParity::1` 257, `pitchClass::4` 251. They are diagnostic only.

## Leakage-safe staged selector — GREEN
- `modal/v144_rhythm_staged_selector.py` commit `68575a4c0d68f54392703a038bf909619a708177`.
- Tests commit `80fe723e45ed7b44f3d9acee8668af8f087a19a4`; CPU-gate integration commit `8bb7929a9f26d331675cb097924a3e2bf2009a16`.
- CPU gate run `32935390792` SUCCESS.
- Fit ranking never reads validation/canary; exactly one fit candidate is locked. Validation and canary are pass/fail only. Failure returns to deterministic `no-prune`; no alternate candidate may be selected from later-stage feedback.
- Config requires fit pitch gain >= `0.005`, no musical metric regression, no critical mismatch increase, exact PDF-event fidelity `1.0`, and closed unseen holdout.

## First fit-only single-signature prune experiment — COMPLETE / REJECTED
- Search script `validation/v144_rhythm_calibration/search_single_signature_prunes.py`, commit `cb2e6b86bc849501f0debdb8db29517fdc70ab06`.
- CPU workflow `.github/workflows/v144-single-signature-prune-search.yml`, commit `8162e6372c0c6feaab78a7e1b4ec51e89f328e8b`.
- Workflow run `32935621669` = **SUCCESS** operationally; protocol result is **reject / fallback to no-prune**.
- Persisted report bot commit `e19972d0df128852717bcc9506ae154586d4f4ee` at `debug/v144-rhythm-calibration/candidates/single-signature-prune-search.json`, Git blob `c9ac83c05b4d614adf972e897b399cf40299ca6a`.
- Candidate family: 61 single context-signature prunes learned/ranked from **fit-only gross unmatched generated notes**. Runtime rule uses only `context_signature(event)`; gold reference is not a runtime input.
- Fit locked candidate: `prune-pitchclass-11` / rule `pitchClass::11`.
- Locked candidate stream: 1049 events; canonical SHA256 `cf031f8bb1efb788af4da464169c9dd2de246fc4e3e75bb51c80e46078b15c70`.
- Fit gains for locked candidate versus no-prune:
  - pitch-content F1 `+0.006373856969392133` — clears configured +0.005 minimum
  - pitch/timing F1 `+0.0033375642330478947`
  - string/fret/timing F1 `+0.002383974452177081`
  - chord pitch-set F1 `+0.003244287434340229`
  - exact voicing F1 `+0.003244287434340229`
  - critical mismatches `-89`
  - no fit metric regression.
- Locked stream independently re-proved exact renderer/PDF-event identity: fidelity `1.0`, event SHA256 exactly `cf031f8bb1efb788af4da464169c9dd2de246fc4e3e75bb51c80e46078b15c70`, 1049 events, and no reference opened during the fidelity check.
- Validation gate for that **already locked** candidate:
  - critical mismatches improved by `-35`
  - chord pitch-set F1 `+0.013805499254273587`
  - exact voicing F1 `+0.007476385330222955`
  - pitch/timing F1 `+0.0005202236961893564`
  - string/fret/timing F1 `+0.002961273347539442`
  - **pitch-content F1 regressed by `-0.002140920595856244`**, violating the zero-regression rule.
- Therefore validation `passed=false`; selected result is `no-prune`; `promotionAllowed=false`; stopped at `validation`.
- **Canary was not opened/scored in this experiment.**
- Do not alter `pitchClass::11` or choose a different single-signature candidate in response to this validation result. The failed gate is evidence only; it may not steer an alternate selection from the same candidate family.
- V5/main/Production remain unchanged; no Modal/L4/GPU used.

## Current interpretation
- Broad single-signature pruning can improve fit substantially, but the first locked rule did not generalize even to the internal validation split under the strict zero-regression policy.
- Rendering remains solved at the event-identity layer; musical content remains the bottleneck.
- A next hypothesis is allowed only if its construction is independently predeclared from fit evidence, not selected because of which validation metric failed. Canary remains unopened and should stay protected until a later locked candidate first clears validation.

## Unrelated workflow noise
- Pre-existing `.github/workflows/cleanup-tab-preview.yml` continues to fail on branch pushes. It is unrelated and untouched.

## Immediate next resume actions
1. Keep the first experiment immutable as a rejected V144 calibration result; do not edit/reselect within its candidate family.
2. Define a **new fit-only, more specific rule family** before any further validation access. Preferred next family: conjunctions of two reference-free context signatures, generated/ranked solely from fit unmatched-vs-matched evidence so rules are narrower than single signatures.
3. Add CPU tests proving conjunction candidate construction/ranking uses fit only and runtime inference uses no reference input.
4. Lock exactly one conjunction candidate from fit before validation. If no fit candidate clears every strict fit gate, stop at `no-prune` without opening validation/canary.
5. If a new fit candidate locks, independently re-prove its own PDF-event identity, then gate that single candidate on validation. Only if validation passes may canary be opened once.
6. Never use the previous validation failure details to tune thresholds or select the next candidate; keep thresholds fixed.
7. Save this checkpoint after the conjunction protocol is defined/tested and after any locked-candidate result.
8. Continue CPU/repository-only work; **no Modal/L4/GPU without fresh explicit authorization**.
