# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-15 America/Toronto — EGFxSet boundary-aware V2 remains a frozen non-authorizing FAIL; AG-PT-set cleared pre-media ingress but its frozen reference-blind audit closed as structural decision C before any WAV/model correctness exposure; later metadata-only searches rejected GuitarDuets, EG-Solo, Guitar Style Dataset and historical GPT, and a focused 2025–2026 pass found no new admissible independent holdout. EGDB-PG was discovered but is an EGDB-derived re-rendering with no explicit license value on the current Zenodo records, so the closed EGDB line was not reopened. No Basic Pitch or V6 correctness run is currently authorized.

Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

Key records:

- hardening result: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_HARDENING_V1_RESULT.md`
- boundary V2 PRE: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_PRE.md`
- boundary V2 real result: `docs/checkpoints/SONGSTERR_FRESH_BOUNDARY_QUALIFIER_V2_RESULT.md`
- GuitarJam rejection: `docs/checkpoints/SONGSTERR_FRESH_V6_GUITARJAM_PREMEDIA_REJECTION.md`
- URMP/GAPS/EGDB batch: `docs/checkpoints/SONGSTERR_FRESH_V6_PREMEDIA_BATCH_URMP_GAPS_EGDB.md`
- AG-PT-set pre-media clearance: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_PREMEDIA_CLEARANCE.md`
- AG-PT-set reference-blind PRE: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_PRE.md`
- AG-PT-set reference-blind result: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_RESULT.md`
- GuitarDuets/EG-Solo/Guitar Style/GPT batch: `docs/checkpoints/SONGSTERR_FRESH_V6_PREMEDIA_BATCH_GUITARDUETS_EGSOLO_GUITARSTYLE_GPT.md`
- 2025–2026 no-new-candidate search: `docs/checkpoints/SONGSTERR_FRESH_V6_PREMEDIA_2025_2026_SEARCH_NO_NEW_CANDIDATE.md`
- V3 physical-template synthetic PRE: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE.md`, frozen commit `0292869c1e1e1bc138f2fdff4e839326c0e5d082`
- V3 physical-template synthetic iteration-1 result: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT.md`, frozen FAIL commit `6a6965730250f2000cc480ede2ed3d2638b0df44`
- V3 physical-template synthetic iteration-2 PRE: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE_ITERATION2.md`, frozen commit `b2821f8690bea49783071ead87e69424fd63c787`
- V3 physical-template synthetic iteration-2 result: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT_ITERATION2.md`, frozen FAIL commit `7153a02ede14b0a43af58609bdc12cd4b792e9b9`

## HARD SCOPE

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- **Do not resume archived V143/Gomyway unless the user explicitly asks.**
- GOAT/reference scoring remains closed unless explicitly reopened.
- Guitar-TECHS, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, protected-song work and other closed lines remain closed.
- Reserved Guitar Fretboard Notes `deb` / `ele_natural` remain untouched.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; model/DSP/research stays under `scripts/songsterr-fresh/`.
- Budget checkpoint `e7f0146d4f01605b642f8aeaa100962254b5ce58` remains binding; physical calibration/holdout work remains paused.
- Synthetic/smoke diagnostics are never authoritative correctness validation.
- Never rewrite or soften any frozen historical FAIL/C result.

## GLOBAL AUTHORIZATION — UNCHANGED

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Consumed real-run authorizations:

- `Please try the run again` -> hardened-V1 EGFxSet run `34938917218`, attempt 1.
- `Lets take what was learned, repair and run again` -> one V2 repair cycle plus one new EGFxSet V2 diagnostic, consumed by run `34940292514`, attempt 1.

There is no remaining authorization for another EGFxSet run, Basic Pitch rerun, V6 correctness run, threshold variation, modified-real-rule execution, AG-PT-set structural re-audit, or candidate-media experiment.

## EGFxSET HISTORY — ALL FROZEN

Historical all-events smoke: EGFxSet `Clean.zip#Clean/Bridge/6-0.wav`, truth string 6 / fret 0 / MIDI 40. Repaired Basic Pitch run `34936227380` emitted immutable proposals `[40,68]`; overall remains `FAIL_NON_AUTHORIZING_SMOKE`.

