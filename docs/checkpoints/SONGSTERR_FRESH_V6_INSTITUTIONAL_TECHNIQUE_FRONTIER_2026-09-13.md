# Songsterr Fresh V6 — Institutional / Technique Dataset Frontier

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: **metadata/reference/rights screening only — no candidate media acquired and no V6 correctness exposed**

## Scope

Continue the replacement untouched-holdout search outside generic guitar dataset indexes, focusing on institutional multimodal projects, technique-recognition corpora, Mendeley/Figshare-style repositories and recently cited dataset names.

This does not reopen archived V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research or protected-song execution.

## University of Manchester / NOVARS AI Guitar Assistant — substantial unreleased multimodal data, reference insufficient

Primary 2025 article:
https://www.frontiersin.org/journals/computer-science/articles/10.3389/fcomp.2025.1549335/full

Related institutional records:
- https://discovery.ucl.ac.uk/id/eprint/10209747/
- https://discovery.ucl.ac.uk/id/eprint/10169054/

Published project facts:
- 21 guitarists (11 amateur / 10 professional under the project's classification);
- recording sessions at the NOVARS Research Centre, University of Manchester;
- performers execute designed musical exercises;
- captured streams include two Myo-armband biometric streams, GoPro video and microphone audio through a MOTU interface;
- custom Max patches handle synchronized acquisition/metronome timing;
- four files per exercise: two biometric CSVs, audio, video;
- reported total collected performance data: 61.93 GB;
- the 2025 article explicitly says the multimodal performance data are not the subject of that publication and are intended for future work.

The published acquisition design reviewed does **not** establish a contemporaneous independent note-level MIDI/performed-onset stream. A known exercise, metronome, biometric trace, video, or later score alignment cannot substitute for immutable performed note onset+pitch truth under the frozen V6 gate.

**Disposition: institutional lead only, not audit-ready.** Do not seek/access participant media for V6 under current evidence. Reconsider only if a future authoritative release establishes explicit usable data rights plus an independent performed note-level onset+pitch reference and sufficient immutable population identities.

## MagCIL / `guitar_style_dataset` — real technique corpus, reference semantics fail

Primary sources reviewed:
- Data in Brief article: `A multimodal dataset for electric guitar playing technique recognition`, DOI `10.1016/j.dib.2023.109842`;
- dataset/release DOI `10.5281/zenodo.10075352`;
- GitHub repository `magcil/guitar_style_dataset`.

Published facts:
- 549 WAV recordings plus 549 MP4 videos;
- nine electric-guitar technique classes;
- one recruited player;
- three guitars and three simulated amplifiers;
- 18 MuseScore/PDF exercise definitions;
- technique-class/fold metadata for recognition experiments.

The public structure is a playing-technique classification dataset. Exercise scores and class labels do not establish immutable performed per-note onset+pitch truth for each real recording. Converting MuseScore exercises into nominal MIDI, aligning them to audio, or transcribing the evaluated audio would violate the frozen independent-reference requirement.

Rights are also not cleanly promoted by the repository's software license: the GitHub `LICENSE` explicitly grants an MIT license to the **Software** and associated documentation. That does not by itself establish that the 13+ GB performance media have a permissive commercial/product-validation data license. The associated publication is distributed under non-commercial/no-derivatives Creative Commons terms in surfaced copies. Regardless, reference semantics already fail independently.

**Disposition: reject before media access for V6 admission.** Do not infer note truth from MuseScore, technique labels, video or evaluated audio.

## Mendeley / Figshare targeted repository sweep — no qualifying note-reference corpus surfaced

A targeted search of public research-data repositories surfaced guitar-related collections, but the potentially relevant ones do not satisfy the frozen combination of real performance + independent performed note truth + volume:

### Box-shaped acoustic-guitar fret-note collections

Mendeley records such as:
- `10.17632/k5hvbmdt47.1` (string 1, 20 frets, plectrum);
- `10.17632/pfv2jvf8bk.1` (string 1, 20 frets, finger plucking).

These are small isolated-note/fret collections. Even broadening to analogous fret/string recordings would not establish a sufficiently large diverse external holdout here, and the record metadata does not provide an independent within-file performed onset timestamp stream.

**Disposition: not a V6 admission candidate.**

### Traditional Portuguese instrument dataset

Mendeley `10.17632/yjdfnymgf2.1` contains 1,734 five-second field-recording clips, including Portuguese guitar/Viola Braguesa classes, but it is an instrument-classification corpus derived from ethnographic video audio and licensed CC BY-NC-SA 4.0. It provides class/take metadata, not independent note-level performed truth.

**Disposition: reject on rights/reference semantics; not an isolated-guitar note-reference holdout.**

## Current implication

The institutional/technique repository pass did not produce an audit-ready replacement. It reinforces a consistent split:

- large/interesting real-performance collections often lack independent performed note-level onset+pitch reference or usable product-validation rights;
- independently pitch-labeled isolated-note collections are too small/narrow and typically lack performed-onset timestamps;
- technique-class datasets expose class/exercise labels rather than exact performed notes.

The remaining high-value search targets are therefore:
1. explicit rights-holder/private corpora with simultaneous independently sensed guitar note events;
2. authoritative rights clarification for AG-PT-set;
3. future releases of institutional multimodal data only if their note-reference semantics materially improve;
4. the already-documented purpose-built untouched holdout design, if the user later explicitly selects/acquires that route.

## Authority unchanged

No media was downloaded/inspected. No corpus is selected. No Basic Pitch/V6 correctness, threshold tuning, archived-line scoring, protected-song execution, procurement, performer/vendor contact or production promotion is authorized.

Fail-closed state remains:
- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed
