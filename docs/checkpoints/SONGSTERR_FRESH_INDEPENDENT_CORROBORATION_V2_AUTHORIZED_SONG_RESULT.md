# Songsterr Fresh — Independent Corroboration V2 Authorized-Song Result

Status: completed frozen research execution; **not admission authority**

Recorded: 2026-09-11 America/Toronto

Branch at execution: `songsterr-fresh-pipeline-v1`
Frozen source commit at execution: `a76ab8cebb47a2dd1cf78243f00e436470e32df3`
Policy C-S epoch: `87926671-e6e9-4cda-87ea-8f248a6dae93`
Evaluator contract: `songsterr-fresh-independent-pitch-corroboration-research-v2`

## Execution prerequisites satisfied

Before the authorized-song V2 run:
- the V2 evaluator and controlled-fixture manifest were frozen;
- focused controlled CI was green at 15/15 fixtures with the frozen 6 corroborated / 7 not corroborated / 2 insufficient distribution;
- non-promotion guards were green;
- a new Policy C-S Codespaces epoch was probed and enrolled on exact source commit `a76ab8cebb47a2dd1cf78243f00e436470e32df3` with a clean worktree;
- the epoch passed exactly three qualification canaries;
- qualification reported `surfaceQualifiedForCurrentBootSession=true`;
- `modelValidationComplete=false`, `customerEligibleEvents=0`, `mayAdvanceDelivery=false`, and duration authority unchanged;
- final session verification after qualification remained `CODESPACES_SESSION_AUTHORITY_VERIFIED`.

The qualified epoch remained on the same running Codespaces boot for the authorized-song V2 research run.

## Bound research inputs

The authorized-song V2 execution used the exact canary-3 isolated-guitar stem and duration-free evidence already bound by Policy C-S.

The fail-closed pre-run wrapper required, before invoking V2:
- clean Git worktree;
- exact source commit `a76ab8cebb47a2dd1cf78243f00e436470e32df3`;
- current Policy C-S verification;
- qualified epoch identity/session/source equality;
- three-canary qualification;
- exact canary-bound guitar-stem SHA-256 equality;
- exact canary-bound canonical evidence SHA-256 equality;
- exact event-count equality;
- evidence contract `songsterr-fresh-isolated-polyphonic-note-evidence-v1`;
- `referenceBlind=true`;
- `structureFrozen=true`;
- role `guitar`;
- every event remained duration-free (`sourceEnd=null`, `durationSeconds=null`).

The wrapper reached `AUTHORIZED_SONG_V2_RESEARCH_RUN_COMPLETE`, so all pre-run assertions and the post-run session verification completed without failing closed.

Canonical evidence SHA-256 observed during input binding:
- `03068378fda6e553af2e74cf8ee3e405ce0df860b6e4fd20c81b36b089f7ca2`

Research output path inside the historical Codespaces epoch:
- `/workspaces/.songsterr-fresh-session-authority/epochs/87926671-e6e9-4cda-87ea-8f248a6dae93/authorized-song-independent-corroboration-v2.json`

## Frozen V2 authorized-song result

Across exactly 1,140 preserved upstream events:
- `independently-corroborated-candidate`: **187**
- `not-independently-corroborated`: **951**
- `insufficient-evidence`: **2**

The V2 result itself reported:
- `eventCount = 1140`
- policy status `INDEPENDENT_CORROBORATION_V2_RESEARCH_ONLY`
- `admissionDecisionMade=false`
- `modelValidationComplete=false`
- `customerEligibleEvents=0`
- `mayAdvanceDelivery=false`
- `durationAuthorityChanged=false`

No reference tab, professional scorer, archived V143 scorer, GOAT research, Basic Pitch activation/decision-surface acceptance, generic next-onset duration, or same-pitch-reattack duration logic was authorized by this run.

## Interpretation boundary

This is a frozen research observation, not proof of model correctness and not customer admission authority.

The aggregate 187/951/2 distribution must not be converted into a fitted threshold, confidence prior, tuning target, or post-hoc promotion rule.

The previously known MIDI-55 (~46.2024095 s) and MIDI-64 (~79.6261406 s) cases may now be inspected only as retrospective stress diagnostics. They may not change V2 under this preregistration.

A separate explicit V2 policy review is required before any promotion decision.

Until that review independently establishes a justified admission contract:
- `modelValidationComplete:false`
- customer-eligible events: `0`
- `mayAdvanceDelivery:false`
- duration authority unchanged
- duration research remains paused

## Epoch status after recording

The execution epoch was valid for the completed frozen run on source commit `a76ab8cebb47a2dd1cf78243f00e436470e32df3`.

Any subsequent repository commit changes the source binding and therefore makes this epoch historical-only for future execution. Do not reuse it as authority for another model run.
