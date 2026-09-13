# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-13 America/Toronto
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, duration research and protected-song execution remain closed unless explicitly reopened by the user.
- Never silently alter/drop event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` stays deterministic/model-free/process-free/network-free; model/DSP research stays under `scripts/songsterr-fresh/`.
- Authority remains fail-closed: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, Policy C `UNENROLLED`, protected song embargoed.

## USER COMPUTE AUTHORIZATION RULE

The user authorized continued work at assistant discretion. Ask again only before any **Modal**, **Vercel heavy-GPU**, or **L4 GPU** run. Normal research, coding, GitHub work, CPU runs, checkpoints, tests and ordinary Vercel work may proceed without another authorization prompt.

## CLOSED / REVEALED LINES

V1/V2 are rejected diagnostics. GuitarSet/V3 and IDMT/V4 are closed/revealed.

V5 is closed/rejected. Official FLGD result: run `34748789583`, job `103701492462`; 79/79 files, 84,577 decoded/classified, 43,349 positives, 27,850 correct, precision `0.642460033680131`, one-sided 95% Wilson LB `0.6386648804090969` vs required `0.9900`, `externalValidationPassed:false`.

Immutable V5 result: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_OFFICIAL_CORRECTNESS_RESULT.md`, commit `df6a306a055303a6f37b229bfc9e538803f25337`.
Policy rejection: `docs/checkpoints/SONGSTERR_FRESH_FLGD_V5_POST_RESULT_POLICY_REVIEW.md`, commit `44c99d54ed7e728e85ef4042d1f15ba09643713c`.

FLGD is revealed. Do not rerun/tune V5 on FLGD or use FLGD/IDMT/GuitarSet/protected-song correctness to choose V6 constants.

## V6 — METHOD + SCORING RULES FROZEN / NO REAL CORRECTNESS

Successor charter: `docs/checkpoints/SONGSTERR_FRESH_SUCCESSOR_RESEARCH_CHARTER_V6.md`, commit `2b96fba0e3df955e62386691023cb31eeb2d11f6`.

V6 asks whether the selected Basic Pitch MIDI has an **onset-synchronous acoustic birth signature** relative to immediately preceding audio, distinct from prior steady-state/post-onset evidence.

