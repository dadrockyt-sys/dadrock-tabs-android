# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 00:55 America/Montreal
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

## Immutable V5 diagnostic baseline
- Final workflow run `32919666736`; critical mismatches `1875`; PDF fidelity `1.0`; measure coverage `1.0`.
- F1: pitch `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.03062645011600928`; chord/voicing `0.022757697456492636`.

## V144 gold calibration target
- Visual target remains read-only at `main/public/Professionalexample.jpg`, blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- Structured source SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`; exact reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Reference completeness: 113 measures / 603 onsets / 946 notes / 104 populated measures.
- Semantics: **gold calibration benchmark, not unseen holdout**. Never claim unbiased generalization from it.
- Exact reference build run `32934718066` SUCCESS; persisted bot commit `0df6204909ca79bdd3a5bf1be4f1ca4d55cca53f` under `debug/v144-rhythm-calibration/reference/`.

## Reproducible V144 baseline and deterministic splits
- Baseline run `32934939964` SUCCESS; report bot commit `4511f05493cff7dc8828e61329b4ba439db168aa`.
- Split run `32935079594` SUCCESS; report bot commit `5dd431f65eec0dfb99fd3c3d8d77b5590190dd2a`.
- Split by measure+step, seed 144: 60% fit / 20% validation / 20% canary; cross-split matching forbidden.
- **Fit labels may drive calibration. Validation/canary may only gate an already locked candidate.**
- Fit baseline: 688 generated / 594 reference; pitch F1 `0.21528861154446177`; pitch/timing `0.043681747269890804`; string/fret/timing `0.031201248049921994`; chord/voicing `0.024858757062146894`; critical `1150`; gross unmatched 622 generated / 528 reference.
- Validation baseline pitch F1 `0.13733905579399142`, critical `426`; canary baseline pitch F1 `0.15233415233415235`, critical `385`.

## Leakage-safe staged selector — GREEN
- `modal/v144_rhythm_staged_selector.py` commit `68575a4c0d68f54392703a038bf909619a708177`.
- Tests commit `80fe723e45ed7b44f3d9acee8668af8f087a19a4`; CPU integration `8bb7929a9f26d331675cb097924a3e2bf2009a16`; run `32935390792` SUCCESS.
- Fit ranking cannot read validation/canary. Exactly one fit winner locks. Validation and canary are pass/fail only; any failure returns to `no-prune` with no alternate selection.
- Config: fit pitch gain >= `0.005`; no musical metric regression; no critical mismatch increase; exact PDF-event fidelity `1.0`; unseen holdout closed.

## First single-signature experiment — COMPLETE / REJECTED
- Search script commit `cb2e6b86bc849501f0debdb8db29517fdc70ab06`; workflow commit `8162e6372c0c6feaab78a7e1b4ec51e89f328e8b`.
- Run `32935621669` SUCCESS operationally; report bot commit `e19972d0df128852717bcc9506ae154586d4f4ee`, report blob `c9ac83c05b4d614adf972e897b399cf40299ca6a` at `debug/v144-rhythm-calibration/candidates/single-signature-prune-search.json`.
- 61 single-signature candidates learned/ranked from fit-only unmatched generated notes; runtime rules use only `context_signature(event)`.
- Fit locked `pitchClass::11`, 1049 events, SHA256 `cf031f8bb1efb788af4da464169c9dd2de246fc4e3e75bb51c80e46078b15c70`.
- Fit deltas: pitch `+0.006373856969392133`; pitch/timing `+0.0033375642330478947`; string/fret/timing `+0.002383974452177081`; chord/voicing `+0.003244287434340229`; critical mismatches `-89`; no fit regression.
- Locked candidate PDF/event identity independently re-proved `1.0` with exact locked event SHA.
- Validation: critical `-35`; chord `+0.013805499254273587`; voicing `+0.007476385330222955`; pitch/timing `+0.0005202236961893564`; string/fret/timing `+0.002961273347539442`; **pitch-content `-0.002140920595856244`**, so validation failed the zero-regression rule.
- Result: `no-prune`, promotion false, stopped at validation. **Canary was not opened.**
- Do not modify/reselect that candidate family in response to validation evidence.

## Second protocol: two-signature conjunction prunes — DEFINED / CPU-GREEN
- Purpose: create narrower contextual pruning rules without using the previous validation result to construct/rank them.
- Added `modal/v144_rhythm_conjunction_prune_policy.py` in commit `9d40ebec909aa203538403a2f7104d91383d1132`.
- Added `modal/tests/test_v144_rhythm_conjunction_prune_policy.py` in commit `45b9972133144cf9653508c85e65702433167d58`.
- Updated CPU gate in commit `c35fb5790d9134718f698dac827acac6f8e36dbf`.
- CPU gate run `32935847927` = **SUCCESS**.
- Fixed construction policy before search:
  - runtime rule requires exactly two distinct signatures from `context_signature(event)`;
  - candidate construction API receives only fit unmatched-generated rows plus all fit generated rows; there is no validation/canary input parameter;
  - pair support/precision are computed only from fit rows;
  - default minimum fit false-positive support = `3`;
  - default maximum candidate family = `256`;
  - deterministic ranking: fit false-positive precision descending, FP support descending, total fit support ascending, signature tuple lexical;
  - runtime transform checks only event context; no reference input;
  - tests prove deterministic unique pairs, both-signature requirement, reference-free transform, fit-only ranking, stable cap/order, and rejection of duplicate-signature rules.
- Added search implementation `validation/v144_rhythm_calibration/search_conjunction_prunes.py` in commit `c03ee8babcc61dca5aa510f5c64812430cad7ea8`; it reuses the already-gated split/scoring helpers and staged selector.
- Search semantics are predeclared: build/rank conjunction family on fit only; lock one candidate; only then compute validation for that locked rule; compute canary only if validation passes. Previous single-signature validation result is explicitly marked unused for construction/ranking.

## Unrelated workflow noise
- Pre-existing `.github/workflows/cleanup-tab-preview.yml` continues to fail on branch pushes. It is unrelated and untouched.

## Immediate next resume actions
1. Add/run a CPU-only conjunction-search workflow with frozen V5/gold-reference guards and exact locked-candidate PDF-event identity reproof.
2. Persist only V144 conjunction report output under `debug/v144-rhythm-calibration/candidates/`.
3. If no conjunction clears strict fit gates: stop at `no-prune` without opening validation/canary.
4. If one fit candidate locks: gate only that candidate on validation. If validation fails, return to `no-prune` and keep canary unopened. Only if validation passes may canary be opened once.
5. Checkpoint exact locked rule, fit deltas, validation/canary state, event hash, fidelity proof, and run/commit IDs.
6. Continue CPU/repository-only work; **no Modal/L4/GPU without fresh explicit authorization**.
