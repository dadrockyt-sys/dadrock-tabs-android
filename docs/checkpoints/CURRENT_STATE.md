# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-07 America/Toronto
Branch: `v143-contextual-prune-lobo`

Compact fresh-chat source of truth. Full prior detail remains in Git history.

## CURRENT USER GOAL

Improve the `gomyway` deterministic score toward near-perfect quality while preserving musical/notation quality and the frozen real-candidate invariants. Work remains evidence-driven: recover the exact comparator/formulas and raw mismatch counts first, classify the score loss, then patch only the highest-impact deterministic stage.

Keep this checkpoint updated after each meaningful provenance, diagnosis, fix, or regression milestone.

## SAFETY / AUTHORIZATION

The prior model-bearing evaluation budget is consumed. Current work is limited to source/history inspection, read-only GitHub Actions/artifact inspection, static/unit validation, CPU-only synthetic proofs, and deterministic compare work unless the user explicitly authorizes more.

**Do not touch Production.**

Do not dispatch a model-bearing workflow, professional scorer, Modal/GPU inference, optimizer/training/threshold sweep, manual real-audio canary, deployment, or promotion merely to continue this investigation.

## FROZEN `gomyway` PRODUCT INVARIANTS

Preserve until measured evidence explicitly requires a deliberate contract change:

- **725 retained attacks**
- **970 selected pitches**
- **967 rendered notes**
- exactly **3 legal-voicing drops**
- **0 recovery**
- all **113 measures** populated
- `referenceFree=true`
- `newInferenceUsed=false`
- tuning **D# standard**
- capo **2**

Exact drops:
- m40/s14 MIDI 78
- m63/s14 MIDI 47
- m113/s13 MIDI 43

Current product metrics carried forward:
- pitch accuracy **100%**
- onset match **90.321%**
- note-count quality **69.004%**
- tablature valid
- technique valid

These percentages are protected context, not reconstructed formulas. Do **not** infer denominators or mismatch counts from the rounded values.

## RESUME / COMPARATOR EXCLUSIONS

- Actual pre-resume behavior commit: `86c1bc7031c385830394ca1626713c0a15181d13` (`Add contextual lobo rules and snapping guard`). The old recorded `5334ee0...` is its tree SHA, not commit SHA.
- `validation/rhythm_holdout/score_rhythm_holdout.py` is a different F1/gate holdout scorer with ±0.50-step timing tolerance. It does not define `note_count_quality`.
- `analyzer/analyze_and_grade_gomyway_gpu_separator_stem_v1.py` is an older **949-event** professional-reference GPU separator grader. It is not the current 967-note comparator.
- Historical correction-plan commit `e35b481a3c6103846d10d486c325f1d8ac9da470` separates exact-`quantizedStep` unresolved refs/extras from fret/duration/technique mismatches, but is not yet proven to be the wrapper behind the carried percentages.
- Historical autonomous rhythm-search commit `86566f75bbe5bf3f1ec4da75bac3a1f2b46702d5` uses a different six-category composite score and is not the target comparator.
- Historical scoring-core blob `ee62a86adc5f60119d00b5b57a25ee8f0b06f4fe` is an upstream fixed-count event-selector/reranker using TP/FP/FN precision/recall/F1. The recovered 17–113 closure proves exact selected-event replay semantics; this blob contains neither `note_count_quality` nor `deterministic_score`, so it is not the target product comparator.
- Persisted schema evidence at `dc2c2ad843365a5c0d7efaecaebd5226722f594d` independently confirms the relevant **967 total / 725 inherited base** baseline. Later V5 **1209-event** rescue work is a different candidate family and must not be mixed into this trace.
- Repaired-timing candidate product blob `20e7a583fcb96249636cc63b01cf9ae0044f2c62` contains no `pitch_accuracy`, `onset_match`, `note_count_quality`, or `deterministic_score` fields. The named percentages come from a separate post-product report/compare layer.

## PROVENANCE TRACE — METRIC IMPORT BOUNDARY

Checkpoint history gives a hard boundary:

