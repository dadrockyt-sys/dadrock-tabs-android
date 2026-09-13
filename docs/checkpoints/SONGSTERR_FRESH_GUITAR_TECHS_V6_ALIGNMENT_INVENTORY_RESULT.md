# Songsterr Fresh — Guitar-TECHS V6 Alignment/Inventory Result

Status: **IMMUTABLE REFERENCE-BLIND AUDIT RESULT — OUTCOME C / REJECT FOR V6 ADMISSION**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Ordering / authority

This result records the already-preregistered Guitar-TECHS reference-blind inventory/alignment audit. It was produced before any Guitar-TECHS Basic Pitch or V6 correctness run. It does not change the frozen V6 method or external-scoring framework.

Frozen preregistration: `docs/checkpoints/SONGSTERR_FRESH_GUITAR_TECHS_V6_ALIGNMENT_INVENTORY_PREREGISTRATION.md`, commit `29818b9bfcb11b0da2b3e9efb57c5f2cd51193ae`.

Frozen audit source: `77510e2e797915166a5737750769824e44c49e89`.

Official workflow: `.github/workflows/songsterr-fresh-guitar-techs-v6-alignment-inventory.yml`

Official run: `34754519541`
Official job: `103716527380`
Conclusion: `success`

All controlled pre-package guards, all nine package audits, merged-result generation, fail-closed boundary verification and artifact upload completed successfully.

## Artifact integrity

Artifact name: `guitar-techs-v6-alignment-inventory`
Artifact ID: `10317695640`
GitHub artifact size: `44,242` bytes
GitHub artifact archive digest: `sha256:d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`
Downloaded ZIP SHA-256: `d6e4395f815ce51e1ae83ebdd5c770ca6cd485bb7e90e150dc0e7f7944bf4125`
Merged JSON: `guitar-techs-v6-alignment-inventory.json`
Merged JSON SHA-256: `ffd7e44d0e65c53dbdafc948e51f8f15810dbbd628100e3226eec4a2fc3a04ab`

The downloaded archive hash exactly matched GitHub's published artifact digest.

## Exact package identities

| Package | Preregistered/verified MD5 | Archive SHA-256 | DI/MIDI pairs | Reference events |
|---|---|---|---:|---:|
| `P1_chords.zip` | `be9ef8bbdceb1912d565254e607a6d94` | `de4aa76ef4b86ce981496161b741dc39bd22dec5250da351e5e68a44da249326` | 28 | 4,429 |
| `P1_scales.zip` | `9c0b98e8fb42a522df727ea8bf545e4f` | `79d7e9d148820867a9095697c9521e40a4b11c198384edfce1951de7219b3509` | 12 | 3,627 |
| `P1_singlenotes.zip` | `ca0c4674dde3805574685a313f7c39eb` | `130592ae5555476ea8e4070c0f3421794ef8b5e252dfa780745d07eedd0eb4a4` | 1 | 142 |
| `P1_techniques.zip` | `18634a41a6db5a8de10d07eb3122a872` | `1e4b80a464182d345e129f3e1158b6c05690c60b5f9be4bde3fb26f23263236e` | 5 | 629 |
| `P2_chords.zip` | `eb6f74dd19162237189281688ad7ad2e` | `9d4a46261cc840d6a66412ad0ebffcfba1fbce579bec0205127190b7bd7a4bce` | 28 | 4,022 |
| `P2_scales.zip` | `96664853872f51e5f8aa4447313b7cf5` | `d5efc7134764bd8124a712fd301d020d143a6e589eb8e1f2e0ddcbf94524ff17` | 12 | 3,490 |
| `P2_singlenotes.zip` | `40fbf03d8b04bb2cf42df20f36dc2254` | `d6b54e40d22113d6c0a663165cb2af63735897a35bb45fc6d0ed49c944b548d9` | 1 | 137 |
| `P2_techniques.zip` | `f4189251ce50be25f06a173b2c2bba00` | `05fc065c010add9e5348095d7198fdc45b967c657e3e12ef8afdb74808371816` | 5 | 510 |
| `P3_music.zip` | `071ba80aecf00f4a31fbd167b3f22198` | `033489e22600751fb5a1633e7d856b901c6782e0486fa02135e830780d9dbfe2` | 12 | 1,948 |

