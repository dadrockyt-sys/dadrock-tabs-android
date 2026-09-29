# Independent Real-Development Web Source Review V1

Date: 2026-09-28  
Status: **WEB SOURCING COMPLETE — CANDIDATES ONLY, NO AUDIO DOWNLOADED OR INFERRED**

## Purpose

This review was created after the independent real-development design freeze. It identifies web-hosted real audio candidates that can satisfy the first-tranche evaluation contract without reopening P1/P2/P3 or reusing synthetic data.

The sources were discovered on 2026-09-28 after the design freeze. None of these web candidates has been used for model output, tuning, threshold selection, architecture selection, or decoder selection in this project.

## Source policy

Primary source: Pixabay sound effects.

Pixabay's current Content License summary states that content may be used for free and may be modified/adapted, while standalone redistribution is prohibited. This project should therefore:
- use the files only for internal evaluation;
- preserve the source page and creator metadata;
- never commit or redistribute the original audio in the public repository;
- keep only hashes, provenance, annotations and derived evaluation receipts in Git.

License summary reviewed:
- https://pixabay.com/service/license-summary/

No download or model inference occurred during this sourcing pass.

## Positive candidates

These are **candidates**, not yet frozen intake clips. Final admission still requires download, hashing, duration verification, human annotation before model output, and no-overlap review.

| ID | Candidate | Duration | Coverage value | Source |
|---|---|---:|---|---|
| P01 | Guitar Riff in E Minor 95 BPM (Dry) — SunnyScy | 10 s | dry electric, riff, chords | https://pixabay.com/sound-effects/musical-guitar-riff-in-e-minor-95-bpm-dry-475013/ |
| P02 | Jingle - clean guitar - funky and rock style — ShidenBeatsMusic | 7 s | clean electric, funky articulation | https://pixabay.com/sound-effects/jingle-clean-guitar-funky-and-rock-style-21690/ |
| P03 | Clean Electric Guitar Loop — mooncubedesign/Freesound | 5 s | clean electric, loop/repeated attacks | https://pixabay.com/sound-effects/musical-clean-electric-guitar-loop-83895/ |
| P04 | Electric guitar Metal Riff — davidkyoku/Freesound | 7 s | distorted electric, metal riff | https://pixabay.com/sound-effects/musical-electric-guitar-metal-riff-107087/ |
| P05 | Midwest Emo Guitar Sample B Minor Clean 120 bpm — Farran_Ez | 10 s | clean electric, melodic/chordal | https://pixabay.com/sound-effects/musical-midwest-emo-guitar-sample-b-minor-clean-120-bpm-448316/ |
| P06 | Midwest Emo Guitar Sample B Minor Clean 120 bpm — Farran_Ez | 9 s | clean electric, alternate phrase | https://pixabay.com/sound-effects/musical-midwest-emo-guitar-sample-b-minor-clean-120-bpm-448311/ |
| P07 | Guitar jingle - Hard rock style — ShidenBeatsMusic | 5 s | distortion, hard-rock/heavy-metal | https://pixabay.com/sound-effects/musical-guitar-jingle-hard-rock-style-21867/ |
| P08 | Electric Guitar Accent — Black_Kumizhi | 10 s | isolated attack/single-note style evidence | https://pixabay.com/sound-effects/musical-electric-guitar-accent-485733/ |
| P09 | Jingle - Slide guitar — ShidenBeatsMusic | 10 s | slide guitar, blues, alternate tuning | https://pixabay.com/sound-effects/jingle-slide-guitar-22108/ |
| P10 | Bossa Nova Eletric Guitar Loop — Liecio | 8 s | clean chord sequence, jazz/bossa | https://pixabay.com/sound-effects/musical-bossa-nova-eletric-guitar-loop-258055/ |
| P11 | Clean Country Lick-Bend — u_1aiqn32afi | 7 s | clean lick, bend, twang | https://pixabay.com/sound-effects/musical-clean-country-lick-bend-289052/ |
| P12 | AcousticGuitar-C-Chord — spitefuloctopus/Freesound | 4 s | explicit palm-muted major chord | https://pixabay.com/sound-effects/musical-acousticguitar-c-chord-103782/ |
| P13 | Em Guitar Chord Strum 10 — SOUND_GARAGE | 9 s | repeated chord strums | https://pixabay.com/es/sound-effects/musical-em-guitar-chord-strum-10-309542/ |
| P14 | AloneInTheRoom(guitar) — Freesound community | 9 s | acoustic E-major short arpeggio | https://pixabay.com/sound-effects/search/acousticguitar/ |
| P15 | Baritone Guitar with mute — Freesound community | 6 s | muted baritone scale | https://pixabay.com/sound-effects/search/baritone%20guitar/ |
| P16 | electric guitar strumming 3 — Freesound community | 9 s | electric strumming/chord attack | https://pixabay.com/sound-effects/search/guitar%20strumming/ |
| P17 | Guitar Riff — mleckert82 | 7 s | acoustic steel-guitar riff | https://pixabay.com/sound-effects/search/guitar-riff/ |
| P18 | 8-string distortion guitar E1 — Freesound community | 7 s | distorted electric single notes | https://pixabay.com/sound-effects/search/distortion%20guitar/ |

