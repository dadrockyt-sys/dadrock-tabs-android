# CURRENT STATE — Songsterr Fresh Pipeline V1

Updated: 2026-09-14 America/Toronto — software-only budget boundary active; Stage-0 contact replay synthetic CI PASS
Canonical branch: `songsterr-fresh-pipeline-v1`
Canonical checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PIPELINE_CURRENT_STATE.md`

## HARD SCOPE / AUTHORITY

- Work only on `songsterr-fresh-pipeline-v1`; do not change `main` or Production.
- Archived V143/Gomyway and GOAT/reference scoring remain closed unless the user explicitly reopens them.
- GuitarSet/V3, IDMT/V4, V5/FLGD, duration research and protected-song execution remain closed/revealed.
- Never silently alter/drop decoded event identity or selected MIDI. Preserve `/ai-tab` UX.
- `songsterr_pipeline/` remains deterministic/model-free/process-free/network-free; DSP/model research stays under `scripts/songsterr-fresh/`.
- Fail closed: `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`, duration authority unchanged/paused, Policy C `UNENROLLED`, protected-song embargoed.
- Ordinary metadata research/coding/GitHub/CPU/checkpoint work may proceed.
- **2026-09-14 19:18 ET user authorization:** the purpose-built route is explicitly reopened and the user authorizes actions reasonably deemed necessary. Apply that authorization conservatively: design/coding/synthetic CPU CI first; procurement/spending, performer/vendor contact or hiring, calibration recording, holdout recording/data acquisition, or gated compute may proceed only when objectively necessary to advance the frozen validation plan. Do not spend/contact/acquire merely because authorization exists. V6/scoring/correctness constraints below remain unchanged.
- **Current budget override:** the user has now clarified that available budget is effectively limited to existing Vercel/model costs. Therefore no new hardware, bench equipment, audio interface, piezo system, donor instrument, performer/studio/vendor service, rights package, or other paid acquisition should be assumed available. This current budget boundary supersedes earlier language that a low-cost Stage-0 purchase should happen now.

## V6 — FROZEN

Method preregistration: `docs/checkpoints/SONGSTERR_FRESH_V6_FINAL_METHOD_PREREGISTRATION.md`, commit `f72be7635fbcadfa6e5a8ec7e193a7b9d47c7f75`.
Implementation: `scripts/songsterr-fresh/onset_birth_corroboration_v6.py`, commit `3a6cbb144fec5613ab6350deb6539297d713df28`, blob `2b18ef0ee710a6ad5ecb27253b977495db7d6534`.
External scoring framework: `docs/checkpoints/SONGSTERR_FRESH_V6_EXTERNAL_SCORING_FRAMEWORK_PREREGISTRATION.md`, commit `d46e4c5dbc35b907b71c0608a602c7c4db0d6abc`.

Frozen essentials: Basic Pitch `0.4.0`, CPU, MIDI 40..88, onset `0.5`, frame `0.3`, minimum note `127.7 ms`, bends false, melodia true; preserve every decoded event and selected integer MIDI exactly once; isolated-guitar DI evaluation path; one-to-one within-performance match onset <= `0.050 s`, pitch <= `50 cents`; V6-positive precision with one-sided 95% Wilson LB; >=`1,000` pooled V6-positive estimates; pooled Wilson LB >=`0.9900`; player/category strata with >=100 positives require point precision >=`0.9500`; frozen categories `chords`, `scales`, `singlenotes`, `techniques`, `music`; deferred correctness reveal and exactly one official correctness run.

Do not alter method/runtime/settings/matching/tolerances/gates/strata from holdout observations.

## GUITAR-TECHS — CLOSED OUTCOME C BEFORE CORRECTNESS

Immutable result checkpoint: `docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_RESULT.md`, commit `9ec1dcf396341f5e95d76a32d90183cb7f70b725`.
Official audit run `34754519541`, job `103716527380`, artifact `guitar-techs-v6-alignment-inventory`, artifact ID `10317695640`, run head `f3c9d4a88740146918c34a3538c565f21079f3bf`.

Artifact/inventory integrity was independently reverified 2026-09-14 18:27 ET:
- job `completed/success`;
- artifact live/unexpired;
- GitHub archive digest `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`;
- fresh downloaded ZIP independently SHA-256 matched the same digest;
- merged JSON SHA-256 `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`;
- 104 DI/MIDI pairs, 18,934 reference events, all 104 alignment statuses `OK`;
- structural anomalies 5 same-key overlaps + 7 unmatched note-ons;
- frozen decision `C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`; `datasetStructurallySuitable:false`.

Run status was rechecked again at 2026-09-14 19:07 ET and remained `completed/success` on the correct branch/head.

Basic Pitch/V6/correctness were never run on Guitar-TECHS. Do not score, repair/drop events, bind or rerun.

## REPLACEMENT HOLDOUT GATES

Before candidate media access all must be defensible:
1. explicit usable/permissive performance-audio rights for product validation;
2. real guitar;
3. immutable independent performed note-level onset + pitch truth, not reconstructed from evaluated audio;
4. plausible >=1,000 V6-positive capacity without duplicate/effect inflation;
5. defensible untouched status.

If all five clear, freeze corpus-specific reference-blind inventory/alignment preregistration before media access; structural audit first; reject unsuitable data without correctness. Only after a structural pass may immutable population identities be bound, controlled synthetic/contract-only harness CI run, and exactly one ordinary-GitHub-CPU external correctness run occur. No tuning/rerun after correctness exposure.

## REPLACEMENT CORPUS STATUS

No currently reviewed public candidate clears all five gates.

Closed/rejected or otherwise non-qualifying families include: Guitar-TECHS (closed C), AG-PT-set, GAPS v1.1/v2, François Leduc Guitar Dataset, EGSet12, IDMT-SMT-Audio-Effects / GUITAR-FX-DIST, EG-Solo / G&N / TENT, EG-IPT, Multimodal Electric Guitar Data, MMIP, M-M Guitar / Perez-Carrillo, GIHME, MUSMET, Klangio GST-MM-2025, EGFxSet as narrow backup only, EGDB / EGDB-PG, EGDB-NDSP, GuitarDuets, DoMP, Geoff Bremner Multimodal Music Corpus as private-license lead only, GRAUX / Water commercial packs, PolyMap, TART 2026, Five guitar dataset, SJSU Patil 2025 thesis corpus, FretboardFlow, ToneTwist AFx, GM Dataset (Chieppa et al. 2025), Semantic Timbre, and other previously logged non-qualifying synthetic/stem/robot/chord-only leads. GOAT mentions remain literature-only and do not reopen archived GOAT/reference scoring.

Latest sweep decision remains `NO_NEW_ADMISSIBLE_REPLACEMENT_HOLDOUT`. Public/institutional/commercial search is near exhausted but this is not proof that no qualifying corpus exists.

## PURPOSE-BUILT HOLDOUT — ACTIVE IN SOFTWARE, PHYSICAL ROUTE PAUSED BY BUDGET

The purpose-built independent-sensor route remains the best technically defensible design path, but the user's current budget boundary means it may advance only through zero-additional-cost software/documentation/synthetic CI. Real hardware procurement, non-holdout physical calibration and real holdout capture are paused until equivalent hardware becomes available at no additional cost or the budget constraint changes.

Design authority:
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_HOLDOUT_EXPANDED_DESIGN_2026-09-14.md`, commit `e37d2b4662db949157d2cf4797370f05648b6940`;
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_PHYSICAL_REFERENCE_SEMANTICS_V1_2026-09-14.md`, commit `ea5f50212cd1cd3794c65cb648a4d781e49e4082`;
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_CAPTURE_QA_STRUCTURAL_GATE_MATRIX_V1_2026-09-14.md`, commit `2b191b39f2f1c19564f1353381779acbc96fbeda`.

