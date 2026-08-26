# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. The accepted 1144-event three-signature baseline remains locked. The additive four-signature conjunction family is now consumed and sealed: its single actual CPU search evaluated 512 fit-ranked candidates, none cleared the fixed fit lock, and the selector deterministically kept the accepted 1144-event baseline. No quad validation/canary candidate was opened and no quad promotion occurred. Do not begin Bass/Lead unless Rhythm quality is proven or the user explicitly redirects.**

## Permanent safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge `main` or Production.
- Protected V5 analyzer `analyzer/v143_reference_free_rhythm_pipeline.py`, Git blob `7f72f8ed9b14af8bc93e95544195204d99c6bec1`.
- Frozen V5 final-result sentinel Git blob `511fd244f231b66d08306f97b5a47ed41f5415c7`.
- Frozen V5 render SHA256 `7c3399d3f5e05ecc8ac98d71d0e5300e1e78f63ae96c1642fe4a19debb4061b2`; PDF SHA256 `f4c1238e868cadfb90b8a359b1555b0b90e7740b9ebaa276aa394c8991f37ce5`; canonical event SHA256 `7ed5166a73793e3a40c9a21f6532fee5ba784e43ef4180727404a37a038fb6d1`.
- Original V5 professional one-shot holdout is permanently consumed. Never rerun/retry its final workflow, alter its candidate/thresholds/result, or retune V5 from V144 evidence.
- `main`, Production, `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` remain untouched.
- **No Modal/L4/GPU without fresh explicit user authorization. None has been used in V144.**

## Gold calibration reference
- Read-only visual target remains `main/public/Professionalexample.jpg`, main blob `16106197cc1269cca0b3c443908d5ef75e8b4d3e`, image SHA256 `aca2da3e8d551b2fd82b4ab3ecafa0c8932d6c0a27b54b6213ffc990ca08a9a9`.
- Structured source SHA256 `18cdb4f8afb49562aac5b600730384636070d6ca8650823e759276a81ee4afc8`; exact reference SHA256 `18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`.
- Reference completeness: 113 measures / 603 playable onsets / 946 notes / 104 populated measures.
- This is a **gold calibration benchmark, not an unseen holdout**. Never claim unbiased generalization from scores against it.
- Exact reference build run `32934718066` SUCCESS; persisted bot commit `0df6204909ca79bdd3a5bf1be4f1ca4d55cca53f`.

## Immutable V5 calibration baseline
- Full V5: critical mismatches `1875`; pitch F1 `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.03062645011600928`; chord/voicing `0.022757697456492636`; measure coverage `1.0`; PDF fidelity `1.0`.
- Baseline run `32934939964` SUCCESS; report bot `4511f05493cff7dc8828e61329b4ba439db168aa`; baseline report blob `ad5fa9d0b6c552035405c1cca81ee4e3f25b5764`.
- Deterministic split: measure+step, seed 144, 60% fit / 20% validation / 20% canary. Fit labels may construct/rank; validation/canary only gate the locked candidate.
- V5 fit baseline: pitch `0.21528861154446177`; pitch/timing `0.043681747269890804`; string/fret/timing `0.031201248049921994`; chord/voicing `0.024858757062146894`; critical `1150`; gross unmatched generated/reference `622/528`.

## Selector / invariant safety
- Fit ranking cannot read validation/canary; one winner locks; later failure returns to deterministic baseline fallback, never an alternate.
- Fixed numeric gate: fit pitch gain >= `0.005`; no musical metric regression; no critical mismatch increase; PDF-event fidelity `1.0`.
- Selector requires reference-free `baselineGeneratedMeasureSetPreserved=true` before fit lock.
- Every accepted-baseline additive candidate must preserve the accepted baseline's full 113 generated-measure IDs before fit lock.
- Fixed staged order remains fit → validation → canary → full-gold → PDF-event invariant. Do not change thresholds from residual/search outcomes.
- Measure-set helper commit `702e5cb5477af2f44e940be9a80fea8fa8e7922d`; selector correction `c1bd13e790c3e9304d9dcb2d789b0953d158bc49`; corrected CPU gate run `32936974998` SUCCESS.

