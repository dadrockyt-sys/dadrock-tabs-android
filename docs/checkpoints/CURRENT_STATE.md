# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-07 America/Toronto
Branch: `v143-contextual-prune-lobo`

Compact fresh-chat source of truth. Full prior detail remains in Git history.

## CURRENT USER GOAL

Review the new Songsterr-inspired pipeline and improve the `gomyway` score toward near-perfect quality. Work should be evidence-driven: improve the deterministic score and the musical/notation quality together, not merely cosmetic rendering.

Keep this checkpoint updated after each meaningful diagnosis/fix.

## SAFETY / AUTHORIZATION

The prior model-bearing evaluation budget is consumed. The current user request authorizes continued deterministic engineering toward a better `gomyway` score, but does **not** by itself require a new Rhythm/Lead/Bass model run, professional scorer, Modal/GPU inference, Production deployment/promotion, optimizer/training/threshold sweep, or manual workflow run.

Prefer source/history inspection, static/unit validation, CPU-only synthetic proofs, and deterministic compare work first.

**Do not touch Production.**

## FROZEN `gomyway` PRODUCT INVARIANTS — PRESERVE UNTIL EVIDENCE REQUIRES A CONTRACT CHANGE

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

The deterministic compare guard is the primary evaluator. The historical final candidate input that encoded 970 selected pitches -> 3 drops -> 967 rendered notes / 0 recovery was a workflow artifact and is not a currently committed file; do not pretend it can be reconstructed from source alone.

## RESUME NOTE — 2026-09-07

- Resumed directly on `v143-contextual-prune-lobo`. The actual pre-resume branch commit was `86c1bc7031c385830394ca1626713c0a15181d13` (`Add contextual lobo rules and snapping guard`). The previously recorded `5334ee0ad66c13202c28f269b1e79eb16d8fa923` is that commit's **tree SHA**, not its commit SHA.
- Re-read this checkpoint before making any behavior changes.
- Current task is the exact evaluator/report lookup and formula scrub described below; no score, product invariant, Production, model/GPU, or workflow state has been changed in this resumed session yet.
- Branch-current `validation/rhythm_holdout/score_rhythm_holdout.py` has been identified as an F1/gate-style holdout scorer with a ±0.50-step timing tolerance across pitch/timing/string-fret/chord/voicing/coverage/PDF checks. It does **not** define the named `note_count_quality` metric.
- Historical Gomyway grading/report evidence explicitly names `pitch_accuracy`, `onset_match`, `note_count_quality`, and `deterministic_score`, with underlying onset, onset+string, and pitch+onset match counts. Therefore the carried-forward **90.321% onset** / **69.004% note-count** values belong to a separate Gomyway compare/report layer, not the branch-current rhythm-holdout F1 scorer.
- Historical targeted correction-plan logic (commit `e35b481a3c6103846d10d486c325f1d8ac9da470`) compares events by exact `quantizedStep`, counts unresolved reference events and extras, and separately evaluates fret, duration, and techniques. This proves the older deterministic pipeline explicitly separated event-density/timing mismatch from notation-detail mismatch, but it is not yet the exact wrapper for the carried-forward percentages.
- Branch-current `analyzer/analyze_and_grade_gomyway_gpu_separator_stem_v1.py` was inspected and ruled out as the current product comparator: it is an older **949-event** GPU separator benchmark grader, uses professional-reference pitch tokens for downstream grading, and protects the 949-event candidate hash. It therefore cannot explain the current protected **967-note / 725-onset** product metrics.
- Exact Gomyway comparator formulas and mismatch counts are still being recovered from branch history/artifacts. Do **not** infer them from the percentages.
- No deterministic decoder patch has been made in this resumed session.

## CONTINUATION PROVENANCE TRACE — 2026-09-07

