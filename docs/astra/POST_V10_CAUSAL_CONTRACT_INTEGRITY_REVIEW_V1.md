# Post-V10 causal and contract-integrity review V1

Date: 2026-09-29 UTC  
Status: **DOCUMENTATION/REVIEW ONLY — NO NEW PROJECT OPENED**

This review obeys the current generic-continue boundary: no new model project is opened, no waveform is rendered, no optimizer step is taken, and no inference is run.

## Executive finding

V9 and V10 produced useful evidence, but the next decision should not be another broad synthetic package change.

Two important review findings narrow what can safely be concluded:

1. **The executed V9 implementation does not fully match one explicit frozen-contract requirement for legato state semantics.**
2. **V10 did not isolate “attacked-note-label exposure” as cleanly as its title suggests, because matching label count was achieved by changing which positive-onset frames were sampled; in this corpus, three-label positive frames are chord attacks, so the intervention also changes positive-onset family/content mixture.**

The recorded numeric results remain valid observations of the code that actually ran. What must be narrowed is the causal interpretation.

## 1. V9 contract/implementation discrepancy: legato continuation

The frozen V9 contract says:

> For legato, attacked acoustic groups are measured as attack groups; any non-attacked continuation remains a state-label event and is not counted as a new acoustic attack group.

The retained S0 source defines legato as:
- attacked event from 0.28 to 0.78 s;
- non-attacked soft continuation from 0.78 to 1.52 s.

However, `astra_backend/synthetic/v9_empirical_v1.py` constructs V9 positive templates by first filtering prototypes to:

`base_t["segments"] if x.get("attack", True)`

and then creates V9 rows only from those attacked prototypes. No path re-adds the original non-attacked legato continuation.

Therefore the actually executed V9/V10 4-second corpus **drops the S0 non-attacked legato continuation** instead of preserving it as required by the frozen prose contract.

### Consequence

Do not describe V9 as an exact execution of every family-state semantic in `FALLBACK_FREE_CURRICULUM_V9_FINAL_CONTRACT_V1`.

The timing gate is still valid for the generated attack groups, and the empirical metrics are valid measurements of the executed dataset. But the package identity should be described as:

- frozen V9 attack timing/count package;
- S0-derived attacked-note content;
- **implemented V9 state semantics, with the original non-attacked legato continuation omitted.**

This discrepancy is especially relevant because the failure being investigated is a precision/state-onset generalization failure.

## 2. V10 causal-isolation limitation

V10 kept the same:
- V9 dataset arrays;
- nonlinear S6 model;
- initialization;
- losses;
- thresholds;
- optimizer;
- 500 updates/model;
- 16,000 positive-onset frame slots;
- non-positive stratum selections;
- per-step shuffle.

It changed positive-onset frame selection so total attacked-note labels rose from 17,676 to 19,702.

The intervention required:
- 1,851 three-label positive frames;
- 14,149 one-label positive frames.

In this synthetic construction, simultaneous three-label attacked frames are the chord attacks. Thus exact label-count matching necessarily increases the sampled chord-onset share.

So V10 changed two linked quantities:
- attacked-note-label count;
- positive-onset content/family composition.

### Consequence

The strongest supported V10 conclusion is:

> The specific chord-enriched positive-onset resampling scheme that exactly matched attacked-note-label count did not materially recover the V9 common-population precision/F1 loss.

A broader statement that “attacked-note-label exposure itself is disproven as a cause” is too strong.

The result still makes a large simple exposure explanation less plausible, because the intervention raised label count by 11.46% and recovered only +0.0242 precision and +0.0033 F1 on the primary population. But it is not a perfectly isolated causal test of positive-label gradient mass.

## 3. Cross-population evidence points to a distribution mismatch

Frozen V9/V10 control performance:

Common 2-second comparator test:
- precision 0.324427
- recall 0.658915
- F1 0.434783

V9 4-second test:
- precision 0.486631
- recall 0.705426
- F1 0.575949

The same V9 control model performs materially better on the V9-domain test than on the old comparator-domain test:
- precision difference: **+0.162204**
- recall difference: **+0.046512**
- F1 difference: **+0.141167**

