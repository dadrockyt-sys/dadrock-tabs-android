# Songsterr Fresh V6 — replacement holdout pre-media batch: GuitarDuets / EG-Solo / Guitar Style Dataset / GPT

Date: 2026-09-15 (America/Toronto)
Branch: `songsterr-fresh-pipeline-v1`
Status: **FROZEN PRE-MEDIA REJECTIONS — NO CANDIDATE PAYLOAD ACCESSED, NO MODEL RUN**

## Scope

This checkpoint continues the metadata/license/alignment/provenance-only replacement-holdout search after the frozen AG-PT-set reference-blind decision C.

The frozen ingress requirement remains unchanged. Before any media/reference payload access, a candidate must establish from public metadata:

1. a real human guitar performance suitable for the holdout domain;
2. a usable public license/right to use the exact scoring media;
3. synchronized note-event ground truth aligned to the exact performance to be scored; and
4. reference provenance sufficiently independent of Basic Pitch/V6 to serve as frozen truth.

A failure at any one pre-media gate closes the candidate. No candidate payload may then be opened merely to see whether it could be rescued.

This search does not alter any closed line. V143/Gomyway and GOAT/reference scoring remain closed. GuitarSet/V3, IDMT/V4, V5/FLGD, Guitar-TECHS, GAPS, EGDB, GuitarJam and AG-PT-set remain in their previously frozen states.

## Candidate 1 — GuitarDuets

Public source inspected:

- Zenodo record `10.5281/zenodo.12802440`
- https://zenodo.org/records/12802440
- dataset description/publication metadata only; `GuitarDuets.zip` was **not** downloaded, previewed or opened.

Public metadata establishes:

- approximately three hours of real and synthesized classical-guitar duet recordings;
- real recordings made with four physical classical guitars;
- WAV format at 44.1 kHz / 16-bit stereo;
- note-level MIDI annotations are described specifically **for the synthesized duets**.

The Zenodo description states that the dataset contains real and synthesized recordings, “with note-level midi annotations for the synthesized duets.” The associated paper likewise describes note-level annotations of the synthesized duets.

### Frozen disposition

**REJECT_PREMEDIA — EXACT REAL-PERFORMANCE NOTE REFERENCE NOT ESTABLISHED**

The real guitar subset is suitable audio in principle, but the public metadata does not establish synchronized note-event MIDI truth for those real performances. The symbolic truth belongs to the synthesized subset, which is not an untouched real-performance holdout.

License does not need to be adjudicated further because the exact-reference gate already fails.

No archive/media/reference payload was accessed.

## Candidate 2 — EG-Solo

Public sources inspected:

- project/demo page: https://bryanyu1997.github.io/EG-Solo_demo/
- ICASSP 2023 paper metadata and later AG-PT-set dataset survey metadata.
- no YouTube performance video was opened or downloaded; no Drive annotation payload was opened.

Public metadata establishes:

- 76 clips / about 40 minutes of professional electric-guitar solo demonstrations;
- 6,833 note events;
- note and playing-technique annotations stored in MIDI-track format;
- explicit pitch/onset/technique labels;
- real-world performances include polyphonic backing tracks;
- source performances are popular-rock-song guitar-solo videos hosted on YouTube.

The later AG-PT-set survey explicitly notes that EG-Solo provides MIDI/technique annotations while the audio was obtained from several YouTube videos and therefore cannot be provided separately.

### Frozen disposition

**REJECT_PREMEDIA — USABLE PUBLIC RIGHTS FOR THE EXACT SCORING MEDIA NOT ESTABLISHED**

EG-Solo clears the note-reference-content gate at the metadata level, but the exact audio to be scored is third-party YouTube material derived from popular-rock-song performances and is not distributed as a licensed dataset audio payload. Public availability of a YouTube video is not a license grant for this holdout pipeline.

No attempt was made to download, rip, cache or inspect any YouTube audio. No annotation payload was opened.

