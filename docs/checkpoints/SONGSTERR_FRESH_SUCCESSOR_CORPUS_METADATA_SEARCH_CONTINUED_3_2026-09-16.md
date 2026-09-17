# Songsterr Fresh — Successor Corpus Metadata Search, Continued 3

Date: 2026-09-16 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Parent state: `152e104b53290dd5ec0f16b96a2e0fe179f68f91`
Scope: metadata/provenance research only

Status: **NO ELIGIBLE UNTOUCHED REAL-GUITAR NOTE-BIRTH CORPUS SELECTED**

## Purpose

Continue the strict successor-corpus search without opening candidate corpus media, annotation payloads, model output, or correctness results. The required successor remains a genuinely new real-guitar population with deterministic performed-note onset + integer-MIDI-pitch truth, stable prospective source identities, a defensible research-use basis, and no prior Songsterr-fresh lineage exposure.

No Basic Pitch inference, Songsterr-fresh qualification, correctness scoring, candidate change, threshold change, or archived V143/Gomyway work is authorized or performed here.

## Newly reviewed candidates

### GOOD-SOUNDS

Public metadata for the GOOD-SOUNDS dataset initially looked relevant because the corpus supplies carefully annotated isolated musical-instrument notes, including attack/onset information and pitch/semitone labels.

However, the published instrument inventory does not contain guitar. The listed instrument classes are flute, cello, clarinet, trumpet, violin, alto/tenor/baritone/soprano saxophone, oboe, piccolo and bass.

Disposition: **REJECT — no guitar population.**

This result also reinforces that generic isolated-note instrument databases must not be promoted merely because their onset/pitch labels are convenient. The present scientific question requires a real guitar population compatible with the frozen Songsterr-fresh qualifier semantics.

No GOOD-SOUNDS audio or annotation payload was opened.

### GM Dataset — Chieppa / Brutti / Paiva, 2025

Paper reviewed:

- `Automatic Guitar Transcription With Deep Neural Networks`;
- Simone Chieppa, Pierpaolo Brutti, Rui Pedro Paiva;
- IEEE Access, 2025;
- DOI `10.1109/ACCESS.2025.3583646`.

The paper introduces a small `GM Dataset` used as a test set with more varied realistic material than the principal training corpus. It includes acoustic and electric guitar recordings, different genres and both pick and fingerstyle playing.

Initial Songsterr-fresh repository-history searches found no prior commit hit for:

- `GM Dataset`;
- `3583646`;
- `Chieppa`.

Therefore this lead is not presently known to be lineage-exposed.

However, the paper's reference-generation procedure is not an independent instrument-captured performed-note truth source. The authors selected existing songs/harmonic progressions, obtained MIDI/tab transcriptions from Ultimate Guitar, corrected/edited those transcriptions in Guitar Pro, asked performers to follow the score as closely as possible, then imported the score MIDI into a DAW and manually aligned it to the newly recorded audio. The transcription was also expanded into six string-specific MIDI tracks.

That is a useful research construction, but for the present untouched correctness boundary it is weaker than a reference generated directly from performed-event capture or independent manual note annotation. The score is an external transcription that is manually aligned to a cover performance, so exact performed-note deviations need not be represented by construction. The material also derives from well-known song transcriptions, which raises a source/use-rights question for any public corpus release.

A search of public records located the paper and institutional record but did not establish an authoritative public GM Dataset archive/version, file identity, license or DOI that could be frozen for a prospective one-shot evaluation.

Disposition: **INITIAL-LINEAGE-CLEAN BUT NOT PRE-READY / REJECT FOR THE PRESENT BOUNDARY — no stable public corpus release was established, and the note truth is score-derived/manual-alignment rather than an independent performed-event reference.**

No GM Dataset audio, MIDI or annotation payload was opened.

## Search observation

Recent guitar-transcription literature continues to emphasize the scarcity of realistic, note-level guitar datasets. The 2025 Chieppa/Brutti/Paiva paper itself discusses the small set of established realistic corpora around GuitarSet, IDMT/EGDB and synthetic alternatives. Those principal real corpora are already exposed or closed in the Songsterr-fresh lineage.

This scarcity is not permission to relax the successor requirements. A model-derived MIDI reference, a score loosely aligned to a performance, a non-guitar instrument corpus, a synthetic corpus, or an inaccessible/unversioned dataset must not be substituted merely to obtain a result.

## Current result

- successor corpus selected: `none`;
- new evaluation PRE created: `no`;
- successor media opened: `0`;
- successor annotation payloads opened: `0`;
- successor model runs: `0`;
- successor correctness scores: `0`;
- candidate/threshold changes: `0`;
- V143/Gomyway activity: `0`.

## Next boundary

Continue metadata/provenance-only discovery, with priority on obscure or recently released datasets from institutional repositories, HCI/performance-analysis projects, hexaphonic/MIDI-pickup studies, and research-data supplements rather than only mainstream automatic-transcription benchmarks.

For any promising candidate:

1. search full repository history for exact corpus name, DOI/record ID, source repository and distinctive identifiers before media access;
2. reject prior lineage exposure immediately;
3. verify stable public source/version identities and defensible research-use rights;
4. verify that onset + MIDI-pitch truth is tied to the actual performed audio and is independent of Basic Pitch or another AMT model being evaluated;
5. only then write a new prospective PRE;
6. update the canonical current-state checkpoint;
7. stop for fresh post-freeze authorization before any media/model/correctness execution.

Archived V143/Gomyway remains untouched.
