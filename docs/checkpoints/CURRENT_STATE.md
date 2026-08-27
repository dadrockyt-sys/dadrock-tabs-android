# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-27 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V153 Phase C CPU GOLD SCORE = CONSUMED / BEFORE GOLD. CPU-only scoring is permitted at assistant discretion under the standing user policy; fresh authorization is required only before Modal/L4/CUDA/GPU execution. V153 Phase B event-347 candidate construction remains COMPLETE / SEALED and immutable.**

## Preserved historical checkpoint
- Full pre-compaction history remains preserved at `docs/checkpoints/archive/CURRENT_STATE-pre-phase-c-auth-intake-20260827.md`; Git blob `f71ba11394e6f2f46843055e748e8717ff484158`.

## Standing execution-authorization policy — 2026-08-27
- User instruction: **`You only need authorization for l4 gpu modal runs. Scoring and cpu work is at your discretion`**.
- Effective immediately, **CPU-only work and scoring do not require a fresh user authorization boundary**. The assistant may preregister, execute, persist, compare, checkpoint, and seal CPU-only analysis/construction/scoring phases at its discretion.
- **Fresh explicit user authorization is required before any execution using Modal, NVIDIA L4, CUDA, or any GPU resource.**
- This policy supersedes older checkpoint language that required fresh authorization for CPU scoring or other CPU-only work.
- Scientific safeguards remain in force unless explicitly changed: immutable candidate identity once sealed, preregistration before reference-facing scoring when appropriate, no silent candidate search/variants, no post-score tuning of the scored candidate, no automatic Production promotion, and no rerun of consumed one-use workflows.
- Historical sealed runs remain sealed; this policy does not reopen or legitimize rerunning already-consumed V147–V153 one-use executions.

## Historical V147 real-audio boundary
- V147 Phase C real-audio execution is COMPLETE / SEALED; run `33038518285`, job `98406611428`; workflow seal commit `4b125f42dfa447e1fe86741c8f41c09dcaffc895`.
- Immutable V147 candidate canonical event SHA256 `ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77`.
- Do not reopen or rerun V147 Phase C.

## Best sealed scored result — V152
- Candidate canonical event SHA256 `5ebedfb173730bb5e2639e7450841fb113f7db9af2acec19b88e58cca50679e6`; candidate file SHA256 `9b15ab3aa9540438db0750bb11c592a686e87b00b3acba491c80791badd349cb`.
- Changed events `[132, 347, 457]`; `1144` events / `113` measures / `3` singleton changed onsets / `0` polyphonic changes / PDF fidelity `100%`.
- V152 percentages: **35.311 / 6.699 / 5.455 / 5.805 / 100.000 / 100.000**; accepted baseline **35.407 / 6.699 / 5.455 / 5.805 / 100.000 / 100.000**; both critical mismatches `1712`.
- V152 scoring is consumed/sealed; do not rescore.

## V153 Phase A — COMPLETE / SEALED / REFERENCE-FREE
- One-use run `33052235521`, job `98450303953`: SUCCESS; workflow deleted at commit `cf00747a8c2b40089ebb82e7a64e377d4d4a78f3`.
- Result `debug/v153-reference-free-strength/phase-a-analysis.json`; file SHA256 `cd2cef3fd1491f950ad795cab6e39b4013d137abfa2f4c94c1d96db133783c53`; Git blob `012353df21573a4e34f50500c1fa5deb4b63422b`.
- Frozen ranking `[347, 132, 457]`; unique strongest event **347**.
- Event 347 evidence tuple `[2, 2, 2, 3.5114020000000004]`; event 132 `[1, 2, 2, 26.004246]`; event 457 `[1, 1, 2, 6.516224999999999]`.

