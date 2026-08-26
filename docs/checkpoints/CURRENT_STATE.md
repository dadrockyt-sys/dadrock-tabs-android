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

## Leakage-safe staged selector — GREEN, BUT FULL-MEASURE PRESERVATION GAP DISCOVERED
- `modal/v144_rhythm_staged_selector.py` commit `68575a4c0d68f54392703a038bf909619a708177`.
- CPU gate run `32935390792` SUCCESS.
- Fit ranking cannot read validation/canary. Exactly one fit winner locks. Validation and canary are pass/fail only; failure returns to `no-prune` with no alternate selection.
- Existing fixed split gate: fit pitch gain >= `0.005`; no split musical metric regression; no split critical mismatch increase; exact PDF-event fidelity `1.0`.
- **Protocol gap now proven:** split metrics did not include/reference-free enforce preservation of the baseline generated measure set. Therefore a candidate could pass fit/validation/canary while deleting the last generated note from an entire measure. This must be fixed before another candidate search is trusted.

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

## Conjunction candidate — SPLIT-PASSED, FULL-INVARIANT REJECTED
- CPU search workflow `.github/workflows/v144-conjunction-prune-search.yml` commit `58ab544917d172a9cac1fc41b53b9af421e57a0b`; run `32936171588` SUCCESS.
- Split report bot commit `b6f2f9213ac38bf70c568bdf78ec769f24fff46d`; report blob `b92a3638d5b8fff0e911df43fb381f89f088afd6` at `debug/v144-rhythm-calibration/candidates/conjunction-prune-search.json`.
- Split locked candidate `prune-conjunction-33ac980932c68313`, rule `register::high && section16::1`.
- Fit FP precision `1.0`, support `62/62`; 97 total events removed; resulting stream 1112 events, SHA256 `db5c8e8fbbb767c386f14a00df188c89738230694840c48bed1bae32b2653b4f`.
- Split fit deltas: pitch `+0.007662208127669379`; pitch/timing `+0.0022198920743714892`; string/fret/timing `+0.0015856371959796466`; chord/voicing `+0.001207593648753582`; critical `-62`.
- Split validation PASSED: pitch `+0.0030118213989910325`; pitch/timing `+0.0013176718620585698`; string/fret/timing `+0.0007529553497477581`; chord/voicing `+0.0005221737346611452`; critical `-10`.
- Split canary PASSED: pitch `+0.009969512587313628`; pitch/timing `+0.0019295830814155396`; string/fret/timing `+0.0016079859011796163`; chord/voicing `+0.0010555262353823518`; critical `-25`.
- Independent locked-stream PDF/event fidelity proof PASSED at `1.0`, exact candidate SHA, reference not opened during fidelity proof.
- **Do not treat the split `promotionAllowed=true` field as current promotion authority. It is superseded by the full-gold invariant result below.**

## Full-gold selected-candidate invariant — FAILED / CANDIDATE REJECTED
- Added full-score script `validation/v144_rhythm_calibration/score_selected_conjunction_candidate.py` in commit `f76635d1db58d5ed11a018c5ee461c566bb983ae`.
- Added full-score workflow `.github/workflows/v144-selected-candidate-full-calibration.yml` in commit `4c01deac45d8df47f5f1a94c516f37aa7f005da5`.
- First run `32936501819` successfully reconstructed/scored the candidate and independently proved PDF-event fidelity, but failed on an assertion that had assumed measure coverage remained `1.0`; no candidate artifacts were persisted by that failed run.
- Workflow was corrected without weakening the invariant in commit `89ac9806b324160dda7c5a331e6e336c969049ea`: it now records the full invariant result explicitly rather than assuming it passes.
- Corrected run `32936612852` = **SUCCESS** operationally and persisted the evaluated result in bot commit `e03d0d25a3c1e8ab8d68e51737e0abd84a920fb9`.
- Persisted spec: `debug/v144-rhythm-calibration/selected/selected-rhythm-candidate.json`, Git blob `904b3fe644d3ed11c0ff03a3d680b8c1718e2ebd`.
- Persisted full score: `debug/v144-rhythm-calibration/selected/selected-rhythm-full-gold-score.json`, Git blob `570d1d91410ac7452c5ed0d6f6ddd3c9ea6ecb4b`.
- Full candidate absolute metrics:
  - pitch-content F1 `0.293488824101069` (`+0.010426179089468135` vs V5 baseline)
  - pitch/timing F1 `0.04664723032069971` (`+0.0020996665155953026`)
  - string/fret/timing F1 `0.03206997084548104` (`+0.001443520729471761`)
  - chord pitch-set F1 `0.023826208829712685` (`+0.0010685113732200498`)
  - exact voicing F1 `0.023826208829712685` (`+0.0010685113732200498`)
  - PDF-event fidelity `1.0`, exact event/PDF SHA `db5c8e8fbbb767c386f14a00df188c89738230694840c48bed1bae32b2653b4f`.
- Full critical mismatches improved from `1875` to `1779` (`-96`): 972 gross unmatched generated + 806 gross unmatched reference + **1 missing reference measure**.
- **Measure coverage regressed from `1.0` to `0.9911504424778761`: generated measure count 112/113; missing measure is exactly `28`.**
- Full invariant therefore `passed=false`; `calibrationPromotionAllowed=false`; candidate spec says `splitSelectionSupersededByFullInvariant=true`.
- Candidate is **REJECTED as the V144 calibration baseline** despite its musical-score improvements and split passes.
- Do not repair this exact rule using knowledge that measure 28 was missing. Measure 28 is diagnostic evidence only; next candidate construction must remain fit/reference-free and satisfy a predeclared baseline-measure-preservation safety invariant.
- V5/main/Production remain unchanged; no Modal/L4/GPU used.

## Current interpretation
- Narrow conjunction pruning can improve musical precision substantially, but the current selector lacked a whole-stream structural invariant.
- The next selector version must reject any candidate whose full generated measure-ID set differs from the immutable baseline generated measure-ID set, computed **without the gold reference**. Since V5 already spans all 113 measures, preserving the baseline-generated measure set safely protects full measure coverage without using professional labels at runtime or during fit selection.
- Only after this reference-free measure-preservation gate is CPU-tested may a new candidate family be searched.
- Rendering/event identity remains exact; musical transcription is still far from near-100% quality.

## Unrelated workflow noise
- Pre-existing `.github/workflows/cleanup-tab-preview.yml` continues to fail on branch pushes. It is unrelated and untouched.

## Immediate next resume actions
1. Add `baselineGeneratedMeasureSetPreserved=true` (or equivalent) as a required staged-selector safety condition.
2. Compute that condition reference-free for each candidate by comparing the candidate full event-stream measure IDs to the immutable source candidate measure IDs before fit lock.
3. Add unit tests proving a candidate that drops a baseline-generated measure cannot lock even if all split musical metrics improve.
4. Update single-signature/conjunction search helper safety payloads and CPU gate tests/fixtures as required; keep all numeric thresholds unchanged.
5. Run the CPU gate and checkpoint the corrected selector protocol.
6. Only then define/run a new fit-only candidate family. Do not hand-edit the rejected `register::high && section16::1` rule based on the discovered missing measure.
7. Continue CPU/repository-only work; **no Modal/L4/GPU without fresh explicit authorization**.
