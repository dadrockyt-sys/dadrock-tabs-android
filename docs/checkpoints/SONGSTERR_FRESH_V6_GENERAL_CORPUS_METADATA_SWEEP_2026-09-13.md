# Songsterr Fresh V6 — General Replacement Corpus Metadata Sweep

Date: 2026-09-13 America/Toronto
Branch: `songsterr-fresh-pipeline-v1`
Status: metadata/reference-rights screening only; **no candidate media acquired and no V6 correctness run**

## Scope

This sweep continues the frozen replacement-holdout search after Guitar-TECHS was rejected structurally before correctness. It does not reopen V143/Gomyway, GOAT/reference scoring, GuitarSet/V3, IDMT/V4, V5/FLGD, duration research, or protected-song execution.

A replacement still needs all of the following before media access: explicit usable dataset-audio rights, real guitar, immutable performed note-level onset+pitch truth independent of the evaluated audio, plausible >=1,000 V6-positive evidence volume without duplicate inflation, and defensible untouched status.

## Sources consulted

Authoritative or primary project sources where available:

- Academia Sinica / Music & Culture Technology Lab resource page: https://sites.google.com/view/mctl/resource
- Su, Yu & Yang, ISMIR 2014, *Sparse Cepstral and Phase Codes for Guitar Playing Technique Classification* (official proceedings)
- Stefani, Giudici & Turchet, Audio Mostly 2024, *On the Importance of Temporally Precise Onset Annotations for Real-Time Music Information Retrieval: Findings from the AG-PT-set Dataset*
- Gerelmaab et al. physical-augmentation guitar-chord repository: https://github.com/gerelmaab/Physically_augmented_guitar_chord_dataset
- Gerelmaab et al., Sensors 2020, *Guitar Chord Sensing and Recognition Using Multi-Task Learning and Physical Data Augmentation with Robotics*: https://www.mdpi.com/1424-8220/20/21/6077
- Google Magenta NSynth dataset page: https://magenta.withgoogle.com/datasets/nsynth
- University of Rochester URMP project page: https://labsites.rochester.edu/air/projects/URMP.html
- Magenta/DDSP URMP instrument vocabulary (corroborating corpus instrument inventory): https://github.com/magenta/ddsp/blob/main/ddsp/training/data.py

## Candidate 1 — Guitar Playing Techniques (GPT, Su et al. 2014)

### Public metadata

The ISMIR 2014 paper reports an electric-guitar playing-technique corpus with 6,580 clips and 11,928 notes across seven techniques. The current Music & Culture Technology Lab resource page still points the GPT dataset entry at the historical `mac.citi.sinica.edu.tw/GuitarTranscription/` location.

The 2024 AG-PT-set paper independently reports that the GPT hyperlink had been broken for years and that attempts to obtain the data from the authors had been unsuccessful.

### Gate result

**REJECT / NOT AUDIT-READY: authoritative corpus bytes and current dataset-use terms are not available through a stable release.**

Even though the historical scale could satisfy the evidence-volume requirement, an inaccessible corpus cannot support immutable byte identities, license verification, reference-semantics verification, untouched-history screening, or a frozen reference-blind inventory.

Do not reconstruct GPT from papers, derived features, mirrors of uncertain provenance, or downstream experiments. Reconsider only if an authoritative release with stable files and explicit usable data terms appears.

## Candidate 2 — Physically Augmented Guitar Chord Dataset

### Public metadata

The public repository and Sensors paper describe real acoustic-guitar audio produced by a guitar-playing robot. The dataset covers 97 chord classes, with each chord played under five stroking patterns and manually annotated chord labels. The paper explicitly describes the proposed augmented dataset as containing audio recordings and **only chord labels**.

### Reference-semantics result

**REJECT BEFORE MEDIA ACCESS: no immutable performed per-note onset+pitch reference is established.**

A chord class/root-quality label is not the frozen V6 reference object. V6 admission requires individual performed note identities with onset timing and pitch. Chord voicing knowledge, robot commands, nominal chord templates, signal-derived onset detection, or inferred within-chord note times cannot be substituted after the fact.

The corpus therefore cannot enter the V6 structural audit under the current frozen reference gate, regardless of its real-guitar signal path or duration.

## Candidate 3 — NSynth guitar-family subset

### Public metadata and rights

Google Magenta describes NSynth as 305,979 four-second monophonic note snippets generated from 1,006 instruments in commercial sample libraries. Metadata includes MIDI pitch, velocity, instrument family and source type; `guitar` is one instrument family and `acoustic`, `electronic`, and `synthetic` are source labels. Google releases the dataset under CC BY 4.0.

### Holdout-provenance result

**REJECT FOR V6 EXTERNAL ADMISSION: sampler-generated isolated notes are not a real performed-guitar holdout.**

NSynth is constructed by programmatically ranging sample-library instruments over MIDI pitch and velocity, holding each generated note for three seconds and allowing one second of decay. Even when a source instrument was originally recorded acoustically/electronically, the evaluated corpus item is a sampler-generated note, not an untouched human guitar performance carrying an independent contemporaneous performed-note reference stream.

Its permissive license and large volume do not cure the frozen real-performance/provenance gate. Do not use NSynth as the replacement external V6 admission holdout.

## Candidate 4 — URMP

### Public metadata

The University of Rochester Multi-Modal Music Performance (URMP) corpus provides separately recorded real classical-instrument tracks with MIDI scores and note/pitch annotations. However, the published instrument inventory contains violin, viola, cello, double bass, flute, oboe, clarinet, saxophone, bassoon, trumpet, horn/trombone/tuba-class winds/brass depending on representation; the DDSP loader's canonical URMP vocabulary likewise contains no guitar class.

### Gate result

**REJECT: no guitar signal population exists.**

URMP cannot satisfy the frozen real-guitar holdout requirement and should not be adapted by replacing its instrument family with guitar or by using non-guitar note references as a proxy.

## Landscape implication

This sweep did not identify an audit-ready replacement. It also reinforces that the commonly cited real-guitar note-annotated landscape is unusually small: GuitarSet, IDMT-SMT-Guitar, EGDB/EGDB-PG, François Leduc, GAPS, Guitar-TECHS, EG-Solo, AG-PT-set, and the technique-focused sets already screened dominate the literature surveys reviewed so far. Each currently known route is either already closed/revealed, rights-blocked, reference-provenance-blocked, contaminated/not untouched, unavailable, or structurally unsuitable under the frozen V6 gate.

This is a search result, not a claim that no qualifying corpus can exist. Continue metadata-only discovery for newer or less-cited releases and re-check authoritative rights/reference updates for scientifically strong blocked candidates.

## Decision

No corpus from this sweep is selected. No downloads, media inspection, alignment audit, Basic Pitch run, V6 run, correctness computation, threshold change, or scoring-framework change is authorized by this checkpoint.

Current fail-closed state remains unchanged:

- `modelValidationComplete:false`
- `customerEligibleEvents:0`
- `mayAdvanceDelivery:false`
- duration authority unchanged/paused
- Policy C `UNENROLLED`
- protected song embargoed

## Next allowed action

Continue metadata-only replacement search. Prefer primary dataset release pages, papers, repository rights files, and immutable reference descriptions. A candidate may advance to untouched-history screening and corpus-specific reference-blind audit preregistration only after rights + real-guitar + independent performed note-level onset/pitch reference + plausible evidence volume are all established without media-derived rescue rules.
