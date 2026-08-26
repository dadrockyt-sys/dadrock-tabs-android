# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. The first corrected all-invariant calibration baseline is now accepted. Continue improving Rhythm from that 1144-event V144 baseline; do not begin Bass/Lead unless Rhythm quality is proven or the user explicitly redirects.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer: `analyzer/v143_reference_free_rhythm_pipeline.py`, Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 final-result sentinel Git blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical event SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout is permanently consumed. Never rerun/retry its final workflow, alter its candidate/thresholds/result, or retune V5 from V144 evidence.
- `main`, Production, `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` remain untouched.
- **No Modal/L4/GPU without fresh explicit user authorization. None has been used in V144.**

## Gold calibration reference
- Visual target remains read-only at `main/public/Professionalexample.jpg`, main blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, image SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- Structured source SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`; exact reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Reference completeness: 113 measures / 603 playable onsets / 946 notes / 104 populated measures.
- This is a **gold calibration benchmark, not an unseen holdout**. Never claim unbiased generalization from scores against it.
- Exact reference build run `32934718066` SUCCESS; persisted bot commit `0df6204909ca79bdd3a5bf1be4f1ca4d55cca53f`.

## Immutable V5 calibration baseline
- Full V5 metrics: critical mismatches `1875`; pitch F1 `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.03062645011600928`; chord pitch-set/exact voicing `0.022757697456492636`; measure coverage `1.0`; PDF fidelity `1.0`.
- Baseline run `32934939964` SUCCESS; bot commit `4511f05493cff7dc8828e61329b4ba439db168aa`; report blob `ad5fa9d0b6c552035405c1cca81ee4e3f25b5764`.
- Split policy is deterministic by measure+step with seed 144: 60% fit / 20% validation / 20% canary. Fit labels may construct/rank; validation/canary only gate an already locked candidate.
- Fit baseline: pitch `0.21528861154446177`, pitch/timing `0.043681747269890804`, string/fret/timing `0.031201248049921994`, chord/voicing `0.024858757062146894`, critical `1150`.
- Validation baseline pitch `0.13733905579399142`, critical `426`; canary pitch `0.15233415233415235`, critical `385`.

## Selector safety — corrected and CPU-green
- Fit ranking cannot read validation/canary; one winner locks; later failures return to deterministic `no-prune`, never an alternate candidate.
- Numeric gate remains fixed: fit pitch gain >= `0.005`; no musical metric regression; no critical mismatch increase; exact PDF-event fidelity `1.0`.
- After a prior split-passed candidate lost an entire generated measure, staged selector was strengthened to require `baselineGeneratedMeasureSetPreserved=true` **before fit lock**.
- Reference-free helper `modal/v144_rhythm_measure_set_guard.py` commit `702e5cb5477af2f44e940be9a80fea8fa8e7922d` compares only source/candidate generated measure IDs.
- Staged selector correction commit `c1bd13e790c3e9304d9dcb2d789b0953d158bc49`; tests `4493bbbc7ca92c45100f0ac09e329d43fc7cb25a` plus measure-set tests `26558303d3ef25880083d6764d8cc1c621a80e57`.
- Corrected CPU gate run `32936974998` SUCCESS.

## Historical consumed candidate families — do not replay
1. **Single signature**: fit locked `pitchClass::11`; validation pitch regressed; rejected. Run `32935621669`, report bot `e19972d0df128852717bcc9506ae154586d4f4ee`. Workflow sealed in `7951564d3d46c99b74628ae1768575d1bbc15f1a`.
2. **Two-signature conjunction**: split locked `register::high && section16::1`; fit/validation/canary passed but full measure coverage fell to 112/113, so full invariant rejected. Split run `32936171588`; full invariant run `32936612852`; evaluated bot commit `e03d0d25a3c1e8ab8d68e51737e0abd84a920fb9`. Workflow sealed in `d13331984ff5b5108ab7e74e77889f79b9e76987`.
- Never reselect either consumed family using later-stage evidence.

## Three-signature measure-safe family — ACCEPTED V144 CALIBRATION BASELINE
- Policy `modal/v144_rhythm_triple_conjunction_policy.py` commit `84dc62f7dc688c7a3e00133598f01a4f46930d2f`; tests `d6e9985dc4fe73547d545143d30c0efd36f22f46`; CPU gate run `32937133401` SUCCESS.
- Search implementation `validation/v144_rhythm_calibration/search_triple_conjunction_prunes.py` commit `d1ee76ffecc3b4e497ce879efe9b786b41184e08`.
- Search workflow commit `c1f03e78ecb0b030e24478d34df3da5f34bcbbec`; run `32937262081` = **SUCCESS**.
- Search report persisted by bot commit `d40a181a0f85e780b08796e0be9d0bf371badf23` at `debug/v144-rhythm-calibration/candidates/triple-conjunction-search.json`, Git blob `3df01c870198a78edc485acd9e2f5bbcaca0a8fe`.
- Search family: 384 deterministic three-signature rules built/ranked from fit-only unmatched-generated evidence. Validation/canary/historical results were not used in construction/ranking. Every candidate had a reference-free full-generated-measure preservation check before eligibility.
- **Accepted candidate:** `prune-triple-67348efe50436fc5`.
- Runtime rule: `register::high && section16::1 && stepParity::0`.
- Candidate event stream: **1144 events**, canonical/PDF-event SHA256 `68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3`.
- Generated measure set preserved exactly: 113/113, missing `[]`, extra `[]`; measure-set guard used no professional reference.
- Independent PDF-event proof: `1.0`, exact same event SHA, reference not opened during fidelity proof.

### Fit gate — PASSED
- pitch-content F1 gain `+0.00783184116370314`
- pitch/timing gain `+0.0015890692216209146`
- string/fret/timing gain `+0.0011350494440149524`
- chord pitch-set gain `+0.000872237089899891`
- exact voicing gain `+0.000872237089899891`
- critical mismatch delta `-45`
- no regressions.

### Validation gate — PASSED
- pitch gain `+0.0011890827341471122`
- pitch/timing `+0.0005202236961893494`
- string/fret/timing `+0.00029727068353677805`
- chord/voicing `+0.00022105961240881378`
- critical delta `-4`
- no regressions.

### Canary gate — PASSED
- pitch gain `+0.006233622601909045`
- pitch/timing `+0.0012065076003694927`
- string/fret/timing `+0.0010054230003079083`
- chord/voicing `+0.0007630259428820577`
- critical delta `-16`
- no regressions.

### Full gold calibration invariant — PASSED
- critical mismatches **1810** (`-65` vs V5): 1004 gross unmatched generated + 806 unmatched reference + 0 missing measures.
- pitch-content F1 **`0.2909090909090909`** (`+0.007846445897490006`).
- pitch/timing F1 **`0.045933014354066985`** (`+0.0013854505489625801`).
- string/fret/timing F1 **`0.031578947368421054`** (`+0.0009524972524117721`).
- chord pitch-set F1 **`0.023496890117484452`** (`+0.0007391926609918165`).
- exact voicing F1 **`0.023496890117484452`** (`+0.0007391926609918165`).
- measure coverage recall **`1.0`**, PDF-event fidelity **`1.0`**, no full metric regressions.
- Report result: `calibrationPromotionAllowed=true`, `selectedReason=locked-candidate-passed-split-and-full-calibration-invariants`, `stoppedAt=complete`.
- This is **calibration baseline promotion only**. Production promotion remains false; Rhythm is not complete; near-100% target is not reached; unseen generalization is not proven.
- Search workflow sealed against replay in commit `abfe8ba4551440a333a24b03ae6c3dc833ccf506`.
- Dedicated accepted-baseline manifest: `debug/v144-rhythm-calibration/selected/v144-triple-selected-baseline.json`, commit `e7355054949e36fd14fdb55ea28bff21d39e9924`.

## Current working baseline
- **All future V144 Rhythm calibration increments must start from the accepted 1144-event triple baseline, not from V5/no-prune.**
- Accepted baseline name `prune-triple-67348efe50436fc5`; event SHA `68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3`; 113 generated measures; PDF fidelity 1.0.
- Any next transformation must be additive/versioned V144-only, reference-free at runtime, fit-learned/ranked only, preserve the accepted 113-measure set before fit lock, then pass locked validation, canary, full-gold no-regression/coverage/critical gates, and exact candidate/PDF identity.

## Immediate next resume actions
1. Reconstruct the accepted 1144-event baseline deterministically from frozen V5 + fixed triple rule and verify SHA/113-measure identity.
2. Build residual split diagnostics against this **accepted V144 baseline**: fit-only unmatched-generated vs missing-reference signals, with validation/canary labels not used for next candidate construction.
3. Persist V144-only residual diagnostics and checkpoint exact counts/signatures/hotspots.
4. Predeclare the next additive candidate family from residual **fit-only** evidence before opening new validation/canary results. Do not replay the consumed triple family or choose an alternate triple from its report.
5. Keep numeric thresholds fixed; keep reference-free measure-set preservation, staged selector, full-gold invariant, and PDF fidelity gates.
6. Continue CPU/repository-only work; **no Modal/L4/GPU without fresh explicit authorization**.