- Reconfirmed the active target is the exact **967-note** Gomyway compare/report layer behind **100% pitch / 90.321% onset / 69.004% note-count**, not a new architecture pass.
- Inspected the older autonomous rhythm-search evidence at commit `86566f75bbe5bf3f1ec4da75bac3a1f2b46702d5`; its score is a separate six-category composite (tuning/consensus/reference/decoder/stability/parity), so it is **not** the target comparator.
- Repository code-search evidence remembers historical `player/evaluate_candidate.js`, `player/scripts/candidate-score.js`, and `player/scripts/gomyway-17-113-sidecar-state.json`, including a legacy sidecar row with score `0.8306460590522214`, pitch accuracy `0.8182769835628637`, onset match `0.8658777120315582`, and note-count quality `0.8753117206982544`.
- The current branch, current `main`, and the surviving `v143-research-checkpoint-fetch` branch do **not** expose `player/evaluate_candidate.js`; the old short SHA `9336275` is also no longer directly resolvable through the current GitHub commit endpoint. Treat code-search snippets as provenance clues only, not as sufficient proof of the formula.
- Immutable historical scoring-core blob `ee62a86adc5f60119d00b5b57a25ee8f0b06f4fe` was recovered from the 17–113 provenance closure. It is an upstream fixed-count reranker/event-selector using set TP/FP/FN precision/recall/F1 logic and contains neither `note_count_quality` nor `deterministic_score`; it is therefore **not** the target 967-note product comparator.
- Persisted V143 schema evidence at commit `dc2c2ad843365a5c0d7efaecaebd5226722f594d` independently confirms the relevant baseline as **967 total events / 725 inherited base events**. Later V5 1209-event rescue work is a different candidate family and must not be mixed into this comparator trace.
- The repaired-timing candidate product remains addressable as immutable blob `20e7a583fcb96249636cc63b01cf9ae0044f2c62`, but the candidate payload itself contains no `pitch_accuracy`, `onset_match`, `note_count_quality`, or `deterministic_score` fields. The named percentages therefore come from a separate post-product report/compare layer.
- Checkpoint history now proves the exact **90.321% onset / 69.004% note-count** percentages first enter `docs/checkpoints/CURRENT_STATE.md` in commit `9b695365ae449fd70ec03fbb2e559ab424c54e3f` as **“Current product metrics carried forward”**. Its immediate parent `57a8ad3c8af87d110f4a3144450bf10d6b1fa2de` already freezes **725 / 970 / 967 / 3 drops / 0 recovery** but contains **no score percentages**. Commit `9b695365...` changes only the checkpoint, not evaluator/report code. Therefore the exact formulas were imported from evidence external to that checkpoint commit and must still be recovered from neighboring workflow/report history; do **not** derive formulas from the percentages.
- No production/decoder/model/GPU/workflow change was made while establishing these boundaries. Continue by tracing the workflow/report artifacts immediately preceding the `9b695365...` checkpoint transition before touching decoder behavior.

## FRESH CHAT HANDOFF — START HERE

Do **not** restart the Songsterr architecture review. The next chat should continue the evaluator provenance search from the exact point below.

### Immediate task A — recover the exact 967-note Gomyway comparator

Search branch files, commit history, checkpoints, reports, and persisted workflow evidence for the layer that reports all of these together:
- `pitch_accuracy = 100%`
- `onset_match = 90.321%`
- `note_count_quality = 69.004%`
- `deterministic_score`
- current candidate facts **725 attacks / 970 selected pitches / 967 rendered notes / 3 drops / 0 recovery**

High-priority branch files to inspect first because they are already present and closely tied to the V143 contextual-prune campaign:
- `analyzer/V143_CONTEXTUAL_PRUNE_RECOVERY_CHECKPOINT.md`
- `analyzer/V143_CONTEXTUAL_PRUNE_17_32_EVIDENCE_GAP_CHECKPOINT.md`
- `analyzer/V143_CONTEXTUAL_PRUNE_17_113_RESEARCH_CLOSURE_CHECKPOINT.md`
- `analyzer/WORKFLOW_RECOVERY_CHECKPOINT.md`
- any current or historical `gomyway` file with `compare`, `guard`, `grade`, `report`, `deterministic`, `candidate`, `reference`, or `correction` in its name or contents

Also search commit history by the exact metric names and exact numeric values, because default-branch code search can miss branch-specific or deleted historical files.

