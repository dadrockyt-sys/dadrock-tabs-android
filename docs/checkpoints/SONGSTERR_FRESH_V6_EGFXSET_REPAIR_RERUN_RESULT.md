# Songsterr Fresh V6 — EGFxSet Repaired One-Shot Result

Date: 2026-09-15 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: `FAIL_NON_AUTHORIZING_SMOKE_PITCH_POSITION`

## Authority and scope

The user explicitly instructed `Please fix and rerun` after the original one-shot failed during TFLite initialization. That instruction authorized exactly one repaired, non-authorizing rerun of the same frozen EGFxSet candidate.

Prospective repair freeze checkpoint:
`docs/checkpoints/SONGSTERR_FRESH_V6_EGFXSET_REPAIR_RERUN_PRE.md`
commit `779313c06382bd875fe314d798d149c4208b3141`.

This run does not authorize V6 correctness, model validation, customer eligibility, delivery, tuning, another retry, alternate candidates, or any closed/reserved dataset line.

## Frozen candidate — unchanged

- dataset: EGFxSet version 1.0
- Zenodo DOI: `10.5281/zenodo.7044411`
- archive: `Clean.zip`
- published archive MD5: `cdb1b401960f56becc8640387910e78a`
- member: `Clean/Bridge/6-0.wav`
- exact member bytes: `722976`
- exact member SHA-256: `0256fd3c55c577970a4c2a06d760cf5798591adecffaa5e790addc38d1f0378e`
- independent physical label: string `6`, fret `0`
- expected MIDI: `40` (E2)

The repaired run reverified both the archive MD5 and exact member SHA-256 before inference.

## Frozen repaired environment

The only intended repair was dependency compatibility:

- Python `3.10.21`
- Basic Pitch `0.4.0`
- TFLite Runtime `2.14.0`
- NumPy `1.26.4`
- CPU only

All exact version checks passed before media access.

Basic Pitch settings were unchanged:

- minimum MIDI `40`
- maximum MIDI `88`
- onset threshold `0.5`
- frame threshold `0.3`
- minimum note length `127.7 ms`
- bends false
- melodia true

## Frozen scoring — unchanged

The same pre-output rule remained binding:

- exactly one inference invocation;
- no listening, waveform inspection, trimming, denoising, EQ, gain tuning, threshold changes, output-driven adjustments, alternate candidates, or second repaired attempt;
- `PASS_RUNTIME`: inference completes and produces parseable output;
- `PASS_PITCH`: decoded output is non-empty and the complete set of emitted MIDI values is exactly `{40}`;
- `PASS_POSITION`: every emitted event maps uniquely to string 6, fret 0, reconstructed MIDI 40;
- overall PASS requires all three.

No event selection or after-the-fact filtering is permitted by this smoke contract.

## Execution identity

Workflow:
`.github/workflows/songsterr-egfxset-repaired-one-shot.yml`

Workflow commit:
`b37d400b186a926985bb16b91702e2f88e55d785`

GitHub Actions run:
`34936227380`

Job:
`104274605954`

Attempt:
`1`

Artifact:
`10383413992`, `songsterr-egfxset-repaired-one-shot`

Artifact ZIP SHA-256:
`c380d39bdee5c3ec2827c1ae682e83b71eabe3bc738fa27016d3bb409afe566a`

Artifact file SHAs:

- `result.json`: `5f1f78c7c9bd153d98ad31854c29aa46c6a200a763fbf49292320752a9b239b9`
- `basic-pitch.json`: `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`
- `media.json`: `3f48ef861df5a2aa57dfd010d191e3b22f5ecadb767cacbe1cb55f5bf393614c`

## Runtime result

All runtime gates passed:

- checkout: PASS
- Python 3.10.21: PASS
- repaired dependency installation/version verification: PASS
- archive download: PASS
- archive MD5: PASS
- exact member extraction: PASS
- exact member SHA-256: PASS
- exact member byte count: PASS
- single Basic Pitch invocation: PASS
- scorer: PASS
- artifact upload: PASS

`predictInvocationCount` in the produced Basic Pitch artifact is exactly `1`.

Therefore the NumPy/TFLite repair successfully fixed the original runtime incompatibility.

## Observed Basic Pitch output

The primary decoded artifact contains exactly **2 note events**.

### Event 1

- note id: `basic-pitch-note-000000`
- start: `0.011609977324263039 s`
- diagnostic model end: `4.948418140589569 s`
- MIDI: `40`
- confidence: `0.7906091809272766`
- deterministic mapping: unique string `6`, fret `0`, reconstructed MIDI `40`

This event matches the independent EGFxSet physical label.

### Event 2

- note id: `basic-pitch-note-000001`
- start: `0.3599092970521542 s`
- diagnostic model end: `1.5325170068027212 s`
- MIDI: `68`
- confidence: `0.3487236797809601`

MIDI 68 is not the frozen expected MIDI 40. Under the unchanged deterministic mapper it has multiple playable positions and therefore cannot satisfy the required unique string-6/fret-0 physical-position rule.

Observed MIDI histogram:

- MIDI `40`: `1`
- MIDI `68`: `1`

Complete emitted MIDI set:
`{40,68}`

## Frozen score

- dependency outcome: `success`
- media outcome: `success`
- inference outcome: `success`
- primary output present: `true`
- primary output SHA-256: `24bffdb267c580625cb8049bdbe6bc1b74549ae8e048a759f26eb24e49d6dc51`
- note count: `2`
- unique MIDIs: `[40,68]`
- runtime: `PASS_RUNTIME`
- pitch: `FAIL_PITCH`
- position: `FAIL_POSITION`
- overall: `FAIL_NON_AUTHORIZING_SMOKE`

## Interpretation

This repaired run is materially different from the original runtime failure. The model executed successfully and did recognize the intended E2/MIDI-40 note, but it also emitted an additional MIDI-68 note. Because the scoring rule was frozen before output and explicitly required **all emitted MIDI values** to equal `{40}`, the extra event causes a genuine diagnostic smoke failure.

Do not discard or post-filter the MIDI-68 event after observing it. Do not retune thresholds from this result. Do not reinterpret the matching MIDI-40 event alone as a PASS.

This one-file result is non-authoritative and statistically insufficient for correctness claims. It does not replace the physical calibrated holdout.

## Authorization effects

Unchanged:

- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

The repaired one-shot authorization is now consumed. No additional inference/retry/tuning/candidate change is authorized by the user's prior instruction.

## Next allowed state

Preserve this result as diagnostic evidence. The authoritative validation route remains the frozen physical calibrated holdout, which is still budget-paused.

Any further smoke experiment, threshold study, event-filtering study, alternate-candidate run, or repaired rerun requires new explicit prospective scope/authorization. Archived V143/Gomyway remains closed unless the user explicitly asks to reopen it.