Hardened V1 real diagnostic run `34938917218` rejected both proposals. MIDI 40 was analyzed with synthetic left zero-padding and failed physical-template plausibility; MIDI 68 failed frozen necessity. Overall remains `FAIL_HARDENED_NON_AUTHORIZING_DIAGNOSTIC`.

Boundary V2 PRE commit `819d7a9a855d6f067aa40a007fdd0570d231d782` prospectively removed fabricated left context. Synthetic gates passed ordinary in-clip birth, confidence inversion, clip-start fundamentals, alias rejection, true polyphony, noise rejection, missing-context fail-closed behavior, and physical-position ambiguity.

Boundary V2 real run:

- run `34940292514`
- job `104287207091`
- artifact `10385620104`
- immutable proposals `[40,68]`
- MIDI 40: `rejected`, `BOUNDARY_SELECTED_TEMPLATE_NOT_PHYSICALLY_PLAUSIBLE`, no synthetic pre-context
- MIDI 68: `rejected`, frozen necessity `0.000513675778819313 < 0.01`
- promoted MIDI `[]`
- overall `FAIL_BOUNDARY_V2_NON_AUTHORIZING_DIAGNOSTIC`

The zero-padding boundary defect is fixed. The remaining concrete EGFxSet weakness is the inherited physical harmonic-template plausibility model. Do not lower frozen ratio `0.20`, remove the gate, special-case MIDI 40, or tune from this real observation.

## FROZEN V6 REPLACEMENT-HOLDOUT INGRESS RULE

Before any untouched candidate media/reference payload access, public metadata must establish all four:

1. real human guitar performance suitable for the intended holdout;
2. usable public rights/license for the exact scoring media;
3. synchronized note-event ground truth aligned to the exact performance;
4. reference provenance sufficiently independent of Basic Pitch/V6.

Fail any gate -> `REJECT_PREMEDIA`. Public downloadability alone is not a license grant. A score/source sequence alone is not a timestamped performance reference. No post-access rescue or candidate substitution is allowed.

## CLOSED REPLACEMENT CANDIDATES / LINES

- GuitarJam — `REJECT_PREMEDIA`: no synchronized pre-existing note-event truth for exact performances.
- URMP — `REJECT_PREMEDIA`: no guitar in corpus instrumentation.
- GAPS — `REJECT_PREMEDIA`: frozen licensing/use restrictions and model-assisted alignment provenance fail ingress; do not reopen from later mirrors.
- EGDB — `REJECT_PREMEDIA`: no usable public dataset license established in the frozen search.
- Guitar-TECHS — decision C; closed.
- GuitarSet/V3, IDMT/V4, V5/FLGD, GOAT/reference scoring — closed by scope.
- GuitarDuets — `REJECT_PREMEDIA`: note-level MIDI described for synthesized duets, not exact real performances.
- EG-Solo — `REJECT_PREMEDIA`: exact performance media are third-party popular-rock YouTube videos without established reusable dataset rights.
- Guitar Style Dataset — `REJECT_PREMEDIA`: MuseScore exercises are not released per-take timestamped note-event truth.
- historical GPT dataset — `REJECT_PREMEDIA`: public payload identity/access unavailable; later survey reports broken link and unsuccessful author contact.

## AG-PT-SET — PRE-MEDIA PASS, THEN FROZEN STRUCTURAL C

AG-PT-set cleared pre-media ingress because public metadata established real monophonic human guitar, CC BY 4.0, released onset/audio/pitch/string fields and acceptable independent reference provenance.

Reference-blind PRE: `docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_PRE.md`, commit `0a84d6be1373d538b251663b1fa7af8f33bbf378`. Only structural/alignment/inventory inspection was authorized; Basic Pitch and V6 correctness were forbidden.

Authoritative first-started audit:

- run `35020989444`
- job `104556302921`
- head `1d37950d03e26af6fcdf3a905aa08e2f863ee878`
- artifact `10418038649`
- artifact ZIP SHA-256 `eefea849f7431ffa20262ce5e1b893dd96ae93f2df0d695b59b056c257f495e4`

Accidental duplicate run `35021035914` / job `104556457264` has byte-identical inner outputs and is preserved only as duplicate history, not independent evidence.

Frozen observed result:

- archive `aGPTset_z.zip`, size `6749621615` bytes
- MD5 exact PRE match `1dff8103f9ad6e1a86cee2e5e39cbe87`
- archive SHA-256 `6d03ee80f53e64e703b64f58526b6465264032fcc195aea9ad1058a7ebefba64`
- annotation `aGPTset/metadata/note_labels.csv`, SHA-256 `75502d20e5149641eb4d3449240413673ace6885a5c822df38760df422e98fa1`
- annotation rows `32592`
- admitted pitched/onset rows `24180`
- admitted WAVs `0`
- fatal anomalies `24180`, all `missing_or_ambiguous_audio`
- Basic Pitch runs `0`
- V6 correctness runs `0`

The prospectively frozen exact/suffix resolver could not bind released `audio_file_path` values to unique archive WAV members, so the audit never reached WAV timing/signal alignment. This is a source-pairing structural C, not a V6 correctness failure and not a claim that the underlying dataset audio is intrinsically unsynchronized.

Frozen decision: **C** — `structural timing/source anomaly requires fail-closed rejection`.

Result checkpoint commit: `89ad50b10c37cece15fbcd03db50672bfad8ea92`.

Do not repair the resolver and rerun this closed attempt. A new AG-PT-set structural-binding experiment would require a new prospective PRE plus explicit authorization.

