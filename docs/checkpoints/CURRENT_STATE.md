# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-08-27 UTC
Branch: `v143-contextual-prune-lobo`

Active phase: **V153 Phase A REFERENCE-FREE STRENGTH RANKING = COMPLETE / RESULT PERSISTED / WORKFLOW SEAL PENDING. Unique strongest event = 347. STOP BEFORE CONSTRUCTION. V152 remains COMPLETE / SEALED. Historical V147 Phase C real-audio remains COMPLETE / SEALED.**

## Preserved historical checkpoint
- Full pre-compaction history is preserved byte-for-byte at `docs/checkpoints/archive/CURRENT_STATE-pre-phase-c-auth-intake-20260827.md`.
- Preserved checkpoint Git blob: `f71ba11394e6f2f46843055e748e8717ff484158`.

## Historical Phase C real-audio boundary
- V147 Phase C real-audio execution completed in run `33038518285`, job `98406611428`; one-use workflow sealed at commit `4b125f42dfa447e1fe86741c8f41c09dcaffc895`.
- Immutable V147 candidate canonical event SHA256: `ca35c3492295a3079c17c35124df7a483166315e85649e95ded095c6c06b2b77`.
- Durable replay manifest blob: `9f67507b448eb3a36f6e5d2d96572af425c42cb5`.
- Do not reopen or rerun V147 Phase C.

## Best sealed scored result — V152
- Canonical candidate event SHA256: `5ebedfb173730bb5e2639e7450841fb113f7db9af2acec19b88e58cca50679e6`.
- Candidate file SHA256: `9b15ab3aa9540438db0750bb11c592a686e87b00b3acba491c80791badd349cb`.
- Changed events `[132, 347, 457]`; `1144` events / `113` measures / `3` singleton changed onsets / `0` polyphonic changes / PDF fidelity `100%`.
- V152 percentages: **35.311 / 6.699 / 5.455 / 5.805 / 100.000 / 100.000**.
- Accepted baseline percentages: **35.407 / 6.699 / 5.455 / 5.805 / 100.000 / 100.000**.
- Critical mismatches: V152 `1712`, accepted baseline `1712`.
- Durable V152 score SHA256 `cc549c6f0a33c0b90648433494ef36a31b5647191058e28b9ea089f12cab7ef4`; run `33050114109`.
- V152 score authorization is consumed; do not rescore V152.

## V153 Phase A — COMPLETE / REFERENCE-FREE
- Fresh user authorization covered exactly one V153 Phase A deterministic reference-free ranking over `[132, 347, 457]`.
- Authorization record `debug/v153-reference-free-strength/phase-a-authorization.json`; blob `46f38b384d47e9ffc38de3e2bc6c3cfe60bf9642`; commit `52a39b8e6553ae628e8d965e0fe5a4b7e74e9c7f`.
- Preregistration `debug/v153-reference-free-strength/phase-a-preregistration.json`; blob `449d668c5959e97f8f1172bc697a9578c4df03f6`; commit `824ec7ce963b1f0ae213be3db7ec2e26d3a72a88`.
- Frozen analyzer `validation/v153_reference_free_strength/analyze_reference_free.py`; blob `0525ce4a9d441a8fe8c6ffeb7fc99c8b70ebee73`; freeze commit `360b6df63096916d6819db9f4ddaceb039a9ea0e`.
- One-use workflow arming commit `e802bada9798b49d70ba9540bac0955fb46b4b4f`; run **`33052235521`**, job **`98450303953`**: **SUCCESS**.
- Attempt sentinel was committed before analysis at **`3c4b24bfdaeb63bef2b584310fc89001bfb750f6`**.
- Reference-facing files and prior V151/V152 score-result files were made unreadable before analyzer execution.
- Result path: `debug/v153-reference-free-strength/phase-a-analysis.json`.
- Result file SHA256: **`cd2cef3fd1491f950ad795cab6e39b4013d137abfa2f4c94c1d96db133783c53`**.
- Result Git blob: **`012353df21573a4e34f50500c1fa5deb4b63422b`**.
- Result persistence commit: **`f49334681cb16e1f2ade404aa52fdd7f58e6e373`**.
- Gate: **`GO_UNIQUE_WINNER`**.
- Frozen ranking order: **`[347, 132, 457]`**.
- Unique strongest event: **`347`**.

### Frozen evidence tuples
- Event `347` — measure 35, step 9, MIDI `62 -> 61`: tuple **`[2, 2, 2, 3.5114020000000004]`**.
- Event `132` — measure 13, step 8, MIDI `65 -> 64`: tuple **`[1, 2, 2, 26.004246]`**.
- Event `457` — measure 45, step 9, MIDI `65 -> 64`: tuple **`[1, 1, 2, 6.516224999999999]`**.
- Tuple order was preregistered as: exact-pitch recurrence delta, pitch-class recurrence delta, two-sided voice-leading improvement, then nearest frozen V147 gate excess only as final tie-breaker.
- Event `347` wins at criterion 1 (`2` versus `1` and `1`), so the much larger V147 gate margin of event `132` was never used to overturn the preregistered ordering.
- No post-result ranking-rule change or tuning occurred.

### V153 safety and preservation
- Gold/reference read: **NO**.
- Professional image read: **NO**.
- Prior V151/V152 score-result read by analyzer: **NO**.
- Candidate constructed: **NO**.
- Candidate search/variants: **NO**.
- Threshold/weight/filter tuning: **NO**.
- Audio read/decode: **NO**.
- HPSS/CQT recomputation: **NO**.
- Modal/L4/CUDA/GPU: **NO**.
- Score calls: **0**.
- Main/Production modification: **NO**.
- Automatic promotion: **NO**.
- Artifact `v153-phase-a-reference-free-strength-33052235521`; artifact ID `9638088563`; ZIP SHA256 `214d640ab0a49604dc3b11e6fd590fda0b9660aed1c74b677a7d84ba418348b2`.

## Fixed safety boundary
- Work only on `v143-contextual-prune-lobo`; never modify/merge/promote `main` or Production.
- `/ai-tab` frontend, Bass/Lead, and `freezeReady=false` remain untouched.
- Do not rerun any consumed V147–V153 one-use execution.
- Do not construct a V153 candidate from event 347 until a separate fresh explicit construction authorization is received.
- Do not open Gold/reference or score any future V153 candidate until that candidate is separately constructed, persisted, sealed, and then receives a separate fresh one-use scoring authorization.
- No audio/HPSS/CQT/Modal/L4/GPU unless separately preregistered and freshly authorized.

## Authoritative stop point
- V147 Phase C real-audio: **COMPLETE / SEALED**.
- V152: **COMPLETE / SEALED; best scored result**.
- V153 Phase A ranking: **COMPLETE; UNIQUE WINNER = EVENT 347**.
- V153 candidate construction: **NOT AUTHORIZED / NOT STARTED**.
- New Gold/reference read: **NO**.
- New score call: **NO**.
- New candidate construction: **NO**.
- New audio/GPU execution: **NO**.
- Main/Production modification: **NO**.
- Immediate administrative action: delete/seal `.github/workflows/v153-phase-a-reference-free-strength-once.yml`, checkpoint the seal, then STOP.
