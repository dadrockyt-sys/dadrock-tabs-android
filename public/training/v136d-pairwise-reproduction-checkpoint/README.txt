DADROCK RHYTHM JIMMY — V136D CORRECTED PAIRWISE EVALUATION CHECKPOINT

Authoritative champion:
V134 = 311/320 = 97.1875%

Corrected V134 reproduction:
311/320
Historical-artifact pass mismatches: 0

Correction required to reproduce authentic V134:
1. Use the V134 pairwise evaluator/model family:
   v124.v2.fit_pairwise_ranker(...)
   v124.v2.scores_for(...)
   v124.v17.pass_at_q(...)

2. Excluded safe-broad ordinary full_phase carriers must fall back to
   ANCHOR_Q, matching authentic V134 behavior.

Frozen V136D sustain candidate:
15 sustain-envelope interactions
tuningAfterFreezeAllowed = false

Valid corrected evaluation:
Current reproducible baseline: 311/320
V136D fixed interactions: 305/320
Gains/losses vs baseline: +0/-6
Net: -6

Decision:
V136D REJECTED.
V134 remains Rhythm Jimmy champion.

Scientific safeguards:
- Protected 949-event candidate unchanged.
- No post-freeze hyperparameter tuning.
- Professional/midterm answers were not used.
- 11-mod-16-over-1024 untouched reserve was NOT inspected.
- The six V136D evaluation losses must NOT be used to tune a replacement candidate.
- No production promotion.

Historical note:
The earlier 285 -> 287 V136D result used the wrong ridge evaluator/model
family and is not valid for comparison with V134.

Next development step:
Design a fresh sustain candidate using legitimate development/training
material only. Freeze it before evaluation. Prefer improvement that
preserves all 311 V134 passes and recovers at least one remaining failure.