Implementation: `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, implementation commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
Frozen synthetic fixtures commit `ca71eb218ce701686e4a4806813ac84580defa78`.

Controlled CPU synthetic run `34754079541`, job `103715385229`: SUCCESS; 23/23 fixtures matched expected behavior (12 corroborated / 7 not / 4 insufficient). Immutable result `docs/checkpoints/SONGSTERR_FRESH_V6_SYNTHETIC_RESULT.md`, commit `ed0b597d7e86f1756395445952db1f40b62e9b13`. Synthetic success is not admission evidence.

### Final V6 method freeze

`docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`
Commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.

This freezes the exact V6 implementation/constants before any V6 real-corpus correctness. Any later method amendment is a new successor requiring a new untouched holdout.

### External scoring framework freeze

`docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`
Commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen before the Guitar-TECHS alignment A/B/C outcome:
- DI-only future scoring path if the audit approves Guitar-TECHS;
- canonical mono 44.1-kHz audio path;
- unchanged Basic Pitch 0.4.0 CPU settings: MIDI 40..88, onset 0.5, frame 0.3, min note length 127.7 ms, no multiple pitch bends, melodia trick true;
- every Basic Pitch event preserved/classified exactly once;
- only `onset-birth-corroborated-candidate` is positive;
- deterministic per-performance maximum-cardinality matching, onset <=50 ms inclusive, pitch <=50 cents inclusive, durations ignored;
- one-sided 95% Wilson LB with z `1.6448536269514722`;
- pooled positives >=1000 and Wilson LB >=0.9900;
- player/category strata with >=100 positives require point precision >=0.9500;
- full-population reference-blind Phase 1 before Phase-2 correctness reveal;
- one official holdout run, immutable result before interpretation, separate policy review.

The active alignment audit may now bind only immutable population/lag identities; it cannot change V6, Basic Pitch settings, audio path, matcher, tolerances, uncertainty or gates.

## GUITAR-TECHS V6 HOLDOUT PREPARATION

Leading candidate: Guitar-TECHS Zenodo record `14963133`, version `v1`. Public materials describe real electric-guitar DI/amp/ego/exo signals, Fishman Triple Play per-string MIDI, CC BY 4.0, and possible signal-path misalignment up to 100 ms.

Frozen reference-blind audit preregistration: `docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_PREREGISTRATION.md`, commit `29818b9bfcb11b0da2b3e9efb57c5f2cd51193ae`.

The audit freezes **DI (`audio/directinput`)** as the only candidate future scoring path and forbids Basic Pitch/V6/correctness.

Audit implementation commit `0d7d57675694946e8a156b5c8e53fc2ae0347341`; merger commit `5b2b7871844d7b7ccac6d50f56f0b0eaf09065a2`.

Controlled audit CI:
- run `34754383492` failed before real-data access only because a synthetic known-lag assertion allowed exactly one hop while a -40 ms fixture recovered as -46.44 ms (~1.11 hops);
- only the synthetic assertion tolerance changed to 1.25 hops; the actual lag estimator was unchanged, commit `77510e2e797915166a5737750769824e44c49e89`;
- corrected run `34754452415`, job `103716353507`: SUCCESS, including no-scorer-import guard.

No Guitar-TECHS archive was accessed before controlled CI was green.

### Official alignment/inventory run — ACTIVE

Workflow `.github/workflows/songsterr-fresh-guitar-techs-v6-alignment-inventory.yml`
Wrapper commit `f3c9d4a88740146918c34a3538c565f21079f3bf`
Run `34754519541`, job `103716527380`
Frozen audit source `77510e2e797915166a5737750769824e44c49e89`
GitHub-hosted CPU only; no Modal/Vercel-heavy-GPU/L4.

Pre-package gates are green: exact source binding, pinned CPU runtime, controlled synthetic alignment tests and reference-blind audit guard.

Fresh-chat status checkpoint: steps 1–7 are `success`; step 8 `Download and audit exact Guitar-TECHS v1 packages sequentially` is `in_progress`; steps 9 `Merge frozen inventory and alignment result`, 10 `Verify fail-closed audit result boundary`, and 11 `Upload immutable audit outputs` are pending. Do not inspect/interpret partial per-package alignment output and do not launch a duplicate.

The frozen alignment decision is A raw timestamps / B immutable per-file constant offsets / C dataset unsuitable. Future model correctness cannot change that decision or any lag.

## NEXT ALLOWED ACTION

Inspect only run `34754519541` / job `103716527380` until the alignment/inventory audit finishes; do not start a duplicate.

On success: integrity-check the audit artifact, write an immutable Guitar-TECHS alignment/inventory result checkpoint and update this file. If A/B, create a final binding checkpoint that fills only immutable audit/population/alignment identities into the already-frozen scoring framework, then build controlled scoring harness CI with **no real correctness** before one official external run. If C, do not score Guitar-TECHS; reject it and search metadata-only for another untouched holdout.

Ask the user only if a Modal, Vercel heavy-GPU or L4 run becomes necessary.

## FRESH-CHAT NEXT STEPS — EXECUTE IN THIS ORDER

1. Fetch this canonical file from `songsterr-fresh-pipeline-v1` and treat it as source of truth. Do not infer state from older chat text if this file has moved.
2. Inspect GitHub Actions run `34754519541`, job `103716527380` first. Do not dispatch, rerun or trigger another copy.
3. If step 8 is still active, inspect only status/step state. Do not interpret partial package alignment values, do not run Basic Pitch, and do not run V6 correctness.
4. If the audit completes successfully, verify steps 9–11 are successful and fetch artifact `guitar-techs-v6-alignment-inventory`.
5. Capture and verify: run/job IDs, artifact ID, GitHub artifact archive digest, downloaded ZIP SHA-256, merged-result JSON SHA-256, all nine archive MD5 identities, package count, DI/MIDI pair count, reference-event count, pitch range, unpaired DI/MIDI counts, MIDI anomaly totals, sample-rate/channel/subtype/MIDI-format/PPQ counts, alignment status counts, lag summary, pairing identity manifest SHA-256, alignment lag manifest SHA-256, proposed scoring population SHA-256, policy-boundary fields, `datasetStructurallySuitable`, and frozen alignment decision A/B/C.
6. Write a dedicated immutable Guitar-TECHS audit-result checkpoint **before** using the result to advance execution. The checkpoint should record facts/identities and the frozen A/B/C outcome, not modify V6/scoring rules.
7. Update this canonical current-state file to point to that immutable audit result.
8. If outcome **C**, fail closed: do not score Guitar-TECHS. Record rejection and search only metadata/licensing/structure for a new untouched holdout. Do not expose another corpus to correctness until preregistered.
9. If outcome **A or B**, create a binding checkpoint that fills only the pending immutable holdout identities into `SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`'s already-frozen framework. For B, bind the exact per-pair lag manifest; for A, bind raw-MIDI timing authority. Do not change V6 constants, Basic Pitch settings, canonical audio preparation, matching tolerances, Wilson statistic, gates, player/category strata rules, or deferred-reveal policy.
10. Build the external scoring harness and wrapper against the frozen V6 implementation and bound Guitar-TECHS population. Preserve every Basic Pitch event and selected MIDI exactly; classify every decoded event exactly once; use DI-only canonical audio; no Demucs; no duration authority.
11. Run controlled synthetic/contract-only CI for the scoring harness. It must not invoke real Guitar-TECHS correctness. Verify source/runtime/population binding, event preservation, matcher boundary behavior, Wilson math, strata accounting, policy guards, and two-phase deferred reveal.
12. Checkpoint the controlled harness green state before any official correctness run.
13. Then launch exactly one official Guitar-TECHS V6 external correctness execution on the frozen source/population using ordinary GitHub CPU unless a different compute path becomes necessary. If Modal, Vercel heavy-GPU or L4 would be used, stop and ask the user for explicit authorization first.
14. During official Phase 1, do not inspect or interpret partial correctness. Require every immutable pair to finish reference-blind Basic Pitch decoding + V6 classification before Phase 2 begins.
15. After Phase 2 completes, retrieve the one final result artifact and verify all source/runtime/population/alignment/event-preservation/policy identities before interpreting metrics.
16. Record the immutable official V6 correctness result **before** pass/fail interpretation. Capture pooled decoded/classified/positive/correct counts, V6-positive precision, one-sided Wilson LB, player/category strata, all mandatory gate booleans, and `externalValidationPassed`.
17. After any correctness result is exposed, do not tune V6, Basic Pitch, audio preparation, matching/tolerances, uncertainty, gates, population, alignment or strata, and do not rerun Guitar-TECHS to seek a better result.
18. Only after the immutable result record exists, perform a separate policy review. A technical pass alone does not authorize customer/Production promotion, duration work, protected-song execution, or reopening archived V143/Gomyway.
19. Keep authority fail-closed unless a later explicit policy checkpoint legitimately changes it: `modelValidationComplete:false`, customer-eligible events `0`, `mayAdvanceDelivery:false`, duration authority paused, Policy C `UNENROLLED`, protected song embargoed.
20. Continue updating this canonical file frequently at meaningful state transitions. Check workflow path filters before documentation pushes when an active push-triggered experiment exists, and verify no duplicate experiment was spawned after any potentially relevant workflow-file change.

## STILL FORBIDDEN

- V5 FLGD rerun/post-result tuning
- using FLGD/IDMT/GuitarSet/protected-song correctness to tune V6
- changing frozen V6/scoring rules from Guitar-TECHS observations
- Guitar-TECHS Basic Pitch/V6 correctness before immutable audit result + final binding/harness controls
- changing Guitar-TECHS alignment from future correctness
- protected-song execution
- duration research
- archived V143/Gomyway / GOAT/reference scoring
- real-corpus optimizer/threshold sweeps
- training/fine-tuning on a proposed admission holdout
- Production/customer promotion without untouched external validation + separate policy approval
- Modal, Vercel heavy-GPU or L4 execution without explicit user authorization.

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1` and read this file first. V5 is closed/rejected. V6 method and external scoring framework are frozen before real correctness. Guitar-TECHS reference-blind audit run `34754519541` / job `103716527380` is the current active work and was still in step 8 at the latest checkpoint; inspect that run first.

Do not resume V143/Gomyway. Do not run Guitar-TECHS correctness until the audit result is immutable, A/B binding is frozen, and controlled scoring-harness CI is green. Ask the user only before Modal, Vercel heavy-GPU or L4 execution; everything else within these scientific/policy boundaries may proceed at assistant discretion.
