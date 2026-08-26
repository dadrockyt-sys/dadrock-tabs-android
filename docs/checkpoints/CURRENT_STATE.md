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
- Historical V5 full-reference metrics: critical mismatches `1875`; PDF fidelity `1.0`; pitch F1 `0.2830626450116009`; pitch/timing `0.044547563805104405`; string/fret/timing `0.03062645011600928`; chord/voicing `0.022757697456492636`; measure coverage recall `1.0`.
- Repro baseline run `32934939964` SUCCESS; report bot commit `4511f05493cff7dc8828e61329b4ba439db168aa`.
- Deterministic split run `32935079594` SUCCESS; report bot commit `5dd431f65eec0dfb99fd3c3d8d77b5590190dd2a`.
- Split by measure+step, seed 144: 60% fit / 20% validation / 20% canary; cross-split matching forbidden.
- Fit baseline: 688 generated / 594 reference; pitch F1 `0.21528861154446177`; pitch/timing `0.043681747269890804`; string/fret/timing `0.031201248049921994`; chord/voicing `0.024858757062146894`; critical `1150`; gross unmatched 622 generated / 528 reference.
- Validation baseline pitch F1 `0.13733905579399142`, critical `426`; canary baseline pitch F1 `0.15233415233415235`, critical `385`.

## First single-signature experiment — REJECTED / WORKFLOW SEALED
- Run `32935621669` SUCCESS operationally; report bot commit `e19972d0df128852717bcc9506ae154586d4f4ee`.
- Fit locked `pitchClass::11`, 1049 events, SHA256 `cf031f8bb1efb788af4da464169c9dd2de246fc4e3e75bb51c80e46078b15c70`.
- Fit gains: pitch `+0.006373856969392133`; pitch/timing `+0.0033375642330478947`; string/fret/timing `+0.002383974452177081`; chord/voicing `+0.003244287434340229`; critical `-89`.
- Validation pitch-content regressed `-0.002140920595856244`; result fell back to `no-prune`. Canary was not opened.
- Historical workflow was sealed against replay in commit `7951564d3d46c99b74628ae1768575d1bbc15f1a`.

## Two-signature conjunction experiment — SPLIT-PASSED, FULL-INVARIANT REJECTED / WORKFLOW SEALED
- Conjunction policy commit `9d40ebec909aa203538403a2f7104d91383d1132`; tests `45b9972133144cf9653508c85e65702433167d58`; CPU gate run `32935847927` SUCCESS.
- Search run `32936171588` SUCCESS; split report bot commit `b6f2f9213ac38bf70c568bdf78ec769f24fff46d`, report blob `b92a3638d5b8fff0e911df43fb381f89f088afd6`.
- Split locked `prune-conjunction-33ac980932c68313`, rule `register::high && section16::1`, 1112 events, SHA256 `db5c8e8fbbb767c386f14a00df188c89738230694840c48bed1bae32b2653b4f`.
- Fit, validation, and canary all improved every split musical metric and critical mismatch count; independent PDF-event fidelity was `1.0`.
- Full-score script commit `f76635d1db58d5ed11a018c5ee461c566bb983ae`; workflow first commit `4c01deac45d8df47f5f1a94c516f37aa7f005da5`.
- First full run `32936501819` exposed a measure-coverage assertion; no selected artifacts persisted.
- Full invariant workflow fix commit `89ac9806b324160dda7c5a331e6e336c969049ea`; corrected run `32936612852` SUCCESS and bot commit `e03d0d25a3c1e8ab8d68e51737e0abd84a920fb9` persisted the evaluated result.
- Full absolute candidate metrics: pitch `0.293488824101069`; pitch/timing `0.04664723032069971`; string/fret/timing `0.03206997084548104`; chord/voicing `0.023826208829712685`; PDF fidelity `1.0`.
- Full critical mismatches improved `1875 → 1779` (`-96`), but measure coverage regressed `1.0 → 0.9911504424778761`: only 112/113 generated measures remained; diagnostic missing measure is `28`.
- Full invariant `passed=false`; `calibrationPromotionAllowed=false`; split selection is superseded and candidate is **REJECTED as the V144 baseline**.
- Persisted spec blob `904b3fe644d3ed11c0ff03a3d680b8c1718e2ebd`; full score blob `570d1d91410ac7452c5ed0d6f6ddd3c9ea6ecb4`.
- Historical conjunction search workflow was sealed against replay in commit `d13331984ff5b5108ab7e74e77889f79b9e76987`.
- Do not hand-edit/reselect that consumed family based on the discovered missing measure.

## Corrected V144 measure-preservation safety protocol — CPU-GREEN
- Staged selector now requires `candidate.safety.baselineGeneratedMeasureSetPreserved is True` **before fit lock**; missing/false proof adds reason `baseline-generated-measure-set-not-preserved`.
- Selector correction commit `c1bd13e790c3e9304d9dcb2d789b0953d158bc49`.
- Updated staged-selector tests commit `4493bbbc7ca92c45100f0ac09e329d43fc7cb25a`.
- Tests explicitly prove a candidate with large musical gains and fewer critical mismatches still cannot lock if the baseline-generated measure set is not preserved; absence of proof also fails closed.
- Added reference-free helper `modal/v144_rhythm_measure_set_guard.py` in commit `702e5cb5477af2f44e940be9a80fea8fa8e7922d`.
- `measure_set_evidence(baseline_events, candidate_events)` compares generated measure IDs only and returns missing/extra IDs plus `baselineGeneratedMeasureSetPreserved`; professional reference use is explicitly false.
- Added guard tests in commit `26558303d3ef25880083d6764d8cc1c621a80e57`, including the exact structural failure mode: dropping the final event of a measure fails preservation even if overall event count remains large.
- CPU workflow updated in commit `2fa297bdcaa3e19068c719a8c6bd08e1a85c6841`.
- CPU gate run `32936974998` = **SUCCESS**: frozen V5 guards, provenance safety, staged selector, conjunction policy, and reference-free measure-set tests all passed.
- Numeric musical thresholds were not changed.
- This closes the structural gap that allowed the prior split-passed candidate to lose a whole measure.

## Current interpretation
- V144 has proven that selective pruning can improve musical precision, but no candidate has yet satisfied the corrected full calibration invariant.
- Future candidates must preserve the immutable source candidate’s full generated measure-ID set before fit ranking. This is reference-free and independent of gold labels.
- The rejected two-signature rule is historical evidence only; its missing-measure detail must not be used to patch/reselect that family.
- Rendering/event identity remains exact; musical transcription is still far from near-100% quality.

## Unrelated workflow noise
- Pre-existing `.github/workflows/cleanup-tab-preview.yml` continues to fail on branch pushes. It is unrelated and untouched.

## Immediate next resume actions
1. Define a **new** fit-only candidate family rather than replaying the consumed single-/two-signature families. Preferred next family: deterministic three-signature conjunction prunes from existing reference-free `context_signature(event)` values.
2. Candidate construction/ranking must use fit-only unmatched-vs-generated evidence; validation/canary cannot enter construction/ranking.
3. Every candidate must compute `measure_set_evidence()` from the immutable 1209-event source stream and its transformed full stream; any non-preserving candidate is ineligible before fit lock.
4. Keep fixed musical thresholds, deterministic no-prune fallback, exact PDF-event fidelity, and staged validation/canary semantics.
5. Add CPU tests for the three-signature policy before running a search.
6. Use a new workflow/report path; do not reopen historical search workflows.
7. Checkpoint after protocol definition and after any locked-candidate/full-invariant result.
8. Continue CPU/repository-only work; **no Modal/L4/GPU without fresh explicit authorization**.
