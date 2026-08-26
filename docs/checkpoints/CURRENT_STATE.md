# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. The first corrected all-invariant calibration baseline is accepted. Continue improving Rhythm from that 1144-event baseline; do not begin Bass/Lead unless Rhythm quality is proven or the user explicitly redirects.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer `analyzer/v143_reference_free_rhythm_pipeline.py`, Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
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
- Full V5: critical mismatches `1875`; pitch F1 `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.03062645011600928`; chord/voicing `0.022757697456492636`; measure coverage `1.0`; PDF fidelity `1.0`.
- Baseline run `32934939964` SUCCESS; report bot `4511f05493cff7dc8828e61329b4ba439db168aa`; baseline report blob `ad5fa9d0b6c552035405c1cca81ee4e3f25b5764`.
- Deterministic split: measure+step, seed 144, 60% fit / 20% validation / 20% canary. Fit labels may construct/rank; validation/canary only gate the locked candidate.
- V5 fit baseline: pitch `0.21528861154446177`; pitch/timing `0.043681747269890804`; string/fret/timing `0.031201248049921994`; chord/voicing `0.024858757062146894`; critical `1150`; gross unmatched generated/reference `622/528`.

## Corrected selector safety
- Fit ranking cannot read validation/canary; one winner locks; later failure returns to deterministic `no-prune`, never an alternate.
- Numeric gate fixed: fit pitch gain >= `0.005`; no musical metric regression; no critical mismatch increase; PDF-event fidelity `1.0`.
- Selector also requires reference-free `baselineGeneratedMeasureSetPreserved=true` before fit lock.
- Measure-set helper `modal/v144_rhythm_measure_set_guard.py` commit `702e5cb5477af2f44e940be9a80fea8fa8e7922d`; selector correction `c1bd13e790c3e9304d9dcb2d789b0953d158bc49`; tests `4493bbbc7ca92c45100f0ac09e329d43fc7cb25a` and `26558303d3ef25880083d6764d8cc1c621a80e57`.
- Corrected CPU gate run `32936974998` SUCCESS.

## Consumed historical candidate families — never replay/reselect
1. Single-signature family: `pitchClass::11` fit winner failed validation pitch; run `32935621669`, report bot `e19972d0df128852717bcc9506ae154586d4f4ee`; workflow sealed `7951564d3d46c99b74628ae1768575d1bbc15f1a`.
2. Two-signature conjunction family: `register::high && section16::1` passed split gates but lost one whole generated measure and failed the later full invariant; full evaluated bot `e03d0d25a3c1e8ab8d68e51737e0abd84a920fb9`; workflow sealed `d13331984ff5b5108ab7e74e77889f79b9e76987`.
- Later evidence may not be used to choose a different member of either family.

## Accepted V144 calibration baseline — three-signature measure-safe winner
- Triple policy commit `84dc62f7dc688c7a3e00133598f01a4f46930d2f`; tests `d6e9985dc4fe73547d545143d30c0efd36f22f46`; CPU gate run `32937133401` SUCCESS.
- Search implementation `validation/v144_rhythm_calibration/search_triple_conjunction_prunes.py`, commit `d1ee76ffecc3b4e497ce879efe9b786b41184e08`.
- One-shot search workflow commit `c1f03e78ecb0b030e24478d34df3da5f34bcbbec`; run `32937262081` **SUCCESS**.
- Search report persisted by bot `d40a181a0f85e780b08796e0be9d0bf371badf23` at `debug/v144-rhythm-calibration/candidates/triple-conjunction-search.json`, Git blob `3df01c870198a78edc485acd9e2f5bbcaca0a8fe`.
- 384 predeclared triple rules were constructed/ranked from fit-only unmatched-generated evidence. Validation/canary/historical results were not construction/ranking inputs. Every candidate received a reference-free full-measure-set safety check before fit lock.
- **Accepted candidate:** `prune-triple-67348efe50436fc5`.
- Runtime rule: `register::high && section16::1 && stepParity::0`.
- Stream: **1144 events**, canonical/PDF-event SHA256 `68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3`.
- Generated measure set: exactly 113/113, missing `[]`, extra `[]`; measure guard used no professional reference.
- Independent PDF-event identity proof `1.0` with exact same SHA; reference not opened during fidelity proof.

