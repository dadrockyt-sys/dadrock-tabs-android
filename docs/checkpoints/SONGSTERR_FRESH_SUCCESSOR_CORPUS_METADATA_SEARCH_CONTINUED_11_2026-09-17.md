# Songsterr Fresh Pipeline — Successor Corpus Metadata Search 12

Date: 2026-09-17 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/provenance discovery only

## Frozen boundary

No successor PRE or correctness/model run is authorized. No candidate media or annotation payload was opened. Archived V143/Gomyway remains untouched.

## Capacitive-fret sensing descendants / related work

### Guaus et al. — A Left Hand Gesture Caption System for Guitar Based on Capacitive Sensors

NIME 2010, DOI `10.5281/zenodo.1177783`.

Primary-paper metadata shows a capacitive-sensor system mounted on a real guitar fingerboard. The sensor stream is converted to MIDI/PitchBend and synchronized with guitar audio in a sequencer. This is materially closer to the frozen reference requirement than audio pitch tracking because the left-hand state is sensed physically rather than inferred from the waveform.

However, the surfaced public record is the conference paper itself; no public performance corpus/release with immutable synchronized audio + exact note-event annotation files was established. The sensor stream is described as gesture/fret-position data and PitchBend-resolution control, not a released event corpus with deterministic actual note-onset + integer-MIDI pitch semantics.

Prospective status:

`REJECT_METHOD_ONLY_NO_PUBLISHED_QUALIFYING_SYNCHRONIZED_EVENT_CORPUS`

No paper-supplement payload or performance data was opened.

### Let’s Frets! descendants

Fresh searches did not surface a later public synchronized dataset built from the 2021 Let’s Frets capacitive-fret prototype. Public material still points to code/3D models/prototype evaluation rather than an immutable real-performance corpus with synchronized guitar audio and exact note-event truth.

Status remains:

`PROMISING_INDEPENDENT_PHYSICAL_FRET_STRING_SENSING_MECHANISM / REJECT_NO_PUBLIC_SYNCHRONIZED_AUDIO_NOTE_EVENT_CORPUS`

### Capacitive Touch Guitar / Air Guitar / Diapasonix

These projects demonstrate capacitive touch and direct MIDI generation, but they are electronic or stringless instruments / controllers rather than qualifying recordings of a conventional real guitar performance paired with independent event truth.

Status:

`REJECT_NON_QUALIFYING_INSTRUMENT_OR_NO_REAL_GUITAR_AUDIO_CORPUS`

## Articulation-analysis lineage — Ozaslan/Guaus/Palacios/Arcos

The related `Identifying Attack Articulations in Classical Guitar` work uses professional classical-guitar recordings containing single articulations and short melodies, but the public metadata describes an analysis system combining audio algorithms to identify articulations. No authoritative public synchronized corpus with independent note-onset + integer-MIDI event truth was established.

Prospective status:

`REJECT_NO_PUBLIC_INDEPENDENT_NOTE_EVENT_REFERENCE_CORPUS`

## Direct-laser sensing follow-up

The 2024 Pesatori/Norgia laser system remains a promising *reference mechanism* because it directly measures finger positions and uses a pluck detector to produce direct MIDI. Fresh searches still did not identify a public synchronized evaluation corpus with paired real-guitar audio and timestamped event truth; the paper states data are contained in the article.

Status:

`PROMISING_DIRECT_REFERENCE_MECHANISM / REJECT_NO_PUBLIC_QUALIFYING_CORPUS`

## GM watch

No authoritative GM Dataset package, immutable release/file manifest, or dataset-specific license/research-use grant surfaced in this pass. GM remains unresolved and not PRE-ready.

## State after this pass

- Eligible successor selected: `no`.
- New PRE: `none`.
- Successor run authorization: `none`.
- Successor media opened: `0`.
- Successor annotation payloads opened: `0`.
- Model/correctness runs: `0`.
- Candidate/threshold changes: `0`.
- V143/Gomyway activity: `0`.
- Real correctness: `unknown`.

## Next discovery direction

The strongest pattern remains clear: several direct physical sensing systems could in principle satisfy reference independence, but none reviewed so far publishes the required synchronized real-guitar audio + immutable exact note-event truth corpus. Continue metadata-only search for released datasets or supplements from these sensor lineages and for manually reconciled note-event datasets whose source annotations are explicitly independent of audio AMT/pitch estimation.