## V153 Phase B event-347 construction — COMPLETE / SEALED / REFERENCE-FREE
- User continuation instruction `Please continue 💚` was bound to exactly one V153 event-347 candidate construction.
- Authorization record `debug/v153-reference-free-strength/phase-b-construction-authorization.json`; Git blob `ee74c80e0d50c01a8ca5deddee0fd04d7c9d005d`; commit `23dabdd9aea2a599128ae24e09891936f4861451`.
- Preregistration `debug/v153-reference-free-strength/phase-b-construction-preregistration.json`; Git blob `524a53b19c2ea737d2a01c9b959cfadd5b6cb9d8`; commit `18e9138235eb578015e60dbb43b1e699bd502731`.
- Frozen constructor `validation/v153_reference_free_strength/construct_event347_once.py`; Git blob `ff5f395cad43ea2c8d88c34501cc02ef56933ef6`; freeze commit `87030b7311e95517c9fb57dacb1176f375165496`.
- Pre-execution checkpoint commit `ca4888afbbbb84e0ed91975877020739945e0307`.
- One-use workflow arming commit `3b7009f739634c394b8659fea593c19739138d2d`; run **`33082187789`**, job **`98552098420`**: **SUCCESS**.
- Attempt sentinel was persisted before construction at commit **`408f4dbc`** (`debug: consume V153 event-347 construction attempt [skip ci]`).
- Reference-facing Gold/image files and prior V151/V152 score-result files were made unreadable before constructor execution.
- Candidate persistence commit **`2a514935`** (`debug: persist V153 event-347 candidate [skip ci]`).
- One-use workflow `.github/workflows/v153-event347-construct-once.yml` was deleted/sealed at commit **`7ae1b0ac9f2d388830905dcc88bc9fc51c13485d`**.

### Immutable V153 candidate identity
- Candidate path: `debug/v153-reference-free-strength/candidate/candidate.json`.
- Candidate canonical event SHA256: **`df40a771219fb69ae3c129c90ef5351e64b89006ff678e484741ecf0418e3d4b`**.
- Candidate file SHA256: **`f90889acb034b61036951843846e2954d0c685f005a35eb667360a5a57391e67`**.
- Candidate Git blob: **`975ab36c234b423d1b56e59588e960f7d9d7103f`**.
- Construction proof path: `debug/v153-reference-free-strength/candidate/construction-proof.json`; file SHA256 **`8c4fe77799fb247c0a744d3650aed2f69ed44aa43d7ee5b2e97c5d4211deedc7`**; Git blob **`efe6107df544086f62babf737ef044116ed551f0`**.
- PDF fidelity file SHA256 **`fe06f93619bbe51862933a1e235f7ff2f01356bcb02167b5b6b934a39784f33e`**; Git blob **`f6b1b7b463c9b55e2e70fb116d97f3508b6c269f`**.
- Preservation manifest path: `debug/v153-reference-free-strength/candidate/preservation-manifest.json`; file SHA256 **`174c8b060b02c8eb1cb1b147c150d922f169d9cbfec2061640096efdd9e31149`**; Git blob **`f690aeefd81090b4f558353cb3f30b7fe4dca0b9`**.
- Artifact `v153-event347-construction-33082187789`; artifact ID **`9650533630`**; ZIP SHA256 **`cfac9c3e9a921e21b5401c6f741318817323c642fe779e3c425ca8c506e45de1`**.

### Structural result
- Gate: **GO**.
- Policy: **accepted baseline + only V152 event 347**.
- Event count: `1144`; generated measures: `113`.
- Changed event set versus accepted: exactly **`[347]`**.
- Changed event count: `1`; changed onset count: `1`; polyphonic changed events: `0`.
- Retained V152 changes: `33.333333333333336%`; V152 events 132 and 457 reverted to accepted baseline.
- Timing/metadata invariant violations: `0`; position identity violations: `0`; V152 projection violations: `0`.
- Deterministic replay event SHA equals candidate SHA.
- PDF event fidelity: **`1.0` / 100%**.