Do **not** treat these as the target comparator:
- `validation/rhythm_holdout/score_rhythm_holdout.py` — different F1/gate holdout evaluator
- `analyzer/analyze_and_grade_gomyway_gpu_separator_stem_v1.py` — older 949-event professional-reference GPU separator grader

The first checkpoint in the new chat should be made as soon as the exact formula source or a definitive provenance boundary is established.

### Immediate task B — write down formulas and raw counts before touching decoder behavior

Once the comparator/report is found, record the exact definitions and denominators for:
- pitch accuracy
- onset match
- note-count quality
- deterministic score

Then extract the underlying raw counts, not just percentages. Build a compact mismatch table covering:
- matched attacks/onsets
- missing attacks/onsets
- extra attacks/onsets
- timing misses outside tolerance
- matched notes/pitches
- missing notes/pitches
- extra notes/pitches
- simultaneous-note grouping/chord-cluster mismatches
- duplicated or split events
- duration/tie/rest-only differences
- measure-boundary differences
- any quantization/rhythm-spelling-only differences

Do **not** reverse-engineer counts from `90.321` or `69.004` unless the actual formula is independently found and verified.

### Immediate task C — decide whether the score loss is upstream or downstream

Make one evidence-backed classification:

1. **Upstream event-set problem** — wrong density, grouping, selection, alignment, duplicates/splits, missing/excess attacks.
   - First patch should target deterministic event selection/grouping/alignment.

2. **Downstream notation/timing-normalization problem** — event set is right but onset snapping, beat placement, ties/rests, or rhythm spelling causes compare loss.
   - First patch should target contextual onset-cluster decoding/rhythm spelling.

3. **Evaluator-contract limitation** — product is musically right but the metric penalizes representation choices that should not define quality.
   - Document the contract issue before changing either metric or decoder.

Do not implement fretboard/path improvements merely because they are musically desirable if they cannot move the diagnosed Gomyway metric.

### Immediate task D — patch exactly one highest-impact deterministic stage

Only after A–C are complete, make the smallest deterministic patch that directly targets the largest proven mismatch class.

Protect these invariants unless measured evidence explicitly justifies a deliberate revision:
- **100% pitch accuracy**
- **725 retained attacks**
- **970 selected pitches**
- **967 rendered notes**
- exactly **3 legal-voicing drops**
- **0 recovery**
- all **113 measures populated**
- D# standard + capo 2

Preferred Songsterr-inspired changes, in priority order only if supported by the mismatch evidence:
- contextual onset-cluster snapping using measure/beat position rather than independent nearest-grid rounding
- simultaneous-note grouping that preserves one attack for one musical chord/shape
- rhythm spelling aware of beat boundaries, ties, rests, syncopation, triplet consistency, and phrase continuity
- joint simultaneous-note string/fret optimization as playable shapes
- phrase-level fretboard path optimization instead of single-note greedy placement

### Immediate task E — deterministic regression proof

For the chosen patch, add or strengthen tests proving:
- exact MIDI pitch preservation
- no unintended event-count drift
- legal tuning/capo fretboard placement
- stable simultaneous-note grouping
- improvement in the exact diagnosed onset/note-count compare class
- no regression to async/runtime invariants

Allowed validation remains source inspection, unit/static tests, deterministic compare tests, CPU-only synthetic fixtures, and read-only historical/artifact inspection.

Do **not** dispatch model-bearing workflows, a professional scorer, Modal/GPU inference, optimizer/training/threshold sweeps, a manual real-audio canary, or Production actions merely to continue this investigation.

### Fresh-chat checkpoint cadence

Update `docs/checkpoints/CURRENT_STATE.md` immediately after each of these milestones:
1. exact comparator/formulas located or provenance boundary proven;
2. raw mismatch counts classified;
3. first deterministic patch committed;
4. deterministic regression results known.

## SONGSTERR-INSPIRED PIPELINE REVIEW — ACTIVE

Architecture/history already inspected on the current branch:

- `docs/checkpoints/SONGSTERR_ARCHITECTURE_GAP_INVENTORY_20260903.md`
- `d49f8fcebd3fe5f973562d2c1c403036dcbe8db7` — architecture gap inventory
- `d597e7bbf85a206b915e58ee2a62b60cfd0ed236` — dual-context implementation
- `a36235371441e2e1209335dd4017093a2aa0da7a` — role/tuning/capo conditioning
- `854b6eb572efec6dc145611395462cb41b0cc965` — conditioned shadow projection
- `ed776202b60ee410beb455db16ee820e260ff17b` — later hardening phase

The new architecture correctly separates:
1. **global song structure authority** — measure grid, section/harmony/chord trajectory;
2. **local note-carrier evidence** — pitches/onsets;
3. **conditioned decoding** — instrument role, tuning, capo, tablature grammar;
4. **late deterministic shadow/product comparison** — structure model has no product-scoring authority.

### High-leverage weaknesses already found

Inspection of `lib/aiTabConditionedShadowProjectionV1.mjs` and `lib/aiTabConditioningV1.mjs` showed:

- string/fret placement is still essentially **greedy from the previous single note**;
- simultaneous notes are not optimized as a joint playable chord/shape;
- there is no phrase-level fretboard-position optimization / beam/Viterbi path;
- timing is independently rounded to the **nearest fixed straight/triplet subdivision**;
- rhythm spelling does not yet reason about measure context, ties, rests, syncopation, or phrase consistency.

These are credible reasons a pitch-correct result can still look machine-generated. However, changing fingering/rhythm spelling alone may not improve the numeric **90.321% onset** or **69.004% note-count** scores if those metrics are driven by upstream event-set mismatch.

## ASYNC / RUNTIME NON-NEGOTIABLES

Async lifetime must remain:
- shared result/control TTL **1800s**
- orchestrator timeout **1200s**
- ownership margin **600s**

Endpoint exact blob must remain `169b4bb136eba742c3422a73ee5dd0174ca06c49` unless a deliberately authorized endpoint change is made later.

Real-audio canary remains manual `workflow_dispatch` only.

## PRESERVED VERIFIED EVIDENCE

Source-only sweep previously verified with no model/GPU/scorer/Production activity:

- `analyzer/v143_async_job_protocol.py`: `ASYNC_RESULT_TTL_SECONDS = 30 * 60` = 1800s.
- `app/api/analyze-audio-tab/route.js`: async-result fallback = 1800s.
- `analyzer/v143_modal_http_endpoint.py`: orchestrator timeout = 1200s and exact blob SHA `169b4bb136eba742c3422a73ee5dd0174ca06c49`.
- `.github/workflows/v143-ai-tab-real-audio-canary.yml`: `workflow_dispatch` only.
- persisted real-candidate PDF evidence at commit `2470225d9cb726e35a07459e29783997a3447699`: **967 source/projected events**, **113 unique measures**, **725 unique onsets**, `referenceFree: true`, `professionalReferenceUsed: false`, `modalInvoked: false`, `productionModified: false`.

Historical async crash-loop root cause remains closed: persisted run `34047990402` proved `worker.done` after 936.836s while old ownership TTL was 900s; runtime ownership is now 1800s with 600s margin over the 1200s orchestrator ceiling.

Key repair commits:
- `b55d9db517fe356b40600bae85ba98ead879aeb6` — shared async TTL 900 -> 1800
- `330a3d5dbde5bcc3e51eb577892c8d9643fcba58` — Next.js fallback 900 -> 1800
- `fd230ee2ad4c19ad4758bbc753f4d110233591ff` — stale async protocol gate aligned
- `c3c09c2d8e1c93f286d24e3c398922becaf8e8b8` — real-audio canary automatic push trigger removed
- `ab27ae3b95d6aa5942f2d456c3f29792c96ecc3b` — cleanup preview workflow converted to read-only verifier

## NON-NEGOTIABLES

- protect **100% pitch accuracy**
- preserve **725 / 970 / 967 / exactly 3 drops / 0 recovery** until evidence requires deliberate revision
- preserve **1800s / 1200s / 600s** async ownership
- real-audio canary remains **manual-only**
- no Production modification
- no accidental new Modal/GPU/model inference, professional scoring, optimizer/training, or threshold sweep
- keep `docs/checkpoints/CURRENT_STATE.md` updated often