## 2025–2026 METADATA-ONLY SEARCH — NO NEW ADMISSIBLE CANDIDATE

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V6_PREMEDIA_2025_2026_SEARCH_NO_NEW_CANDIDATE.md`
Checkpoint commit: `0e8c552cd52bb8a816035cb16ae46467e047523b`

A focused recent search mainly returned already-closed GAPS, Guitar-TECHS, GuitarSet, GOAT/reference, François Leduc/V5 and EGDB-derived work. Those were not reopened.

EGDB-PG was the only materially new guitar-transcription release found. Public paper metadata describes it as a re-rendering/expansion of EGDB using many amplifier/cabinet presets. The current Zenodo records (`10.5281/zenodo.19542613` and `10.5281/zenodo.19789500`) display a Rights/License heading without an actual license value; the full original WAV form is request-only. Therefore EGDB-PG is recorded as `NOT_ADMITTED_NEW_CANDIDATE / DO_NOT_REOPEN_EGDB`, not as a new independent holdout and not as a revision of the frozen EGDB decision.

No dataset file was previewed, downloaded or opened in this search pass. Basic Pitch runs `0`; V6 correctness runs `0`.

## CURRENT SAFE ENGINEERING DIRECTION

The public metadata-only holdout search is now yielding predominantly already-closed datasets or derivatives. Continue it only if a genuinely independent candidate is identified without reopening frozen lines.

The productive default safe direction is now **independent synthetic/non-EGFxSet V3 physical-template plausibility research**:

- inspect frozen V2/V6 template code;
- formulate a prospective timbre-robust multi-harmonic/support criterion independent of the EGFxSet real measurement;
- test only on synthetic/non-EGFxSet fixtures;
- preserve harmonic-alias rejection, genuine polyphony recovery, confidence independence, exact identity and fail-closed behavior;
- do not execute any real candidate/model workflow.

Not permitted without new explicit prospective authorization: Basic Pitch on real candidates, any V6 correctness run, AG-PT-set re-audit/repair against real archive, EGFxSet retry/modified real rule, candidate payload opening after pre-media rejection, heavy-GPU correctness work, physical calibration/capture, protected-song execution, V143/Gomyway or GOAT/reference work.

## FRESH CHAT — EXACT NEXT STEPS

Fresh-chat handoff saved at the user's request on 2026-09-15. Start here and do not infer authorization beyond these steps.

1. Re-fetch live `songsterr-fresh-pipeline-v1` and read this checkpoint before making changes. Verify the branch head rather than relying on an older chat summary.
2. Preserve all frozen evidence exactly as recorded: EGFxSet V2 run `34940292514` remains FAIL; AG-PT-set remains pre-media PASS followed by structural decision C; duplicate AG-PT run `35021035914` is not independent evidence; all listed pre-media rejections remain closed.
3. **Do not resume V143/Gomyway.** Also do not reopen GOAT/reference scoring, GuitarSet/V3, IDMT/V4, V5/FLGD, Guitar-TECHS, duration, protected-song work, `main`, Production, reserved GFN splits, physical calibration/capture, or any rejected replacement candidate.
4. Before adding V3 research code, inspect `.github/workflows/` and relevant path filters/triggers. Confirm that edits under the intended V3 synthetic research paths cannot automatically launch any closed real-media, Basic Pitch, V6 correctness, EGFxSet, AG-PT-set, protected-song, or heavy-compute workflow. If trigger isolation is not provable, harden the workflow boundary first without executing the closed job.
5. Inspect the frozen V2/V6 physical-template implementation, especially `_candidate_template()` in `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`. The research target is the inherited single-bin plausibility rule that rejects a candidate when its fundamental support is below `0.20` of its strongest observed harmonic. Treat the `0.20` value and the EGFxSet observation as frozen historical evidence: do **not** lower/tune that threshold or special-case MIDI 40.
6. Freeze a new prospective documentation checkpoint before implementation, preferably `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE.md`. The PRE must define the V3 hypothesis, synthetic fixtures, immutable pass/fail gates, exact files allowed to change, and explicit prohibition on real-media/model execution.
7. V3 hypothesis direction: replace the fragile single-fundamental-bin plausibility concept with a timbre-robust **multi-harmonic/support** criterion that can tolerate a weak fundamental while still requiring physically coherent harmonic evidence. Design it independently of the EGFxSet measurement.
8. Preserve the protections that are already doing useful work: NNLS necessity, lower-harmonic-owner/alias protection, genuine polyphony recovery, confidence independence, exact proposal identity, boundary fail-closed behavior, and no promotion from Basic Pitch confidence alone. V3 must not weaken these merely to make a synthetic fixture pass.
9. Create only synthetic/non-EGFxSet fixtures for V3. Include at minimum: weak-fundamental/strong-overtones valid guitar-like tone; ordinary strong-fundamental tone; octave/harmonic alias trap; lower-note-owner trap; true two-note polyphony; broadband/noise rejection; missing/insufficient support fail-closed case; clip-start and ordinary in-clip cases. Add adversarial timbre variation prospectively rather than after seeing failures.
10. Keep V3 research isolated from frozen V6 until its synthetic gates are prospectively defined and pass. Prefer a new research module/test file under `scripts/songsterr-fresh/` rather than silently changing the frozen V6 implementation in place.
11. Run only synthetic/local code-level tests that cannot access real candidate media or invoke Basic Pitch/V6 correctness. Do not download/open EGFxSet, AG-PT-set, rejected holdouts, protected songs, or any new candidate payload as part of V3 synthetic research.
12. Record every meaningful V3 state transition in this checkpoint and in the V3 PRE/result checkpoint. If synthetic V3 fails, freeze the failure and revise only through a new prospective iteration; do not tune against closed real evidence.
13. A future real-media V3/V6 evaluation is **not authorized by this handoff**. It requires a separately frozen real-evaluation PRE plus new explicit user authorization after the synthetic line is complete.
14. Metadata-only holdout search may continue in parallel only for a genuinely independent untouched candidate. It must clear all four frozen ingress gates before payload access. Do not use a newer mirror/derivative to reopen a closed dataset.
15. Keep `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` updated often so another fresh chat can resume without reconstructing state from conversation history.

### Immediate first task for the next chat

Perform steps 1–4 only: verify the live branch/checkpoint and audit workflow trigger isolation. Then create/freeze the V3 synthetic PRE described above before writing or executing V3 research code.

## V3 SYNTHETIC RESEARCH — VERIFIED WORKFLOW ISOLATION / READ-ONLY TEMPLATE AUDIT

Verified 2026-09-15 before any V3 implementation or execution.

- Live branch audited: `songsterr-fresh-pipeline-v1`, head `5831ea4e9fb6066d2d5184148f180e7b7beaafe1`, tree `a68dc2692dd9a75908fade10f410444c21157633`.
- Authoritative `.github/workflows` tree: `fc9fcc316e0173342e6dbf2b73d891bbc0e26a2b`; it contains 61 exact `songsterr-fresh-*.yml` workflow filenames.
- The automatic-trigger scan identified 30 fresh workflows with automatic events relevant to branch commits. Every detected `push` trigger was path-filtered. `songsterr-fresh-decoder-trace-followup.yml` additionally has a `workflow_run` trigger tied to successful completion of `Songsterr Fresh Model Evidence Cross-Run Measurement Canary`; the upstream measurement canary is itself path-scoped to its enumerated evidence files.
- No audited automatic workflow uses a catch-all `scripts/songsterr-fresh/**` path. The only broad research wildcard observed in the audited automatic set was `songsterr_pipeline/**`, which is outside the intended V3 research boundary.
- `songsterr-fresh-independent-pitch-support-structure-trigger.yml` is path-scoped to its own workflow plus `analyze_full_mixture_structure.py` and `build_structure_map.mjs`; the planned V3 files cannot trigger its downstream dispatch.
- The current checkpoint filename is referenced inside `songsterr-fresh-decoder-trace-followup.yml` and `songsterr-fresh-record-policy-b-research-once.yml`, but neither workflow watches the checkpoint path on `push`; each push filter is scoped to its own workflow YAML. A documentation-only checkpoint/PRE commit therefore does not satisfy those push filters.
- Proposed isolated V3 paths are frozen for the PRE boundary as `scripts/songsterr-fresh/physical_template_plausibility_v3.py`, `scripts/songsterr-fresh/test_physical_template_plausibility_v3.py`, and `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE.md`. None matches the audited automatic workflow path filters.
- No workflow, Basic Pitch job, V6 correctness job, real-media job, heavy-compute job, model inference, candidate payload access, or protected-song execution was performed during this audit. Archived V143/Gomyway was not resumed or modified.

Read-only V2/V6 lineage review:

- `scripts/songsterr-fresh/qualify_basic_pitch_note_births_v2.py` leaves normal in-clip classification on frozen V6 unchanged and only routes clip-start proposals lacking genuine left context to the separate one-sided clip-start pitch-presence classifier. V3 must not alter that boundary semantic as part of this research line.
- In frozen `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, `_candidate_template()` selects the candidate fundamental bin within the MIDI cell, constructs up to six local harmonic supports weighted `1/h`, and rejects the candidate before NNLS when selected fundamental support is less than `0.20` of the strongest observed harmonic.
- Candidates surviving that physical-template gate enter the shared NNLS dictionary; the separate leave-one-out necessity protection remains `necessityFraction >= 0.01`. V3 research targets the physical-template plausibility stage only; it must preserve the NNLS necessity protection rather than weakening it.
- Frozen V6 synthetic fixtures already exercise ordinary/detuned notes, octave/harmonic aliases, neighbor mismatch, continuing-plus-new notes, dyad/triad polyphony, unrelated transient/noise, a weak selected note under a stronger owner, silence/low-noise, and pre/post-context fail-closed cases. These protections are inputs to the prospective V3 gates, not post-result tuning targets.

Prospective V3 PRE is frozen at commit `0292869c1e1e1bc138f2fdff4e839326c0e5d082`, created before any V3 research implementation or V3 synthetic execution. Its immutable iteration-1 boundary allowed only the isolated V3 module/test, the V3 synthetic result checkpoint, and state-only updates to this current checkpoint. The frozen V6/V2 implementations and all workflow files remained read-only.

### Iteration 1 — frozen FAIL

- first module commit: `3f679a0f701d23e6ad15dc567e2728e89a4abd87`
- complete first implementation/test pair head: `f34f256ec9747d65eee6381b00b1324336e433c4`
- frozen result checkpoint commit: `6a6965730250f2000cc480ede2ed3d2638b0df44`
- local execution files were verified byte-for-byte against Git blobs `45b8f3b66df7500824071489205a732dfe05d759` (module) and `71289b9ed6654199e40936a1e9ccbde5dbf0054c` (test)
- the first synthetic run was fail-fast and stopped at `octave_alias_lower_a3_selected_a4`: frozen expected composite FAIL, observed composite PASS
- all prospective PASS cases reached before that point had passed, including weak/zero-fundamental support, clip-start-post-only support, true-polyphony cases and the nine-case timbre/detuning matrix
- no iteration-1 algorithm, constant, fixture, expected decision, PRE, module or test was changed after observing the failure; no second iteration-1 run was used to search for a rescue
- no workflow, Basic Pitch, V6 correctness, real-media/model, protected-song, closed-line, V143/Gomyway or heavy-compute execution occurred

Iteration 1 is permanently `FAIL_SYNTHETIC_ALIAS_PROTECTION`. This does not alter any frozen historical result and does not authorize real evaluation.

### Iteration 2 — frozen FAIL

- prospective PRE commit: `b2821f8690bea49783071ead87e69424fd63c787`
- wrapper commit: `0587daa4cd1055255fb394939af2162e20b80be4`
- complete first implementation/test pair head: `4d69b7bc20637507c3a9167a5fb9c5ad498773ca`
- frozen result checkpoint commit: `7153a02ede14b0a43af58609bdc12cd4b792e9b9`
- exact local execution blobs: iteration-1 base `45b8f3b66df7500824071489205a732dfe05d759`, iteration-2 wrapper `7090e17baff60f91700a760f617e905ff53484ab`, iteration-2 test `eefe00346a94e8f0ed433ac916352a4b2e9331c5`
- pre-execution PRE→pair compare contained only the two new iteration-2 Python files; no workflow or frozen file changed
- first committed test execution evaluated 31 fixtures × 3 in-process repetitions and was deterministic
- result: `FAIL`, 5 mismatches, all unexpected PASS: `two_harmonics_only`, `single_peak_only`, `broadband_noise`, `nonharmonic_impulses`, and `clip_start_insufficient_support`
- the original octave-alias gate and third-harmonic-owner trap matched FAIL expectations; new `true_octave_polyphony_a3_plus_a4`, `weak_lower_a3_plus_a4`, inherited A3+E5 and A4+B4 polyphony controls matched PASS expectations
- all other 26 prospective cases matched their frozen expectations
- no iteration-2 PRE/code/test/fixture/threshold was changed after the result and no second iteration-2 run was used to search for a rescue
- no workflow, Basic Pitch, V6 correctness, real-media/model, protected-song, closed-line, V143/Gomyway or heavy-compute execution occurred

Iteration 2 is permanently `FAIL_SYNTHETIC_SPURIOUS_SUPPORT`. The owner-aware guard repaired the iteration-1 synthetic alias defect, but the inherited candidate-evidence stage still admits sparse/non-harmonic/noise controls. This does not alter any historical result and does not authorize real evaluation.

Next permitted action: if continuing synthetic research, freeze a **new prospective iteration-3 PRE** before any code revision or execution. A successor may preserve the successful iteration-2 lower-owner guard while adding a separately justified candidate-evidence significance control against spurious detuning-anchor support. It must preserve all 31 iteration-2 fixture expectations and must not be tuned on closed real evidence.

## FRESH CHAT HANDOFF — CURRENT AFTER ITERATION 2

Saved 2026-09-15 at the user's request for a new chat. This section supersedes the earlier pre-V3 "FRESH CHAT — EXACT NEXT STEPS" section above. The live branch immediately before this handoff commit was `0c830e82f5f8e0c9458ac570caf0ef0210f12ec1` (`docs: record V3 synthetic iteration 2 FAIL`). A new chat must still re-fetch the live branch before writing because this handoff commit itself advances HEAD and later concurrent changes may exist.

1. Work only on `songsterr-fresh-pipeline-v1`. Re-fetch live HEAD and this checkpoint first; do not rely on the pre-handoff SHA as current.
2. Read the frozen iteration-2 PRE and result before designing anything: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE_ITERATION2.md` and `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT_ITERATION2.md`. Preserve iteration 1 and iteration 2 as permanent FAIL records; do not edit, reinterpret, or rerun them as rescue attempts.
3. Treat workflow-trigger isolation as already verified for the previously frozen isolated V3 paths. If iteration 3 uses any new filename or path, re-audit that exact path against `.github/workflows/` before committing executable code. Do not launch or dispatch any workflow during the audit.
4. The next permitted engineering action is documentation-only: create and commit a **new prospective iteration-3 PRE** before changing or executing V3 research code. Prefer `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE_ITERATION3.md`. The PRE must freeze the hypothesis, exact allowed files, immutable fixtures/expected outcomes, constants/gates, execution command, fail-fast/result-recording policy, and explicit prohibition on real/model/closed-line access.
5. Iteration-3 motivation is the frozen iteration-2 result only: five unexpected PASS cases (`two_harmonics_only`, `single_peak_only`, `broadband_noise`, `nonharmonic_impulses`, `clip_start_insufficient_support`) show insufficient candidate-evidence significance. The successful iteration-2 lower-owner/alias guard should remain protected. Do not use EGFxSet or any other closed real observation to choose thresholds or special cases.
6. Prospectively preserve all 31 iteration-2 fixture expectations as regression gates. Any additional adversarial synthetic fixtures must be specified in the iteration-3 PRE **before** the first iteration-3 execution. Do not add rescue fixtures or tune expectations after seeing results.
7. Keep frozen V2/V6 implementations read-only. Do not edit `scripts/songsterr-fresh/onset_birth_corroboration_v6.py` or `scripts/songsterr-fresh/qualify_basic_pitch_note_births_v2.py` during the isolated iteration-3 research line. Implement iteration 3 in new isolated research/test files named and frozen by the PRE.
8. Preserve NNLS necessity (`necessityFraction >= 0.01`), lower-harmonic-owner/alias protection, genuine polyphony recovery, confidence independence, exact proposal identity, clip-start/ordinary-in-clip boundary semantics, and fail-closed behavior. Do not lower the historical `0.20` V6 ratio or special-case MIDI 40.
9. After the iteration-3 PRE is committed and its commit SHA is recorded, verify the PRE→implementation diff contains only the prospectively allowed files. Only then may the single prospectively defined **synthetic/local** test execution occur. No Basic Pitch, Demucs/model inference, V6 correctness, real-media, candidate-payload, protected-song, workflow, GPU/heavy-compute, physical calibration/capture, or network-dependent research execution is authorized.
10. Freeze the first iteration-3 result exactly as observed. PASS or FAIL, write a dedicated result checkpoint and update this current-state file. If it fails, do not modify that iteration's code/test/PRE and rerun to search for a rescue; any successor requires a new prospective iteration PRE.
11. **Do not resume archived V143/Gomyway.** Do not reopen GOAT/reference scoring, GuitarSet/V3 validation, IDMT/V4, V5/FLGD, Guitar-TECHS, duration, EGFxSet, AG-PT-set, rejected holdouts, `main`, Production, reserved GFN splits, physical calibration/capture, or protected-song work.
12. A real-media V3/V6 evaluation remains unauthorized. It would require a separate prospectively frozen real-evaluation PRE plus new explicit user authorization after a synthetic line is complete.
13. Keep `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md` updated at every meaningful state transition so a later fresh chat can resume without reconstructing history.

### Immediate first task for the next chat

Re-fetch the live branch and current checkpoint; verify no concurrent change invalidates the isolation assumptions; then create/freeze **iteration-3 PRE only**. Do not revise or execute iteration-3 research code until that PRE commit exists.

## AUTHORITATIVE ROUTE

The software-lineage no-gap conclusion remains unchanged. Official correctness still requires the frozen physical calibrated route, currently budget-paused. Do not manufacture another synthetic software-lineage gate.

## V3 SYNTHETIC RESEARCH — ITERATION 3 PRE-EXECUTION STATE

Recorded 2026-09-15 America/Toronto before the first iteration-3 synthetic execution.

- Prospective iteration-3 PRE: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE_ITERATION3.md`, frozen commit `26ac58fe54c179744ef036a9dc4f4a7d69598038`, parent `eca05f1c46208f0df4273a2948e98de7db611563`.
- Iteration-3 research module commit: `e4db75be46a49b1035b5ec11d29f9ade1fa8658a`; Git blob `39629250c6d141d5cda9e9d7f570580ec725ae42`.
- Complete first implementation/test pair head: `6f2041679f0ee4540b63d74a61b113e5267f8e8b`; test Git blob `76455337bd17a952dd36c1dabd03ce741e806b07`.
- PRE→pair compare `26ac58fe54c179744ef036a9dc4f4a7d69598038..6f2041679f0ee4540b63d74a61b113e5267f8e8b` contains exactly the two prospectively allowed new iteration-3 Python files and no other changes.
- Exact isolated local materialization has been verified against Git blobs for the frozen iteration-1 base `45b8f3b66df7500824071489205a732dfe05d759`, frozen iteration-2 wrapper `7090e17baff60f91700a760f617e905ff53484ab`, frozen iteration-2 test `eefe00346a94e8f0ed433ac916352a4b2e9331c5`, iteration-3 module `39629250c6d141d5cda9e9d7f570580ec725ae42`, and iteration-3 test `76455337bd17a952dd36c1dabd03ce741e806b07`.
- No iteration-3 synthetic test has been executed yet at this state transition.
- No workflow, Basic Pitch, V6 correctness, model/Demucs, real-media, candidate-payload, protected-song, physical capture/calibration, or heavy-compute execution has occurred. Archived V143/Gomyway remains untouched.

Next permitted action under the frozen PRE: perform the final forbidden import/I/O scan on the exact committed pair, then execute only `python3 test_physical_template_plausibility_v3_iteration3.py` once if the scan is clean. Freeze that first result exactly as observed; do not tune or rescue-rerun iteration 3.

## V3 SYNTHETIC RESEARCH — ITERATION 3 FROZEN PASS

Frozen 2026-09-15 America/Toronto after the first and only prospectively authorized iteration-3 synthetic execution.

- prospective PRE commit: `26ac58fe54c179744ef036a9dc4f4a7d69598038`
- module commit: `e4db75be46a49b1035b5ec11d29f9ade1fa8658a`
- complete implementation/test pair head: `6f2041679f0ee4540b63d74a61b113e5267f8e8b`
- pre-execution state checkpoint commit: `bc947f71cf3a92a079c55c76f80e79d130be58d1`
- frozen result checkpoint: `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_RESULT_ITERATION3.md`, commit `e97ab67c9c2794f4a50c5170102d1380484f5fb1`
- exact execution blobs: iteration-1 base `45b8f3b66df7500824071489205a732dfe05d759`, iteration-2 wrapper `7090e17baff60f91700a760f617e905ff53484ab`, iteration-2 test `eefe00346a94e8f0ed433ac916352a4b2e9331c5`, iteration-3 module `39629250c6d141d5cda9e9d7f570580ec725ae42`, iteration-3 test `76455337bd17a952dd36c1dabd03ce741e806b07`
- final import/I/O isolation scan: clean; no forbidden file/network/process/model/workflow access in the execution dependency chain
- only prospectively defined local synthetic test command executed once: `python3 test_physical_template_plausibility_v3_iteration3.py`
- canonical first-run summary: `fixtureCount=34`, `repetitions=3`, `deterministic=true`, `mismatchCount=0`, `result=PASS`, process exit `0`
- all 31 frozen iteration-2 fixture expectations were preserved; the five iteration-2 spurious PASS controls are now rejected under the frozen iteration-3 evidence-significance guard
- all three prospective iteration-3 scale controls matched their expected outcomes, including the low-scale coherent harmonic PASS and low/high-scale broadband-noise FAIL controls
- frozen `MIN_CANDIDATE_EVIDENCE_FRACTION=0.10` was not changed after observation; no rescue rerun or post-result tuning occurred
- no workflow, Basic Pitch, V6 correctness, model/Demucs, real-media, candidate-payload, protected-song, physical calibration/capture, heavy-compute, main/Production, or closed-line execution occurred; archived V143/Gomyway remains untouched

Iteration 3 is permanently `PASS_SYNTHETIC_EVIDENCE_SIGNIFICANCE`. This is synthetic-only evidence and does not revise the frozen EGFxSet V2 FAIL or AG-PT structural C.

### Current authorization boundary after iteration 3

No real/model correctness evaluation or frozen V6/V2 integration is authorized by this PASS. Before any successor integration or real-media evaluation, freeze a new prospective PRE defining the exact integration/evaluation boundary, files, immutable gates, and prohibitions. Any real-media/model execution also requires new explicit user authorization. Do not infer authorization from the synthetic PASS itself.
