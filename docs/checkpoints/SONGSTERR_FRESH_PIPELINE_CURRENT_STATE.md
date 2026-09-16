# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-15 America/Toronto — V3 iteration 3 and the V7 mechanical successor integration remain frozen synthetic PASSes. The first prospectively authorized V7 real-evaluation attempt was blocked by its synthetic prerequisite before any prior Basic Pitch artifact or EGFxSet media was fetched. Two subsequent synthetic-only representation-bridge iterations improved the V6-audio→V3 seam from the original failure to 18/23 and then 20/23 frozen V6 audio expectations, but both are frozen FAILs. No real/model evaluation is currently authorized.

Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- **Do not resume archived V143/Gomyway unless the user explicitly asks.**
- GOAT/reference scoring remains closed unless explicitly reopened.
- Guitar-TECHS, GuitarSet/V3 validation, IDMT/V4, V5/FLGD, duration research, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/**` remains deterministic/model-free/process-free/network-free and read-only for this research line.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Synthetic/smoke diagnostics are never authoritative correctness validation.
- Never rewrite or soften any frozen historical FAIL/C/PASS result.

## GLOBAL AUTHORIZATION — UNCHANGED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Consumed real-run authorizations:

- `Please try the run again` -> hardened-V1 EGFxSet run `34938917218`, attempt 1.
- `Lets take what was learned, repair and run again` -> boundary-aware V2 repair plus EGFxSet V2 run `34940292514`, attempt 1.
- `I authorize please continue` -> V7 real-evaluation attempt run `35051186125`, attempt 1; synthetic prerequisite failed and therefore the prior Basic Pitch artifact, EGFxSet media and V7 real qualifier were all skipped. That authorization is consumed; there is no retry under it.

There is currently **no authorization** for another EGFxSet run, Basic Pitch rerun, V6/V7 real correctness run, threshold variation, modified-real-rule execution, AG-PT-set structural re-audit, rejected-candidate payload access, physical capture/calibration, or protected-song execution.

## KEY FROZEN RECORDS

Historical / holdout:

- hardening result: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_HARDENING_V1_RESULT.md`
- boundary V2 PRE: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_PRE.md`
- boundary V2 real result: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_RESULT.md`
- AG-PT-set reference-blind PRE/result: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_PRE.md`, `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_RESULT.md`
- 2025–2026 no-new-candidate search: `docs/checkpoints/SONGSTERR_FRESH_V6_PREMEDIA_2025_2026_SEARCH_NO_NEW_CANDIDATE.md`

V3 / V7:

- V3 iteration-3 PRE: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE_ITERATION3.md`, commit `26ac58fe54c179744ef036a9dc4f4a7d69598038`
- V3 iteration-3 result: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT_ITERATION3.md`, commit `e97ab67c9c2794f4a50c5170102d1380484f5fb1`
- V7 successor integration PRE: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_INTEGRATION_PRE.md`, commit `638b045aea5a9fc66cee30c78772e792b38b8c79`
- V7 successor integration result: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_INTEGRATION_RESULT.md`, commit `9f6345e971f36a0def367a70564ba9b86c948e23`
- V7 real-evaluation PRE: `docs/checkpoints/SONGSTERR_FRESH_V7_REAL_EVALUATION_PRE.md`, commit `b7f5f681d6ef39669bcec44ba8116a4ae177e680`
- V7 blocked real-evaluation result: `docs/checkpoints/SONGSTERR_FRESH_V7_REAL_EVALUATION_RESULT.md`, commit `089d6a152f9ce2bce499775b74b6e9cb4e7cdfc4`
- representation bridge iteration-1 PRE/result: `docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_PRE.md`, commit `6502f00670efe9987ff5a76707d9cf32476ac4fe`; `docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_RESULT.md`, commit `d2eb412bec5bcf920a397b2d7e69642464497320`
- representation bridge iteration-2 PRE/result: `docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_PRE_ITERATION2.md`, commit `7cc8fc88a9b3d12596dfdce553bb717bc77fb05b`; `docs/checkpoints/SONGSTERR_FRESH_V7_REPRESENTATION_BRIDGE_SYNTHETIC_RESULT_ITERATION2.md`, commit `dfa51a1a6da521a36feb3733d199dfbbeea99de8`

## EGFxSET HISTORY — FROZEN

Immutable real member remains EGFxSet v1.0 `Clean.zip#Clean/Bridge/6-0.wav`:

- archive MD5 `cdb1b401960f56becc8640387910e78a`
- member SHA-256 `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`
- member bytes `722976`.

Immutable repaired Basic Pitch proposal artifact remains:

- source run `34936227380`
- artifact `10383413992`
- artifact ZIP SHA-256 `c380d39bdee5c3ec2827c1ae682e83b71eabe3bc738fa27016d3bb409afe566a`
- `basic-pitch.json` SHA-256 `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`
- note identity SHA-256 `2e30685479444a8120dc3490c9c41329a89e57aa16979de42053b89a4bbb0444`
- raw proposals exactly `[40,68]`.

Frozen historical outcomes:

- all-events smoke remains `FAIL_NON_AUTHORIZING_SMOKE`.
- hardened V1 run `34938917218` remains `FAIL_HARDENED_NON_AUTHORIZING_DIAGNOSTIC`; MIDI40 used fabricated left zero-padding and failed physical-template plausibility, MIDI68 failed necessity.
- boundary V2 run `34940292514` remains `FAIL_BOUNDARY_V2_NON_AUTHORIZING_DIAGNOSTIC`; zero-padding was removed, MIDI40 still failed the inherited physical-template plausibility gate, MIDI68 remained rejected at necessity `0.000513675778819313 < 0.01`.

Do not lower the historical V6 `0.20` physical-template ratio, remove historical gates, special-case MIDI40, or tune from any frozen EGFxSet observation.

## REPLACEMENT-HOLDOUT / CLOSED-LINE STATE

Frozen ingress rule still requires, before payload access, public metadata establishing all four: real human guitar performance; usable public rights for the exact scoring media; synchronized note-event ground truth for that exact performance; and reference provenance sufficiently independent of Basic Pitch/V6.

Closed/rejected lines remain closed, including GuitarJam, URMP, GAPS, EGDB/EGDB-PG, GuitarDuets, EG-Solo, Guitar Style Dataset, historical GPT, Guitar-TECHS, GuitarSet/V3, IDMT/V4, V5/FLGD and GOAT/reference scoring.

AG-PT-set remains pre-media PASS followed by frozen structural decision C:

- authoritative audit run `35020989444`, job `104556302921`
- duplicate `35021035914` is not independent evidence
- archive admitted, annotation rows `32592`, pitched/onset rows `24180`
- admitted WAVs `0`
- fatal anomalies `24180`, all `missing_or_ambiguous_audio`
- Basic Pitch runs `0`, V6 correctness runs `0`
- result checkpoint commit `89ad50b10c37cece15fbcd03db50672bfad8ea92`.

Do not repair/re-run AG-PT-set without a new prospective PRE plus explicit authorization.

## V3 SYNTHETIC PHYSICAL-TEMPLATE LINE — FROZEN

Iteration 1 remains `FAIL_SYNTHETIC_ALIAS_PROTECTION`.

Iteration 2 remains `FAIL_SYNTHETIC_SPURIOUS_SUPPORT` with five unexpected PASS controls: `two_harmonics_only`, `single_peak_only`, `broadband_noise`, `nonharmonic_impulses`, `clip_start_insufficient_support`.

Iteration 3 remains permanently `PASS_SYNTHETIC_EVIDENCE_SIGNIFICANCE`:

- module blob `39629250c6d141d5cda9e9d7f570580ec725ae42`
- test blob `76455337bd17a952dd36c1dabd03ce741e806b07`
- 34 fixtures × 3 repetitions
- deterministic `true`
- mismatch count `0`
- frozen `MIN_CANDIDATE_EVIDENCE_FRACTION = 0.10`
- NNLS necessity minimum remains `0.01`
- no rescue rerun/tuning.

Frozen V3 base geometry/threshold semantics remain read-only. The synthetic PASS is not real/model correctness evidence.

## V7 SUCCESSOR MECHANICAL INTEGRATION — FROZEN PASS

Frozen V7 module:

- `scripts/songsterr-fresh/onset_birth_corroboration_v7.py`
- commit `a2d312aa1dfd86be617fba35724de8aa1fba40d6`
- Git blob `6dfadda70db6b902f1dcc4d804f2d66da547314d`.

Frozen V7 integration test blob: `a5443cae88f4ba49e5a9712822a5c371b67a1c30`.

First mechanical integration result:

- 34 frozen fixtures represented as 33 selected-proposal composite fixtures plus one direct-template structural control
- 3 repetitions
- deterministic `true`
- mismatch count `0`
- octave-alias lower-owner case stayed FAIL through `LOWER_OWNER_EXPLAINS_SELECTED`, with MIDI57 among vetoing owners
- every V7 PASS preserved finite `necessityFraction >= 0.01` and `candidateEvidenceFraction >= 0.10`
- result `PASS_SYNTHETIC_MECHANICAL_INTEGRATION`.

This PASS established wrapper consistency only. It did **not** establish that frozen V6 audio-derived onset innovation has the same representation geometry as the direct synthetic spectra used by V3.

## V7 REAL-EVALUATION ATTEMPT — BLOCKED BEFORE REAL ACCESS

Prospective real PRE commit: `b7f5f681d6ef39669bcec44ba8116a4ae177e680`.

Authoritative attempt:

- workflow `.github/workflows/songsterr-egfxset-v7-real-evaluation-one-shot.yml`
- run head `1fa782b7165ab91995179ac0dd52a79459a43cb8`
- run `35051186125`
- job `104651706632`
- attempt `1`
- failure artifact `10428433425`, ZIP SHA-256 `12c3df736082f3ce479364cb54940bd31ee63c683a578750c62b48ee81d1b1f2`.

The prospectively frozen first synthetic prerequisite failed immediately on the ordinary in-clip E2 control:

- expected MIDI40 `corroborated`
- observed `SELECTED_TEMPLATE_INELIGIBLE`
- selected template `NO_ELIGIBLE_DETUNING_ANCHOR`
- all 17 V3 anchors `INSUFFICIENT_MULTI_HARMONIC_SUPPORT`
- analysis RMS `0.4252074715940777`
- innovation energy `306.85426206148344`.

The same fixture's later MIDI68 remained rejected through `FAIL_NECESSITY`, necessity `7.773057600779459e-06 < 0.01`.

Because the prerequisite failed:

- prior Basic Pitch artifact fetch: `skipped`
- EGFxSet media fetch: `skipped`
- V7 real qualifier: `skipped`
- Basic Pitch invoked: `false`
- real media fetched: `false`.

Frozen interpretation: `FAIL_V7_BOUNDARY_SYNTHETIC_PREREQUISITE / REAL_EVALUATION_NOT_EXECUTED`. No EGFxSet conclusion may be inferred from that attempt, and there is no same-authorization retry.

## REPRESENTATION-SEAM ROOT CAUSE

Frozen V6 audio analysis uses:

- Hann analysis frame `2048` samples
- zero-padded FFT `8192`
- zero-padding factor `4`
- nonnegative pre/post magnitude innovation on the 8192-point real-FFT grid.

A Hann-windowed sinusoid's first null is approximately two native frame-DFT bins from its center. Under the frozen 4× zero-padding this main-lobe half-width occupies about 8 bins on the frozen grid.

Frozen V3 direct-spectrum fixtures use narrow local line peaks. V3 local-background logic samples nearby bins within radius 6. When raw V6 Hann-windowed innovation is supplied directly, those background bins can lie inside the physical harmonic's own deterministic Hann main lobe, causing the harmonic's leakage to be treated as local background. This explains the original all-17-anchor support failure despite high total innovation energy.

The bridge research therefore targets representation geometry only; it does not relax V3/V6 decision thresholds.

## REPRESENTATION BRIDGE ITERATION 1 — FROZEN FAIL

PRE commit: `6502f00670efe9987ff5a76707d9cf32476ac4fe`.

Frozen bridge pair:

- `v6_innovation_line_bridge_v1.py` blob `a63d62371e3ad97cb2ce085ccb1c2950a5cd23a1`
- test blob `a8a4bd8399763a2581209ae594349d39b38d6e7c`
- pair head `73652d19f6dc71964e788330e3a94b163a6fb4af`.

Execution:

- workflow head `59a1bdb84a00e34c42906f2425d2d556572a5f78`
- run `35051843902`
- job `104653711197`
- attempt `1`.

Hypothesis: identify local maxima with geometry-derived ±8-bin Hann-lobe suppression and retain only each center's exact original amplitude.

Result:

- 23 frozen V6 audio fixtures × 3
- deterministic `true`
- 18/23 matched, 5 mismatches
- structural bridge checks passed
- untouched V3 direct-spectrum regression stayed 34/34 PASS.

Five mismatches were `clean_low_m40` (`REDUCED_DICTIONARY_EMPTY`), `selected64_enters_over_existing60` (`FAIL_NECESSITY`), unexpected PASS `simultaneous_dyad_sel60`, `simultaneous_triad_sel60` (`FAIL_NECESSITY`), and `reattack_m64` (`SELECTED_TEMPLATE_INELIGIBLE`).

Frozen result: `FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_SINGLE_BIN_SPARSIFICATION`. No iteration-1 rerun or repair.

## REPRESENTATION BRIDGE ITERATION 2 — FROZEN FAIL, 20/23

PRE commit: `7cc8fc88a9b3d12596dfdce553bb717bc77fb05b`.

Frozen bridge pair:

- `v6_innovation_peak_band_bridge_v2.py` commit `56baaf07552fea521073d976c81a26658e2d5b6b`, blob `402aa23f3f1821c4e5c45ccf7f170b542d76a453`
- test pair head `46f4b71405946e0da68ff80e23b006f4393172c4`, test blob `167fe534cf99ac825c8127efa7828237551a5759`.

Execution:

- workflow head `b176a8665bef71ae99ff73733005ac083165c581`
- run `35052132987`
- job `104654595776`
- attempt `1`.

Hypothesis: keep the same geometry-derived ±8-bin local-max separation but preserve exact original amplitudes at each local maximum's `[-1,0,+1]` band, inherited from frozen V3 `PEAK_BIN_RADIUS=1`.

Result:

- 23 V6 audio fixtures × 3
- deterministic `true`
- 20/23 matched, 3 mismatches
- structural bridge checks all passed
- untouched V3 direct-spectrum suite remained 34/34 PASS.

Concrete repaired iteration-1 cases:

- `clean_low_m40` now PASS, necessity `0.12936434618438644`, candidate evidence `0.38443223142641103`
- `simultaneous_triad_sel60` now PASS, necessity `0.11027472693544244`, candidate evidence `0.3339493660329132`.

Three persistent mismatches:

1. `selected64_enters_over_existing60`: expected PASS, observed `FAIL_NECESSITY`; RMS `0.336542505699681`, raw innovation energy `217.8264003573765`, 11 retained centers / 33 retained positive bins.
2. `simultaneous_dyad_sel60`: expected reject, observed PASS; necessity `0.1840904226252075`, candidate evidence `0.34678943650665484`, no lower-owner veto; 12 centers / 36 positive bins.
3. `reattack_m64`: expected PASS, observed `SELECTED_TEMPLATE_INELIGIBLE`; RMS `0.43590990398881657`, raw innovation energy `248.79801311654884`, 11 centers / 32 positive bins.

Frozen result checkpoint commit: `dfa51a1a6da521a36feb3733d199dfbbeea99de8`.

Frozen result: `FAIL_SYNTHETIC_REPRESENTATION_BRIDGE_THREE_MISMATCHES`. No iteration-2 rerun or repair.

## CURRENT TECHNICAL CONCLUSION

The two bridge iterations establish a strong synthetic-only diagnosis:

- raw V6 Hann-lobe innovation is not directly compatible with V3's narrow-line local-background assumptions;
- leakage suppression is necessary and materially improves compatibility;
- reducing a physical lobe to one bin is too sparse;
- preserving V3's ±1 support band improves the frozen V6 population to 20/23;
- the remaining mismatches are not a single support-width problem.

The persistent cases indicate one transformed spectrum is being asked to serve two distinct semantic roles:

1. **harmonic support / local-background eligibility**, which benefits from a leakage-cleaned support view;
2. **candidate competition / NNLS necessity**, which may need richer/raw innovation structure.

Do **not** continue by searching peak width, suppression radius, thresholds, per-MIDI exceptions or fixture-specific rules. That would be post-result tuning.

## CURRENT SAFE NEXT ACTION

The next productive action is a **prospectively frozen synthetic-only dual-view diagnostic**, not a new final decision rule.

Before executing anything, create a new PRE that freezes:

- exact diagnostic module/test paths;
- all 23 frozen V6 audio fixtures as the population;
- iteration-2 peak-band representation as the support/eligibility view, read-only;
- raw frozen V6 innovation as the competition/necessity comparison view;
- exact diagnostics to collect for every fixture, including selected-template eligibility, candidate-support diagnostics, valid candidate population, NNLS necessity, owner diagnostics and candidate-evidence fraction where mechanically definable;
- no changed classification expectations and no new decision rule in the diagnostic iteration;
- one first execution only, deterministic repetitions, frozen result afterward;
- no real/model/media/network access.

The purpose is to determine whether support eligibility and competition/necessity can be separated cleanly without weakening alias, polyphony, transient, insufficiency or identity protections. Only after that diagnostic is frozen should a successor composition rule be designed prospectively.

Any future real-media V7 evaluation requires a **new real-evaluation PRE plus fresh explicit user authorization** after the synthetic line is complete.

Archived V143/Gomyway remains untouched.