### Capture-manifest V2.1 — SYNTHETIC CI PASS

V2 historical implementation remains inherited history. It contained one demonstrated internal contradiction: a nominal valid failed-attempt -> admitted-retry fixture reused one `underlyingPerformanceId` within the same frozen slot, while V2 globally rejected any repeated underlying ID across attempts.

V2.1 fixes only that identity semantics defect while preserving all V1/V2 fail-closed boundaries:
- same-slot retries must retain the same `underlyingPerformanceId`;
- changing the underlying identity within a slot fails;
- reuse of one underlying identity across distinct slots/population units fails;
- first-transport-valid-take chronology remains inherited from V1.

Implementation: `scripts/songsterr-fresh/purpose_built_capture_manifest_contract_v2_1.py`, commit `72e8861f50680f45e586eb1e1352db59bda1f0ae`.
Synthetic tests: `scripts/songsterr-fresh/test_purpose_built_capture_manifest_contract_v2_1.py`, commit `ff5717a4aeb9b74e971694703f6d6cb785389845`.
Workflow head: `3d7f1770a3b8df0018008a49defe189db306de39`.
Successful GitHub-hosted CPU run: `34908936464`, job `104191861049`, conclusion `success`.
Detailed checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_CAPTURE_MANIFEST_V2_1_SYNTHETIC_CI_2026-09-14.md`, commit `9d3b17b392bd486753cb657318c048a7ae2460a7`.

The successful run explicitly reasserted that a nominal declaration may reach only `mayAdvanceToReferenceBlindStructuralAudit:true`; all of `authoritativeStructuralSuitabilityEstablished`, `basicPitchAuthorized`, `v6Authorized`, and `correctnessAuthorized` remain false.

Initial run `34908849001` failed because the first workflow version also required the superseded contradictory V2 test suite to pass. That demonstrated the known V2 contradiction rather than a V2.1 safety failure. The final authoritative gate runs V1 + V2.1; V2 remains inherited implementation history.

Existing eight-stage preregistration/artifact-proof governance remains historical PASS and should not be reopened absent a concrete new loophole. Successful declaration/governance never establishes source truth, structural suitability, Basic Pitch/V6/correctness authorization, model validation, customer eligibility or delivery advancement.

### Reference-blind physical-reference structural audit V1 — PREREGISTRATION FROZEN

Frozen preregistration: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_REFERENCE_BLIND_STRUCTURAL_AUDIT_PREREGISTRATION_V1_2026-09-14.md`, commit `067875e3aa1538ff5483b74cc9071b00e9e82b07`.

