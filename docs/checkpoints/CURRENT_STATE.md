# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-26 America/Montreal
Branch: `v143-contextual-prune-lobo`
Active phase: **V144 Rhythm gold calibration. The accepted 1144-event three-signature baseline remains locked. Single/pair/triple/quad pruning families are consumed; the quad family kept deterministic fallback. The fit-only error-mechanism diagnostic has now completed successfully and shows deletion/pruning has a much lower structural ceiling than pitch correction on fit. Next is to pre-register and CPU-test a materially new reference-free pitch-correction family; no new candidate search has started. Do not begin Bass/Lead unless Rhythm quality is proven or the user explicitly redirects.**

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

## Additive four-signature conjunction family — CONSUMED / SEALED
- Policy `modal/v144_rhythm_quad_conjunction_policy.py` commit `2932f6cdad713f70c4f24970274768efe6768b8a`; tests commit `d0f75fd2cd3a196be1ca22fbdf7a89a276f83da3`; CPU-gate integration `5387cce022c7cb91ac0691a3a749668fbcc9921a`; CPU gate run `32937890621` SUCCESS.
- Search implementation `validation/v144_rhythm_calibration/search_additive_quad_prunes.py`, commit `a95b1523143b5f38ce2a4c3e7a9fa7d7abd48944`.
- Initial workflow registration run `32938601146` failed before any job existed; actual one-shot trigger commit `8a28b3af9f72a5b109b6988991f769f88bed1a4c`.
- **Single actual search run `32938769540` SUCCESS**; exactly 512 fit-only candidates evaluated from 577 fit unmatched generated notes.
- Outcome: no candidate cleared fit; deterministic fallback kept accepted baseline. Validation/canary/fullCalibration were not opened. Report bot `fa272999273a5421901cdb4601f8ef33c8dd0dab`; report blob `5928e9687414c1e118653f139eda205237584ee0`.
- Workflow archived/sealed commit `69db5acad3e313610f22617f06fbb325e5b8941d`, archived blob `abd950baf353da20ae581b5a524b54970abb9c8c`.

## Fit-only error-mechanism diagnostic — COMPLETE / SEALED
- Implementation `validation/v144_rhythm_calibration/analyze_fit_error_mechanisms.py`, commit `4dc645f7443fea9c5bb270419eb74488a121b6f6`; deterministic tests `modal/tests/test_v144_rhythm_fit_error_mechanisms.py`, commit `2cc3ef0c90fa34bc306a2ccf9fdbeaed93ea4991`.
- CPU-only diagnostic trigger commit `251110e0c317ce4df69922f37bff36925a72f296`; run **`32939297662` SUCCESS**.
- Persisted report `debug/v144-rhythm-calibration/baseline/v144-fit-error-mechanisms.json`; bot commit `fea13223dadab7f8ef9932ad7feb6b803c9e9d0e`; report blob `4d1f143142b15b3cb9270eca291dbc12d30dff80`.
- Diagnostic performed **no candidate construction, ranking, selection, promotion, or threshold adjustment**; validation/canary labels were not used; runtime reference input false; Modal GPU false.
- Fit counts: generated `643`, reference `594`; pitch-content matched `138`; tight ±0.5-step pitch/timing matched `28`; gross ±2-step pitch/timing matched `66`; exact string/fret/timing matched `20`.
- Fit mechanisms: same-onset wrong-pitch substitution slots `184`; same-measure pitch matches displaced from exact onset `110`; gross-only timing recovery `38`; same-measure pitch matches still outside gross tolerance/competing `72`; correct pitch/timing but wrong string/fret `8`; gross unmatched generated/reference `577/528`; pitch-content FP/FN `505/456`.
- **Structural conclusion from fit-only oracle ceilings:** perfect pitch-FP deletion while holding matches fixed can reach only pitch F1 `0.3770491803278688`; perfect gross-unmatched deletion reaches gross timing F1 `0.2`; count-preserving pitch correction has a diagnostic pitch-content ceiling `0.9603880355699272`. This does not authorize an oracle runtime rule, but it does show that another deletion/pruning family is structurally much less promising than a materially new correction family.
- Diagnostic workflow archived/sealed commit `f391a52870c8e6eb8da5a476f4592a104dd15aae`; archived workflow blob `b900a3c2f8f408b20d560a41ebc69e4b2f938e1d`.

## Immediate next actions
1. Never replay/reselect from consumed single/pair/triple/quad families or the completed diagnostic, and do not alter fixed selector thresholds after seeing outcomes.
2. Pre-register a **materially new reference-free pitch-correction family** from accepted-baseline fit evidence only. The family may learn deterministic context-to-correction rules from fit labels, but runtime application must use only generated-event/context fields and must not consult the professional reference.
3. Prefer pitch correction over more deletion: pitch correction changes note identity while preserving event count/measure coverage; any string/fret change must remain internally consistent with MIDI and the render contract.
4. Add deterministic policy tests and pass a CPU-only safety gate before any one-shot correction search. No correction candidate has been searched or selected yet.
5. Preserve one-winner fit lock and fixed validation → canary → full-gold → independent PDF-event invariant sequence; fallback remains the accepted 1144-event baseline.
6. Do not promote Rhythm, start Bass/Lead, or claim near-100% quality. **No Modal/L4/GPU without fresh explicit user authorization.**