## Consumed historical candidate families — never replay/reselect
1. Single-signature family: `pitchClass::11` fit winner failed validation pitch; run `32935621669`; workflow sealed `7951564d3d46c99b74628ae1768575d1bbc15f1a`.
2. Two-signature conjunction family: `register::high && section16::1` passed split gates but lost one whole generated measure and failed later full invariant; full evaluated bot `e03d0d25a3c1e8ab8d68e51737e0abd84a920fb9`; workflow sealed `d13331984ff5b5108ab7e74e77889f79b9e76987`.
3. Three-signature family is consumed by its accepted winner below. Do **not** use later evidence to choose another triple candidate.
4. Four-signature additive family is consumed by run `32938769540`; no candidate cleared fit. Do **not** replay, retune thresholds, enlarge the same candidate list, or choose a quad runner-up later.

## Accepted V144 calibration baseline — locked
- Triple policy commit `84dc62f7dc688c7a3e00133598f01a4f46930d2f`; tests `d6e9985dc4fe73547d545143d30c0efd36f22f46`; CPU gate `32937133401` SUCCESS.
- One-shot triple search run `32937262081` SUCCESS; search report bot `d40a181a0f85e780b08796e0be9d0bf371badf23`; workflow sealed `abfe8ba4551440a333a24b03ae6c3dc833ccf506`.
- **Accepted candidate:** `prune-triple-67348efe50436fc5` = `register::high && section16::1 && stepParity::0`.
- Stream: **1144 events**, canonical/PDF-event SHA256 `68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3`.
- Generated measure set exactly 113/113, missing `[]`, extra `[]`; independent PDF-event identity proof `1.0`.
- Fit gains: pitch `+0.00783184116370314`; pitch/timing `+0.0015890692216209146`; string/fret/timing `+0.0011350494440149524`; chord/voicing `+0.000872237089899891`; critical `-45`.
- Validation gains: pitch `+0.0011890827341471122`; pitch/timing `+0.0005202236961893494`; string/fret/timing `+0.00029727068353677805`; chord/voicing `+0.00022105961240881378`; critical `-4`.
- Canary gains: pitch `+0.006233622601909045`; pitch/timing `+0.0012065076003694927`; string/fret/timing `+0.0010054230003079083`; chord/voicing `+0.0007630259428820577`; critical `-16`.
- Full gold: critical `1810` (`-65` vs V5); pitch `0.2909090909090909`; pitch/timing `0.045933014354066985`; string/fret/timing `0.031578947368421054`; chord/voicing `0.023496890117484452`; measure coverage `1.0`; PDF fidelity `1.0`.
- Dedicated manifest `debug/v144-rhythm-calibration/selected/v144-triple-selected-baseline.json`, commit `e7355054949e36fd14fdb55ea28bff21d39e9924`, blob `ba8dec9a1c3155816f5841a32ee52ced7998c110`.
- This is **calibration-baseline promotion only**. Production promotion false; Rhythm complete false; near-100% false; unseen generalization not proven.

## Accepted-baseline residual diagnostics
- Residual workflow run `32937711754` SUCCESS; report bot `93614064a5fa788c6f74d1bd81b2cc02b7659cd2` at `debug/v144-rhythm-calibration/baseline/v144-accepted-residual-diagnostics.json`, blob `9e01f1f509fa537fb9e330ee0c13087cdf3b4fe4`.
- Accepted baseline reconstructed at 1144 events / SHA `68b8cdf...`, 113 generated measures, PDF-event fidelity `1.0`.
- Fit residual gross unmatched generated/reference: **577 / 528**, versus V5 **622 / 528**.
- Largest fit-only false-positive signals begin `register::high` 356, `stepParity::0` 320, `stepParity::1` 257, `pitchClass::4` 228, `register::mid` 191.
- These are diagnostics only; validation/canary/historical outcomes may not construct/rank the next family.

