# Pixabay Bass Provenance and Classification Review V1

Date: 2026-10-02
Branch: `astra-work`
Status: **PROVENANCE REVIEW / NO MODEL EXECUTION**

This review follows `PIXABAY_BASS_AUDIO_CATALOG_V1.md`.

## 1. Current Pixabay license basis

Pixabay's current Terms state that non-CC0 downloaded Content receives an irrevocable, worldwide, non-exclusive, royalty-free right to use, copy, modify or adapt the Content for commercial or non-commercial purposes, subject to prohibited uses.

Important restrictions include:
- no sale/distribution of Content on a standalone basis;
- do not imply ownership/exclusive rights;
- third-party rights can still matter;
- responsibility for determining any additional permissions rests with the user.

Pixabay's FAQ recommends retaining records of downloads, including filenames and source URLs.

For this project, the intended use is private software development/evaluation and derived metrics—not redistribution of the MP3s. Audio remains outside Git.

This is a project documentation review, not legal advice.

## 2. Exact provenance retained

Every uploaded filename contains a Pixabay asset ID suffix. Those IDs are now treated as the stable primary provenance key even when a human-readable asset-page slug is not yet frozen.

Examples already verified on current Pixabay pages/search results:
- 43631 — Electric bass guitar loop 2 bpm 110
- 43630 — Electric bass guitar loop 4 bpm 110
- 101327 — Bass Guitar Death Metal loop 240 bpm
- 490941 — Bass Riff Am 106bpm
- 490940 — Funk Rock Slap Bass Riff Em 106bpm
- 490938 — Emotional Bass Riff In Bm 106BPM
- 90288 — slap_bass
- 108236 — bass G2
- 108235 — bass B2
- 78680 — bass60bpm
- 107704 — bassriff2

The remaining asset IDs are still preserved in their filenames and can be resolved directly before benchmark admission.

## 3. Conservative instrument-type classification

This classification is intentionally based on asset title/tags and collection context. It is not a claim of independently verified recording technique.

### Strong physical-bass candidates

These titles directly identify bass guitar, fretless bass, picked bass, P-bass, or string-note material:

- B01 43631 Electric bass guitar loop 2 bpm 110
- B02 43630 Electric bass guitar loop 4 bpm 110
- B06 101327 Bass Guitar Death Metal loop 240 bpm
- B12 100710 Picked_BassNote_A
- B15 98127 Simple P bass slap loop 100 bpm
- B19 101274 Bass Guitar_C2 [RAW]
- B20 100754 Fretless bass, open D, bridge pickup
- B21 43765 Bass Guitar three notes
- B22 77384 distorted bass note guitar string
- B23 77385 bass note guitar string
- B24 34323 distorted bass note guitar string #2

### Probable physical-bass candidates

Titles strongly suggest performed bass but do not specify instrument construction in the title:

- B04 39561 Bass Slide
- B05 93230 bass B1
- B07 490941 Bass Riff Am 106bpm
- B08 490940 Funk Rock Slap Bass Riff Em 106bpm
- B09 490938 Emotional Bass Riff In Bm 106BPM
- B10 100708 Rock_BassLine_Gm
- B11 30321 Bminor_Rock_BassGroove_120bpm
- B13 37245 Em Electric Bassline
- B14 308711 Funky Bassline 02
- B16 90288 slap_bass
- B17 108236 bass G2
- B18 108235 bass B2
- B25 75423 slappbass
- B26 78680 bass60bpm
- B27 92080 bassriff1
- B28 92079 bassriff0
- B29 107704 bassriff2

### Uncertain / keep out of physical-bass evaluation until manually verified

- B03 88983 Simple Bass — generic title.
- B30 603128 riff dom Cm — uploaded result is bass-heavy/electronic but title does not establish physical bass guitar.

## 4. Recommended diagnostic subset

For a future **non-study T1 smoke/range diagnostic**, use a compact subset that covers distinct failure modes without over-representing one performer or style.

Recommended candidate subset:

1. B05 — bass B1 — low-register short note.
2. B19 — Bass Guitar_C2 [RAW] — raw mono single note.
3. B20 — Fretless bass open D — fretless/open-string sustain.
4. B12 — Picked_BassNote_A — picked articulation.
5. B15 — Simple P bass slap loop — slap articulation.
6. B21 — Bass Guitar three notes — compact multi-note phrase.
7. B23 — clean sustained F bass-string note — long sustain/false-positive stress.
8. B22 — distorted F bass-string note — distortion contrast.
9. B01 — electric bass loop 110 — short regular loop.
10. B06 — death-metal bass loop 240 — fast/heavy articulation.
11. B08 — slap/funk riff 106 — longer expressive phrase.
12. B26 — bass60bpm — slow phrase.

This is a **diagnostic fixture proposal only**, not the independent 12-performance paired study.

## 5. Why this pool is valuable

The uploaded Pixabay set can answer narrow questions cheaply:
- does the frozen T1 path detect low bass at all?
- are single notes stable?
- do repeated/slapped attacks fragment?
- does distortion increase octave/confusion errors?
- does long sustain create false retriggers?
- do mono/stereo and sample-rate differences expose input handling bugs?

It cannot answer:
- separator penalty from mix to isolated stem;
- exact original fingering;
- lead vs rhythm separation;
- commercial product accuracy on full songs.

## 6. Remaining provenance work

Before any asset enters a scored benchmark:
1. resolve its exact Pixabay asset page using its retained numeric asset ID;
2. record contributor display name and published date;
3. snapshot the applicable Pixabay license/terms date;
4. note any asset-specific warning or third-party-rights issue;
5. preserve the uploaded SHA-256 from the catalog;
6. freeze the admitted subset before seeing model output.

## 7. Next execution boundary

No model run is authorized by this provenance review.

The next reversible preparation step is:
- create the exact smoke-test manifest from the 12 candidates above;
- define expected metadata-only checks and failure reporting;
- leave execution disabled;
- then request bounded authorization for a smoke diagnostic separately from the paired real-development study.