- `57a8ad3c8af87d110f4a3144450bf10d6b1fa2de` at **2026-09-08T02:05:23Z** already freezes **725 / 970 / 967 / 3 drops / 0 recovery** but contains **no** 100 / 90.321 / 69.004 score percentages.
- Its direct child `9b695365ae449fd70ec03fbb2e559ab424c54e3f` at **2026-09-08T02:23:10Z** changes only `docs/checkpoints/CURRENT_STATE.md` and introduces the values under the literal label **“Current product metrics carried forward.”**
- The interval is **17m47s** and there were **zero GitHub Actions runs on the target branch and zero Actions runs anywhere in the repository during that exact interval**.

Conclusion: `9b695365...` imported prior score evidence; it did not generate or define the formulas. Do not reverse-engineer the formulas from the checkpoint values. The absence of runs in the import interval does **not** prove the evidence was manual/external; an earlier workflow/report may still be the source.

Current default-branch code search has no exact `onset_match` or `note-count` source matches. Historical code-search clues remember `player/evaluate_candidate.js`, `player/scripts/candidate-score.js`, and `player/scripts/gomyway-17-113-sidecar-state.json`, including a legacy row with score `0.8306460590522214`, pitch `0.8182769835628637`, onset `0.8658777120315582`, note-count `0.8753117206982544`. However:

- the current branch, `main`, and surviving `v143-research-checkpoint-fetch` do not expose those evaluator paths;
- commit-history-by-path for those deleted `player/` files returns no reachable history;
- old short SHA `9336275` is not currently resolvable.

Treat those snippets only as provenance clues, not formula proof.

## FROZEN CANDIDATE RUN / ARTIFACT — AUTHORITATIVE DETAILS

Frozen candidate GitHub Actions run: **`32805316807`**.

Authoritative run/job metadata now reconciled:
- workflow name: **`V143 Repaired Timing Precision Candidate Product`**
- workflow path: `.github/workflows/v143-repaired-timing-precision-candidate-product.yml`
- head SHA: `74b0f815ff3f66f325220975c410621503de440f`
- head commit: `chore: dispatch authorized precision retry`
- event: `workflow_dispatch`
- started: **2026-08-25T03:28:39Z**
- completed: **2026-08-25T04:05:20Z**
- job: `candidate`

The head commit changes only `debug/v143-contextual-prune/paid-retry-dispatch-authorized.once`, adding `relay-condition-fixed=true`; it does not alter scoring/decoder code.

Run evidence reports:
- **984 input attacks -> 725 retained attacks**
- **7535 original pitch hypotheses -> 970 retained/selected pitches**
- **967 rendered pitches**
- exactly **3 voicing drops**
- **0 fail-safe attacks**
- `newInferenceUsed=false`

Persisted candidate commit: `c1451df43cc1162ed2b38aa3f3300b7af4d9b527`.

The run artifact is still available and was inspected read-only:
- artifact ID `9548666053`
- `v143-precision-v2-one-shot-32805316807`
- four files only:
  1. `precision-v2-one-shot-artifact-validation.json`
  2. `precision-v2-one-shot-policy-compare.json`
  3. `precision-v2-one-shot-candidate-plan.json`
  4. `precision-v2-one-shot-candidate-product.json`
- none contains `90.321`, `69.004`, `pitch_accuracy`, `onset_match`, `note_count_quality`, or `deterministic_score`.

Therefore the frozen candidate artifact is **not** the missing score report.

The preserved-PDF run **`32821330353`** materializes the immutable candidate CPU-only and renders **967 events / 725 unique onsets**. Its preserved evidence likewise does not provide the target metric trio. The target comparator is downstream/separate from candidate generation and PDF rendering.

## OTHER AUG. 25 HISTORY CHECKED

- Commits `a8527bda2e33919495dd8cae0908aa9bf1fc34aa` (`Checkpoint exact downstream source discovery`) and `d6cecb794b93a3bbb6883948789f9dbcdbf3ecd0` (`Checkpoint nested downstream evidence`) were inspected. They document technique/sustain/fingering replay evidence, not the 100 / 90.321 / 69.004 comparator. Do not mix their `score >= 0.99` professional-scorer context into this product-metric trace.
- Immediate post-candidate history around 04:05–06:00Z includes harmonic-shadow and bounded research-fetch work; no target formula has yet been recovered from that window.

