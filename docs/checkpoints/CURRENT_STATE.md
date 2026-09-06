# CURRENT STATE — DadRock `/ai-tab` V143

Updated: 2026-09-06 20:xx America/Toronto
Branch: `v143-contextual-prune-lobo`
Branch head observed during continuation: `d3c38ce10f1af0551d20a02ad2a0dc93e750ec23`
Previous full-detail checkpoint blob: `00bbec5b9a3465db35659f73e957c600c8b985bb` (retained in Git history; use it for the long-form run/artifact record if needed)

## NON-NEGOTIABLE AUTHORIZATION / BUDGET BOUNDARY

The one authorized replacement V143 Rhythm model-bearing start has been consumed.
The one authorized professional full-1–113 score has been consumed.

Current counters:
- replacement live model start: **0 available / 1 consumed**
- professional full-1–113 score: **0 available / 1 consumed**
- replacement PDF E2E: **1 performed / passed**

**DO NOT** start another Rhythm/Lead/Bass model-bearing analysis and **DO NOT** run the professional scorer again without new explicit user authorization.
Also do not deploy/promote production, weaken Deployment Protection, run optimizer/training/threshold sweeps, or mutate model/scheduler parameters as part of evaluation.

Safe work now is deterministic/model-free source analysis, repair, static validation, and read-only evidence inspection.

## IMMUTABLE RECOVERED RUN / FROZEN RESULT

Exact authorized Rhythm run:
- workflow `.github/workflows/v143-one-shot-final-rhythm-e2e.yml`
- run `34046854397`
- job `101523324268`
- one start accepted around `2026-09-06T16:54:33Z`
- polls 1–130 returned 202
- poll 131 returned 502 at ~908 s

Exact worker evidence:
- worker Function ID `fu-cXv3G2TXumycjiCTABviS7`
- worker FunctionCall `fc-01M1VT9BDS5TYWE52GPYQQ8W9E`
- parent orchestrator FunctionCall `fc-01M1VT98JAEX2NZ83DSM5GJQ8A`
- worker completed successfully at `elapsed=936.836`
- worker completed about 29 seconds after the client-side 900-second tracking record expired

Same-run recovery succeeded read-only:
- recovery run `34048291636`
- job `101527199470`
- job ID `K7aeTJDV7fp7l5R5UwsOvJkrC_mCDQt0`
- recovered worker-result SHA-256 `185a19dcd58df7bece23a75b300bb3f9fbf6d6322bf61b52b1e667b5ba684293`

Frozen product facts:
- E Standard
- ~129.199 BPM
- 4/4
- raw events: **925**
- canonical render events: **925**
- frozen events: **925**
- frozen canonical event SHA-256 `f5b526e608fc552925b252ecdbf7d0a6e918b04f423374798d2772939af3e2af`
- playable string/fret 925/925
- musical placement 925/925
- pitch validity 925/925
- render survival 100%
- PDF event fidelity **1.0**

## PROFESSIONAL HOLDOUT — CONSUMED, DO NOT RERUN

Scoring run:
- workflow `.github/workflows/v143-score-recovered-frozen-result.yml`
- run `34048719525`
- job `101528345557`
- authoritative result file `rhythm-professional-holdout-score.json`

Result:
- `near100ProfessionalGatePassed = false`
- `rhythmComplete = false`
- `criticalMismatchCount = 1581`
- measure coverage recall: `0.9823008849557522`
- pitch-content F1: `0.30892570817744525`
- pitch-timing tolerant F1: `0.05879208979155532`
- string/fret timing tolerant F1: `0.02672367717797969`
- chord pitch-set tolerant F1: `0.004136504653567736`
- exact voicing tolerant F1: `0.004136504653567736`
- PDF event fidelity: `1.0`
- missing professional measures: `88, 99`
- extra generated measures: `114, 115`
- gross unmatched generated notes: `779`
- gross unmatched reference notes: `800`

Interpretation: infrastructure/render fidelity succeeded; the frozen musical event stream did not. Primary engineering problem is musical structure—pitch/timing agreement, chord grouping and voicing—not PDF plumbing.

## CONFIRMED ASYNC DEFECT

Evidence says the parent control/result tracking lifetime is **900 seconds** while worker/orchestrator runtime budget is **1200 seconds**.
Observed worker completion at 936.836 s is consistent with the client losing ownership/tracking before the successful worker result became available.

Important: older checkpoint prose names `ASYNC_RESULT_TTL_SECONDS = 900`, but branch searches have not yet safely located a literal source symbol with that exact name. **Do not patch a guessed constant.** Find the exact ownership/control-state implementation first, then extend only that lifetime comfortably beyond 1200 seconds while preserving cleanup/runtime semantics.

Known async path inspected:
- `app/api/analyze-audio-tab/route.js`
- `.github/scripts/patch_v143_async_ai_tab_ui.py`
- Modal analyzer/job-token handoff path

## MODEL-FREE TIMING REPAIR

The timing repair was already committed before this continuation (checkpoint-era commit `f387377b538342f284e03b617ce6f4f13e31e6b0`). Preserve it.
Later branch evidence/debug commits must also be preserved; do not reset/rebase over them.

### Verified continuation finding

`analyzer/v143_reference_free_timing.py` is **not** the note/score-construction layer. It estimates timing structure (beat grid/bar phase and related candidate timing context) and exposes adapter data such as `candidate_adapter_kwargs()`. It does not itself construct the final note stream, assign the final score, or perform the target polyphony/voicing decisions.

