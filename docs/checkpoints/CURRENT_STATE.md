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

- Resumed directly on `v143-contextual-prune-lobo` from branch HEAD `5334ee0ad66c13202c28f269b1e79eb16d8fa923` (`Add contextual lobo rules and snapping guard`).
- Re-read this checkpoint before making any behavior changes.
- Current task is the exact evaluator/report lookup and formula scrub described below; no score, product invariant, Production, model/GPU, or workflow state has been changed in this resumed session yet.
- Next evidence checkpoint will record the evaluator/report paths and formulas before any deterministic patch is attempted.

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

## EXACT NEXT STEPS FOR A FRESH CHAT

Resume directly from this section; do not restart architecture review.

### 1. Locate the exact branch-current deterministic evaluator/report

Find the code and persisted evidence that computes or reports:
- onset match **90.321%**
- note-count quality **69.004%**
- pitch accuracy **100%**

Search by metric names, numeric values, compare/guard/report terminology, and `gomyway` references. Do not rely only on default-branch GitHub code search if it misses branch-specific files; use branch contents/history as needed.

Goal: identify the exact formulas and the compared event sets before changing decoder behavior.

### 2. Break the score loss into concrete mismatch classes and counts

For `gomyway`, determine which penalties come from:
- missing attacks/events;
- extra attacks/events;
- onset timing displacement outside the evaluator tolerance;
- simultaneous-note grouping/chord clustering;
- duplicated/split notes;
- duration/tie/rest normalization;
- measure-boundary placement;
- deterministic quantization/rhythm spelling;
- any note-count denominator/normalization behavior.

Produce a mismatch table/count summary. The key decision is whether the score loss is **upstream event selection/alignment/grouping** or **downstream notation/quantization**.

### 3. Patch the highest-impact deterministic stage only

Decision fork:

- If penalties are upstream event density/alignment/grouping errors, improve deterministic selection/grouping/alignment first.
- If penalties are downstream timing/notation normalization errors, improve onset-cluster decoding and contextual rhythm spelling first.
- If numeric score is already limited by the evaluator contract rather than product quality, document that clearly before changing the metric.

Protect **100% pitch accuracy** and preserve **725 / 970 / 967 / exactly 3 drops / 0 recovery** unless measured evidence demonstrates a deliberate contract revision is necessary.

### 4. Preferred Songsterr-inspired deterministic improvements after the score-loss class is known

Highest-value decoder improvements currently identified:

- joint optimization of simultaneous-note string/fret assignments as playable chord shapes;
- phrase-level fretboard path optimization instead of single-note greedy placement;
- contextual onset-cluster snapping using measure/beat position rather than independent nearest-grid rounding;
- rhythm spelling aware of ties, rests, beat boundaries, syncopation, triplet consistency, and phrase continuity;
- penalties for implausible position jumps/string crossings while preserving exact MIDI pitch;
- deterministic section/phrase continuity priors from the global structure authority, with no product-scoring authority given to the structure model.

Do **not** implement all of these blindly. Use evaluator evidence to choose the first patch that can move the actual `gomyway` score.

### 5. Add deterministic regression coverage

For every patch, add or strengthen tests that prove:
- exact pitch preservation;
- no accidental event-count drift unless explicitly intended;
- legal tuning/capo fretboard placement;
- stable simultaneous-note grouping;
- improved onset/note-count compare behavior for the diagnosed failure class;
- no regression to the async/runtime safety invariants below.

### 6. Validation allowed now

Safe validation:
- source inspection;
- static/unit tests;
- deterministic compare tests;
- CPU-only synthetic fixtures;
- read-only history/artifact inspection.

Do **not** dispatch model-bearing workflows, professional scorer runs, Modal/GPU inference, optimizer/training/threshold sweeps, or Production actions without a new explicit reason/authorization.

### 7. Checkpoint cadence

Update `docs/checkpoints/CURRENT_STATE.md`:
- after the evaluator/formula is located;
- after mismatch classes/counts are known;
- after each meaningful patch;
- after deterministic validation results.

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