No decoder, scoring contract, model, workflow dispatch, GPU job, professional scorer, Production state, or frozen product invariant was changed during this provenance investigation.

## NEXT TASK — EXACT COMPARATOR FIRST

Continue read-only history/artifact inspection for the layer that reports all of these together:
- `pitch_accuracy = 100%`
- `onset_match = 90.321%`
- `note_count_quality = 69.004%`
- `deterministic_score`
- the **725 / 970 / 967 / 3 drops / 0 recovery** candidate family

Best next search order:
1. historical workflow/report runs after candidate completion at **2026-08-25T04:05:20Z**;
2. V143 checkpoints/reports that mention professional/reference compare, candidate score, grade, guard, or correction-plan outputs;
3. historical workflow definitions around `74b0f815...` and subsequent commits for any report artifact or evaluator invocation;
4. retained artifacts/run logs that contain exact metric labels or raw mismatch counts.

Once the exact source is found, write down the formulas and raw counts for:
- matched/missing/extra onsets and timing misses outside tolerance;
- matched/missing/extra notes/pitches;
- simultaneous/chord grouping mismatches;
- duplicate/split events;
- duration/tie/rest-only differences;
- measure-boundary and quantization/rhythm-spelling-only differences.

Then classify the score loss as exactly one of:
1. **upstream event-set problem**;
2. **downstream notation/timing-normalization problem**;
3. **evaluator-contract limitation**.

Only after that classification should one smallest deterministic patch be made.

## SONGSTERR-INSPIRED ARCHITECTURE — DO NOT RESTART REVIEW

Already inspected:
- `docs/checkpoints/SONGSTERR_ARCHITECTURE_GAP_INVENTORY_20260903.md`
- `d49f8fcebd3fe5f973562d2c1c403036dcbe8db7`
- `d597e7bbf85a206b915e58ee2a62b60cfd0ed236`
- `a36235371441e2e1209335dd4017093a2aa0da7a`
- `854b6eb572efec6dc145611395462cb41b0cc965`
- `ed776202b60ee410beb455db16ee820e260ff17b`

Known deterministic weaknesses:
- greedy single-note string/fret placement;
- no joint simultaneous-note chord-shape optimization;
- no phrase-level fretboard path optimization;
- independent nearest-grid straight/triplet timing rounding;
- no measure-aware rhythm spelling, ties/rests/syncopation/phrase consistency.

These are plausible quality issues but must not be patched merely because they are musically desirable; the exact comparator mismatch class must first show which stage can move the protected Gomyway metric.

## ASYNC / RUNTIME NON-NEGOTIABLES

- shared result/control TTL **1800s**
- orchestrator timeout **1200s**
- ownership margin **600s**
- endpoint exact blob `169b4bb136eba742c3422a73ee5dd0174ca06c49`
- real-audio canary remains manual `workflow_dispatch` only

Preserved repair commits:
- `b55d9db517fe356b40600bae85ba98ead879aeb6` — shared async TTL 900 -> 1800
- `330a3d5dbde5bcc3e51eb577892c8d9643fcba58` — Next.js fallback 900 -> 1800
- `fd230ee2ad4c19ad4758bbc753f4d110233591ff` — stale async protocol gate aligned
- `c3c09c2d8e1c93f286d24e3c398922becaf8e8b8` — automatic real-audio canary push removed
- `ab27ae3b95d6aa5942f2d456c3f29792c96ecc3b` — cleanup preview converted to read-only verifier

## NON-NEGOTIABLES

- protect **100% pitch accuracy**
- preserve **725 / 970 / 967 / exactly 3 drops / 0 recovery** until measured evidence requires deliberate revision
- preserve **1800s / 1200s / 600s** async ownership
- real-audio canary stays **manual-only**
- no Production modification
- no accidental Modal/GPU/model inference, professional scoring, optimizer/training, or threshold sweep
- keep this checkpoint updated often
