# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-27 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V152 = COMPLETE / SEALED. V153 = NOT STARTED / NOT AUTHORIZED. Historical V147 Phase C real-audio execution = GO / COMPLETE / SEALED and MUST NOT be rerun.**

## Preserved prior checkpoint
- The complete pre-update checkpoint is preserved byte-for-byte at `docs/checkpoints/archive/CURRENT_STATE-pre-phase-c-auth-intake-20260827.md`.
- Preserved checkpoint Git blob: `f71ba11394e6f2f46843055e748e8717ff484158`.
- Verified live branch head before this checkpoint update: `bc4c3d6e961e1ac0a194bce33d0089e3575b7b31` (`docs: dedupe V152 fresh-chat handoff [skip ci]`).
- The preserved checkpoint remains the authoritative detailed history for V147–V152 identities, workflows, scores, recovery notes, and safety records. This file is the compact current-state handoff.

## User authorization intake — Phase C real-audio request
- Fresh user instruction received: **`Authorize Phase C real-audio execution`**.
- The only Phase C in the current checkpoint explicitly described as **real-audio execution** is historical **V147 Phase C**.
- V147 Phase C real-audio execution already completed successfully in GitHub Actions run `33038518285`, job `98406611428`, and its one-use workflow was deleted/sealed at commit `4b125f42dfa447e1fe86741c8f41c09dcaffc895`.
- Immutable V147 real-audio candidate canonical event SHA256: `ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77`.
- Durable replay preservation is already complete at `debug/v147-phase-c-real-audio/preserved-run-33038518285/`; preservation manifest blob `9f67507b448eb3a36f6e5d2d96572af425c42cb5`.
- Therefore this fresh authorization **cannot reopen, duplicate, rerun, or recreate** the consumed one-use V147 Phase C real-audio execution.
- This authorization also **cannot be silently repurposed** as authorization for V153 Phase A, a V153 candidate, another Gold score, another audio/CQT computation, Modal/L4/GPU work, or Production integration.
- Result of this authorization intake: **NO EXECUTION PERFORMED; SEALED PHASE PRESERVED.**

## Best sealed experimental result — V152
- V152 candidate canonical event SHA256: `5ebedfb173730bb5e2639e7450841fb113f7db9af2acec19b88e58cca50679e6`.
- Candidate file SHA256: `9b15ab3aa9540438db0750bb11c592a686e87b00b3acba491c80791badd349cb`.
- Changed event indices: `[132, 347, 457]`.
- Structure: `1144` events / `113` measures / exactly `3` changed singleton events / `3` changed onsets / `0` polyphonic changes / PDF fidelity `100%`.
- V152 Gold-calibration percentages (pitch content / pitch timing / string-fret timing / chord pitch-set / measure coverage / PDF fidelity): **35.311 / 6.699 / 5.455 / 5.805 / 100.000 / 100.000**.
- Accepted baseline percentages: **35.407 / 6.699 / 5.455 / 5.805 / 100.000 / 100.000**.
- V152 critical mismatches: `1712`; accepted baseline critical mismatches: `1712`.
- V152 therefore ties the accepted baseline on critical mismatches and on all displayed metrics except pitch content, where it trails by about `0.096` percentage points.
- Durable V152 score result: `debug/v152-active-recurrence/phase-c-score/score-result.json`; SHA256 `cc549c6f0a33c0b90648433494ef36a31b5647191058e28b9ea089f12cab7ef4`; score run `33050114109`.
- V152 construction and scoring authorizations are consumed/sealed. **Do not rescore V152.**

## Current next scientific boundary — V153 Phase A
- V153 has not started. No V153 preregistration, analyzer, candidate, Gold read, or score is currently authorized.
- The next recommended phase is a **reference-free deterministic strength ranking** over exactly the three immutable V152 edits `[132, 347, 457]`.
- Freeze the ranking rule before calculation. Preferred rule remains transparent lexicographic ordering using only already-preserved reference-free evidence: exact-pitch recurrence support delta, pitch-class recurrence support delta, two-sided immediate-neighbor voice-leading improvement magnitude, then frozen V149/V147 evidence-margin strength only as a deterministic final tie-breaker.
- No threshold sweep, weight tuning, alternate rule, post-result rule change, Gold/reference inspection, prior per-event correctness inspection, audio reread, HPSS/CQT recomputation, Modal/L4/GPU, candidate search, or Production modification.
- If the frozen rule does not produce a unique strongest event, fail closed and stop.
- If it produces a unique strongest event, candidate construction remains a **separate fresh authorization boundary**. A future one-use Gold score remains another separate authorization boundary after candidate persistence/seal.

## Fixed safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge/promote `main` or Production.
- `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` remain untouched.
- Do not rerun any consumed V147–V152 one-use workflow.
- No candidate variants/search, threshold/weight/filter retuning, automatic promotion, or post-result tuning.
- No Gold/reference/professional-image access unless a newly frozen reference-facing phase is explicitly authorized.
- No audio reread/decode, HPSS/CQT recomputation, Modal/L4/GPU unless a newly frozen real-audio/GPU phase is explicitly authorized.

## Authoritative stop point
- Historical V147 Phase C real-audio execution: **COMPLETE / SEALED; fresh request does not reopen it**.
- V152: **COMPLETE / SEALED; best current experimental result**.
- V153 Phase A reference-free ranking: **NOT STARTED / NOT AUTHORIZED**.
- New audio execution: **NO**.
- New Gold/reference read: **NO**.
- New score call: **NO**.
- New candidate construction: **NO**.
- Modal/L4/GPU: **NO**.
- Main/Production modification: **NO**.
- Next executable action requires fresh explicit authorization specifically for **V153 Phase A reference-free strength ranking**.