This preregistration was frozen before real purpose-built calibration or holdout media. It consumes only independent hardware/reference configuration, birth/dynamics stream, pitch-latch stream, and clock/sync proof plus expected SHA-256 identities. Evaluated DI/audio, Basic Pitch, V6 outputs, correctness matches and model-score data are forbidden inputs. The frozen independent-reference timing bound is `0.025 s`.

A PASS may establish only `authoritativeStructuralSuitabilityEstablished:true` for the audited reference population. Even on PASS it must leave `basicPitchAuthorized:false`, `v6Authorized:false`, `correctnessAuthorized:false`, `modelValidationComplete:false`, `customerEligibleEvents:0`, and `mayAdvanceDelivery:false` until a later separate population-binding/governance gate explicitly authorizes the one official correctness path.

### Reference-blind structural audit V1 — SYNTHETIC CI PASS

- Frozen implementation/test/workflow integration head: `8f4b41ce2cff075a6e7be25032142a0e8288b7be`; tree `6dfce1a944332f3339bfbc1ae347c8418cad1e7c`.
- Implementation: `scripts/songsterr-fresh/purpose_built_reference_blind_structural_audit_v1.py`; Git blob `18e1344b7feb3977208b97146c9882c0d0299ea9`.
- Synthetic tests: `scripts/songsterr-fresh/test_purpose_built_reference_blind_structural_audit_v1.py`; Git blob `eed135e275da2257797c62e5d99a4158afb02eaf`; local pre-commit result `24/24 PASS`.
- Workflow: `.github/workflows/songsterr-fresh-purpose-built-reference-blind-structural-audit-v1.yml`; Git blob `35fbbcda5c40bfd107d5c4136c6a68afa4d396f4`.
- Successful GitHub-hosted ordinary CPU run: `34912172056`; job `104201857367`; attempt `1`; head `8f4b41ce2cff075a6e7be25032142a0e8288b7be`; status `completed`; conclusion `success`.
- Dedicated evidence checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_REFERENCE_BLIND_STRUCTURAL_AUDIT_V1_SYNTHETIC_CI_2026-09-14.md`, commit `df7eb9edacb170ab24e2c200b1c0a8028625f87a`.
- Repository blob identities matched the exact locally tested implementation/test bytes before CI evidence was frozen.
- The audit preserves SHA-256-before-JSON ordering, exactly four independent reference-only inputs, deterministic derived MIDI/population identity, the inclusive frozen `0.025 s` bound, and all preregistered zero-anomaly blockers. Same-string overlap is audited directly from valid independent birth/string evidence so a separate latch anomaly cannot hide it.
- No real purpose-built calibration/holdout media, evaluated audio, model outputs, correctness matches, or correctness scores were accessed. Archived V143/Gomyway remains untouched and closed.
- This synthetic CI PASS does **not** establish a real holdout population. Downstream authorization remains closed: `basicPitchAuthorized:false`, `v6Authorized:false`, `correctnessAuthorized:false`, `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`.

### Real reference hardware / calibration necessity — TECHNICALLY REQUIRED, CURRENTLY BUDGET-PAUSED

Necessity + bench-gate commit: `a0279b8c48c51176678229abfa92576b1d1c0c95`.

- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_HARDWARE_CALIBRATION_NECESSITY_DECISION_V1_2026-09-14.md` establishes that physical string/fret identity, same-pitch rearticulation, real clock/sync behavior, sensor health, technique capability and real calibration identities cannot be proven from synthetic fixtures alone.
- `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_REFERENCE_HARDWARE_BENCH_QUALIFICATION_PREREGISTRATION_V1_2026-09-14.md` freezes document/API criteria and NON_HOLDOUT bench tests before any device is allowed to determine truth semantics.
- This remains a technical necessity statement, not a current spending instruction.

