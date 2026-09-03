# STRUCTURE_INSTRUMENT_CONDITIONING_V1 — PHASE 1 RESULT

Date: 2026-09-03 UTC  
Branch: `v143-contextual-prune-lobo`  
Status: **`PHASE1_REFERENCE_BLIND_CONTRACT_PASS / NO_ACCURACY_CLAIM / NO_REFERENCE_SCORE`**

## Purpose

Close Phase 1 of the independently specified Songsterr-inspired DadRock architecture work after the schema/plumbing and deterministic contract tests passed on the isolated research branch.

This checkpoint does **not** claim transcription-accuracy improvement and does **not** reconstruct Songsterr's private implementation.

## Frozen predecessor

Pre-implementation freeze:

`docs/checkpoints/SONGSTERR_STRUCTURE_INSTRUMENT_CONDITIONING_V1_PREIMPLEMENTATION_FREEZE_20260903.md`

Creation commit:

`29ef4f7e131e35378a58abb4cf68095bd284c075`

The T1–T10 test expectations and scientific boundaries were fixed before implementation.

## Implementation

### Pure conditioning contract

Commit `a36235371441e2e1209335dd4017093a2aa0da7a`

Added `lib/aiTabConditioningV1.mjs` with:

- `conditioning.version=1` normalization;
- Auto/manual structure prior validation for tempo, time signature, pickup and feel;
- lead/rhythm/bass role validation;
- standard guitar/bass defaults;
- arbitrary valid physical open-string MIDI tuning;
- separate capo fret;
- fail-closed role/tuning/structure validation;
- server-owned reference-blind dual-context provenance.

### API plumbing

Commit `71beaa8a947ede8a706d28c48bf9bd26852aeb3c`

`app/api/analyze-audio-tab/route.js` now:

- validates/normalizes optional Conditioning V1 after transcription-type validation;
- returns HTTP 400 for invalid conditioning;
- forwards the **normalized** conditioning object to the already-selected analyzer;
- leaves analyzer selection unchanged;
- leaves the V143 anti-leakage gate unchanged;
- appends a server-owned `conditioningContract` after analyzer payload normalization;
- never trusts analyzer-returned conditioning to authorize scoring or provenance.

The historical `analyzer/modal_analyzer.py` was inspected and intentionally left unchanged. It reads only the request fields it needs and tolerates the additional `conditioning` member. No Modal redeployment was required or performed.

### Deterministic verifier

Commit `2444a0528fa21dcb69dd490ab43ddd1adc132f97`

Added `analyzer/verify_ai_tab_conditioning_v1.mjs`, covering the frozen T1–T10 cases:

1. default Lead;
2. default Bass;
3. explicit 96 BPM / 6/8 / pickup 1.5 / triplet structure;
4. Drop D + capo 2 preserved separately;
5. role mismatch fail closed;
6. invalid tuning fail closed;
7. invalid structure fail closed;
8. normalized analyzer forwarding while route selection remains unchanged;
9. server-owned reference-blind dual-context provenance;
10. legacy/V143 safety preserved.

### Existing end-to-end gate extension

Commits:

- `d4304cb63c95d025b2943b338a4ac17b86f0a98d`
- `6769391329dfac08c2c199fb7e5f91ba5f576d0f`
- `81caf0f59e69c7df95622f2b0909133d432ecb74`
- `ab84f27bcd55990fadbc824cfc8ad883e786d971`

The branch-only AI Tab end-to-end verifier now requires Conditioning V1 wiring, reference-blind status, zero reference authorization, dual-context provenance, legacy Lead/Bass preservation and V143 fail-closed behavior.

Workflow commit `7ce26de92e4018d8849f07d3b57ee82c7e030784` added the Conditioning V1 verifier as the first test stage.

## Intermediate workflow failures — verifier maintenance, not Conditioning V1 failures

### Run `33803596381` / job `100808640322`

- Conditioning V1 T1–T10 stage: **PASS**.
- Existing end-to-end stage: **FAIL** because a stale source-text assertion expected `renderEvents.length > 0` in the professional renderer.
- Actual current renderer is stricter: authenticated V143 Rhythm explicitly throws when `renderEvents.length === 0`, preventing legacy downgrade.
- Assertion was aligned to the current stricter fail-closed implementation; production code was not weakened.

### Run `33803890711` / job `100809606751`

- Conditioning V1 T1–T10 stage: **PASS**.
- Existing end-to-end stage: **FAIL** because another stale source-text assertion expected `referenceFree` alone to gate structured render events.
- Actual current payload code requires the complete `v143RuntimeSafetyVerified` contract before projecting structured render events.
- Assertion was aligned to the current stricter fail-closed implementation; production code was not weakened.

These failures did not use any reference corpus and did not trigger an analyzer.

## Final deterministic result

GitHub Actions run: `33804010524`  
Job: `100810007255`  
Tested implementation head: `ab84f27bcd55990fadbc824cfc8ad883e786d971`  
Conclusion: **SUCCESS**

Successful stages:

- Verify reference-blind Conditioning V1 — PASS;
- Verify complete AI Tab product wiring — PASS;
- Enforce compact safety evidence — PASS;
- Commit compact contract evidence — PASS.

The workflow committed compact evidence as:

`22b0bf3661b251eddeb9e41f0f844683ba2d3ca6` — `Record AI Tab end-to-end contract`

Evidence path:

`debug/v143-contextual-prune/ai-tab-end-to-end-contract.json`

Evidence blob SHA:

`8bf20c176c27edb01cca649c36e8ac144c3d684a`

Evidence asserts:

- `conditioningV1Wired=true`;
- `conditioningV1ReferenceBlind=true`;
- `conditioningV1ReferenceScoreAuthorized=false`;
- `dualContextProvenanceWired=true`;
- Lead legacy path preserved;
- Bass legacy path preserved;
- V143 Rhythm route fail closed;
- V143 structured renderer fail closed;
- no manufactured structured placement for legacy output;
- no payment attempt;
- no token redemption;
- no customer email;
- no Vercel deployment attempt;
- `productionModified=false`;
- `productionPromotionAuthorized=false`.

## Scientific accounting

During Phase 1:

- GuitarSet read for this implementation/testing: **false**;
- SplitMySong read: **false**;
- restricted GOAT bytes read: **false**;
- reference-facing score calls: **0**;
- Modal analyzer invoked: **false**;
- GPU/CUDA used: **false**;
- Production modified: **false**.

No accuracy metric is produced from this result. Contract correctness is not evidence of transcription-quality improvement.

## Phase 1 conclusion

Phase 1 successfully establishes the information contract needed for the independently motivated dual-context architecture:

```text
full mixture -> future global structure context
role/carrier  -> local note evidence
                    |
structure prior + instrument config
                    |
          future conditioned fusion
```

The current analyzer may ignore Conditioning V1; that is expected for Phase 1. The request/response boundary is now ready for a separately frozen, shadow-only Phase 2 that deterministically applies explicit structure and tuning/capo to copied event projections without changing generated tablature or V143 historical outputs.

## Next safe action

Before Phase 2 code:

1. freeze `STRUCTURE_CONDITIONED_SHADOW_PROJECTION_V1` separately;
2. keep Auto structure unresolved rather than inventing tempo/meter;
3. use only deterministic synthetic/reference-blind fixtures;
4. append shadow metadata only — never overwrite `generatedTab`, `events`, `renderEvents`, `measureGrid` or `analysisEngine`;
5. keep `referenceScoreAuthorized=false`, `productionEligible=false`;
6. do not use GuitarSet, SplitMySong or GOAT;
7. keep CPU-only/no-Modal/no-GPU and `main`/Production untouched.
