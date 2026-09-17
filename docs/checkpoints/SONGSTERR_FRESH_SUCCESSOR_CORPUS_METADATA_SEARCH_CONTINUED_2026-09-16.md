# Songsterr Fresh — Successor Corpus Metadata Search, Continued

Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Parent search state: `9e92faee8b650449d67042732f05f00739f0778a`
Scope: metadata/provenance research only

Status: **NO ELIGIBLE UNTOUCHED REAL-GUITAR NOTE-BIRTH CORPUS SELECTED**

## Purpose

Continue the successor-corpus search after EGSet12 and GAPS were blocked by the strict untouched-lineage requirement. This continuation does not open candidate corpus media or annotation payloads, run Basic Pitch or the Songsterr-fresh qualifier, inspect candidate correctness, or change `S AND E AND O AND K`.

The required successor remains a corpus with real guitar audio, deterministic performed-note onset + MIDI-pitch ground truth, stable prospective identity, a defensible research-use basis, and no prior Songsterr-fresh lineage exposure.

## Newly reviewed candidates

### GuitarJam — `Julian-br/GuitarJam`

Public dataset metadata describes approximately 2.5 hours / 580 clips of clean monophonic electric-guitar improvisation, recorded DI at 44.1 kHz / 16 bit, under CC0-1.0. Repository history searches found no prior Songsterr-fresh `GuitarJam` commit hit.

However, the public dataset card and repository tree surfaced only WAV audio and no aligned MIDI, note-event CSV, pitch labels, or other deterministic performed-note reference.

Disposition: **REJECT FOR THIS BOUNDARY — real audio but no note-birth pitch reference established.**

No GuitarJam audio was opened.

### AG-PT-set — Zenodo `10159492`

A correction to the earlier coarse metadata assessment is required. The authoritative AG-PT publication describes `note_labels.csv` containing `onset_label_seconds` and ground-truth `pitch_midi`, plus per-file onset/pitch label files. The labeled corpus therefore does provide precise performed-note onset + MIDI-pitch reference for its monophonic acoustic-guitar material.

That scientific suitability does not make it untouched. Full repository commit search found prior lineage exposure:

- `e114eab039e588484d4f91fba153dd56e4a4cbaf` — `checkpoint: freeze AG-PT and EG-Solo triage`;
- `225aaf022fc1fe64077d96e635bd57e99626e10e` — `checkpoint: record AG-PT and EG-Solo triage`;
- `2c7becc8787202be05770bb9d9153f146880e1aa` — `Fix checkpoint AG-PT commit transcription`.

The first of those explicitly records Zenodo `10159492`, DOI `10.5281/zenodo.10159492`, version `v1`, archive identity and dataset facts.

Disposition: **REJECT AS UNTOUCHED — scientifically suitable reference semantics, but prior lineage exposure is proven.**

No AG-PT media or annotation payload was opened in this continuation.

### EG-Solo

Historical AG-PT/EG-Solo triage at `e114eab...` already records EG-Solo metadata, including its professional YouTube-source guitar solos and MIDI note/technique annotations, and blocks it on exact-source use/rights basis.

Disposition: **REJECT AS UNTOUCHED / RIGHTS-UNRESOLVED — already exposed in lineage.**

No EG-Solo media/reference content was opened.

### G&N / TENT electric-guitar solo lead

The same historical triage already records the older G&N electric-guitar solo dataset as a metadata-only fallback lead and identifies the unresolved commercial textbook-CD acquisition/use basis.

Disposition: **NOT UNTOUCHED — already surfaced in lineage; source-use basis also unresolved.**

No G&N media/reference content was opened.

### `magcil/guitar_style_dataset` — Zenodo `10075352`

Public metadata describes 549 electric-guitar technique recordings plus exercise scores in MuseScore/PDF form. Repository commit search for Zenodo `10075352` found no prior hit.

The public dataset description establishes a playing-technique recognition/classification corpus and exercise score materials, but it does not establish synchronized per-performance ground-truth note events whose onsets and MIDI pitches are bound deterministically to every evaluated recording.

Disposition: **REJECT FOR THIS BOUNDARY — no verified aligned note-birth reference for the performed audio.**

No corpus media was opened.

## Search conclusion

The continuation found no corpus that clears all frozen requirements simultaneously.

Important correction: AG-PT is not rejected because it lacks pitch ground truth; it does have pitch + onset ground truth. It is rejected for the present untouched-lineage question because this repository already contains explicit AG-PT triage and identifying metadata.

GuitarJam is a clean-looking real-DI audio source but cannot support the frozen correctness metric without an independent aligned note reference. The Magcil technique corpus likewise does not establish the necessary audio-bound note-event truth from public metadata. EG-Solo and G&N were already exposed historically.

Therefore:

- successor corpus selected: `none`;
- new evaluation PRE created: `no`;
- successor media opened: `0`;
- successor annotation payloads opened: `0`;
- model runs: `0`;
- correctness scores: `0`;
- candidate/threshold changes: `0`;
- V143/Gomyway activity: `0`.

## Next boundary

Continue metadata/provenance-only discovery for genuinely new guitar corpora. For a new promising corpus, search full repository history for exact corpus name, DOI/record ID, source repository and distinctive identifiers before any media access. Only a corpus that remains clean and has deterministic onset + MIDI-pitch truth plus a defensible use basis may receive a new prospective evaluation PRE.

Do not reopen EGSet12, GAPS, AG-PT, EG-Solo, G&N, Guitar-TECHS, GuitarSet, IDMT, FLGD, EGFxSet, EGDB or GOAT under the untouched-lineage label. Do not execute any successor corpus without a new PRE and fresh post-freeze user authorization.

Archived V143/Gomyway remains untouched.