All nine preregistered archive MD5 checks passed.

## Population / structure

Packages: `9`
Paired DI/MIDI performances: `104`
Paired reference note events: `18,934`
Reference pitch range observed: MIDI `38..93`
Unpaired DI count: `0`
Unpaired MIDI count: `0`

WAV sample-rate counts:
- `48,000 Hz`: `102`
- `44,100 Hz`: `2`

WAV channel counts:
- mono: `44`
- stereo: `60`

WAV subtype: `PCM_24` for all `104` pairs.

MIDI format: type `1` for all `104` files.
Ticks per beat: `960` for all `104` MIDI files.

Alignment status: `OK` for all `104` pairs.

## Frozen MIDI anomaly result

Merged anomaly totals:
- `sameKeyOverlapCount`: `5`
- `unmatchedNoteOffCount`: `0`
- `unmatchedNoteOnCount`: `7`

Package distribution:
- `P1_chords.zip`: 1 unmatched note-on
- `P2_chords.zip`: 4 same-key overlaps and 6 unmatched note-ons
- `P2_techniques.zip`: 1 same-key overlap
- all other packages: zero recorded MIDI anomalies

Under the preregistered merger, structural suitability requires all archive MD5s valid, no unpaired DI/MIDI files, **and total MIDI anomaly count equal to zero**. The nonzero anomaly total therefore makes `datasetStructurallySuitable:false` even though every pair received an `OK` reference-blind alignment estimate.

## Alignment lag result

Alignment-status counts: `OK: 104`.

Frozen lag summary:
- count: `104`
- minimum: `-8` hops = `-0.042666666666666665 s`
- maximum: `+10` hops = `+0.05333333333333333 s`
- median: `-5` hops = `-0.026666666666666665 s`
- all absolute lags within one hop: `false`

Lag-hop distribution:
- `-8`: 1
- `-7`: 2
- `-6`: 22
- `-5`: 39
- `-4`: 24
- `-3`: 2
- `+6`: 1
- `+7`: 4
- `+8`: 3
- `+9`: 4
- `+10`: 2

These lags are audit facts only. Because outcome C rejects the dataset, they do not authorize a V6 scoring correction or correctness run.

## Immutable manifest identities

Pairing identity manifest SHA-256: `24ff1b4eef07f28eb678f38fbec80f8cc26668329812868a89992e20eb73efa7`

Alignment lag manifest SHA-256: `95b244d78014e20ea0f468ecf88aacf90e8442f4aef675b246845202d98fcc84`

Proposed scoring population SHA-256: `bd239d63ba39a370f7c9e09df544b3b207596acf523b09e2be57bbc49cf0b765`

These identities are retained for reproducibility only; the proposed population is **not approved for scoring**.

## Frozen A/B/C decision

Official merged decision:

`C_DATASET_UNSUITABLE_FOR_V6_ADMISSION`

`datasetStructurallySuitable:false`

This follows the preregistered rule. The audit did not fail because of model correctness; model correctness was never run. The dataset is rejected at the reference-blind structural/alignment gate.

Therefore:
- do not run Basic Pitch on Guitar-TECHS for V6 correctness;
- do not run V6 correctness on Guitar-TECHS;
- do not create an A/B binding checkpoint for Guitar-TECHS;
- do not repair/drop anomalous reference events post hoc to rescue this holdout;
- do not tune V6, Basic Pitch, matching, thresholds, lags, gates, or population from these observations;
- search only metadata/license/structure/alignment for a new untouched real-guitar holdout before any new correctness exposure.

## Policy boundary verified by artifact

- `basicPitchInvoked:false`
- `v6Invoked:false`
- `correctnessComputed:false`
- `protectedSongUsed:false`
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- `durationAuthorityChanged:false`

Policy C remains `UNENROLLED`; duration authority remains paused/unchanged; protected-song execution remains embargoed; Production remains unchanged.