### Initial reference-hardware document/API screen — NO COMPLETE OFF-THE-SHELF QUALIFIER

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_REFERENCE_HARDWARE_DOCUMENT_SCREEN_V1_2026-09-14.md`, commit `39e9e0bb3667874534e6aa8cc4a8522299e0a140`.

- Current Jamstik and Fishman TriplePlay approaches derive notes through per-string pitch recognition/detection and are rejected as authoritative physical pitch-state truth.
- BOSS/Roland GK divided pickups preserve per-string vibration but not physical fret/contact state; component lead only.
- Graph Tech Ghost/Hexpander exposes a plausible six-discrete-string piezo architecture useful as an excitation-plane component, but still does not establish physical fret/contact truth.
- Historical FretTraX is the strongest commercial precedent found for string-to-fret physical scanning, but current retrofit procurement is unavailable and its developer described no right-hand/pluck detection.
- Public conductive/capacitive fret-sensing work supports feasibility of a custom physical fret/contact plane.
- Frozen result: `NO_COMPLETE_OFF_THE_SHELF_AUTHORITATIVE_REFERENCE_QUALIFIER_FOUND_IN_INITIAL_SCREEN`; `HYBRID_OR_CUSTOM_REFERENCE_ARCHITECTURE_LIKELY_REQUIRED:true`; do not buy a commercial MIDI guitar merely to treat pitch-derived MIDI as truth.

### Custom/hybrid reference prototype topology V1 — FROZEN, PHYSICAL EXECUTION PAUSED

Checkpoint: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_CUSTOM_REFERENCE_PROTOTYPE_TOPOLOGY_V1_2026-09-14.md`, commit `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`.

The frozen prototype separates four planes:
1. clean magnetic evaluated DI, never used for reference truth;
2. custom physical string/fret/contact state with raw ticks and explicit ambiguity;
3. six raw per-string excitation/vibration channels used for births/rearticulation only, never frequency-to-pitch truth;
4. common hardware audio clock plus immutable conditioned sync markers linking the physical-state logger without content alignment.

A minimum eight-channel common-audio-clock layout is explicit: 1 magnetic DI + 6 raw per-string excitation channels + 1 hardware sync-marker channel. These are architecture requirements only; no component purchase is currently authorized under the budget boundary.

Critically, the topology does not assume one continuous conductive fret can resolve chords. Cross-string electrical coupling/multi-contact ambiguity remains a mandatory future bench gate. Multiplexed conductive-fret scanning may pass or fail; electrically isolated segmented/capacitive per-string fret sensing is the defined fallback class.