## Additive four-signature conjunction family — CONSUMED / SEALED
- Policy `modal/v144_rhythm_quad_conjunction_policy.py` commit `2932f6cdad713f70c4f24970274768efe6768b8a`; tests commit `d0f75fd2cd3a196be1ca22fbdf7a89a276f83da3`; CPU-gate integration `5387cce022c7cb91ac0691a3a749668fbcc9921a`; CPU gate run `32937890621` SUCCESS.
- Search implementation `validation/v144_rhythm_calibration/search_additive_quad_prunes.py`, commit `a95b1523143b5f38ce2a4c3e7a9fa7d7abd48944`.
- Initial workflow creation `036a8cbded62ea1d004095d2dba696164e6b5686` produced infrastructure-only startup failure run `32938601146` with `jobs=[]`; search execution count remained zero. The YAML defect was the unquoted colon-bearing job-level `if:` scalar. Do not Actions-rerun this failed registration.
- Narrow YAML repair/actual one-shot trigger commit `8a28b3af9f72a5b109b6988991f769f88bed1a4c`; **single actual search run `32938769540` SUCCESS**.
- All substantive steps passed: immutable V5/accepted-baseline checks; selector/measure/triple/quad CPU tests; fit-only search; construction isolation assertions; exact 113-measure guard; independent PDF-event proof; final invariant handling; immutable recheck; single-report persistence.
- Candidate construction: accepted 1144-event baseline only; fit unmatched-generated count `577`; minimum false-positive support `3`; maximum/evaluated candidate count **512**; validation/canary/historical consumed-family results used for construction/ranking = false; runtime rule input is reference-free four-signature context only.
- **Outcome:** `selected="accepted-v144-baseline"`, `selectedReason="fit-no-qualified-additive-candidate"`, `stoppedAt="fit"`, `splitPromotionAllowed=false`, `calibrationPromotionAllowed=false`, `validation=null`, `canary=null`.
- Locked stream is therefore unchanged accepted baseline: **1144 events**, SHA `68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3`, signatures `null`, exact 113/113 generated measures preserved.
- Independent locked-stream proof passed with PDF-event fidelity `1.0`, event count `1144`, event SHA `68b8cdf14ed02265c5e3c204b2af51b0aae4849462e7b3e4243192d8855cc3c3`, and no professional reference opened during PDF fidelity check.
- Persisted report `debug/v144-rhythm-calibration/candidates/additive-quad-search.json`; bot commit `fa272999273a5421901cdb4601f8ef33c8dd0dab`; report blob `5928e9687414c1e118653f139eda205237584ee0`.
- Workflow archived/sealed commit `69db5acad3e313610f22617f06fbb325e5b8941d`, archived blob `abd950baf353da20ae581b5a524b54970abb9c8c`. The seal commit triggered no quad workflow run; only unrelated `cleanup-tab-preview` ran.
- **No quad candidate was promoted. Accepted V144 baseline remains exactly the locked triple baseline.**

## Immediate next actions
1. Never replay/reselect from the consumed single/pair/triple/quad candidate families and do not alter their thresholds after seeing outcomes.
2. Because the accepted baseline did not change, use only its already-authorized **fit** evidence for any next diagnostic/family construction; do not use validation/canary/full outcomes to invent or rank a new rule.
3. Before another one-shot candidate search, define a **materially new, pre-registered correction family** (not an enlarged/reordered quad list), add deterministic tests, preserve all 113 accepted-baseline generated measures, and pass the CPU gate first.
4. A safe next investigation is a fit-only error-mechanism diagnostic on the accepted 1144-event baseline (e.g. false-positive deletion vs pitch/onset/string-fret correction opportunity) to decide whether further pruning is structurally capable of meaningful improvement. Diagnostics must be labeled calibration-only and may not claim unseen generalization.
5. Do not promote Rhythm, do not start Bass/Lead, and do not claim near-100% quality; current full-gold accepted baseline remains pitch F1 `0.2909090909090909` with critical mismatch count `1810`.
6. **No Modal/L4/GPU without fresh explicit user authorization.**
