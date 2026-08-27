# V147 Phase C — Pre-Audio Workflow Guard Repair Preregistration

Status: **FROZEN AFTER PROCEDURAL PREFLIGHT FAILURE, BEFORE REPAIR**

Branch: `v143-contextual-prune-lobo`

## Consumed failure

The first repository-native Phase-C pre-audio workflow execution is consumed:

- workflow creation/run commit `d523387cbbca0ab3b97d03beee93e0cae6d5527f`
- workflow blob `1ebe1a637d16aed29a6583538b98533f14dfbd75`
- run `33036467967`
- job `98400119788`
- conclusion `failure`

Frozen source-identity verification passed. The job then stopped in the procedural `Prove workflow has no real-audio or reference input` step before pytest or the generated proof harness executed.

The cause is self-matching negative grep: the workflow searched its own text for the forbidden calibration-reference filename and historical raw-audio SHA while embedding those exact forbidden strings inside the grep commands themselves. Therefore the guard necessarily found itself and exited non-zero.

No generated tests or proof executed; no candidate or proof payload was produced; no real audio was supplied/read/decoded; no reference/gold was opened; no calibration score ran; no Modal/GPU or Production path was used.

## Frozen repair scope

Exactly one workflow-only behavioral repair is authorized:

Replace the two self-matching negative grep assertions with a small inline Python guard that:

1. reads `.github/workflows/v147-phase-c-pre-audio-proof.yml` as text;
2. constructs each forbidden string at runtime from multiple string fragments so the complete forbidden string is not itself present literally in the workflow source;
3. asserts the reconstructed forbidden calibration-reference filename is absent from the workflow source;
4. asserts the reconstructed historical raw-audio SHA is absent from the workflow source.

The existing `test ! -e debug/v147-phase-c-real-audio` assertion remains unchanged.

No other workflow behavior may change.

## Identities that MUST remain unchanged

- Phase-C prereg blob `5c19ed572d17cc9a760f1b63ee03c1b2c4543d30`
- Phase-C clarification blob `6ced1bae4cdaad8306b008827657afbb27a87dbc`
- V145 decoder blob `2fd979aebb4685e86c7f24a0162f69de306c06e9`
- V147 pitch hypothesis blob `49bce8b968406bb0d61ab61394954ef8a8303eb7`
- Phase-C support blob `f4278ffaacaca3f66baf7a3112e2af0f3bc387cf`
- Phase-C tests blob `e99f791cd0ab401a9e393ab9b89a6b167cee3c7f`
- Phase-C proof harness blob `531384706b8b7444cf7ed22f414b47215e59b653`
- canonical helper `088d44827fb23e20d9aeeb4944a672989af5846c`
- selected V144 transform helper identities already frozen in the Phase-C checkpoint.

## Explicitly forbidden repair changes

- no changes to generated test/proof cases or expectations;
- no threshold/window/CQT/evidence/fingering/reconstruction changes;
- no change to accepted family #10;
- no audio input, decoding, waveform/CQT analysis, or real-song candidate construction;
- no calibration/reference/gold access;
- no Modal/L4/GPU;
- no main/Production/frontend/Bass/Lead changes;
- no replay of consumed run `33036467967`.

## Repaired execution rule

After the workflow-only repair is committed and its new blob is checkpointed, allow exactly one fresh repository-native CPU/generated/reference-free pre-audio execution. This is the first execution permitted to reach the frozen tests/proof because attempt #1 never reached them.

If the repaired execution reaches the generated tests/proof and they fail, STOP. Do not retune or run a second generated proof under this repair.

If it succeeds, persist exact proof/runtime/run evidence, checkpoint, delete/seal the one-use workflow, checkpoint again, and STOP before real-audio decoding/analysis.