Therefore the next engineering target is the **consumer downstream of this module**: locate where the returned timing/adaptation data enters the post-model event pipeline, then identify the exact grouping/string-fret/voicing/export hook there.

Do not modify the timing estimator merely to force chord/polyphony behavior unless the downstream trace proves the timing module is actually responsible for the defect.

## V143 PRODUCT TARGET — SELF-CORRECTING TAB, NOT A DRAFT

User wants V143 pushed beyond a Songsterr-style AI draft toward a generator that does not require human correction. Treat this as an engineering target, not a marketing claim until a broad validation corpus proves it.

Deterministic post-model design rules:
1. **Preserve polyphony.** Do not collapse compatible dyads, power chords, full chords, ringing notes, or overlapping voices just because one candidate has lower confidence.
2. **Prune contradictions, not complexity.** Contextual pruning removes mutually impossible evidence; it should not default to winner-take-all monophony.
3. **Separate confidence from feasibility.** A slightly lower-confidence note may be retained when it completes a musically/physically coherent voicing.
4. **Self-check before export.** Validate timing/grid, bar count, pickup/meter, tuning, string/fret reachability, duplicate-string collisions, simultaneous-note feasibility, durations/sustain, chord integrity, and event ordering.
5. **Correct deterministic defects when unambiguous; otherwise retain diagnostics instead of silently deleting evidence.**
6. Preserve musical context as first-class data: BPM, meter, pickup, tuning, role/instrument, onset grouping, sustain/voice relationships.
7. Do not tune the professional reference/scorer thresholds to manufacture a pass.

## FRESH-CHAT HANDOFF — EXACT NEXT STEPS

Start here in a new chat. Do **not** repeat the expensive validation work.

1. Read this file first and stay on branch `v143-contextual-prune-lobo`.
2. Reconfirm the branch head and preserve all existing V143 commits; no reset/rebase over checkpoint/debug evidence.
3. Trace every branch-specific import/call/use of `analyzer/v143_reference_free_timing.py`, especially `candidate_adapter_kwargs()`, using branch-aware file reads rather than default-branch code search when necessary.
4. Identify the first downstream function that receives model candidates + reference-free timing context and produces canonical/post-model note events.
5. From that function, trace the exact code responsible for:
   - onset/simultaneous-note grouping,
   - candidate pruning,
   - pitch retention,
   - string/fret assignment,
   - chord/voicing construction,
   - duration/sustain overlap handling,
   - final canonical event ordering/export.
6. Check for any winner-take-all, top-1, nearest-only, confidence-only, same-onset dedupe, same-string overwrite, or “one note per frame/onset” logic that could be collapsing valid polyphony.
7. Implement the **smallest deterministic post-model repair** at the narrowest confirmed hook:
   - retain compatible simultaneous/overlapping notes,
   - prune only physically/musically contradictory candidates,
   - avoid duplicate-string collisions inside one chord unless sequential/voice logic clearly allows it,
   - preserve lower-confidence notes when they complete a feasible voicing,
   - do not use the professional reference at runtime.
8. Add a deterministic pre-export structural validator/diagnostic layer checking at minimum:
   - sorted event times,
   - nonnegative/valid durations,
   - bar/beat/grid consistency,
   - tuning-aware pitch ↔ string/fret consistency,
   - fret reachability,
   - duplicate-string simultaneous collisions,
   - impossible simultaneous voicings,
   - chord grouping integrity,
   - sustain/overlap coherence,
   - measure-count/pickup anomalies.
9. Prefer diagnostics over deletion when a deterministic correction is not unambiguous.
10. Run **only** model-free static/unit tests or pure functions that cannot initialize the model. Do not trigger Rhythm/Lead/Bass inference indirectly through imports.
11. Save `docs/checkpoints/CURRENT_STATE.md` again immediately after the downstream hook is found, and again after any source change + validation result. Include exact file paths and commit/blob SHAs.
12. After score-structure work, locate the **actual** 900-second async ownership/control-state TTL source. Change only the ownership/result retention lifetime so it safely exceeds the 1200-second worker/orchestrator budget; do not guess a constant and do not change the 1200-second compute budget.
13. Diagnose the user-observed Modal “reporting function crash-looping” read-only unless a deterministic source-level fix is clearly proven.
14. Before **any** new model-bearing run or professional scorer invocation, explain exactly what would run and obtain fresh explicit user authorization.

## CONTINUATION STATUS — SAVED FOR FRESH CHAT

No new model-bearing run or professional scorer run was executed during this continuation.
No live/scorer evaluation budget was consumed.
No post-model analyzer repair was committed yet during this continuation because the downstream consumer/hook still needs to be located exactly.

The key newly verified fact is that `analyzer/v143_reference_free_timing.py` is a timing/context provider rather than the final score-construction layer. The fresh chat should continue by finding its exact downstream consumer and repairing polyphony/voicing there, not by changing the estimator blindly.

## CURRENT STATE

**The 925-event frozen V143 result proves the infrastructure/render path can preserve events exactly, but the consumed professional score proves the musical score construction is still far from the no-human-correction target. Continue deterministically downstream of `v143_reference_free_timing.py`: find the canonical event-construction hook, preserve valid polyphony, enforce coherent voicings, add structural self-validation, checkpoint frequently, and do not run another model/scorer without fresh authorization.**
