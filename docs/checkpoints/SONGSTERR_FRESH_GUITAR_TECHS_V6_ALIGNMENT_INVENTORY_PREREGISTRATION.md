# Songsterr Fresh — Guitar-TECHS V6 Alignment / Inventory Preregistration

Status: **FROZEN BEFORE ANY GUITAR-TECHS BASIC PITCH / V6 CORRECTNESS RESULT**

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`

## Purpose

This audit determines whether Guitar-TECHS can become an untouched real-audio external holdout for V6 and, if so, freezes its population, source identities, reference-event semantics and audio/MIDI alignment before any Basic Pitch/V6 correctness is computed.

This is an inventory/alignment audit only. It MUST NOT invoke Basic Pitch, V6, any admission classifier, or any estimate-to-reference correctness matcher.

## Authority boundary

This audit cannot change:
- `modelValidationComplete:false`
- customer-eligible events `0`
- `mayAdvanceDelivery:false`
- duration authority paused/unchanged
- Policy C `UNENROLLED`
- protected-song embargo
- Production state.

It does not reopen FLGD/V5, GuitarSet/V3, IDMT/V4, archived V143/Gomyway, GOAT/reference scoring or duration research.

No Modal, Vercel heavy-GPU or L4 run is authorized by this document.

## Public source identity

Dataset: **Guitar-TECHS: An Electric Guitar Dataset Covering Techniques, Musical Excerpts, Chords and Scales Using a Diverse Array of Hardware**.

Canonical public record used for this audit:
- Zenodo record `14963133`
- public version label `v1`
- published 2025-04-06
- record page `https://zenodo.org/records/14963133`
- project site `https://guitar-techs.github.io/`
- license stated by project site: CC BY 4.0.

Top-level Zenodo packages and published MD5 identities:
- `P1_chords.zip` — `be9ef8bbdceb1912d565254e607a6d94`
- `P1_scales.zip` — `9c0b98e8fb42a522df727ea8bf545e4f`
- `P1_singlenotes.zip` — `ca0c4674dde3805574685a313f7c39eb`
- `P1_techniques.zip` — `18634a41a6db5a8de10d07eb3122a872`
- `P2_chords.zip` — `eb6f74dd19162237189281688ad7ad2e`
- `P2_scales.zip` — `96664853872f51e5f8aa4447313b7cf5`
- `P2_singlenotes.zip` — `40fbf03d8b04bb2cf42df20f36dc2254`
- `P2_techniques.zip` — `f4189251ce50be25f06a173b2c2bba00`
- `P3_music.zip` — `071ba80aecf00f4a31fbd167b3f22198`.

Any acquired archive MUST match its published MD5 before its contents are used.

## Published structure / recording semantics

Public materials state:
- three professional guitarists;
- DI, miked-amplifier, egocentric and exocentric audio perspectives;
- Fishman Triple Play Connect multi-track pickup for per-string MIDI note capture;
- Player 01/02 provide notes/techniques/chords/scales; Player 03 provides musical excerpts;
- public site states signals and MIDI are synchronized;
- Zenodo additionally warns that signal paths may exhibit up to 100 ms misalignment and recommends correction for alignment-critical applications.

Zenodo previews show package structures with matching semantic basename families such as:
- `audio/directinput/directinput_<item>.wav`
- `audio/micamp/micamp_<item>.wav`
- `midi/midi_<item>.mid`
- `video/ego/ego_<item>.mp3`
- `video/exo/exo_<item>.mp3`.

`__MACOSX`, `.DS_Store` and AppleDouble `._*` entries are packaging metadata and are excluded structurally.

## Primary audio path — frozen before data alignment values

The primary candidate scoring audio path is **direct input (`audio/directinput`) only**.

Reason fixed before correctness:
- DI captures the guitar electrical output before amplifier/microphone coloration;
- public recording description places DI and amp-mic capture on the audio-interface path, while ego/exo are separate video-device audio captures;
- V6 requires precise onset-local evidence, making the least acoustically/transport-delayed path preferable.

Amp-mic/ego/exo signals may be inventoried as metadata but MUST NOT become alternate scoring paths after correctness is observed.

## Inventory rules

For each archive, inventory without model inference:
1. verify archive MD5;
2. enumerate all non-packaging entries;
3. identify DI WAV, amp WAV, ego/exo audio and MIDI entries;
4. pair DI and MIDI strictly by semantic basename after removing only the fixed prefixes `directinput_` and `midi_` plus extensions;
5. require zero ambiguous duplicate DI or MIDI basenames;
6. record unpaired DI and unpaired MIDI items rather than silently dropping them;
7. record WAV sample rate, channel count, sample count, duration and sample subtype/bit depth;
8. parse MIDI structural metadata: format, tracks, PPQ/time division, tempo events, channels, note-on/off edges, pitch range and per-track/channel note counts;
9. pair note-on/off deterministically by MIDI standard semantics; any orphan/overlap anomaly must be reported before correctness and cannot be silently repaired.