### Budget constraint — SOFTWARE-ONLY ROUTE ACTIVE

Budget checkpoint: `docs/checkpoints/SONGSTERR_FRESH_BUDGET_CONSTRAINT_SOFTWARE_ONLY_ROUTE_2026-09-14.md`, commit `e7f0146d4f01605b642f8aeaa100962254b5ce58`.

Current binding boundary:
- `HARDWARE_PROCUREMENT_PAUSED:true`
- `PAID_VENDOR_CONTACT_PAUSED:true`
- `PAID_PERFORMER_OR_STUDIO_WORK_PAUSED:true`
- `REAL_CALIBRATION_CAPTURE_PAUSED:true`
- `REAL_HOLDOUT_CAPTURE_PAUSED:true`
- `SOFTWARE_DOCUMENTATION_SYNTHETIC_CI_ALLOWED:true`

The earlier minimum-BOM checkpoint `9ddb612a7dbf1ad42210514728c4af604599142b` remains useful future planning history, but its statement that Stage-0 hardware was objectively justified **now** is superseded operationally by this newer user budget constraint. Do not purchase anything for the validation route unless the user later changes this constraint or equivalent hardware is available at no additional cost.

Without either a qualifying already-existing external corpus or eventual physical reference hardware, untouched real-world external correctness cannot honestly be established. The correct response is to finish all zero-cost preparation and stop at that evidence boundary, not weaken the validation standard.

### Stage-0 contact replay V1 — SOFTWARE-ONLY SYNTHETIC CI PASS

Preregistration: `docs/checkpoints/SONGSTERR_FRESH_PURPOSE_BUILT_STAGE0_CONTACT_REPLAY_PREREGISTRATION_V1_2026-09-14.md`, commit `c5082e8357e674f401bbc37fd42961e91e5d1606`.

Implementation/test/workflow integration head: `fdcad7bcb3f48dd75630b694f7b27d23b037f016`, tree `c307456ed6e197306b252a3d0738fa9f235ee2d3`.

- Implementation: `scripts/songsterr-fresh/stage0_contact_replay_v1.py`; Git blob `14cd141aa21301887e1edf2a7d99a8dab0e43d58`.
- Synthetic tests: `scripts/songsterr-fresh/test_stage0_contact_replay_v1.py`; Git blob `956c518eef8e1ea2e1e87a42575e68dde6e636a0`; local result `16/16 PASS`.
- Workflow: `.github/workflows/songsterr-fresh-stage0-contact-replay-v1.yml`; Git blob `fd51102d34be8446eebec36ff65e5aa1a0e4afe7`.
- Successful GitHub CPU run: `34913326360`; job `104205441130`; attempt `1`; head `fdcad7bcb3f48dd75630b694f7b27d23b037f016`; status `completed`; conclusion `success`.
- Evidence checkpoint: `docs/checkpoints/SONGSTERR_FRESH_STAGE0_CONTACT_REPLAY_V1_SYNTHETIC_CI_2026-09-14.md`, commit `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`.

The Stage-0 validator accepts exactly three immutable JSON byte streams (`configuration`, `fixture`, `scanLog`) plus expected hashes; verifies SHA-256 before parsing; has no audio/model/correctness input path; detects missing/extra/crosstalk contacts, sequence/tick/drive-string/health/provenance failures; and preserves all downstream authorizations as false even on PASS.

This PASS proves only software-contract behavior. It is not evidence that any real physical sensing topology works.

## NEXT ALLOWED ACTION — START HERE IN A FRESH CHAT

