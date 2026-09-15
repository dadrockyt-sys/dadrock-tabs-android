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

Next authorized action: create and freeze `docs/checkpoints/SONGSTERR_FRESH_V3_PHYSICAL_TEMPLATE_SYNTHETIC_PRE.md` prospectively. Do not create or execute V3 research code until that PRE commit exists.

## AUTHORITATIVE ROUTE

The software-lineage no-gap conclusion remains unchanged. Official correctness still requires the frozen physical calibrated route, currently budget-paused. Do not manufacture another synthetic software-lineage gate.
