# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. Rhythm-first; do not begin Bass/Lead unless V144 quality is proven or the user explicitly redirects.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1` at `analyzer/v143_reference_free_rhythm_pipeline.py`.
- Frozen V5 final-result sentinel blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical event SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout is permanently consumed. Never rerun/retry its workflow, change its trigger, alter V5 candidate/thresholds/result, or retune V5 from V144 evidence.
- `main`, Production, `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` state remain untouched.
- **No Modal/L4/GPU without fresh explicit user authorization. None has been used.**

## V144 gold calibration target
- Visual target remains read-only at `main/public/Professionalexample.jpg`, blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, image SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- Structured source SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`; exact reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Reference completeness: 113 measures / 603 onsets / 946 notes / 104 populated measures.
- Semantics: **gold calibration benchmark, not unseen holdout**. Never claim unbiased generalization from it.
- Exact reference build run `32934718066` SUCCESS; persisted bot commit `0df6204909ca79bdd3a5bf1be4f1ca4d55cca53f`.

## Immutable V5 → V144 calibration baseline
- Historical V5 full-reference metrics: critical mismatches `1875`; PDF fidelity `1.0`; pitch F1 `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.03062645011600928`; chord/voicing `0.022757697456492636`.
- Repro baseline run `32934939964` SUCCESS; report bot commit `4511f05493cff7dc8828e61329b4ba439db168aa`.
- Deterministic split run `32935079594` SUCCESS; report bot commit `5dd431f65eec0dfb99fd3c3d8d77b5590190dd2a`.
- Split by measure+step, seed 144: 60% fit / 20% validation / 20% canary; cross-split matching forbidden.
- Fit baseline: 688 generated / 594 reference; pitch F1 `0.21528861154446177`; pitch/timing `0.043681747269890804`; string/fret/timing `0.031201248049921994`; chord/voicing `0.024858757062146894`; critical `1150`; gross unmatched 622 generated / 528 reference.
- Validation baseline pitch F1 `0.13733905579399142`, critical `426`; canary baseline pitch F1 `0.15233415233415235`, critical `385`.

## Leakage-safe staged selector — GREEN
- `modal/v144_rhythm_staged_selector.py` commit `68575a4c0d68f54392703a038bf909619a708177`.
- CPU gate run `32935390792` SUCCESS.
- Fit ranking cannot read validation/canary. Exactly one fit winner locks. Validation and canary are pass/fail only; failure returns to `no-prune` with no alternate selection.
- Fixed gate: fit pitch gain >= `0.005`; no musical metric regression; no critical mismatch increase; exact PDF-event fidelity `1.0`.

## First single-signature experiment — REJECTED
- Run `32935621669` SUCCESS operationally; report bot commit `e19972d0df128852717bcc9506ae154586d4f4ee`.
- Fit locked `pitchClass::11`, 1049 events, SHA256 `cf031f8bb1efb788af4da464169c9dd2de246fc4e3e75bb51c80e46078b15c70`.
- Fit gains: pitch `+0.006373856969392133`; pitch/timing `+0.0033375642330478947`; string/fret/timing `+0.002383974452177081`; chord/voicing `+0.003244287434340229`; critical `-89`.
- Validation pitch-content regressed `-0.002140920595856244`; result fell back to `no-prune`. Canary was not opened in that experiment.

## Second protocol: two-signature conjunction prunes — CPU-GREEN
- Policy `modal/v144_rhythm_conjunction_prune_policy.py` commit `9d40ebec909aa203538403a2f7104d91383d1132`.
- Tests commit `45b9972133144cf9653508c85e65702433167d58`; CPU gate commit `c35fb5790d9134718f698dac827acac6f8e36dbf`; gate run `32935847927` SUCCESS.
- Construction is fit-only: exactly two distinct reference-free `context_signature(event)` values; default minimum fit FP support `3`; max family `256`; deterministic support/precision ranking; no validation/canary inputs to candidate construction.
- Search implementation added in `c03ee8babcc61dca5aa510f5c64812430cad7ea8`; scorer import-path correction in `2bffc57a0fea7428ad21cd639936f4a4ace68c08`.

## First all-stage V144 candidate — PASSED FIT + VALIDATION + CANARY
- CPU search workflow `.github/workflows/v144-conjunction-prune-search.yml` added in commit `58ab544917d172a9cac1fc41b53b9af421e57a0b`.
- Workflow run `32936171588` = **SUCCESS**.
- Persisted report bot commit `b6f2f9213ac38bf70c568bdf78ec769f24fff46d`.
- Report: `debug/v144-rhythm-calibration/candidates/conjunction-prune-search.json`, Git blob `b92a3638d5b8fff0e911df43fb381f89f088afd6`.
- Candidate family was capped at 256 conjunction rules; construction/ranking used fit labels only and explicitly did **not** use validation/canary labels or the earlier single-signature validation result.
- Locked candidate: `prune-conjunction-33ac980932c68313`.
- Runtime rule: `register::high && section16::1`.
- Fit evidence for that rule: fit FP precision `1.0`, fit FP support `62/62`; runtime rule removes 97 total events from the immutable 1209-event V5 baseline.
- Locked candidate stream: **1112 events**, canonical SHA256 `db5c8e8fbbb767c386f14a00df188c89738230694840c48bed1bae32b2653b4f`.
- Fit deltas versus no-prune:
  - pitch-content F1 `+0.007662208127669379`
  - pitch/timing F1 `+0.0022198920743714892`
  - string/fret/timing F1 `+0.0015856371959796466`
  - chord pitch-set F1 `+0.001207593648753582`
  - exact voicing F1 `+0.001207593648753582`
  - critical mismatches `-62`
  - no fit metric regressions.
- Validation gate **PASSED** with no regressions:
  - pitch-content F1 `+0.0030118213989910325`
  - pitch/timing F1 `+0.0013176718620585698`
  - string/fret/timing F1 `+0.0007529553497477581`
  - chord pitch-set F1 `+0.0005221737346611452`
  - exact voicing F1 `+0.0005221737346611452`
  - critical mismatches `-10`.
- Canary gate **PASSED** with no regressions:
  - pitch-content F1 `+0.009969512587313628`
  - pitch/timing F1 `+0.0019295830814155396`
  - string/fret/timing F1 `+0.0016079859011796163`
  - chord pitch-set F1 `+0.0010555262353823518`
  - exact voicing F1 `+0.0010555262353823518`
  - critical mismatches `-25`.
- Independent locked-stream renderer/PDF-event identity proof **PASSED**: PDF-event fidelity `1.0`, event count `1112`, event SHA exactly `db5c8e8fbbb767c386f14a00df188c89738230694840c48bed1bae32b2653b4f`, reference not opened during fidelity proof.
- Protocol result: `selected=prune-conjunction-33ac980932c68313`, `promotionAllowed=true`, `stoppedAt=complete`.
- This is a V144 **calibration candidate promotion**, not Production promotion and not evidence of unseen generalization.
- V5/main/Production remain unchanged; no Modal/L4/GPU used.

## Current interpretation
- Narrow contextual conjunction pruning is materially safer than the broad single-signature rule and has now produced the first candidate with positive fit, validation, and canary behavior simultaneously.
- The accepted rule specifically suppresses high-register generated notes in section-16 bucket 1 while leaving the rest of the stream unchanged.
- Rendering/event identity remains exact; musical transcription remains far from the near-100% product target, so this is a meaningful calibration increment, not Rhythm completion.
- Because the professional reference and all three internal splits are calibration data, none of these results may be described as unbiased final generalization performance. A separate unseen professional example is still required for a true final holdout later.

## Unrelated workflow noise
- Pre-existing `.github/workflows/cleanup-tab-preview.yml` continues to fail on branch pushes. It is unrelated and untouched.

## Immediate next resume actions
1. Persist a V144-only selected-candidate specification for `register::high && section16::1` plus its exact 1112-event identity; do not modify V5.
2. Reproduce a **full gold-calibration score** for the selected 1112-event candidate and record absolute whole-reference metrics/critical mismatches, while keeping PDF fidelity as an independent exact gate.
3. Treat that selected conjunction candidate as the new V144 calibration baseline for further residual analysis; keep its rule fixed.
4. Generate residual fit-only diagnostics after applying the accepted rule, then predeclare the next incremental rule family before consulting later-stage labels.
5. Any next candidate must be an additive V144-only transformation from the accepted 1112-event candidate, use reference-free runtime inputs, lock on fit first, and preserve exact candidate/PDF event identity.
6. Save this checkpoint after the selected-candidate spec/full-score milestone and after each later calibration increment.
7. Continue CPU/repository-only work; **no Modal/L4/GPU without fresh explicit authorization**.