1. **Verify branch + canonical state first.** Work only on `songsterr-fresh-pipeline-v1`; confirm the live head and reread this checkpoint before any mutation so concurrent commits are not overwritten.
2. **Honor the software-only budget boundary.** Do not shop for, recommend purchasing, contact vendors/performers for paid work, or plan real capture unless the user changes the budget constraint. Existing Vercel/model costs are the practical ceiling.
3. **Continue only zero-additional-cost preparation that has real future value.** Good targets include remaining deterministic reference/capture schemas, population-binding/governance code, synthetic no-real-correctness harnesses, replay/provenance validation, and GitHub CPU CI within existing available capacity.
4. **Do not redesign already-frozen gates without a concrete contradiction.** Structural preregistration `067875e3aa1538ff5483b74cc9071b00e9e82b07`, structural CI run `34912172056`, hardware-neutral bench gate `a0279b8c48c51176678229abfa92576b1d1c0c95`, prototype topology `e45e9b8c32b511d2cd7a89fbeffc8783f2f95fbf`, and Stage-0 replay preregistration `c5082e8357e674f401bbc37fd42961e91e5d1606` remain prospective authority.
5. **Keep synthetic evidence labeled synthetic.** Stage-0 run `34913326360` does not qualify hardware, calibration, a real population or correctness.
6. **Before any eventual real holdout recording, if budget/hardware later becomes available, freeze the final calibrated hardware/configuration identities, objective acquisition-QA thresholds, deterministic decoder/config, technique capability/exclusions, reference-only release rule, capture roster/population, rights/provenance and population-binding details.**
7. **For any future real admitted population, structural audit comes before correctness.** Any nonzero blocker makes that population structurally unsuitable; do not listen to DI to rescue it, repair/drop events, replace an admitted take, tune thresholds, or run Basic Pitch/V6/correctness on a failed population.
8. **Exactly one official correctness run remains the eventual maximum** after all rights, calibration, capture-manifest, structural, population-binding and governance gates pass. No tuning/rerun after correctness exposure.
9. **Keep closed lines closed.** Do not resume archived V143/Gomyway, GOAT/reference scoring, Guitar-TECHS rescue, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, protected-song execution, or other explicitly closed/revealed paths unless the user separately and explicitly reopens them.

## STILL FORBIDDEN

Guitar-TECHS correctness/repair/rescue; archived V143/Gomyway; GOAT/reference scoring; GuitarSet/V3; IDMT/V4; V5/FLGD; duration research; protected-song execution; NC/ND or otherwise restricted corpus use outside rights; rescue via evaluated-audio-derived truth; counting synthetic/effect/duplicate/simultaneous-view derivatives as independent real evidence; changing frozen V6/scoring rules from holdout observations; real-corpus optimizer/threshold sweeps or fine-tuning; treating vendor MIDI as infallible truth; purpose-built calibration/model decisions informed by admitted holdout correctness; Production/customer promotion without untouched external validation + separate policy review; **and under the current user budget constraint, all new validation-route hardware/performance/vendor/studio spending is paused.** Heavy GPU remains unnecessary.

## FRESH-CHAT HANDOFF

Continue only on `songsterr-fresh-pipeline-v1` and begin by rereading this file. Guitar-TECHS remains closed outcome C before correctness; V6 method/scoring remain frozen; no replacement-holdout correctness has been exposed.

Capture-manifest V2.1 remains synthetic GitHub CPU PASS at run `34908936464`, job `104191861049`. Reference-blind structural-audit V1 remains synthetic GitHub CPU PASS at integration head `8f4b41ce2cff075a6e7be25032142a0e8288b7be`, run `34912172056`, job `104201857367`. Stage-0 contact replay V1 is now also synthetic GitHub CPU PASS at head `fdcad7bcb3f48dd75630b694f7b27d23b037f016`, run `34913326360`, job `104205441130`, with evidence checkpoint commit `8ecc0601f84c4f7916ce1a8c08ac021fc425be25`.

The user's budget is currently limited to existing Vercel/model costs, so the purpose-built physical route is **software-prepared but hardware-paused**. The immediate task in a fresh chat is to continue only zero-additional-cost software/documentation/synthetic CI that reduces future discretion. Do not buy hardware, recruit performers, run real calibration/holdout capture, Basic Pitch, V6 or correctness. Keep `basicPitchAuthorized:false`, `v6Authorized:false`, `correctnessAuthorized:false`, `modelValidationComplete:false`, `customerEligibleEvents:0`, `mayAdvanceDelivery:false`, duration paused, Policy C `UNENROLLED`, and protected-song execution embargoed. Do not reopen V143/Gomyway or GOAT/reference scoring unless separately explicit.
