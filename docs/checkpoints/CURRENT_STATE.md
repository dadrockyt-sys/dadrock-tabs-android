# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-27 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V153 Phase A REFERENCE-FREE STRENGTH RANKING = AUTHORIZED / FROZEN / STOP BEFORE EXECUTION. V152 remains COMPLETE / SEALED. Historical V147 Phase C real-audio execution remains COMPLETE / SEALED and MUST NOT be rerun.**

## Preserved prior checkpoint
- The complete pre-compaction historical checkpoint is preserved byte-for-byte at `docs/checkpoints/archive/CURRENT_STATE-pre-phase-c-auth-intake-20260827.md`.
- Preserved checkpoint Git blob: `f71ba11394e6f2f46843055e748e8717ff484158`.
- The archive remains the authoritative detailed history for V147–V152 identities, workflows, scores, recovery notes, and safety records. This file is the compact current-state handoff.

## Historical Phase C real-audio boundary
- V147 Phase C real-audio execution already completed successfully in GitHub Actions run `33038518285`, job `98406611428`, and its one-use workflow was deleted/sealed at commit `4b125f42dfa447e1fe86741c8f41c09dcaffc895`.
- Immutable V147 real-audio candidate canonical event SHA256: `ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77`.
- Durable replay preservation is complete at `debug/v147-phase-c-real-audio/preserved-run-33038518285/`; preservation manifest blob `9f67507b448eb3a36f6e5d2d96572af425c42cb5`.
- No fresh instruction may silently reopen or duplicate that consumed one-use execution.

## Best sealed experimental result — V152
- V152 candidate canonical event SHA256: `5ebedfb173730bb5e2639e7450841fb113f7db9af2acec19b88e58cca50679e6`.
- Candidate file SHA256: `9b15ab3aa9540438db0750bb11c592a686e87b00b3acba491c80791badd349cb`.
- Changed event indices: `[132, 347, 457]`.
- Structure: `1144` events / `113` measures / exactly `3` changed singleton events / `3` changed onsets / `0` polyphonic changes / PDF fidelity `100%`.
- V152 Gold-calibration percentages (pitch content / pitch timing / string-fret timing / chord pitch-set / measure coverage / PDF fidelity): **35.311 / 6.699 / 5.455 / 5.805 / 100.000 / 100.000**.
- Accepted baseline percentages: **35.407 / 6.699 / 5.455 / 5.805 / 100.000 / 100.000**.
- V152 critical mismatches: `1712`; accepted baseline critical mismatches: `1712`.
- V152 ties baseline on critical mismatches and on all displayed metrics except pitch content, where it trails by about `0.096` percentage points.
- Durable V152 score result: `debug/v152-active-recurrence/phase-c-score/score-result.json`; SHA256 `cc549c6f0a33c0b90648433494ef36a31b5647191058e28b9ea089f12cab7ef4`; score run `33050114109`.
- V152 construction and scoring authorizations are consumed/sealed. **Do not rescore V152.**

## V153 Phase A reference-free strength ranking — AUTHORIZED / FROZEN / PRE-EXECUTION
- Fresh explicit user authorization received for exactly **V153 Phase A reference-free strength ranking**.
- Authorization record: `debug/v153-reference-free-strength/phase-a-authorization.json`; Git blob **`46f38b384d47e9ffc38de3e2bc6c3cfe60bf9642`**; authorization commit `52a39b8e6553ae628e8d965e0fe5a4b7e74e9c7f`.
- Preregistration: `debug/v153-reference-free-strength/phase-a-preregistration.json`; Git blob **`449d668c5959e97f8f1172bc697a9578c4df03f6`**; freeze commit `824ec7ce963b1f0ae213be3db7ec2e26d3a72a88`.
- Frozen analyzer: `validation/v153_reference_free_strength/analyze_reference_free.py`; Git blob **`0525ce4a9d441a8fe8c6ffeb7fc99c8b70ebee73`**; analyzer freeze commit `360b6df63096916d6819db9f4ddaceb039a9ea0e`.
- Population is exactly immutable V152 events **`[132, 347, 457]`**; no widening is allowed.
- Frozen input Git blobs: V150 contextual analysis `67ad55d005415be2248a57238109a3d8745e4061`; V149 confidence analysis `cd3b52493aa5e3b1945b0a30ba8d6d9dbf492f1a`; V152 construction proof `3530c931bee9ab5888f350cd30d793388ebb5eca`.
- Frozen deterministic rule is descending lexicographic with **no weights** and criteria in this exact order: `(1)` selected-minus-original exact-pitch recurrence count, `(2)` selected-minus-original pitch-class recurrence count, `(3)` two-sided immediate-neighbor voice-leading improvement in semitones, `(4)` nearest frozen V147 gate excess in dB only as the final evidence tie-breaker.
- Event index is **not** a scientific tie-breaker. If the top evidence tuple is tied, fail closed with no unique winner.
- The analyzer is required to reverify all frozen Git blobs plus the V152 candidate/event-set identity before producing a result.
- Execution may produce only the ranking result and unique-winner determination. Candidate construction, Gold/reference access, score calls, audio/HPSS/CQT, Modal/L4/GPU, search/variants, tuning, main/Production changes, and automatic promotion remain forbidden.
- At this checkpoint: ranking execution **NOT YET RUN**; candidate construction **0**; score calls **0**; Gold/reference read **NO**; audio/GPU **NO**.

## Fixed safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge/promote `main` or Production.
- `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` remain untouched.
- Do not rerun any consumed V147–V152 one-use workflow.
- No candidate variants/search, threshold/weight/filter retuning, automatic promotion, or post-result tuning.
- No Gold/reference/professional-image access unless a newly frozen reference-facing phase is explicitly authorized.
- No audio reread/decode, HPSS/CQT recomputation, Modal/L4/GPU unless a newly frozen real-audio/GPU phase is explicitly authorized.

## Authoritative stop point
- V147 Phase C real-audio: **COMPLETE / SEALED**.
- V152: **COMPLETE / SEALED; best scored experimental result**.
- V153 Phase A: **AUTHORIZED / FROZEN / STOP BEFORE EXECUTION**.
- New audio execution: **NO**.
- New Gold/reference read: **NO**.
- New score call: **NO**.
- New candidate construction: **NO**.
- Modal/L4/GPU: **NO**.
- Main/Production modification: **NO**.
- Next action is exactly one execution of frozen analyzer blob `0525ce4a9d441a8fe8c6ffeb7fc99c8b70ebee73`, then persist and checkpoint the result and STOP before any candidate construction.
