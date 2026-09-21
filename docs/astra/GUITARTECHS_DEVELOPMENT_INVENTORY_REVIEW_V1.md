# Guitar-TECHS P1/P2 development inventory review V1

Date: 2026-09-21  
Scope: authorized P1/P2 development media only  
P3: sealed and untouched  
Training: not authorized

## Evidence boundary

The full inventory workflow run `35563511409` re-downloaded all eight already hash-frozen P1/P2 archives, verified exact published byte count + MD5 + Astra SHA-256 before extraction, inspected directory/file layout, WAV headers and Standard MIDI File structure only, then deleted extracted media. All eight matrix jobs completed successfully.

The original P2-chords job completed successfully but its job-log backing blob was unavailable during evidence collection. Recovery run `35563847021` repeated only the already-authorized P2-chords inventory path, re-verified all three frozen byte identities before extraction, uploaded a short-lived receipt artifact, and deleted the media. Artifact `10623565422` has digest `sha256:7e7cf64058903eed463f4e066b0896d0241022d0fae0f8d371e577618bb813f1`.

No alignment, feature generation, model import, training, P3 access, main change, Production change or customer-delivery authorization occurred.

## Grouping result

Across P1 and P2 the eight development archives contain **92 underlying performance groups** and 460 visible files. Each performance group has one MIDI label file and the same correlated capture families:

- audio: `directinput`, `micamp`
- video/audio perspective files: `ego`, `exo`

Every inspected MIDI file is Standard MIDI File format 1 with PPQ 960.

This clears the extracted performance-grouping and capture-view-grouping uncertainty for P1/P2 development material.

## String-track mapping

The project-owned Guitar-TECHS site states that a Fishman Triple Play Connect multi-track MIDI pickup captured MIDI notes independently from each string. Extracted MIDI files expose note-bearing track names from the canonical set:

`e`, `B`, `G`, `D`, `A`, `E`

Single-note, scale and technique files use conductor track 0 plus the six string tracks at indices 1–6. **Chord files cannot use track index as string truth.** Unplayed string tracks can be omitted, so later string tracks shift index. The label pipeline must map string identity from the explicit MIDI track name and fail closed on an unknown/duplicate string name.

## Tuning evidence

P1 single-note labels directly expose minima `64, 59, 55, 50, 45, 40` on `e, B, G, D, A, E`, respectively. This freezes P1 standard tuning evidence as E2-A2-D3-G3-B3-E4.

P2 single-note minima are `64, 59, 55, 51, 45, 40`. Five open strings are directly evidenced, but the P2 D-string open MIDI 50 is **not** observed in the single-note inventory; the minimum there is 51. The reviewed official dataset website does not state tuning explicitly. Therefore Astra does not infer D3 by convenience: full P2 tuning remains unresolved and P2 absolute-fret label generation must remain fail-closed until independent tuning evidence is frozen.

## Technique-MIDI semantics

The five named technique performances for both P1 and P2 are `Bendings`, `Harmonics`, `PalmMute`, `PinchHarmonics`, and `Vibrato`.

The technique MIDIs contain **zero MIDI pitch-bend events**, including `Bendings` and `Vibrato`. Conversely, P2 scale MIDIs contain many pitch-bend controller events, and two P2 chord files contain 128 pitch-bend events in total. Pitch-bend-event presence therefore cannot be treated as a semantic bend/vibrato label.

For V1 note/fret development:
- primary: chords, scales, ordinary single notes, PalmMute;
- auxiliary/held out: Bendings, Harmonics, PinchHarmonics, Vibrato until a separate trustworthy technique-label contract exists.

## Gate result

Frozen receipt: `docs/astra/GUITARTECHS_DEVELOPMENT_INVENTORY_EVIDENCE_V1.json`  
Receipt SHA-256: `4d21d578a275587abe18d9f5382074fa9c33bd2f0698c5d10b340788de306bcd`

Cleared:
- P1/P2 performance grouping verified;
- correlated capture-view grouping verified;
- explicit string-track naming rule frozen;
- technique MIDI semantics reviewed;
- P1 tuning verified.

Still blocked:
- P2 D-string tuning not fully verified;
- alignment correction not verified;
- development metric thresholds not frozen;
- real training not authorized;
- model not trained;
- P3 final gate remains sealed;
- lead/rhythm distinction still requires separate role evidence;
- customer delivery remains unauthorized.
