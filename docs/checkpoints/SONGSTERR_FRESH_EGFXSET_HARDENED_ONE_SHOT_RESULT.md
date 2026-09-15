# Songsterr Fresh — EGFxSet Hardened One-Shot RESULT

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: `FAIL_HARDENED_NON_AUTHORIZING_DIAGNOSTIC`

## Authority

Prospective PRE: `docs/checkpoints/SONGSTERR_FRESH_EGFXSET_HARDENED_ONE_SHOT_PRE.md`
PRE commit: `8b741a8b25b61966c832860f4d91f42a018f898e`

The user's `Please try the run again` authorization has been consumed by exactly one execution. No retry was performed.

## Execution

Workflow: `.github/workflows/songsterr-egfxset-hardened-one-shot.yml`
Workflow commit: `bba6f954d55d54ce0bf660214a059b695c57481d`
Run: `34938917218`
Job: `104282855445`
Attempt: `1`
Workflow conclusion: `failure` because the frozen score failed.

Artifact:
- id `10384459031`
- name `songsterr-egfxset-hardened-one-shot`
- ZIP SHA-256 `a0a6a0021726c40fd4c2381c118a90e85105117b6689cfdc393e7e282a89f3a9`
- `result.json` SHA-256 `6bc52feef13bcdec57b76721eef87ebf94a157b7d4d0a8f4f08590ba95178a06`
- `qualification.json` SHA-256 `784579dd791136424142bb899455cfc6c9242fd8cc2a3efba9c8b11dfa342e85`
- `qualified-evidence.json` SHA-256 `06be0871b9548290061089508d91ce702562ed132ceb9f2ac62367992a287a83`
- `adapted-evidence.json` SHA-256 `9ec94bea1a00e15e848e60a3b1a5d7a414334a9093c5385916d9dc9688ac1e59`

## Input verification

All immutable inputs passed verification:
- prior Basic Pitch artifact ZIP SHA-256 `c380d39bdee5c3ec2827c1ae682e83b71eabe3bc738fa27016d3bb409afe566a`
- `basic-pitch.json` SHA-256 `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`
- note identity SHA-256 `2e30685479444a8120dc3490c9c41329a89e57aa16979de42053b89a4bbb0444`
- raw immutable proposals `[40,68]`
- EGFxSet member SHA-256 `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`
- exact WAV duration `5.0 s`, source sample rate `48000 Hz`, sample count `240000`

No Basic Pitch inference occurred in this run.

## Script execution

All processing stages completed successfully:
- dependencies: success
- immutable model artifact fetch/verification: success
- media fetch/verification: success
- carrier context: success
- independent DSP qualifier: success
- qualified evidence builder: success
- adapter/evaluator: success

The failure is a scored data/qualification outcome, not an infrastructure failure.

## Observed qualification

The qualifier produced exactly two rows, both `rejected`:

### MIDI 40 — genuine labelled E2 proposal

- start `0.011609977324263039 s`
- status `rejected`
- V6 classification `not-onset-birth-corroborated`
- reason `OK_SELECTED_TEMPLATE_NOT_PHYSICALLY_PLAUSIBLE`
- source-domain onset sample after 44.1 kHz resampling: `512`
- required left context samples: `3584`
- deterministic left zero-padding applied: `3072` samples
- analysis RMS `0.29340840126382345`
- innovation energy `75.56575652709044`
- necessity fraction `0.0`

### MIDI 68 — extra harmonic-like proposal

- start `0.3599092970521542 s`
- status `rejected`
- V6 classification `not-onset-birth-corroborated`
- reason `OK`
- left zero-padding `0`
- analysis RMS `0.22146136772942196`
- innovation energy `3.007380617012349`
- necessity fraction `0.000513675778819313`

Candidate confidence was not read for either decision.

## Frozen score

- `PASS_INPUTS`
- `FAIL_QUALIFICATION`
- `FAIL_PROMOTION`
- `FAIL_POSITION`
- overall `FAIL_HARDENED_NON_AUTHORIZING_DIAGNOSTIC`

Raw proposals `[40,68]` were preserved. Rejected evidence preserved `[40,68]`. Zero events promoted. Unresolved onset count was zero because both proposals were explicitly rejected.

## Interpretation

The hardened pipeline successfully solved the original **extra MIDI-68 auto-promotion** weakness: MIDI 68 was rejected and preserved rather than promoted.

However, the run exposed a new general weak point at the **left clip boundary**. The genuine MIDI 40 onset occurs only ~11.6 ms after clip start, while the inherited onset-birth classifier requires ~81.3 ms of left context at 44.1 kHz. The wrapper supplied 3072 samples of synthetic zero pre-context. The classifier then rejected the genuine note on the harmonic-template physical-plausibility/necessity test.

This means the current boundary policy is too strong: deterministic zero-padding made the event numerically evaluable, but it did not provide genuine physical pre-onset evidence. A near-start proposal should not be allowed to become a confident negative merely because missing real pre-context was replaced by zeros.

Do not weaken thresholds or hand-promote MIDI 40 from this observation. Do not rewrite this FAIL into a PASS.

## Next engineering direction

Before any new real-media execution, freeze and test a **boundary-aware qualification policy** using synthetic/non-EGFxSet fixtures. At minimum, fabricated left context must not be treated as sufficient evidence for a hard negative. A boundary-safe positive classifier, if introduced, must be independently specified and synthetically tested before another real run.

Any subsequent real-media rerun requires new explicit user authorization.

Global authorization fields remain false/zero and the historical all-events smoke remains `FAIL_NON_AUTHORIZING_SMOKE`.