## Candidate 3 — Guitar Style Dataset

Public sources inspected:

- Data in Brief article: `A multimodal dataset for electric guitar playing technique recognition`, DOI `10.1016/j.dib.2023.109842`
- dataset identifier reported by the article: Zenodo `10.5281/zenodo.10075352`
- article/repository metadata only; no WAV, MP4, MuseScore, PDF exercise or split payload was opened.

Public metadata establishes:

- 549 real audiovisual samples from one recruited guitarist;
- three physical electric guitars and three amplifier simulations;
- extracted 48-kHz stereo WAV audio;
- nine playing-technique classes;
- 18 MuseScore exercise files and corresponding PDFs used as exercises for the performances.

The public description presents the MuseScore files as the exercises used for/available alongside recordings and as material that future guitarists can use to expand the dataset. It does **not** establish a released note-event annotation timeline synchronized to each exact recorded take.

### Frozen disposition

**REJECT_PREMEDIA — SYNCHRONIZED NOTE-EVENT GROUND TRUTH NOT ESTABLISHED**

A source exercise score is not, by itself, a timestamped record of the performer’s actual note onsets/offsets in each recording. Frozen V6 scoring cannot manufacture alignment from the score after candidate access.

Dataset/license details do not need further adjudication because the exact synchronized-reference gate already fails.

No dataset payload was accessed.

## Candidate 4 — Guitar Playing Techniques (GPT) dataset (Su et al., 2014)

Public sources inspected:

- ISMIR 2014 paper/proceedings metadata;
- 2024 AG-PT-set onset-annotation survey metadata.

Public literature describes the historical GPT dataset as thousands of individual electric-guitar note clips with playing-technique annotations. However, the 2024 AG-PT-set survey reports that its dataset hyperlink had been broken for years and that attempts by those authors to contact the GPT authors for the data were unsuccessful.

### Frozen disposition

**REJECT_PREMEDIA — PUBLIC DATA ACCESS/IDENTITY NOT AVAILABLE**

A holdout cannot be prospectively frozen against media/reference identities that are not publicly retrievable and verifiable. Historical literature describing a dataset is not sufficient to establish an accessible, immutable candidate payload.

No GPT media/reference payload was accessed.

## Batch result

| Candidate | Real guitar | Usable exact-media rights | Exact synchronized note reference | Independent-reference ingress | Frozen disposition |
| --- | --- | --- | --- | --- | --- |
| GuitarDuets | PASS for real subset | not reached | **FAIL** — note-level MIDI described for synthesized duets | not reached | `REJECT_PREMEDIA` |
| EG-Solo | PASS | **FAIL / not established** for third-party YouTube song media | PASS at metadata level | not needed after rights failure | `REJECT_PREMEDIA` |
| Guitar Style Dataset | PASS | not reached | **FAIL / not established** — exercise MuseScore is not a per-take timestamp alignment | not reached | `REJECT_PREMEDIA` |
| GPT (Su et al. 2014) | historical real guitar described | **FAIL operationally** — public payload unavailable | historical labels described but unverifiable as candidate payload | not reached | `REJECT_PREMEDIA` |

## No execution exposure

For all four candidates:

- no candidate archive was downloaded;
- no candidate audio/video was opened;
- no annotation/reference payload was opened;
- no YouTube audio/video was downloaded or analyzed;
- no Basic Pitch inference occurred;
- no V6 correctness run occurred;
- no scoring constant/tolerance/admission rule changed;
- no EGFxSet execution occurred;
- no AG-PT-set re-audit occurred;
- no V143/Gomyway activity occurred.

## Next safe direction

Continue metadata/license/alignment/provenance search for another untouched real-guitar holdout. A candidate must clear all four frozen pre-media gates before any payload access or one-shot PRE planning.

Do not reopen any candidate frozen elsewhere simply because a newer mirror, wrapper or third-party repository appears in search results. Closed-line decisions remain binding unless the user explicitly reopens them.