This is consistent with a synthetic-domain distribution shift between the old 2-second content package and the implemented V9 4-second package.

It does **not** identify which component caused that shift.

## 4. Source-level state-duration changes remain a major unresolved difference

Historical S0 family-state durations include:
- isolated: about **1.03 s**
- scales: **0.27 s**
- chords: **0.48 s**
- repeated: about **0.31 s**
- legato attacked state: **0.50 s**, followed by a **0.74 s non-attacked continuation**
- palmmute: **0.16 s**
- mixed-positive: about **0.86 s**

V9 instead gives each attacked note a deterministic sustain drawn from **0.12–0.48 s**, and, as noted above, omits the non-attacked legato continuation.

Thus V9 did not only alter onset timing/count. It also substantially changed state-duration geometry:
- long isolated/mixed states are shortened;
- family-specific fixed durations are replaced by one common support;
- legato continuation semantics are removed;
- active/non-onset context around attacks is changed.

Given the model uses local five-frame input context and a joint state/onset objective, these state-duration changes are a plausible unresolved mechanism for the common-population precision collapse.

“Plausible” is not a causal conclusion.

## 5. Cleanest next scientific question, if the user later opens a new project

Do **not** automatically create V11.

The cleanest next one-variable question is not another timing redesign. It is:

> With the executed V9 timing, attack groups, note identities, rendered timbre process, model, sampler, thresholds and optimizer fixed, does restoring historical family-specific **state-duration / legato-continuation semantics** materially recover common-population precision/F1?

Why this is cleaner:
- V9 already demonstrated the new attack timing can satisfy the common-unit timing target;
- V10 showed chord-enriched exposure matching is not a large rescue;
- state geometry is both materially changed and directly involved in the state/onset objective;
- there is a documented V9 contract/implementation discrepancy in this exact area.

A future contract would need to choose one exact state-semantics intervention before any new generation:
- preserve V9 attack times/counts;
- restore per-family S0 sustain durations where feasible;
- restore legato non-attacked continuation explicitly;
- specify how state durations are handled when the next attack arrives sooner than historical duration;
- forbid clipping/overlap repair unless prospectively defined;
- freeze one arm only;
- preserve the same timing manifest rather than regenerating/searching timing;
- use the same fixed common 2-second population as primary synthetic sanity.

No empirical work for this question is authorized by this review.

## 6. Alternative smaller diagnostic

If the goal is specifically to revisit label exposure without changing chord-family sampling, a cleaner intervention would keep the **exact frozen V9 batch indices** and alter only positive-onset loss mass prospectively—for example, a single preregistered multiplicative correction derived from 19,702 / 17,676.

That would test positive-label gradient mass without selecting more chord frames.

However, it would change the loss function and would therefore be a new experiment, not a correction to V10. It is secondary to resolving the state-semantics discrepancy.

## 7. Evidence status after review

Preserve as established:
- V9 common-unit timing construction passed its timing gate.
- The executed V9 package failed synthetic sanity badly on common-population precision/F1.
- V10 exactly reproduced that V9 failure.
- V10 chord-enriched label-count matching did not materially recover it.
- V2B was correctly blocked throughout.
- No threshold search or scientific retry occurred.

Add as newly established by source review:
- the V9 implementation omitted the historical non-attacked legato continuation despite the final contract saying it should remain;
- V10 exposure matching changed chord-onset sampling composition as well as attacked-label count.

Remain unknown:
- whether state-duration/continuation semantics explain a material fraction of the V9 failure;
- whether pure positive-label loss-mass equalization would help;
- whether any corrected synthetic package improves real V2B transfer.

## Stop boundary

No new project number is opened by this review.

Do not:
- rerun V9 or V10;
- run V2B;
- silently repair V9 and call it the same experiment;
- create or execute V11 without a new prospective contract and explicit authorization;
- access V1.1/P1/P2/P3/A2;
- mutate main or Production.

At the next explicit project authorization, the preferred design topic is **state-duration / legato-continuation semantics under the already successful V9 attack-timing manifest**.
