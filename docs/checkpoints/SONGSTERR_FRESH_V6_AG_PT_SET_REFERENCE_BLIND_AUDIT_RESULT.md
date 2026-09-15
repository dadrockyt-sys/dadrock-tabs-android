# Songsterr Fresh V6 — AG-PT-set reference-blind audit RESULT

Date: 2026-09-15 (America/Toronto)
Branch: `songsterr-fresh-pipeline-v1`
Status: **FROZEN DECISION C — NO V6 CORRECTNESS EXECUTED**

## Frozen authority

This result closes the reference-blind structural/alignment/inventory audit frozen in:

`docs/checkpoints/SONGSTERR_FRESH_V6_AG_PT_SET_REFERENCE_BLIND_AUDIT_PRE.md`

PRE commit: `0a84d6be1373d538b251663b1fa7af8f33bbf378`.

The audit was explicitly reference-blind with respect to model correctness. It did not authorize Basic Pitch or V6 correctness and it did not change the frozen V6 method or scoring rules.

Guitar-TECHS decision C remains closed. GuitarJam, URMP, GAPS, and EGDB remain closed pre-media rejections. This result does not reopen V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, V5/FLGD, duration, protected songs, `main`, Production, reserved GFN splits, or physical calibration/capture.

## Execution history

The workflow file was added at commit `1d37950d03e26af6fcdf3a905aa08e2f863ee878` with both `workflow_dispatch` and a path-scoped `push` trigger. That commit itself therefore started the first audit automatically.

### Authoritative first-started audit

- workflow: `.github/workflows/songsterr-v6-ag-pt-reference-blind-audit.yml`
- head commit: `1d37950d03e26af6fcdf3a905aa08e2f863ee878`
- run: `35020989444`
- job: `104556302921`
- attempt: `1`
- run conclusion: `success`
- artifact: `10418038649`
- artifact ZIP size: `562394` bytes
- artifact ZIP SHA-256: `eefea849f7431ffa20262ce5e1b893dd96ae93f2df0d695b59b056c257f495e4`

A subsequent commit `6125e000a16a0bb44dfa69721f2120d75e8cfc63` (`trigger frozen AG-PT-set reference-blind audit`) started a second duplicate audit while the first was still running.

### Duplicate execution — not additional evidence

- head commit: `6125e000a16a0bb44dfa69721f2120d75e8cfc63`
- run: `35021035914`
- job: `104556457264`
- attempt: `1`
- run conclusion: `success`
- artifact: `10417543492`
- artifact ZIP size: `562394` bytes
- artifact ZIP SHA-256: `4d55de96b83db084a08862125c8f8444bd2d3a641d4b93552c741757c692e549`

The ZIP container digests differ because the artifact ZIPs were produced by separate runs, but every inner audit file is byte-identical between the two executions. The second execution is preserved as history only and must never be treated as an independent validation replicate.

## Frozen source identity observed

The audit downloaded the already-frozen Zenodo archive identity:

- candidate: AG-PT-set v1
- Zenodo record: `10.5281/zenodo.10159492`
- archive member: `aGPTset_z.zip`
- size: `6749621615` bytes
- MD5: `1dff8103f9ad6e1a86cee2e5e39cbe87` — exact match to the PRE
- SHA-256: `6d03ee80f53e64e703b64f58526b6465264032fcc195aea9ad1058a7ebefba64`

Annotation table located:

- path: `aGPTset/metadata/note_labels.csv`
- SHA-256: `75502d20e5149641eb4d3449240413673ace6885a5c822df38760df422e98fa1`
- rows: `32592`
- released fields observed:
  - `onset_label_seconds`
  - `audio_file_path`
  - `onset_label_samples`
  - `expressive_technique_id`
  - `pitch_midi`
  - `frequency_aubiopitch`
  - `string_number`
  - `string_openpitch_midi`
  - `isPercussive`
  - `playing_intensity`
  - `measured_loudness`

The frozen row filter admitted `24180` rows as pitched/onset-labeled candidates.

## Structural result

The frozen resolver could not bind any admitted row's released `audio_file_path` value to exactly one archive `.wav` member.

Observed:

- admitted reference rows: `24180`
- admitted WAVs: `0`
- total anomalies: `24180`
- fatal anomalies: `24180`
- fatal anomaly type: `missing_or_ambiguous_audio`
- sample rates inspected: none
- channels inspected: none
- source WAVs opened for structural inspection: `0`

Representative released `audio_file_path` values in the frozen artifact include bare filenames such as:

`acoustic_guitar_pitched_allstring1_naturalharmonics_mf_DavRos_20200820.wav`

Every admitted row remained unresolved under the frozen exact/suffix path-binding rule.

Because no scoring WAV identity could be bound, the audit never reached source-WAV timing consistency or signal/onset alignment inspection. This is therefore a **source-pairing structural C**, not a V6 correctness failure and not evidence that the underlying audio itself is unsynchronized.

The artifact also contains some integer `pitch_midi` values outside the conventional MIDI `0..127` range. The PRE does not permit post-access reinterpretation of a released reference field, so no alternate semantic mapping is invented here. This is not needed to reach C because the frozen source-pairing gate already failed.

## Frozen decision

Decision: **C**

Frozen reason:

`structural timing/source anomaly requires fail-closed rejection`

Operational interpretation: the audit could not establish the exact released reference-row -> source-WAV pairing required by the PRE. Under the frozen A/B/C rule, AG-PT-set therefore does not advance to V6 scoring in this attempt.

Do not repair the resolver and rerun this frozen audit as though the C result never happened. Any new AG-PT-set structural-binding experiment would require a new prospective PRE and explicit authorization appropriate to that new data access.

## No correctness exposure

Both executions report:

- `referenceBlind:true`
- `basicPitchRuns:0`
- `v6Runs:0`

Therefore:

- no Basic Pitch inference occurred;
- no V6 correctness occurred;
- no candidate correctness was observed;
- no V6 constant changed;
- no matcher tolerance changed;
- no Wilson statistic changed;
- no scoring/admission rule changed;
- no EGFxSet execution occurred;
- no V143/Gomyway activity occurred.

## Artifact identities

The following inner files are byte-identical between runs `35020989444` and `35021035914`:

- `result.json` — SHA-256 `a7b4602540bfb9762f7960d92479a2ec1c32666f712a0e57a950f26da375bf5d`
- `anomalies.json` — SHA-256 `7c9eec18858ce0445d71e6ed8241f9f6f89a5bf289891d2889429b2c0d8f627f`
- `reference-events.json` — SHA-256 `9e32df0a0ce364022a28fa71370f975fcc3a3626f27ff5b9ff9f87b825f0cba4`
- `population.json` — SHA-256 `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- `audio-identities.json` — SHA-256 `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`

Canonical hashes reported by `result.json`:

- population manifest SHA-256: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- reference-event manifest SHA-256: `ec1e0e843aca37cb497285d91f2d763505d2cbee9962f08e9321a9f9eb0605a3`
- audio-identity manifest SHA-256: `4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945`
- alignment-decision manifest SHA-256: `10fa23bd4e74d9361ac3fdcc1f20314891b0c979f526b0ebcb6b1002ce05439f`

## Delivery state — unchanged

- `realCalibrationAuthorized:false`
- `realHoldoutCaptureAuthorized:false`
- `basicPitchAuthorized:false`
- `v6Authorized:false`
- `correctnessAuthorized:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`

Duration remains paused. Policy C remains `UNENROLLED`. Protected-song execution remains embargoed.

## Next safe direction

Under the PRE's frozen outcome-C rule, AG-PT-set is closed for this audit attempt. Continue only metadata/license/alignment/provenance search for another untouched real-guitar holdout unless the user explicitly authorizes a new prospectively frozen AG-PT-set structural-binding experiment.

Do not rerun this workflow, Basic Pitch, V6 correctness, EGFxSet, V143/Gomyway, or any other closed real-media/model line without the required explicit authorization.