### Accepted candidate gates
- Fit PASSED: pitch `+0.00783184116370314`; pitch/timing `+0.0015890692216209146`; string/fret/timing `+0.0011350494440149524`; chord/voicing `+0.000872237089899891`; critical `-45`; no regressions.
- Validation PASSED: pitch `+0.0011890827341471122`; pitch/timing `+0.0005202236961893494`; string/fret/timing `+0.00029727068353677805`; chord/voicing `+0.00022105961240881378`; critical `-4`; no regressions.
- Canary PASSED: pitch `+0.006233622601909045`; pitch/timing `+0.0012065076003694927`; string/fret/timing `+0.0010054230003079083`; chord/voicing `+0.0007630259428820577`; critical `-16`; no regressions.
- Full-gold invariant PASSED: critical mismatches **1810** (`-65` vs V5), 1004 unmatched generated + 806 unmatched reference + 0 missing measures; pitch `0.2909090909090909`; pitch/timing `0.045933014354066985`; string/fret/timing `0.031578947368421054`; chord/voicing `0.023496890117484452`; measure coverage `1.0`; PDF fidelity `1.0`; no full metric regressions.
- This is **calibration baseline promotion only**. Production promotion false; Rhythm complete false; near-100% false; unseen generalization not proven.
- Search workflow sealed against replay in commit `abfe8ba4551440a333a24b03ae6c3dc833ccf506`.
- Dedicated baseline manifest `debug/v144-rhythm-calibration/selected/v144-triple-selected-baseline.json`, commit `e7355054949e36fd14fdb55ea28bff21d39e9924`, Git blob `ba8dec9a1c3155816f5841a32ee52ced7998c110`.

## Accepted-baseline residual diagnostics — CURRENT RESUME SURFACE
- Residual analyzer `validation/v144_rhythm_calibration/analyze_selected_baseline_residuals.py`, commit `86e70537f5a2ff4797dc320bfaaae460a517418f`.
- CPU workflow `.github/workflows/v144-accepted-baseline-residuals.yml`, commit `88731d7fe4d3723f006fad316f868318e3d2a457`; run `32937711754` **SUCCESS**.
- Residual report persisted by bot `93614064a5fa788c6f74d1bd81b2cc02b7659cd2` at `debug/v144-rhythm-calibration/baseline/v144-accepted-residual-diagnostics.json`, Git blob `9e01f1f509fa537fb9e330ee0c13087cdf3b4fe4`.
- Accepted baseline was reconstructed deterministically from frozen V5 + fixed triple rule at exactly 1144 events / SHA `68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3`, 113 generated measures, and independently re-proved PDF-event fidelity `1.0`.
- Fit residual gross unmatched generated/reference is now **577 / 528**, versus V5 fit baseline **622 / 528**. The accepted rule removed 45 fit gross unmatched generated notes without increasing fit gross unmatched reference notes.
- Largest remaining fit-only false-positive structural signals: `register::high` 356; `stepParity::0` 320; `stepParity::1` 257; `pitchClass::4` 228; `register::mid` 191; `stepQuarter::0` 161; `stepQuarter::2` 159; `measurePhase::2` 156; `measurePhase::0` 151; `measurePhase::3` 144; `section16::6` 122.
- Largest fit-only false-negative structural signals: `stepParity::0` 436; `register::mid` 271; `stepQuarter::0` 225; `stepQuarter::2` 211; `register::high` 182; `pitchClass::4` 157; `measurePhase::0` 150; `registerStep::mid:0` 144.
- Highest residual fit pitch-error measures begin: 34 (18 errors), 110 (17), 109/72/73 (15 each), 8 (14). These are diagnostic fit signals only.
- Next candidate construction contract is explicit: baseline must be accepted SHA `68b8cdf...`; fit labels may construct/rank; validation/canary may not; runtime reference input forbidden; the accepted 113-measure set must be preserved; numeric thresholds may not be changed from residual outcomes.

## Immediate next resume actions
1. Predeclare a **new additive candidate family** from the accepted 1144-event baseline; do not choose an alternate from the consumed triple report.
2. Preferred next family: deterministic four-signature conjunction prune rules built solely from accepted-baseline fit residual unmatched/generated evidence. This is a new family, not a replay of the consumed triple family.
3. Every transformed candidate must compare its full generated measure IDs against the accepted 1144-event baseline before fit lock and preserve all 113 measures.
4. Keep fixed numeric thresholds and staged fit→validation→canary→full-gold→PDF invariant gates.
5. Add CPU policy/tests before any four-signature search. Use a new workflow/report path and seal it after the one-shot search.
6. Continue CPU/repository-only work; **no Modal/L4/GPU without fresh explicit authorization**.