## V153 Phase C CPU Gold score — FROZEN / ARMED / BEFORE GOLD
- CPU-only scoring is permitted at assistant discretion under the standing policy; no fresh scoring authorization is required.
- Scoring preregistration: `debug/v153-reference-free-strength/phase-c-scoring-preregistration.json`; Git blob **`361208d8e57c614e8a509eecb5680f0d6daf841b`**; preregistration commit **`0db9a5e2d378ad0788edee07576d94b2280abbab`**.
- Frozen scorer: `validation/v153_reference_free_strength/score_event347_once.py`; Git blob **`50f08090631ccd14701ff9f3a5d3324c7cf1f3b7`**; scorer freeze commit **`8cd8c8376e6142fc3939a79a10ee79905801f989`**.
- Armed one-use attempt sentinel: `debug/v153-reference-free-strength/phase-c-score-attempt-sentinel.json`; Git blob **`1f1c89d1ddbf950275b2a15820a9f7d868d53740`**; arm commit **`a27e81e926268fe508d33135141a6f1b1ec5218e`**.
- Candidate binding is the immutable V153 event-347 candidate SHA **`df40a771219fb69ae3c129c90ef5351e64b89006ff678e484741ecf0418e3d4b`**; candidate Git blob `975ab36c234b423d1b56e59588e960f7d9d7103f`.
- Reference identity is frozen to Gold SHA256 **`18fd868ae960dfcdd1ffb0110f1a9dfd8acc2ffeb46e247d1116cd54291526ac`**, inherited from the sealed V152 score result.
- Prior comparison source is sealed V152 score result `debug/v152-active-recurrence/phase-c-score/score-result.json`; Git blob `05042410ecd5b9793e1182a1bb1dd63ae949ab51`; file SHA256 `cc549c6f0a33c0b90648433494ef36a31b5647191058e28b9ea089f12cab7ef4`.
- Scoring chain remains exactly: wrapper blob `1ca2b8550d6c08e793f26b3aa91b99fb44fa7ddb`, core scorer blob `cc4bf61a99f22bf87a6c255e5a81220fbc82223b`, canonical adapter blob `088d44827fb23e20d9aeeb4944a672989af5846c`.
- Frozen score-call maximum: **1**. Candidate search, alternate candidate, candidate modification, threshold/weight/filter/rule tuning, audio recomputation, Production promotion, and automatic promotion are **NO**.
- Modal/L4/CUDA/GPU use is **NO / NOT AUTHORIZED** for this score.
- At this checkpoint: Gold/reference opened **NO**; reference parsed **NO**; score calls **0**.

## Fixed safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge/promote `main` or Production.
- `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` remain untouched.
- Do not rerun any consumed V147–V153 Phase A/Phase B one-use execution.
- Do not modify the immutable V153 candidate after construction.
- CPU-only scoring/analysis/construction may proceed at assistant discretion under the standing policy above.
- Explicit authorization is required before **Modal/L4/CUDA/GPU execution**.
- No automatic Production promotion from a calibration result.

## Authoritative stop point
- V153 Phase A ranking: **COMPLETE / SEALED; UNIQUE WINNER = EVENT 347**.
- V153 Phase B construction: **COMPLETE / SEALED; IMMUTABLE CANDIDATE SHA = `df40a771219fb69ae3c129c90ef5351e64b89006ff678e484741ecf0418e3d4b`**.
- V153 Phase C CPU Gold score: **ATTEMPT CONSUMED / BEFORE GOLD**.
- Gold/reference read: **NO**.
- V153 score call count: **0**.
- Modal/L4/CUDA/GPU execution: **REQUIRES FRESH EXPLICIT USER AUTHORIZATION**.
- Main/Production modification: **NO**.
- Next CPU-only executable action is exactly one score run using frozen scorer blob `50f08090631ccd14701ff9f3a5d3324c7cf1f3b7`; the run must consume the sentinel before Gold access, persist the single result, delete/seal its workflow, checkpoint, and never rerun or retune the scored candidate.