Nominal positive duration from these 18 candidates: **139 seconds**, exceeding the 90-second first-tranche minimum if all pass download/annotation screening.

### Legato reserve candidate

A dedicated legato source was found:
- **legato in B Standard — Imij**, 43 s
- https://pixabay.com/sound-effects/musical-legato-in-b-standard-322656/

It is too long for direct admission but is a strong reserve source. If needed, select and freeze one 4–10 second annotated segment **before any model output**. Do not choose a segment based on candidate-model behavior.

## Negative-only candidates

These are chosen to stress false-positive behavior without target guitar notes. Final clips still require download and human confirmation that no target guitar is audible.

| ID | Candidate | Duration | Negative content | Source |
|---|---|---:|---|---|
| N01 | Typing with Keyboard — DRAGON-STUDIO | 5 s | computer keyboard clicks | https://pixabay.com/sound-effects/film-special-effects-typing-with-keyboard-435489/ |
| N02 | Atmospheric Drums — DRAGON-STUDIO | 5 s | percussion/drums | https://pixabay.com/sound-effects/search/atmospheric%20drums/ |
| N03 | Applause - sound effect — PWLPL | 5 s | applause/clapping | https://pixabay.com/sound-effects/search/applause/ |
| N04 | Short Crowd Cheer — Freesound community | 7 s | crowd/cheering | https://pixabay.com/sound-effects/search/short%20crowd%20cheer/ |
| N05 | speech-dramatic-female — Freesound community | 7 s | speech/voice | https://pixabay.com/sound-effects/search/speech/ |
| N06 | Computer keyboard typing — MatthewVakaliuk73627 | 10 s | keyboard typing | https://pixabay.com/sound-effects/search/computer%20keyboard%20typing/ |

Nominal negative duration: **39 seconds**, exceeding the 30-second first-tranche minimum if all six pass human no-guitar screening.

## Why this set is useful

The positive pool spans multiple creators/capture sources and includes:
- clean and distorted electric guitar;
- acoustic and baritone guitar;
- single-note attacks;
- repeated attacks/loops;
- bends and slide;
- palm muting;
- strumming;
- riffs;
- arpeggio;
- dyad/chord-like and full chord material.

This is materially better for the independent-development goal than taking all 18 positives from one historical research corpus or one performer.

The negative pool contains transient-rich non-guitar audio, which is more informative for false-positive testing than silence alone.

## Exclusions

Do not use as V1 intake:
- Guitar-TECHS P1/P2/P3 material;
- P1 or P2 clips already examined in this project;
- P3;
- synthetic renders;
- any previously tuned/evaluated audio;
- music clips with drums/bass/mix contamination unless the target guitar can be independently and reliably annotated.

IDMT-SMT-Guitar was reviewed but is **not selected** for this V1 because its CC BY-NC-ND evaluation license creates unnecessary downstream-use ambiguity for this product project.

GuitarSet is a useful CC-BY annotated resource and remains a backup option, but this V1 web shortlist intentionally favors newly sourced independent creator clips to reduce overlap risk with common research benchmarks.

## Next action

1. Download only the shortlisted candidate files.
2. Preserve source URL, title, creator and license-page snapshot/metadata.
3. Hash original bytes immediately.
4. Human-audition every clip and reject mixed/ambiguous candidates before model inference.
5. For clips longer than the contract, choose any crop only from audio/annotation quality—not model behavior—and freeze exact byte/sample/time boundaries.
6. Annotate pitch/onset events before candidate-model output.
7. Populate the frozen intake manifest.
8. Run the pure intake validator.
9. Freeze the zero-inference verification receipt.
10. Only then may the bounded real-development inference begin.

No candidate above is admitted merely because it appears in this review.