No file may be excluded based on model behavior or future correctness.

## Reference note semantics

Reference note onset/pitch truth comes only from the dataset MIDI paired with the DI item.

MIDI timing must be converted under standard SMF tempo semantics. Sustain/pedal logic is not introduced unless explicitly present and relevant in the Guitar-TECHS MIDI structure discovered by this audit.

For future onset/pitch admission scoring, offsets/durations remain non-authoritative unless separately preregistered; this audit may record durations structurally but grants no duration authority.

Per-string track/channel identity may be retained for future strata/diagnostics, but V6 classification MUST NOT consume string identity.

## Alignment audit — frozen algorithmic boundary

The published <=100 ms warning makes raw MIDI timestamps insufficiently trustworthy for a <=50 ms correctness tolerance without an explicit alignment decision.

Alignment is therefore estimated **without Basic Pitch/V6 predictions** from the paired DI waveform and reference MIDI onsets only.

### Audio onset envelope

For each paired DI file:
- convert to float64;
- if mono, use directly; if multichannel, arithmetic-mean channels to mono;
- retain native sample rate for alignment measurement;
- require finite nonempty samples;
- use 2,048-sample Hann frames with 256-sample hop;
- compute magnitude FFT at the next power of two >= 2,048;
- frame novelty is positive spectral flux: sum of positive bin-wise magnitude differences from the preceding frame;
- normalize the resulting novelty sequence by its L2 norm when nonzero.

### MIDI onset envelope

- convert every valid MIDI note-on onset to seconds under standard tempo semantics;
- create an impulse sequence on the same 256-sample-hop time grid as the DI novelty sequence;
- simultaneous onsets are counted once per distinct onset time for alignment, so chord size does not dominate the correlation;
- convolve the impulse sequence with a symmetric Gaussian kernel with standard deviation 10 ms;
- L2-normalize when nonzero.

### Constant-lag estimate

For each paired recording:
- evaluate normalized dot-product correlation for MIDI-vs-DI lags from `-150 ms` through `+150 ms` inclusive;
- lag candidates are integer audio-envelope hops (256/native-sample-rate seconds);
- choose the unique lag with maximum correlation; exact ties fail the per-file alignment audit rather than selecting by correctness;
- report best lag, best correlation and the next-best correlation outside a +/-2-hop exclusion around the winner;
- do not use any Basic Pitch/V6 event or correctness information.

This audit may observe the resulting lag distribution because alignment—not model correctness—is the subject under study.

## Alignment decision rules

After all structurally paired files in the audited population are measured, freeze one of these outcomes before correctness:

A. **Raw timestamps authoritative** only if every measured absolute best lag is <= one 256-sample hop.

B. **Deterministic per-file constant offset correction authoritative** if the audit yields unique finite lag estimates and the correction rule above is structurally valid. The exact per-file lag manifest must then be frozen by hash before correctness.

C. **Dataset unsuitable for V6 admission** if alignment cannot be resolved reference-blindly or structural anomalies prevent a defensible immutable reference population.

No later correctness result may change an A/B/C decision or any lag.

## Population boundary

The audit begins with all semantic DI/MIDI pairs present in the exact v1 packages. It does not preselect only easy monophonic files.

Category/player counts and potential strata are inventory outputs only. Any future external scoring preregistration must freeze whether all valid paired categories are pooled or whether a category is excluded for a **pre-correctness structural reason** (for example, reference pitch semantics incompatible with integer-MIDI onset/pitch scoring). Such decisions must be made before Basic Pitch/V6 correctness.

## Forbidden during this audit

Do not:
- invoke Basic Pitch;
- invoke V6 on Guitar-TECHS audio;
- compute estimate/reference matches, precision, recall or correctness;
- inspect protected-song behavior;
- compare Guitar-TECHS outcomes to FLGD/IDMT/GuitarSet correctness;
- tune V6 constants from Guitar-TECHS audio/reference agreement;
- select files/categories based on anticipated model performance;
- change matching tolerances/admission bars;
- use amp/ego/exo as alternate post-result rescue paths;
- run Modal, Vercel heavy-GPU or L4 without explicit user authorization.

## Required audit output

Write an immutable result containing:
- exact Zenodo record/version and package MD5 verification state;
- complete structural entry counts;
- DI/MIDI basename pairing manifest hash;
- WAV-format summary;
- MIDI-structure summary and anomalies;
- reference-event count/pitch range by package/category/player;
- alignment lag per pair and lag-manifest hash;
- alignment outcome A/B/C;
- exact proposed scoring population identity if suitable;
- explicit confirmation that no Basic Pitch/V6 correctness was computed.

Only after this immutable audit result exists may a final V6 external-scoring preregistration be written.
