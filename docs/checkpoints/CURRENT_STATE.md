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
**Test Score: NOT RUN.**

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

## Songsterr public AI-transcription observation — ACTIVE REFERENCE-BLIND RESEARCH

Dedicated checkpoint: `docs/checkpoints/SONGSTERR_PUBLIC_AI_TRANSCRIPTION_OBSERVATION_20260903.md`, creation commit `4210b1e6d1ec44fcbb0833d3411118924fd8706b`.

Status: **PUBLIC-OBSERVATION ONLY / NO SONGSTERR PRIVATE OR PAID DATA / NO REFERENCE SCORE CALLS**.

Public Songsterr `/new` currently exposes first-bar time signature, pickup-bar duration, first-bar BPM, triplet feel, instrument Auto/Adjust, separate vocals/rhythm-guitar/lead-guitar/bass/drums targets, and per-guitar/bass tuning/capo controls. Songsterr Help describes the AI output as a draft opened in its editor; a public August 2026 r/Songsterr reply attributed to the Songsterr team says current work has focused on existing instruments and `measure structure`.

This independently motivates architectural investigation of:

1. first-class meter/tempo/downbeat/pickup structure before final tab quantization;
2. instrument-conditioned transcription/routing rather than one generic pitch detector;
3. tuning/capo-conditioned or joint fret/string inference;
4. possible source-separation/routing as a hypothesis only — **no claim** that Songsterr uses any specific separator/model/vendor;
5. draft + editor/uncertainty product flow rather than treating first-pass generation as final.

Current original `analyzer/modal_analyzer.py` directly calls Basic Pitch on whole normalized audio, performs post-hoc fret assignment, and returns `tempo=None` and `timeSignature=None`, making the public Songsterr structure controls a genuinely independent architecture clue rather than a threshold tweak derived from GuitarSet outcomes.

This observation **does not reopen GuitarSet development and does not authorize a V6 threshold sweep or any reference-facing score call**. Before any such score call, a separate checkpoint must freeze a genuinely new reference-blind candidate hypothesis/implementation.

## NEXT SAFE ACTION

1. **Await explicit GOAT owner approval/denial.** On approval/denial follow the already frozen V168 procedures; do not substitute another holdout source.
2. While GOAT remains unavailable, inventory existing DadRock experimental code for already-built reference-blind tempo/downbeat/meter, stem-routing, and tuning-aware modules so the Songsterr clue does not cause duplicate work.
3. Separate already-exhausted experiments from genuinely new architecture suggested by the public Songsterr control surface.
4. If a real new architecture gap exists, freeze its reference-blind design in a dedicated checkpoint **before** any frozen-reference score call.
5. Do not resume SplitMySong or GuitarSet threshold development while waiting.

## Standing methodology

- Open-corpus development cannot mutate V168.
- CPU only; fresh explicit authorization before GPU/CUDA/Modal.
- Never modify/merge/promote `main` or Production without explicit user direction.
- Save checkpoint before/after each scientific boundary and immediately on GOAT approval/denial.
