# CURRENT STATE — DadRock `/ai-tab`

Updated: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`

> Compact continuation checkpoint. Dedicated checkpoints under `docs/checkpoints/` remain authoritative for detailed history; omission here does not revoke earlier frozen boundaries.

## V168 / GOAT — unchanged scientific state

**V168 = `HOLDOUT_ASSET_MISSING / SCORING_NOT_ARMED`. V167 = CLOSED / TERMINAL.**

- GOAT restricted access request for Zenodo `15690894` / DOI `10.5281/zenodo.15690894` v1 is awaiting explicit owner approval/denial.
- No restricted GOAT bytes admitted; V168 prospective reference-facing score calls = **0**.
- Frozen V168 Policy A/B, validators, GOAT integrity/selection contract and promotion gate unchanged.
- No GOAT candidate/scorer adapter armed. `main` / Production untouched.
- CPU only; fresh explicit authorization required immediately before GPU/CUDA/Modal.

**Project Progress Score: 60%.**  
**Test Score: REFERENCE-BLIND CONTRACT PASS; ACCURACY SCORE NOT RUN.**

## Immutable prior boundaries

V167 promoted I005 Guitar F1 **42.7940586109996%**; highest unpromoted gap1 earliest **42.88012872083669%**, +**0.08607010983709418pp**, below frozen +0.10pp; no I006.

SplitMySong remains terminal `FAIL_CLOSED_NO_CANDIDATE`: exactly one private observation, 1421/1471 required steps covered, 50 missing, candidate=false, referenceRead=false, scorerRead=false. Never rerun/score/weaken/interpolate.

## GuitarSet immutable candidate source

Original V3 candidate artifact remains the only frozen prediction/evidence source used by V3/V4/V5:

- original run `33581322528`;
- manifest SHA256 `4568ca0c5f25ba11f17074b43b21e135eb44357c04a963266c61457038120a83`;
- artifact ID `9828683652`;
- ZIP SHA256 `1031aaf913b6292ee961051fed76b91bf003139ab6d3f8db1dad5d0dded270c5`.

Prospective GuitarSet players `00/01/03` remain sealed.

## GuitarSet V3/V4 — terminal history

V3 terminal `NO_DEVELOPMENT_SIGNAL`.

V4 discovery selected `H72-D035` on players `02/04`, but frozen one-shot player-05 confirmation failed:

- run `33584451308`, job `100105524472`;
- 91 changed pitches across 60 tracks;
- primary macro **-0.0701653918423375 pp**;
- primary micro **-0.05407451468121849 pp**;
- strict50 micro **-0.0540745146812327 pp**;
- 1 positive / 56 neutral / 3 negative primary-TP tracks;
- terminal `V4_PLAYER05_CONFIRMATION_FAIL`.

Confirmation report SHA256 `3feb63042c670690221901906045520f17faa01d02a461c01b805ea68867d722`; artifact ID `9829578804`; ZIP SHA256 `556d301e3466a9f6064d52ccd3e37410b492fac147e20e7833ed8bde65dff300`.

Never rerun/retune V4.

## GuitarSet V5 — TERMINAL `NO_V5_CROSS_PLAYER_DEVELOPMENT_SIGNAL`

All `02/04/05` were explicitly development for V5; `00/01/03` stayed sealed.

Frozen family: 48 reference-blind octave-down configs over pitch floor `{72,76,79}`, max duration `{0.20,0.25,0.30,0.35}`, consensus `1.00`, median advantage `{0.05,0.10,0.15,0.20}`.

Run `33584851641`, job `100106765017`: **SUCCESS**.

- 177 development tracks (`02=59`, `04=58`, `05=60`);
- 28,115 reference events;
- baseline primary macro F1 **80.3621313923964%**;
- baseline primary micro F1 **76.62482566248256%**;
- 48 configs scored;
- **0 configs qualified**;
- selected config = `null`;
- status `NO_V5_CROSS_PLAYER_DEVELOPMENT_SIGNAL`.

Result report SHA256 `445a79dba3992c0989f244046eca4d0fc855c3aff8d6f2e043054f3a04c87dda`; artifact ID `9829749729`; ZIP SHA256 `018a9bdcce7cbd2b58e6f2dce13a168c335d69b6649d34fa7c299aeb1e9326c2`.

Descriptive near-signal only: `P79-D035-M005` had combined primary micro **+0.020921 pp** and macro **+0.022795 pp**, but player `02` changed only 2 pitches and had exactly `0.000000 pp` primary-micro gain. It failed the frozen >=5-changes/player and strictly-positive-every-player requirements. This does not authorize retuning.

Terminal result checkpoint `docs/checkpoints/OPEN_CORPUS_V5_GUITARSET_CROSS_PLAYER_DEVELOPMENT_RESULT_20260902.md`, creation commit `a338fbfcf51c871608af83fc470e09dd9b41c7ca`.

V5 development score calls = **1 / terminal for this family**. V5 prospective evaluation processed=false; prospective score calls=0. Never rerun or retune this V5 family.

## GuitarSet development hold — FROZEN

Status: **`GUITARSET_OPEN_CORPUS_DEVELOPMENT_HOLD`**.

Checkpoint `docs/checkpoints/OPEN_CORPUS_GUITARSET_DEVELOPMENT_HOLD_20260902.md`, creation commit `16ba4df1cf2195c0d8cf0050574335e078064429`.

Purpose: stop repeated threshold rescue/mining on the same `02/04/05` development references after V3 no-signal, V4 confirmation failure and V5 zero-qualified cross-player family.

Until a separately justified reopen checkpoint exists:

- do not create V6 by sweeping neighboring thresholds derived from V5 outcomes;
- do not mine V5 per-track/per-event reference outcomes for a rescue gate;
- do not weaken V5 qualification rules;
- do not rerun V3/V4/V5;
- do not reinterpret player `05` as an independent holdout;
- keep prospective `00/01/03` sealed and out of model/feature/threshold selection.

A valid reopen requires genuinely independent motivation fixed before any new GuitarSet reference-facing score call. Recovering a small V5 near-signal alone is not sufficient.

GuitarSet prospective evaluation score calls remain **0**.

## GOAT pre-access gap audit — COMPLETE

Checkpoint `docs/checkpoints/V168_GOAT_PREACCESS_GAP_AUDIT_20260902.md`, creation commit `bb74b64f4a6be8cbab2da46569161c37f2bc09ab`.

Audit result: **`GOAT_PREACCESS_IMPLEMENTATION_COMPLETE / AWAIT_OWNER_DECISION`**.

The existing access/grant provenance rules, complete-base-DI inventory requirement, source/reference SHA256 binding, frozen 50 ms onset-EOF integrity rule, deterministic Tier 1/Tier 2 selection contract, metadata-only selection validator, base manifest validator and provenance validator already cover the full pre-access admission path.

No additional receipt generator/template was added: the exact receipt shape is already embodied and self-tested inside `validate_goat_selection_receipt_v168.py`; duplicating it before real v1 inventory exists would add schema-drift risk.

The absence of a GOAT candidate generator and GOAT/new-song scorer is intentional, not a gap. Do not build either before actual access/admission.

## Songsterr public AI-transcription observation — REFERENCE-BLIND CLUE CAPTURED

Dedicated observation checkpoint: `docs/checkpoints/SONGSTERR_PUBLIC_AI_TRANSCRIPTION_OBSERVATION_20260903.md`, creation commit `4210b1e6d1ec44fcbb0833d3411118924fd8706b`.

Architecture-gap inventory: `docs/checkpoints/SONGSTERR_ARCHITECTURE_GAP_INVENTORY_20260903.md`, creation commit `592762183301a8767cba75c1c9e280a83ab4aa19`.

Dual-context hypothesis: `docs/checkpoints/SONGSTERR_DUAL_CONTEXT_TOPOLOGY_HYPOTHESIS_20260903.md`, creation commit `8da294acc7d5e503fe7b193bf3903caed3d0beca`.

Status: **`DUAL_CONTEXT_TOPOLOGY_INDEPENDENTLY_MOTIVATED / NO SCORE AUTHORIZATION`**.

Public Songsterr `/new` currently exposes first-bar time signature, pickup-bar duration, first-bar BPM, triplet feel, instrument Auto/Adjust, separate vocals/rhythm-guitar/lead-guitar/bass/drums targets, and per-guitar/bass tuning/capo controls. Songsterr Help describes the AI output as a draft opened in its editor; a public August 2026 r/Songsterr reply attributed to the Songsterr team says current work has focused on existing instruments and `measure structure`. A public 2026 Songsterr ML-engineer listing describes production automatic music transcription using `our models` and names Python/PyTorch plus Accelerate/DeepSpeed/W&B in the training stack.

A January 2026 publicly indexed r/Songsterr reply in a thread addressed to Songsterr's developer says the service uses `our models`, performs source separation `under the hood`, and that supplying pre-separated tracks can make **measure-structure prediction harder**. The exact Reddit author identity was not independently authenticated here, so this is treated as a public architecture clue rather than source-code proof.

Repository inventory shows the individual component ideas are not all new:

- original `analyzer/modal_analyzer.py`: full-mix Basic Pitch + post-hoc fixed-standard-tuning fret assignment;
- `analyzer/modal_analyzer_v34.py`: conservative onset-gap beat interval/tempo estimation and pulse-aware harmonic windows;
- `analyzer/build_v7_measure_grid_projection.py`: measure/beat/sixteenth projection;
- prior V143/Backing Track Studio work: Demucs six-source and related carrier/separation paths.

Therefore **do not** treat `add Demucs`, `add tempo`, `quantize to measures`, or another GuitarSet threshold sweep as the Songsterr-derived new idea.

The independent architecture gap is now more specific:

1. end-to-end **`STRUCTURE_INSTRUMENT_CONDITIONING_V1`** — explicit structure priors/estimates (meter, pickup, tempo, triplet feel) plus role/tuning/capo configuration carried through interpretation, quantization and string/fret decoding;
2. **dual-context topology** — preserve the normalized full mix for global structure evidence while any separated/role-specific carrier supplies local note evidence, then fuse those contexts before measure alignment/tab decoding.

This is an architecture hypothesis inspired by public behavior, **not a claim about Songsterr's exact private model topology**. There is still no credible public evidence identifying their exact separator, transcriber architecture, loss functions, training corpus, fingering solver or thresholds.

These checkpoints **do not reopen GuitarSet development and do not authorize a V6 threshold sweep or any reference-facing score call**.

## STRUCTURE_INSTRUMENT_CONDITIONING_V1 — PHASE 1 COMPLETE

Pre-implementation freeze: `docs/checkpoints/SONGSTERR_STRUCTURE_INSTRUMENT_CONDITIONING_V1_PREIMPLEMENTATION_FREEZE_20260903.md`, creation commit `29ef4f7e131e35378a58abb4cf68095bd284c075`.

Result checkpoint: `docs/checkpoints/SONGSTERR_STRUCTURE_INSTRUMENT_CONDITIONING_V1_PHASE1_RESULT_20260903.md`, creation commit `a79ea4e1d62b2dfaeadac165703bf1e2315dd56f`.

Status: **`PHASE1_REFERENCE_BLIND_CONTRACT_PASS / NO_ACCURACY_CLAIM / NO_REFERENCE_SCORE`**.

Implementation:

- `a36235371441e2e1209335dd4017093a2aa0da7a` — pure `lib/aiTabConditioningV1.mjs` validation/default/provenance contract;
- `71beaa8a947ede8a706d28c48bf9bd26852aeb3c` — analyzer API normalization, fail-closed validation, normalized forwarding and server-owned response contract;
- `2444a0528fa21dcb69dd490ab43ddd1adc132f97` — deterministic frozen T1–T10 verifier;
- `7ce26de92e4018d8849f07d3b57ee82c7e030784` — branch-only workflow wiring;
- end-to-end verifier maintenance commits `d4304cb63c95d025b2943b338a4ac17b86f0a98d`, `6769391329dfac08c2c199fb7e5f91ba5f576d0f`, `81caf0f59e69c7df95622f2b0909133d432ecb74`, `ab84f27bcd55990fadbc824cfc8ad883e786d971`.

Final deterministic evidence:

- run `33804010524`;
- job `100810007255`;
- tested head `ab84f27bcd55990fadbc824cfc8ad883e786d971`;
- conclusion **SUCCESS**;
- evidence bot commit `22b0bf3661b251eddeb9e41f0f844683ba2d3ca6`;
- `debug/v143-contextual-prune/ai-tab-end-to-end-contract.json` blob SHA `8bf20c176c27edb01cca649c36e8ac144c3d684a`.

The two preceding end-to-end failures were stale source-text assertions in the old verifier. In both runs the new Conditioning V1 T1–T10 stage itself passed. The assertions were aligned to the already stricter current V143 fail-closed renderer/payload code; no safety gate or product code was weakened.

Phase 1 evidence confirms Conditioning V1 wiring, reference-blind status, no reference-score authorization, dual-context provenance, Lead/Bass legacy preservation, V143 Rhythm fail-closed safety, no manufactured structured placement for legacy output, no payment/token/email/deployment side effects, `productionModified=false` and `productionPromotionAuthorized=false`.

No corpus/reference read or score was performed by this work. GuitarSet/SplitMySong/GOAT were not used; GOAT restricted bytes remain unread. No Modal analyzer was invoked, no GPU was used, and Production was not modified.

## NEXT SAFE ACTION

1. Freeze a separate **`STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1`** Phase 2 contract before code.
2. Phase 2 may deterministically project copied analyzer events using explicit structure priors and tuning/capo, but must remain shadow-only: do not overwrite `generatedTab`, `events`, `renderEvents`, `measureGrid` or `analysisEngine`.
3. If structure remains Auto/unresolved, do not invent tempo/meter; report `UNRESOLVED_AUTO_STRUCTURE`.
4. Use synthetic/reference-blind fixtures only; no GuitarSet, SplitMySong or GOAT reads/scores.
5. **Await explicit GOAT owner approval/denial.** On approval/denial follow the already frozen V168 procedures; do not substitute another holdout source.
6. Keep CPU-only/no-Modal/no-GPU and `main`/Production untouched unless the user gives fresh explicit direction.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
