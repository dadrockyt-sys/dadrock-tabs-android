# Songsterr Fresh Pipeline — Successor Corpus Metadata Search 11

Date: 2026-09-17 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Scope: metadata/provenance discovery only

## Frozen boundary

- No successor PRE or model/correctness run is authorized.
- Do not resume archived V143/Gomyway.
- Do not reopen closed/exposed historical corpus families as “untouched.”
- No successor corpus media or annotation payload may be opened before the prospective source/rights/reference/provenance gates are met, a new exact PRE is frozen, and fresh post-freeze user authorization is received.
- Required correctness truth remains deterministic actual-performance note onset + integer-MIDI pitch, tied to the recorded performance and independent of Basic Pitch or any other AMT/pitch-estimation output.

## New lead — Let’s Frets! capacitive fretboard

Primary/public metadata:

- CHI 2021 DOI `10.1145/3411764.3445595`, `Let’s Frets! Assisting Guitar Students During Practice via Capacitive Sensing`.
- The system replaces the first four frets with capacitive fretboard components and uses six capacitive touch sensors per fret, one per string, allowing direct observation of touched fret/string positions rather than inferring them from audio pitch.
- Public source repository: `Pinyto/lets-frets`.
- GitHub repository metadata describes the repository as source code and 3D models for the paper.
- The repository README likewise says it contains source code and 3D models and licenses those software/model assets under GPLv3.
- Repository root/tree contains 3D models, Android/control software, an APK and Raspberry-Pi/client code; no `.wav` or `.csv` files were found in the published recursive tree.
- GitHub releases list is empty.

Reference-mechanism assessment:

`PROMISING_INDEPENDENT_PHYSICAL_FRET_STRING_SENSING_MECHANISM`

The capacitive sensing principle is materially different from GIHME/DoMP/MMIP/Fretiq: it directly detects finger/fret/string contact state and does not need audio pitch estimation to identify a fretted string position.

Corpus assessment:

`REJECT_NO_PUBLIC_SYNCHRONIZED_AUDIO_NOTE_EVENT_CORPUS`

The public artifact is an HCI prototype/software/model release, not a stable evaluation corpus containing synchronized real guitar audio plus timestamped per-note sensor events and an immutable file manifest. Therefore the sensing mechanism is informative for future discovery, but Let’s Frets itself is not PRE-ready and cannot be used as the successor correctness corpus.

No guitar-performance media or annotation payload was opened/downloaded.

## New lead — instrumented guitar finger-position / plectrum sensing (NIME 2013)

Public metadata for `Finger Position and Pressure Sensing Techniques for String and Keyboard Instruments` (NIME 2013; Zenodo DOI `10.5281/zenodo.1178538`) describes a guitar instrumented with a linear potentiometer for left-hand finger position sensing and a sensor-equipped plectrum. The work demonstrates direct physical sensing with high temporal/spatial resolution.

Prospective corpus status:

`REJECT_METHOD_ONLY_NO_PUBLISHED_QUALIFYING_CORPUS`

No stable public synchronized guitar-audio corpus with deterministic per-note onset + integer-MIDI annotations was established from the surfaced record. The paper is useful as evidence that direct physical reference acquisition is technically possible, not as an evaluation corpus.

No corpus payload was opened.

## Optical motion-capture guitar corpus revisited only to resolve reference mechanism

The 2019 Frontiers paper `Finger-String Interaction Analysis in Guitar Playing With Optical Motion Capture` describes synchronized guitar audio and motion data with about 1,500 plucks. However, the paper explicitly states that pitch and onsets are extracted from the audio signal; those audio-derived events then anchor motion analysis.

Status remains:

`REJECT_REFERENCE_NOT_INDEPENDENT_OF_AUDIO_PITCH_ONSET_ESTIMATION`

The optical stream therefore does not rescue the correctness reference under the frozen independence gate.

No corpus payload was opened.

## 2025 optical/electro-acoustic sensor benchmark

The Sensors 2025 paper `Performance of Acoustic, Electro-Acoustic and Optical Sensors in Precise Waveform Analysis of a Plucked and Struck Guitar String` studies a controlled/simplified electric-guitar setup using microphone, magnetic pickup and laser Doppler vibrometry for waveform/sensor comparison.

Prospective status:

`REJECT_NOT_A_QUALIFYING_NOTE_EVENT_PERFORMANCE_CORPUS`

It is a physical sensor/waveform benchmark rather than a stable musical-performance dataset with independent timestamped onset+MIDI note truth.

## MUSERC as a non-guitar reference-mechanism comparator

MUSERC demonstrates that synchronized audio/video plus a direct finger-position sensor can be publicly packaged as a dataset, but its instrument population is cello.

Status:

`REJECT_NON_GUITAR_POPULATION`

It is useful only as evidence that the desired direct-sensor ground-truth pattern is feasible in another string instrument.

## Other hardware/prototype leads

Additional searches surfaced guitar support systems, smart-instrument patents and capacitive/stringless interfaces that measure fret/string/finger state, but no qualifying public corpus with synchronized real guitar audio plus exact independent note onset + integer-MIDI truth was established.

## GM watch

No authoritative GM Dataset public package, immutable release/file manifest, or dataset-specific license/research-use grant was established in this pass. GM remains:

`UNRESOLVED_STABLE_PUBLIC_RELEASE_AND_DATASET_RIGHTS / REFERENCE_ALIGNMENT_POTENTIALLY_ACCEPTABLE_FROM_METADATA / NOT_PRE_READY`

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

The direct-sensing search now has a concrete reference-mechanism archetype: instrumented fret/string contact sensing such as Let’s Frets, but the missing element is a public synchronized audio+sensor corpus. Continue metadata-only discovery specifically for **recorded study datasets generated by instrumented guitars**, including CHI/NIME/TEI supplementary data, institutional repositories, theses, OSF/Zenodo/Figshare records, and author research-data deposits. Also continue the GM release/license watch.

A candidate may advance only if all of the following are established before payload access:

1. stable public source/version/file identity and defensible data-use rights;
2. real guitar performance audio suitable for the frozen evaluation boundary;
3. direct or manually reconciled actual-performance note onset timestamps;
4. integer-MIDI pitch/string/fret identity independent of AMT/pitch estimation;
5. clean full-history Songsterr-fresh provenance;
6. then freeze exact PRE for unchanged `S AND E AND O AND K` and stop for fresh user authorization.
