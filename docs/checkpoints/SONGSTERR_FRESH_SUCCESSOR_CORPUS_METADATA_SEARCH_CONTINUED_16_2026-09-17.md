# Songsterr Fresh Pipeline — Successor Corpus Metadata Search 17

Date: 2026-09-17 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/provenance discovery only; no evaluation payload access

## Frozen boundary

- Candidate remains exactly `S AND E AND O AND K`.
- No successor PRE or correctness/model run is authorized.
- Do not resume archived V143/Gomyway.
- Do not reopen closed/exposed historical corpus families as untouched.
- Do not open/download candidate audio or annotation payloads before a new exact PRE and fresh post-freeze authorization.
- Required reference remains deterministic actual-performance note onset plus integer-MIDI pitch, independent of Basic Pitch or any other AMT/pitch-estimation output.

## RWC 2.0 Jazz guitar solos — public scrapeability confirmed

The 2026 RWC 2.0 re-release provides a public CC BY-NC 4.0 audio release and a public GitHub annotation repository. The current annotation repository contains aligned MIDI files for the Jazz collection, including the dedicated guitar-solo tracks `RWC_J006` through `RWC_J010`.

Public metadata identifies:

- `RWC_J006` — `Jive (Guitar Solo)`
- `RWC_J007` — `For Two (Guitar Solo)`
- `RWC_J008` — `Lounge Away (Guitar Solo)`
- `RWC_J009` — `Crescent Serenade (Guitar Solo)`
- `RWC_J010` — `Abyss (Guitar Solo)`

The current public aligned MIDI history states that the AIST annotations are the basis, that Johannes Zeitler and Stefan Balke re-aligned the MIDIs with DTW for RWC 2.0 in April 2026, and that all alignments were manually controlled. The repository exposes MIDI files as discrete `.mid` artifacts rather than only framewise F0 tables.

This is useful because pitch identity comes from symbolic human transcription rather than an AMT pitch estimator. However, the modern timing still includes algorithmic audio–MIDI synchronization/warping, so manual control of the alignment is not by itself proof that every note onset is authoritative actual performed-note birth.

Current status remains:

`RWC_J007/J009/J010 = STRONGEST_PUBLIC_SCRAPEABLE_CANDIDATES / RIGHTS_AND_FILE_IDENTITY_CLEAR / HUMAN_TRANSCRIBED_PITCH_TRUTH / CURRENT_PER_NOTE_ONSET_AUTHORITY_NOT_YET_STRONG_ENOUGH_FOR_PRE / FULL_HISTORY_PROVENANCE_NOT_YET_PROVEN`

No RWC MIDI or audio payload was opened.

## Benetos/Dixon hand-edited RWC guitar ground truth — artifact existence reconfirmed

Primary Benetos/Dixon transcription material gives stronger historical semantics than the modern re-warped MIDI.

The ICASSP 2011 material identifies RWC Jazz No. 6, 7, 8 and 9 as guitar in a 12-excerpt test set. The paper states that the supplied MIDI contained note errors and unrealistic durations, and therefore aligned ground-truth MIDI was created for the first 23 seconds of each recording using Sonic Visualiser. Later Benetos/Dixon work is even more explicit: the ground truth was created using Sonic Visualiser for spectrogram visualization and MIDI editing, and evaluation compared transcription to those ground-truth MIDI files at a 10 ms scale.

The surviving public Benetos transcription-examples page exposes original and synthesized-transcription audio examples for RWC guitar recordings No. 7 and No. 9, but does not expose the hand-edited ground-truth `.mid` files themselves. Broad searches of the author pages, QMUL/City resources and indexed filenames did not locate a stable public copy of those GT MIDI artifacts.

Current status:

`TECHNICALLY_STRONG_MANUAL_23S_GUITAR_GT / EXACT_PUBLIC_GT_FILE_NOT_LOCATED / RIGHTS_FOR_DERIVED_GT_NOT_YET_ESTABLISHED / NOT_PRE_READY`

The file hunt remains high value, especially for J007 and J009 because those overlap the strongest current public RWC candidates.

## RWC Instrument Sound 2.0 — diagnostic value, not correctness truth

The 2026 RWC Instruments release remains highly scrapeable and stable:

- Zenodo DOI `10.5281/zenodo.17170844`
- version `v1`
- `RWC-I.zip`
- MD5 `fb5789335fe68abdc09929618e9f0403`
- CC BY-NC 4.0

It includes guitar families and detailed public metadata with instrument/style/dynamics/file identities and pitch ranges. Older literature describes files as sequences of individual notes over an instrument range separated by mute gaps.

A useful correction was established in this pass: original RWC documentation/literature explicitly notes that the Musical Instrument Sound Database itself did not receive the same formal note-labeling attention as the musical-piece databases. Therefore earlier secondary descriptions of these samples as manually annotated into MIDI must not be treated as authoritative evidence that a reusable event-level MIDI truth exists in the public RWC-I release.

Current status:

`AUXILIARY_HIGH_VALUE_PUBLIC_REAL_GUITAR_NOTES / CHROMATIC_SEQUENCE_AND_RANGE_METADATA_AVAILABLE / AUTHORITATIVE_PER_EVENT_ONSET_PLUS_INTEGER_MIDI_MAPPING_NOT_YET_PROVEN`

This keeps RWC-I useful for diagnostics and possible future mapping research without promoting it to correctness evidence.

## Provenance search note

Current project commit-message searches for `RWC` and `RWC_J006` returned no hit. This is not accepted as full-history lineage proof. A candidate cannot become PRE-ready until a defensible full-history audit covers corpus names, RWC IDs, Zenodo IDs/DOIs, repository identifiers and distinctive file/blob identities.

## State after Search 17

- Eligible successor selected: `no`.
- New PRE: `none`.
- Successor run authorization: `none`.
- Successor media opened: `0`.
- Successor annotation payloads opened: `0`.
- Model/correctness runs: `0`.
- Correctness scores: `0`.
- Candidate/threshold changes: `0`.
- V143/Gomyway activity: `0`.
- Real correctness: `unknown`.

## Highest-value next steps

1. Continue targeted archive/file-name hunting for the Benetos/Dixon hand-edited 23-second RWC guitar GT MIDIs, especially J007 and J009.
2. Search public RWC issues/PRs/history for affirmative J007/J009/J010 timing-quality evidence rather than treating absence from a problem list as proof.
3. Continue metadata-only discovery for another public real-guitar corpus whose note events are manually/directly/symbolically authored and whose onset timing is authoritative at the individual-note level.
4. Keep RWC-I/MINST as auxiliary diagnostic sources only unless an authoritative event-to-pitch mapping is established without audio pitch estimation.
5. Complete full-history provenance before any candidate PRE.
6. Preserve the no-payload boundary.
